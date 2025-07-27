"""Base utilities for YouTube tools"""
import os
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_toolkit.config import load_config

class YouTubeAPIClient:
    """Singleton YouTube API client"""
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            config = load_config()
            if not config.youtube_api_key:
                raise ValueError("YouTube API key not configured. Set YOUTUBE_API_KEY environment variable.")
            cls._instance = build('youtube', 'v3', developerKey=config.youtube_api_key)
        return cls._instance

class TranscriptCache:
    """Manages transcript caching"""
    
    def __init__(self):
        config = load_config()
        self.cache_dir = Path(config.transcript_cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_age_days = config.max_cache_age_days
    
    def get_cache_path(self, video_id: str) -> Path:
        """Get cache file path for a video"""
        return self.cache_dir / f"{video_id}.json"
    
    def get(self, video_id: str) -> Optional[Dict]:
        """Get cached transcript if available and not expired"""
        cache_path = self.get_cache_path(video_id)
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            # Check age
            fetched_at = datetime.fromisoformat(data.get('fetched_at', ''))
            age = datetime.now() - fetched_at
            if age.days > self.max_age_days:
                return None
            
            return data
        except Exception:
            return None
    
    def set(self, video_id: str, data: Dict):
        """Cache transcript data"""
        cache_path = self.get_cache_path(video_id)
        data['fetched_at'] = datetime.now().isoformat()
        with open(cache_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def clear(self, video_id: Optional[str] = None, older_than_days: Optional[int] = None) -> int:
        """Clear cache entries"""
        cleared = 0
        
        if video_id:
            # Clear specific video
            cache_path = self.get_cache_path(video_id)
            if cache_path.exists():
                cache_path.unlink()
                cleared = 1
        else:
            # Clear all or by age
            for cache_file in self.cache_dir.glob("*.json"):
                if older_than_days:
                    try:
                        with open(cache_file, 'r') as f:
                            data = json.load(f)
                        fetched_at = datetime.fromisoformat(data.get('fetched_at', ''))
                        age = datetime.now() - fetched_at
                        if age.days > older_than_days:
                            cache_file.unlink()
                            cleared += 1
                    except Exception:
                        pass
                else:
                    cache_file.unlink()
                    cleared += 1
        
        return cleared
    
    def get_info(self, video_id: Optional[str] = None) -> Dict:
        """Get cache statistics"""
        if video_id:
            cache_path = self.get_cache_path(video_id)
            if cache_path.exists():
                stat = cache_path.stat()
                return {
                    "video_id": video_id,
                    "cached": True,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
            else:
                return {"video_id": video_id, "cached": False}
        
        # Get all cache info
        total_size = 0
        cache_files = list(self.cache_dir.glob("*.json"))
        cached_videos = []
        
        for cache_file in cache_files:
            stat = cache_file.stat()
            total_size += stat.st_size
            video_id = cache_file.stem
            cached_videos.append({
                "video_id": video_id,
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return {
            "cache_dir": str(self.cache_dir),
            "total_files": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "cached_videos": cached_videos
        }

def parse_video_id(video_id_or_url: str) -> str:
    """Extract video ID from URL or return as-is"""
    # Handle various YouTube URL formats
    patterns = [
        r'youtube\.com/watch\?v=([^&]+)',
        r'youtu\.be/([^?]+)',
        r'youtube\.com/embed/([^?]+)',
        r'youtube\.com/v/([^?]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, video_id_or_url)
        if match:
            return match.group(1)
    
    # Assume it's already a video ID
    return video_id_or_url

def parse_duration(duration: str) -> int:
    """Convert ISO 8601 duration to seconds"""
    if not duration:
        return 0
    
    # Match ISO 8601 duration format
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds

def format_error_response(error: Exception) -> Dict[str, Any]:
    """Format error for consistent error responses"""
    if isinstance(error, HttpError):
        if error.resp.status == 403:
            return {
                "error": {
                    "type": "quota_exceeded",
                    "message": "YouTube API quota limit reached. Try again later.",
                    "retry_after": 86400  # 24 hours in seconds
                }
            }
        elif error.resp.status == 404:
            return {
                "error": {
                    "type": "not_found",
                    "message": "The requested resource was not found."
                }
            }
        else:
            return {
                "error": {
                    "type": f"api_error_{error.resp.status}",
                    "message": str(error)
                }
            }
    
    return {
        "error": {
            "type": type(error).__name__,
            "message": str(error)
        }
    }

def extract_intro(transcript: List[Dict]) -> List[Dict]:
    """Extract first 60 seconds of transcript"""
    return [entry for entry in transcript if entry['start'] < 60]

def extract_outro(transcript: List[Dict], duration: float) -> List[Dict]:
    """Extract last 60 seconds of transcript"""
    outro_start = max(0, duration - 60)
    return [entry for entry in transcript if entry['start'] >= outro_start]

def extract_main_samples(transcript: List[Dict], num_samples: int = 3) -> List[Dict[str, Any]]:
    """Extract samples from main content (excluding intro/outro)"""
    if not transcript:
        return []
    
    duration = transcript[-1]['start'] + transcript[-1]['duration']
    # Skip first and last 60 seconds
    main_start = 60
    main_end = max(60, duration - 60)
    
    if main_end <= main_start:
        return []
    
    # Calculate sample points
    samples = []
    interval = (main_end - main_start) / (num_samples + 1)
    
    for i in range(1, num_samples + 1):
        sample_time = main_start + (interval * i)
        sample_duration = 30  # 30 second samples
        
        sample_entries = [
            entry for entry in transcript 
            if sample_time <= entry['start'] < sample_time + sample_duration
        ]
        
        if sample_entries:
            samples.append({
                'timestamp': sample_time,
                'duration': sample_duration,
                'text': ' '.join([e['text'] for e in sample_entries]),
                'entries': sample_entries
            })
    
    return samples