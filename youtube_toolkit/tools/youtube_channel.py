"""YouTube channel tools"""
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from mcp import types
from googleapiclient.errors import HttpError
from youtube_toolkit.tools.youtube_base import (
    YouTubeAPIClient, parse_duration, format_error_response
)
from youtube_toolkit.tools.youtube_video import youtube_get_video_transcript
from youtube_toolkit.config import load_config
from youtube_toolkit.logging_config import logger

def youtube_get_channel_videos(
    channel_id: str,
    max_results: int = 10,
    include_transcripts: bool = False,
    use_cache: bool = True,
    delay_seconds: Optional[float] = None
) -> types.TextContent:
    """
    List recent videos from a YouTube channel.
    
    Args:
        channel_id: YouTube channel ID (starts with UC...)
        max_results: Maximum number of videos to return
        include_transcripts: Fetch transcripts for each video
        use_cache: Whether to use cached transcripts (only applies when include_transcripts is True)
        delay_seconds: Delay between transcript fetches
    
    Returns:
        Array of video objects with metadata and optional transcripts
    """
    try:
        # Get YouTube API client
        youtube = YouTubeAPIClient.get_instance()
        
        # First, get channel info
        channel_request = youtube.channels().list(
            part='snippet,statistics,brandingSettings',
            id=channel_id
        )
        channel_response = channel_request.execute()
        
        if not channel_response.get('items'):
            return types.TextContent(
                type="text",
                text=json.dumps({
                    "error": {
                        "type": "not_found",
                        "message": f"Channel {channel_id} not found"
                    }
                })
            )
        
        channel_info = channel_response['items'][0]
        
        # Search for videos from this channel
        videos = []
        next_page_token = None
        
        while len(videos) < max_results:
            search_request = youtube.search().list(
                part='snippet',
                channelId=channel_id,
                maxResults=min(50, max_results - len(videos)),
                order='date',
                type='video',
                pageToken=next_page_token
            )
            search_response = search_request.execute()
            
            if 'items' not in search_response:
                break
            
            videos.extend(search_response['items'])
            
            next_page_token = search_response.get('nextPageToken')
            if not next_page_token:
                break
        
        # Get video details
        video_ids = [v['id']['videoId'] for v in videos[:max_results]]
        if video_ids:
            details_request = youtube.videos().list(
                part='statistics,contentDetails',
                id=','.join(video_ids)
            )
            details_response = details_request.execute()
            
            # Create lookup for details
            details_lookup = {
                item['id']: item 
                for item in details_response.get('items', [])
            }
        else:
            details_lookup = {}
        
        # Format response
        snippet = channel_info['snippet']
        statistics = channel_info['statistics']
        
        # Build custom URL if available
        custom_url = None
        if 'customUrl' in snippet:
            custom_url = f"https://youtube.com/@{snippet['customUrl']}"
        elif 'brandingSettings' in channel_info and 'channel' in channel_info['brandingSettings']:
            if 'customUrl' in channel_info['brandingSettings']['channel']:
                custom_url = f"https://youtube.com/{channel_info['brandingSettings']['channel']['customUrl']}"
        
        result = {
            "channel": {
                "id": channel_info['id'],
                "title": snippet['title'],
                "description": snippet['description'],
                "subscriber_count": int(statistics.get('subscriberCount', 0)),
                "view_count": int(statistics.get('viewCount', 0)),
                "video_count": int(statistics.get('videoCount', 0)),
                "created_at": snippet.get('publishedAt', ''),
                "country": snippet.get('country', ''),
                "custom_url": custom_url,
                "thumbnail_url": snippet.get('thumbnails', {}).get('high', {}).get('url', '')
            },
            "videos": []
        }
        
        # Track transcript statistics
        transcripts_fetched = 0
        transcripts_cached = 0
        
        # Process each video
        for i, video in enumerate(videos[:max_results]):
            video_id = video['id']['videoId']
            details = details_lookup.get(video_id, {})
            
            video_data = {
                "video_id": video_id,
                "title": video['snippet']['title'],
                "description": video['snippet']['description'],
                "published_at": video['snippet']['publishedAt'],
                "duration": details.get('contentDetails', {}).get('duration', ''),
                "duration_seconds": parse_duration(details.get('contentDetails', {}).get('duration', '')),
                "thumbnail_url": video['snippet']['thumbnails'].get('high', {}).get('url', ''),
                "view_count": int(details.get('statistics', {}).get('viewCount', 0)),
                "like_count": int(details.get('statistics', {}).get('likeCount', 0)),
                "comment_count": int(details.get('statistics', {}).get('commentCount', 0)),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "transcript": None
            }
            
            # Fetch transcript if requested
            if include_transcripts:
                # Use delay for all but first video
                transcript_delay = 0 if i == 0 else (delay_seconds or load_config().default_transcript_delay)
                
                logger.info(f"Fetching transcript {i+1}/{len(videos[:max_results])} for: {video_data['title'][:50]}...")
                
                # Get transcript using full mode as per v3 spec
                transcript_response = youtube_get_video_transcript(
                    video_id,
                    extract_mode="full",
                    use_cache=use_cache,
                    delay_seconds=transcript_delay
                )
                
                transcript_data = json.loads(transcript_response.text)
                
                if 'error' not in transcript_data:
                    # Check if transcript was cached (by examining metadata)
                    if '_metadata' in transcript_data and transcript_data['_metadata'].get('cache_hit', False):
                        transcripts_cached += 1
                    else:
                        transcripts_fetched += 1
                    
                    # Set transcript to the full text
                    video_data['transcript'] = transcript_data.get('text', '')
                else:
                    # Keep transcript as null on error
                    logger.warning(f"Failed to get transcript for {video_id}: {transcript_data['error']}")
                    
                    # Stop if rate limited
                    error_info = transcript_data['error']
                    if isinstance(error_info, dict) and 'blocked' in error_info.get('type', ''):
                        logger.warning("Rate limit detected, stopping transcript fetching")
                        break
            
            result['videos'].append(video_data)
        
        # Add metadata
        # Calculate API quota cost:
        # - channels.list: 1 unit
        # - search.list: 100 units per request (we might make multiple)
        # - videos.list: 1 unit
        search_requests = ((len(videos) - 1) // 50) + 1 if videos else 0
        api_quota_cost = 1 + (100 * search_requests) + (1 if video_ids else 0)
        
        result['_metadata'] = {
            "api_quota_cost": api_quota_cost,
            "videos_returned": len(result['videos']),
            "transcripts_fetched": transcripts_fetched,
            "transcripts_cached": transcripts_cached,
            "fetched_at": datetime.utcnow().isoformat() + "Z"
        }
        
        return types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )
        
    except Exception as e:
        logger.error(f"Error fetching channel videos: {e}")
        return types.TextContent(
            type="text",
            text=json.dumps(format_error_response(e))
        )

