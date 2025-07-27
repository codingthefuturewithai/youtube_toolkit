"""YouTube search tools"""
import json
from typing import Optional, Literal
from mcp import types
from youtube_toolkit.tools.youtube_base import (
    YouTubeAPIClient, parse_duration, format_error_response
)
from youtube_toolkit.logging_config import logger

def youtube_search_videos(
    query: str,
    max_results: int = 10,
    order: Literal["relevance", "date", "viewCount", "rating"] = "relevance",
    published_after: Optional[str] = None
) -> types.TextContent:
    """
    Search YouTube videos by query.
    
    Args:
        query: Search query string
        max_results: Maximum results to return
        order: Sort order for results
        published_after: ISO 8601 date string (e.g., "2024-01-01T00:00:00Z")
    
    Returns:
        Array of video search results
    """
    try:
        # Get YouTube API client
        youtube = YouTubeAPIClient.get_instance()
        
        # Build search parameters
        search_params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': min(50, max_results),
            'order': order
        }
        
        if published_after:
            search_params['publishedAfter'] = published_after
        
        # Execute search
        videos = []
        next_page_token = None
        
        while len(videos) < max_results:
            if next_page_token:
                search_params['pageToken'] = next_page_token
            
            search_request = youtube.search().list(**search_params)
            search_response = search_request.execute()
            
            if 'items' not in search_response:
                break
            
            videos.extend(search_response['items'])
            
            next_page_token = search_response.get('nextPageToken')
            if not next_page_token or len(videos) >= max_results:
                break
        
        # Trim to requested max
        videos = videos[:max_results]
        
        # Get detailed information for videos
        video_ids = [v['id']['videoId'] for v in videos]
        
        if video_ids:
            details_request = youtube.videos().list(
                part='statistics,contentDetails',
                id=','.join(video_ids)
            )
            details_response = details_request.execute()
            
            # Create lookup
            details_lookup = {
                item['id']: item 
                for item in details_response.get('items', [])
            }
        else:
            details_lookup = {}
        
        # Format results
        results = []
        for video in videos:
            video_id = video['id']['videoId']
            details = details_lookup.get(video_id, {})
            
            results.append({
                "id": video_id,
                "title": video['snippet']['title'],
                "channel": video['snippet']['channelTitle'],
                "channel_id": video['snippet']['channelId'],
                "description": video['snippet']['description'],
                "published_at": video['snippet']['publishedAt'],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": video['snippet']['thumbnails'].get('high', {}).get('url', ''),
                "duration": details.get('contentDetails', {}).get('duration', ''),
                "duration_seconds": parse_duration(details.get('contentDetails', {}).get('duration', '')),
                "view_count": int(details.get('statistics', {}).get('viewCount', 0)),
                "like_count": int(details.get('statistics', {}).get('likeCount', 0))
            })
        
        response = {
            "query": query,
            "total_results": len(results),
            "order": order,
            "results": results,
            "_metadata": {
                "api_calls": 1 + (1 if video_ids else 0)
            }
        }
        
        if published_after:
            response["published_after"] = published_after
        
        return types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )
        
    except Exception as e:
        logger.error(f"Error searching videos: {e}")
        return types.TextContent(
            type="text",
            text=json.dumps(format_error_response(e))
        )