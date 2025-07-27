#!/usr/bin/env python3
"""Test script to verify metadata is correctly included in all tool responses."""

import json
import os
from youtube_toolkit.tools.youtube_search import youtube_search_videos
from youtube_toolkit.tools.youtube_video import youtube_get_video_metadata, youtube_get_video_transcript
from youtube_toolkit.tools.youtube_cache import youtube_get_transcript_cache_info, youtube_clear_transcript_cache
from youtube_toolkit.tools.youtube_channel import youtube_get_channel_videos, youtube_get_channel_metadata

def test_tool_metadata(tool_name, tool_func, args):
    """Test that a tool returns proper metadata."""
    print(f"\n{'='*60}")
    print(f"Testing: {tool_name}")
    print(f"{'='*60}")
    
    try:
        result = tool_func(**args)
        data = json.loads(result.text)
        
        # Check for _metadata
        if '_metadata' not in data:
            print(f"❌ Missing _metadata section")
            return False
            
        metadata = data['_metadata']
        
        # Check for api_quota_cost
        if 'api_quota_cost' not in metadata:
            print(f"❌ Missing api_quota_cost in metadata")
            return False
            
        # Check for fetched_at (except for transcript which may have cache_hit instead)
        if 'fetched_at' not in metadata and tool_name != 'youtube_get_video_transcript':
            print(f"❌ Missing fetched_at in metadata")
            return False
            
        print(f"✅ Metadata present:")
        for key, value in metadata.items():
            print(f"   - {key}: {value}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run metadata tests for all tools."""
    
    # Skip API tests if no API key
    api_key = os.environ.get('YOUTUBE_API_KEY')
    
    tests = [
        # Cache tools (no API key needed)
        ("youtube_get_transcript_cache_info", youtube_get_transcript_cache_info, {}),
        ("youtube_clear_transcript_cache", youtube_clear_transcript_cache, {"video_id": "test123"}),
    ]
    
    if api_key:
        tests.extend([
            # Search tool
            ("youtube_search_videos", youtube_search_videos, {"query": "test", "max_results": 1}),
            
            # Video tools
            ("youtube_get_video_metadata", youtube_get_video_metadata, {"video_id": "dQw4w9WgXcQ"}),
            
            # Channel tools
            ("youtube_get_channel_metadata", youtube_get_channel_metadata, {"channel_id": "UCuAXFkgsw1L7xaCfnd5JJOw"}),
            ("youtube_get_channel_videos", youtube_get_channel_videos, {"channel_id": "UCuAXFkgsw1L7xaCfnd5JJOw", "max_results": 1}),
        ])
        
        # Transcript tool (special case - no API key needed but let's test the metadata)
        tests.append(("youtube_get_video_transcript", youtube_get_video_transcript, {"video_id": "dQw4w9WgXcQ", "use_cache": False}))
    else:
        print("⚠️  No YOUTUBE_API_KEY found - skipping API tests")
        
    # Run tests
    passed = 0
    failed = 0
    
    for tool_name, tool_func, args in tests:
        if test_tool_metadata(tool_name, tool_func, args):
            passed += 1
        else:
            failed += 1
            
    print(f"\n{'='*60}")
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()