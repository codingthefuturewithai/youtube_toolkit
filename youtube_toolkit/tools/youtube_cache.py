"""YouTube transcript cache management tools"""
import json
from typing import Optional
from mcp import types
from youtube_toolkit.tools.youtube_base import TranscriptCache
from youtube_toolkit.logging_config import logger

def youtube_get_transcript_cache_info(
    video_id: Optional[str] = None
) -> types.TextContent:
    """
    Get information about cached transcripts.
    
    Args:
        video_id: Specific video ID, or None for all
    
    Returns:
        Cache statistics and cached video list
    """
    try:
        cache = TranscriptCache()
        info = cache.get_info(video_id)
        
        return types.TextContent(
            type="text",
            text=json.dumps(info, indent=2)
        )
    
    except Exception as e:
        logger.error(f"Error getting cache info: {e}")
        return types.TextContent(
            type="text",
            text=json.dumps({
                "error": type(e).__name__,
                "message": str(e)
            })
        )

def youtube_clear_transcript_cache(
    video_id: Optional[str] = None,
    older_than_days: Optional[int] = None
) -> types.TextContent:
    """
    Clear transcript cache entries.
    
    Args:
        video_id: Specific video ID to clear, or None for all
        older_than_days: Only clear entries older than X days
    
    Returns:
        Number of cache entries cleared
    """
    try:
        cache = TranscriptCache()
        cleared = cache.clear(video_id, older_than_days)
        
        result = {
            "cleared": cleared,
            "message": f"Cleared {cleared} cache entries"
        }
        
        if video_id:
            result["video_id"] = video_id
        if older_than_days:
            result["older_than_days"] = older_than_days
        
        logger.info(f"Cleared {cleared} cache entries")
        
        return types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )
    
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return types.TextContent(
            type="text",
            text=json.dumps({
                "error": type(e).__name__,
                "message": str(e)
            })
        )