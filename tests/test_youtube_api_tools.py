"""Tests for YouTube tools that require API key"""
import os
import pytest
import json
from youtube_toolkit.tools.youtube_video import youtube_get_video_metadata
from youtube_toolkit.tools.youtube_channel import youtube_get_channel_videos, youtube_get_channel_metadata
from youtube_toolkit.tools.youtube_search import youtube_search_videos
from youtube_toolkit.config import load_config

# Skip all tests in this file if no API key is available
pytestmark = pytest.mark.skipif(
    not os.getenv("YOUTUBE_API_KEY"),
    reason="YOUTUBE_API_KEY not set in environment"
)

class TestYouTubeVideoMetadata:
    """Test video metadata fetching with API key"""
    
    def test_get_video_metadata_success(self):
        """Test fetching metadata for a known video"""
        # Using Rick Astley's Never Gonna Give You Up as a stable test video
        result = youtube_get_video_metadata("dQw4w9WgXcQ")
        data = json.loads(result.text)
        
        assert "video_id" in data
        assert data["video_id"] == "dQw4w9WgXcQ"
        assert "title" in data
        assert "channel" in data
        assert "statistics" in data
        assert "_metadata" in data
        assert data["_metadata"]["api_quota_cost"] > 0
    
    def test_get_video_metadata_not_found(self):
        """Test fetching metadata for non-existent video"""
        result = youtube_get_video_metadata("invalid_video_id_12345")
        data = json.loads(result.text)
        
        assert "error" in data
        assert data["error"]["type"] == "not_found"

class TestYouTubeChannelTools:
    """Test channel-related tools with API key"""
    
    def test_get_channel_videos_success(self):
        """Test fetching videos from a known channel"""
        # Using YouTube's official channel
        result = youtube_get_channel_videos(
            channel_id="UCBR8-60-B28hp2BmDPdntcQ",
            max_results=5,
            include_transcripts=False
        )
        data = json.loads(result.text)
        
        assert "channel" in data
        assert "videos" in data
        assert len(data["videos"]) <= 5
        assert "_metadata" in data
        assert data["_metadata"]["api_quota_cost"] > 0
    
    def test_get_channel_metadata_by_id(self):
        """Test fetching channel metadata by channel ID"""
        # Using MKBHD's channel
        result = youtube_get_channel_metadata("UCBJycsmduvYEL83R_U4JriQ")
        data = json.loads(result.text)
        
        assert "channel" in data
        assert data["channel"]["id"] == "UCBJycsmduvYEL83R_U4JriQ"
        assert "statistics" in data["channel"]
        assert "branding" in data["channel"]
        assert "_metadata" in data
    
    def test_get_channel_metadata_by_handle(self):
        """Test fetching channel metadata by handle"""
        result = youtube_get_channel_metadata("@mkbhd")
        data = json.loads(result.text)
        
        assert "channel" in data
        assert "handle" in data["channel"]
        # Handle might be None if not set in channel branding
        # Just verify the channel was found
        assert data["channel"]["id"] is not None
        assert data["channel"]["title"] is not None

class TestYouTubeSearch:
    """Test search functionality with API key"""
    
    def test_search_videos_basic(self):
        """Test basic video search"""
        result = youtube_search_videos(
            query="python programming tutorial",
            max_results=5
        )
        data = json.loads(result.text)
        
        assert "query" in data
        assert "results" in data
        assert len(data["results"]) <= 5
        assert "_metadata" in data
        assert data["_metadata"]["api_quota_cost"] == 100  # Search costs 100 units
    
    def test_search_videos_with_filters(self):
        """Test video search with filters"""
        result = youtube_search_videos(
            query="react hooks",
            max_results=3,
            order="date"
        )
        data = json.loads(result.text)
        
        assert "results" in data
        assert len(data["results"]) <= 3
        for video in data["results"]:
            assert "duration_seconds" in video

@pytest.fixture(autouse=True)
def check_api_key():
    """Fixture to verify API key is loaded"""
    config = load_config()
    if not config.youtube_api_key:
        pytest.skip("YOUTUBE_API_KEY not configured")