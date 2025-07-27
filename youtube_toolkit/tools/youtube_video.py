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

def youtube_get_video_info(
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
        
        # Build request parts
        parts = ['snippet', 'contentDetails']
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
                    "error": "not_found",
                    "message": f"Video {video_id} not found"
                })
            )
        
        # Extract video data
        video = response['items'][0]
        result = {
            "video_id": video['id'],
            "title": video['snippet']['title'],
            "channel": video['snippet']['channelTitle'],
            "channel_id": video['snippet']['channelId'],
            "description": video['snippet']['description'],
            "published_at": video['snippet']['publishedAt'],
            "duration": video['contentDetails']['duration'],
            "duration_seconds": parse_duration(video['contentDetails']['duration']),
            "thumbnail": video['snippet']['thumbnails'].get('high', {}).get('url', ''),
            "url": f"https://www.youtube.com/watch?v={video_id}"
        }
        
        if include_statistics and 'statistics' in video:
            result['statistics'] = {
                "view_count": int(video['statistics'].get('viewCount', 0)),
                "like_count": int(video['statistics'].get('likeCount', 0)),
                "comment_count": int(video['statistics'].get('commentCount', 0))
            }
        
        # Add metadata
        result['_metadata'] = {
            "api_calls": 1,
            "cache_used": False
        }
        
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
                            "error": "no_transcript",
                            "message": "No transcript available for this video",
                            "video_id": video_id
                        })
                    )
                elif 'Could not retrieve' in error_msg or 'NoTranscriptFound' in error_msg:
                    return types.TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "transcript_blocked",
                            "message": "Transcript blocked or unavailable",
                            "video_id": video_id
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
            "cache_hit": use_cache and cached_data is not None,
            "extract_mode": extract_mode
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