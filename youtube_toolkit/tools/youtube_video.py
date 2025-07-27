"""YouTube video information and transcript tools"""
import json
import time
from typing import Dict, Any, Optional, Literal
from mcp import types
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.errors import HttpError
from youtube_toolkit.tools.youtube_base import (
    YouTubeAPIClient, TranscriptCache, parse_video_id, 
    parse_duration, format_error_response, extract_intro,
    extract_outro, extract_main_samples
)
from youtube_toolkit.config import load_config
from youtube_toolkit.logging_config import logger

# Cache for video categories to avoid repeated API calls
_category_cache = {}

def _get_category_name(youtube, category_id: str) -> str:
    """
    Get category name from category ID, using cache when possible.
    
    Args:
        youtube: YouTube API client instance
        category_id: Category ID to look up
        
    Returns:
        Category name or empty string if not found
    """
    if not category_id:
        return ""
        
    # Check cache first
    if category_id in _category_cache:
        return _category_cache[category_id]
    
    try:
        # Fetch category details
        request = youtube.videoCategories().list(
            part='snippet',
            id=category_id
        )
        response = request.execute()
        
        if response.get('items'):
            category_name = response['items'][0]['snippet']['title']
            _category_cache[category_id] = category_name
            return category_name
    except Exception as e:
        logger.warning(f"Failed to fetch category name for ID {category_id}: {e}")
    
    return ""

