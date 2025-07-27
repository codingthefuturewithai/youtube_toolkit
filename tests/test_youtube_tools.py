"""Tests for YouTube tools that don't require API key"""
import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta
from youtube_toolkit.tools.youtube_base import (
    parse_video_id, parse_duration, TranscriptCache,
    extract_intro, extract_outro, extract_main_samples
)

class TestVideoIdParsing:
    """Test video ID extraction from various URL formats"""
    
    def test_parse_video_id_from_watch_url(self):
        assert parse_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        assert parse_video_id("http://youtube.com/watch?v=dQw4w9WgXcQ&feature=share") == "dQw4w9WgXcQ"
    
    def test_parse_video_id_from_short_url(self):
        assert parse_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        assert parse_video_id("http://youtu.be/dQw4w9WgXcQ?t=1s") == "dQw4w9WgXcQ"
    
    def test_parse_video_id_from_embed_url(self):
        assert parse_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        assert parse_video_id("http://youtube.com/v/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    
    def test_parse_video_id_returns_as_is(self):
        assert parse_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        assert parse_video_id("abc123") == "abc123"

class TestDurationParsing:
    """Test ISO 8601 duration parsing"""
    
    def test_parse_duration_seconds_only(self):
        assert parse_duration("PT30S") == 30
        assert parse_duration("PT0S") == 0
    
    def test_parse_duration_minutes_and_seconds(self):
        assert parse_duration("PT3M45S") == 225
        assert parse_duration("PT10M") == 600
    
    def test_parse_duration_hours_minutes_seconds(self):
        assert parse_duration("PT1H30M45S") == 5445
        assert parse_duration("PT2H") == 7200
    
    def test_parse_duration_edge_cases(self):
        assert parse_duration("") == 0
        assert parse_duration("invalid") == 0
        assert parse_duration(None) == 0

class TestTranscriptExtraction:
    """Test transcript analysis functions"""
    
    def create_mock_transcript(self, duration: int) -> list:
        """Create a mock transcript for testing"""
        transcript = []
        for i in range(0, duration, 10):
            transcript.append({
                'text': f'Text at {i} seconds',
                'start': i,
                'duration': 10
            })
        return transcript
    
    def test_extract_intro(self):
        transcript = self.create_mock_transcript(300)  # 5 minute video
        intro = extract_intro(transcript)
        
        assert len(intro) == 6  # First 60 seconds = 6 entries
        assert intro[0]['start'] == 0
        assert intro[-1]['start'] == 50
    
    def test_extract_outro(self):
        transcript = self.create_mock_transcript(300)  # 5 minute video
        outro = extract_outro(transcript, 300)
        
        assert len(outro) == 6  # Last 60 seconds = 6 entries
        assert outro[0]['start'] == 240
        assert outro[-1]['start'] == 290
    
    def test_extract_main_samples(self):
        transcript = self.create_mock_transcript(300)  # 5 minute video
        samples = extract_main_samples(transcript, num_samples=3)
        
        assert len(samples) == 3
        # Check that samples are from the middle section (60-240 seconds)
        for sample in samples:
            assert 60 < sample['timestamp'] < 240
            assert sample['duration'] == 30

class TestTranscriptCache:
    """Test transcript caching functionality"""
    
    @pytest.fixture
    def temp_cache_dir(self, tmp_path):
        """Create a temporary cache directory"""
        return tmp_path / "test_cache"
    
    @pytest.fixture
    def cache(self, temp_cache_dir, monkeypatch):
        """Create a cache instance with temporary directory"""
        from youtube_toolkit.config import ServerConfig
        
        # Mock the config
        mock_config = ServerConfig(
            name="Test",
            log_level="INFO",
            youtube_api_key=None,
            transcript_cache_dir=str(temp_cache_dir),
            default_transcript_delay=10.0,
            max_cache_age_days=30
        )
        
        monkeypatch.setattr('youtube_toolkit.config.load_config', lambda: mock_config)
        return TranscriptCache()
    
    def test_cache_set_and_get(self, cache):
        """Test setting and getting cached data"""
        test_data = {
            'video_id': 'test123',
            'transcript': ['test'],
            'duration': 300
        }
        
        cache.set('test123', test_data)
        retrieved = cache.get('test123')
        
        assert retrieved is not None
        assert retrieved['video_id'] == 'test123'
        assert 'fetched_at' in retrieved
    
    def test_cache_expiry(self, cache):
        """Test that expired cache entries are not returned"""
        test_data = {'video_id': 'test123'}
        cache.set('test123', test_data)
        
        # Manually modify the cache file to be old
        cache_path = cache.get_cache_path('test123')
        with open(cache_path, 'r') as f:
            data = json.load(f)
        
        # Set fetched_at to 40 days ago
        old_date = datetime.now() - timedelta(days=40)
        data['fetched_at'] = old_date.isoformat()
        
        with open(cache_path, 'w') as f:
            json.dump(data, f)
        
        # Should return None for expired cache
        assert cache.get('test123') is None
    
    def test_cache_clear_specific(self, cache):
        """Test clearing specific cache entry"""
        cache.set('test1', {'data': 1})
        cache.set('test2', {'data': 2})
        
        cleared = cache.clear(video_id='test1')
        
        assert cleared == 1
        assert cache.get('test1') is None
        assert cache.get('test2') is not None
    
    def test_cache_clear_by_age(self, cache):
        """Test clearing cache by age"""
        # Create two cache entries
        cache.set('new_video', {'data': 'new'})
        cache.set('old_video', {'data': 'old'})
        
        # Manually age one entry
        old_path = cache.get_cache_path('old_video')
        with open(old_path, 'r') as f:
            data = json.load(f)
        data['fetched_at'] = (datetime.now() - timedelta(days=20)).isoformat()
        with open(old_path, 'w') as f:
            json.dump(data, f)
        
        # Clear entries older than 15 days
        cleared = cache.clear(older_than_days=15)
        
        assert cleared == 1
        assert cache.get('new_video') is not None
        assert cache.get('old_video') is None
    
    def test_cache_info(self, cache):
        """Test getting cache information"""
        cache.set('test1', {'data': 'test1'})
        cache.set('test2', {'data': 'test2'})
        
        # Test all cache info
        info = cache.get_info()
        assert info['total_files'] == 2
        assert len(info['cached_videos']) == 2
        assert info['cache_dir'] == str(cache.cache_dir)
        
        # Test specific video info
        specific_info = cache.get_info('test1')
        assert specific_info['video_id'] == 'test1'
        assert specific_info['cached'] is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])