def youtube_get_channel_metadata(
    channel_id: str
) -> types.TextContent:
    """
    Fetches detailed metadata for a YouTube channel.
    
    Args:
        channel_id: YouTube channel ID (starts with UC), username, or handle
    
    Returns:
        Comprehensive channel metadata including statistics, branding, and status
    """
    try:
        # Get YouTube API client
        youtube = YouTubeAPIClient.get_instance()
        
        # Try to get channel by ID first, then by username or handle
        channel_response = None
        
        # First try as channel ID
        if channel_id.startswith('UC') and len(channel_id) == 24:
            request = youtube.channels().list(
                part='snippet,statistics,status,brandingSettings,contentDetails',
                id=channel_id
            )
            channel_response = request.execute()
        
        # If not found or not a channel ID, try as username
        if not channel_response or not channel_response.get('items'):
            # Try as username without @
            username = channel_id.lstrip('@')
            request = youtube.channels().list(
                part='snippet,statistics,status,brandingSettings,contentDetails',
                forUsername=username
            )
            channel_response = request.execute()
        
        # If still not found, try as handle (custom URL)
        if not channel_response or not channel_response.get('items'):
            # Search for channel by handle
            search_request = youtube.search().list(
                part='snippet',
                q=channel_id,
                type='channel',
                maxResults=1
            )
            search_response = search_request.execute()
            
            if search_response.get('items'):
                found_channel_id = search_response['items'][0]['snippet']['channelId']
                # Now get full channel info
                request = youtube.channels().list(
                    part='snippet,statistics,status,brandingSettings,contentDetails',
                    id=found_channel_id
                )
                channel_response = request.execute()
        
        if not channel_response or not channel_response.get('items'):
            return types.TextContent(
                type="text",
                text=json.dumps({
                    "error": {
                        "type": "channel_not_found",
                        "message": f"Channel '{channel_id}' not found"
                    }
                })
            )
        
        channel = channel_response['items'][0]
        
        # Build response matching v3 spec
        result = {
            "channel": {
                "id": channel['id'],
                "title": channel['snippet']['title'],
                "handle": None,  # Will be set if available
                "custom_url": None,  # Will be set if available
                "description": channel['snippet']['description'],
                "published_at": channel['snippet']['publishedAt'],
                "country": channel['snippet'].get('country', None),
                "statistics": {
                    "subscriber_count": int(channel['statistics'].get('subscriberCount', 0)),
                    "subscriber_count_hidden": channel['statistics'].get('hiddenSubscriberCount', False),
                    "view_count": int(channel['statistics'].get('viewCount', 0)),
                    "video_count": int(channel['statistics'].get('videoCount', 0))
                },
                "branding": {
                    "keywords": [],  # Will be set if available
                    "banner_url": None,  # Will be set if available
                    "thumbnail_url": channel['snippet'].get('thumbnails', {}).get('high', {}).get('url', None)
                },
                "content_details": {
                    "related_playlists": {}
                },
                "status": {
                    "privacy_status": None,
                    "is_linked": None,
                    "long_uploads_status": None,
                    "made_for_kids": None
                }
            },
            "_metadata": {
                "api_quota_cost": 3,  # channels.list costs 1, search might add 100
                "fetched_at": datetime.utcnow().isoformat() + 'Z'
            }
        }
        
        # Extract handle from custom URL if available
        if 'brandingSettings' in channel and 'channel' in channel['brandingSettings']:
            branding = channel['brandingSettings']['channel']
            
            # Get keywords
            if 'keywords' in branding:
                # Keywords are space-separated, handle quoted phrases
                keywords_str = branding['keywords']
                # Simple parsing - could be improved for quoted phrases
                result['channel']['branding']['keywords'] = keywords_str.split()
            
            # Get custom URL/handle
            if 'customUrl' in branding:
                custom_url = branding['customUrl']
                result['channel']['custom_url'] = f"https://youtube.com/{custom_url}"
                # Extract handle (custom URL often starts with @)
                if custom_url.startswith('@'):
                    result['channel']['handle'] = custom_url
                else:
                    result['channel']['handle'] = '@' + custom_url.lstrip('/')
        
        # Get banner URL if available
        if 'brandingSettings' in channel and 'image' in channel['brandingSettings']:
            banner = channel['brandingSettings']['image'].get('bannerExternalUrl')
            if banner:
                result['channel']['branding']['banner_url'] = banner
        
        # Get content details
        if 'contentDetails' in channel and 'relatedPlaylists' in channel['contentDetails']:
            result['channel']['content_details']['related_playlists'] = channel['contentDetails']['relatedPlaylists']
        
        # Get status details
        if 'status' in channel:
            status = channel['status']
            result['channel']['status']['privacy_status'] = status.get('privacyStatus')
            result['channel']['status']['is_linked'] = status.get('isLinked')
            result['channel']['status']['long_uploads_status'] = status.get('longUploadsStatus')
            result['channel']['status']['made_for_kids'] = status.get('madeForKids')
        
        # If we did a search, add to quota cost
        if not channel_id.startswith('UC'):
            result['_metadata']['api_quota_cost'] = 103  # search (100) + channels (3)
        
        return types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )
        
    except Exception as e:
        logger.error(f"Error fetching channel metadata: {e}")
        return types.TextContent(
            type="text",
            text=json.dumps(format_error_response(e))
        )