def youtube_get_video_metadata(
    video_id: str,
    include_statistics: bool = True
) -> types.TextContent:
    """
    Fetch metadata for a single YouTube video.
    
    Args:
        video_id: YouTube video ID or full URL
        include_statistics: Include view/like/comment counts
    
    Returns:
        Video metadata as JSON
    """
    try:
        # Parse video ID from URL if needed
        video_id = parse_video_id(video_id)
        
        # Get YouTube API client
        youtube = YouTubeAPIClient.get_instance()
        
        # Build request parts - need additional parts for v3 spec
        parts = ['snippet', 'contentDetails', 'status']
        if include_statistics:
            parts.append('statistics')
        
        # Make API request
        request = youtube.videos().list(
            part=','.join(parts),
            id=video_id
        )
        response = request.execute()
        
        if not response.get('items'):
            return types.TextContent(
                type="text",
                text=json.dumps({
                    "error": {
                        "type": "not_found",
                        "message": f"Video {video_id} not found"
                    }
                })
            )
        
        # Extract video data according to v3 spec
        video = response['items'][0]
        snippet = video['snippet']
        content_details = video['contentDetails']
        status = video['status']
        
        # Build thumbnail structure
        thumbnails = snippet.get('thumbnails', {})
        thumbnail_obj = {
            "default": thumbnails.get('default', {}).get('url', f"https://i.ytimg.com/vi/{video_id}/default.jpg"),
            "medium": thumbnails.get('medium', {}).get('url', f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg"),
            "high": thumbnails.get('high', {}).get('url', f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"),
            "standard": thumbnails.get('standard', {}).get('url', f"https://i.ytimg.com/vi/{video_id}/sddefault.jpg"),
            "maxres": thumbnails.get('maxres', {}).get('url', f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg")
        }
        
        # Get channel subscriber count (requires additional API call)
        channel_request = youtube.channels().list(
            part='statistics',
            id=snippet['channelId']
        )
        channel_response = channel_request.execute()
        subscriber_count = 0
        if channel_response.get('items'):
            subscriber_count = int(channel_response['items'][0]['statistics'].get('subscriberCount', 0))
        
        result = {
            "video_id": video['id'],
            "title": snippet['title'],
            "description": snippet['description'],
            "channel": {
                "id": snippet['channelId'],
                "title": snippet['channelTitle'],
                "subscriber_count": subscriber_count
            },
            "published_at": snippet['publishedAt'],
            "duration": content_details['duration'],
            "duration_seconds": parse_duration(content_details['duration']),
            "thumbnail": thumbnail_obj,
            "tags": snippet.get('tags', []),
            "category_id": snippet.get('categoryId', ''),
            "category_name": _get_category_name(youtube, snippet.get('categoryId', '')),
            "statistics": {
                "view_count": int(video.get('statistics', {}).get('viewCount', 0)),
                "like_count": int(video.get('statistics', {}).get('likeCount', 0)),
                "dislike_count": None,  # YouTube removed dislike counts from API
                "comment_count": int(video.get('statistics', {}).get('commentCount', 0))
            } if include_statistics else None,
            "privacy_status": status.get('privacyStatus', 'unknown'),
            "embeddable": status.get('embeddable', False),
            "live_broadcast_content": snippet.get('liveBroadcastContent', 'none'),
            "default_language": snippet.get('defaultLanguage'),
            "default_audio_language": snippet.get('defaultAudioLanguage'),
            "_metadata": {
                "api_quota_cost": 3,  # 1 for video + 1 for channel + potential category lookup
                "fetched_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
        }
        
        # Remove statistics if not requested
        if not include_statistics:
            del result['statistics']
        
        return types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )
        
    except Exception as e:
        logger.error(f"Error fetching video info: {e}")
        return types.TextContent(
            type="text",
            text=json.dumps(format_error_response(e))
        )

def youtube_get_video_transcript(
    video_id: str,
    extract_mode: Literal["full", "analysis", "intro_only", "outro_only"] = "full",
    use_cache: bool = True,
    delay_seconds: Optional[float] = None
) -> types.TextContent:
    """
    Fetch and cache video transcript with smart extraction options.
    
    Args:
        video_id: YouTube video ID
        extract_mode: Extraction mode for transcript
        use_cache: Use cached transcript if available
        delay_seconds: Rate limit delay (uses default if None)
    
    Returns:
        Transcript data based on extraction mode
    """
    try:
        # Parse video ID
        video_id = parse_video_id(video_id)
        
        # Get config
        config = load_config()
        if delay_seconds is None:
            delay_seconds = config.default_transcript_delay
        
        # Enforce minimum delay to avoid IP blocking
        if delay_seconds < 1.0:
            logger.warning(f"Delay of {delay_seconds}s is too low, using minimum of 1.0s to avoid IP blocking")
            delay_seconds = 1.0
        
        # Check cache
        cache = TranscriptCache()
        cached_data = None
        if use_cache:
            cached_data = cache.get(video_id)
            if cached_data:
                logger.info(f"Using cached transcript for video {video_id}")
        
        # Fetch if not cached
        if not cached_data:
            # Apply delay for rate limiting
            if delay_seconds > 0:
                logger.info(f"Waiting {delay_seconds}s before fetching transcript...")
                time.sleep(delay_seconds)
            
            try:
                # Create API instance
                api = YouTubeTranscriptApi()
                
                # Fetch transcript - tries manual first, then auto-generated
                logger.info(f"Fetching transcript for video {video_id}...")
                transcript_list = api.fetch(video_id)
                
                # Convert to our format
                transcript = []
                for entry in transcript_list:
                    transcript.append({
                        'text': entry.text,
                        'start': entry.start,
                        'duration': entry.duration
                    })
                
                # Calculate duration
                duration = transcript[-1]['start'] + transcript[-1]['duration'] if transcript else 0
                
                # Build analysis data
                analysis_data = {
                    'video_id': video_id,
                    'duration': duration,
                    'full_transcript': transcript,
                    'intro': extract_intro(transcript),
                    'outro': extract_outro(transcript, duration),
                    'main_samples': extract_main_samples(transcript),
                    'transcript_length': len(transcript)
                }
                
                # Cache the data
                cache.set(video_id, analysis_data)
                cached_data = analysis_data
                
            except Exception as e:
                error_msg = str(e)
                if 'Subtitles are disabled' in error_msg or 'No transcripts' in error_msg or 'TranscriptsDisabled' in error_msg:
                    return types.TextContent(
                        type="text",
                        text=json.dumps({
                            "error": {
                                "type": "no_transcript",
                                "message": "No transcript available for this video",
                                "details": {"video_id": video_id}
                            }
                        })
                    )
                elif 'Could not retrieve' in error_msg or 'NoTranscriptFound' in error_msg:
                    return types.TextContent(
                        type="text",
                        text=json.dumps({
                            "error": {
                                "type": "transcript_blocked",
                                "message": "Transcript blocked or unavailable",
                                "details": {"video_id": video_id}
                            }
                        })
                    )
                raise
        
        # Prepare response based on extract_mode
        if extract_mode == "full":
            result = cached_data
        elif extract_mode == "analysis":
            # Everything except full transcript
            result = {k: v for k, v in cached_data.items() if k != 'full_transcript'}
        elif extract_mode == "intro_only":
            result = {
                'video_id': video_id,
                'intro': cached_data['intro'],
                'duration': cached_data['duration']
            }
        elif extract_mode == "outro_only":
            result = {
                'video_id': video_id,
                'outro': cached_data['outro'],
                'duration': cached_data['duration']
            }
        
        # Add metadata
        result['_metadata'] = {
            "api_quota_cost": 0,  # No YouTube API calls, uses youtube-transcript-api
            "cache_hit": use_cache and cached_data is not None,
            "extract_mode": extract_mode,
            "fetched_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }
        
        return types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )
        
    except Exception as e:
        logger.error(f"Error fetching transcript: {e}")
        return types.TextContent(
            type="text",
            text=json.dumps(format_error_response(e))
        )