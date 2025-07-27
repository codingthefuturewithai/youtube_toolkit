"""YouTube channel tools"""
import json
import time
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
    delay_seconds: Optional[float] = None
) -> types.TextContent:
    """
    List recent videos from a YouTube channel.
    
    Args:
        channel_id: YouTube channel ID (starts with UC...)
        max_results: Maximum number of videos to return
        include_transcripts: Fetch transcripts for each video
        delay_seconds: Delay between transcript fetches
    
    Returns:
        Array of video objects with metadata and optional transcripts
    """
    try:
        # Get YouTube API client
        youtube = YouTubeAPIClient.get_instance()
        
        # First, get channel info
        channel_request = youtube.channels().list(
            part='snippet,statistics',
            id=channel_id
        )
        channel_response = channel_request.execute()
        
        if not channel_response.get('items'):
            return types.TextContent(
                type="text",
                text=json.dumps({
                    "error": "not_found",
                    "message": f"Channel {channel_id} not found"
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
        result = {
            "channel": {
                "id": channel_info['id'],
                "title": channel_info['snippet']['title'],
                "description": channel_info['snippet']['description'],
                "subscriber_count": int(channel_info['statistics'].get('subscriberCount', 0)),
                "video_count": int(channel_info['statistics'].get('videoCount', 0))
            },
            "videos": []
        }
        
        # Process each video
        for i, video in enumerate(videos[:max_results]):
            video_id = video['id']['videoId']
            details = details_lookup.get(video_id, {})
            
            video_data = {
                "id": video_id,
                "title": video['snippet']['title'],
                "description": video['snippet']['description'],
                "published_at": video['snippet']['publishedAt'],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": video['snippet']['thumbnails'].get('high', {}).get('url', ''),
                "duration": details.get('contentDetails', {}).get('duration', ''),
                "duration_seconds": parse_duration(details.get('contentDetails', {}).get('duration', '')),
                "view_count": int(details.get('statistics', {}).get('viewCount', 0)),
                "like_count": int(details.get('statistics', {}).get('likeCount', 0))
            }
            
            # Fetch transcript if requested
            if include_transcripts:
                # Use delay for all but first video
                transcript_delay = 0 if i == 0 else (delay_seconds or load_config().default_transcript_delay)
                
                logger.info(f"Fetching transcript {i+1}/{len(videos[:max_results])} for: {video_data['title'][:50]}...")
                
                # Get transcript using analysis mode to save space
                transcript_response = youtube_get_video_transcript(
                    video_id,
                    extract_mode="analysis",
                    use_cache=True,
                    delay_seconds=transcript_delay
                )
                
                transcript_data = json.loads(transcript_response.text)
                
                if 'error' not in transcript_data:
                    video_data['transcript_analysis'] = transcript_data
                else:
                    video_data['transcript_error'] = transcript_data['error']
                    # Stop if rate limited
                    if 'blocked' in transcript_data.get('error', ''):
                        logger.warning("Rate limit detected, stopping transcript fetching")
                        break
            
            result['videos'].append(video_data)
        
        # Add metadata
        result['_metadata'] = {
            "api_calls": 2 + (1 if video_ids else 0),  # channel + search + details
            "transcripts_fetched": sum(1 for v in result['videos'] if 'transcript_analysis' in v)
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

def youtube_analyze_channel_style(
    channel_id: str,
    max_videos: int = 5,
    save_profile: bool = True,
    profile_path: Optional[str] = None
) -> types.TextContent:
    """
    Perform comprehensive channel analysis for content style profiling.
    
    Args:
        channel_id: YouTube channel ID
        max_videos: Number of recent videos to analyze
        save_profile: Save creator profile to file
        profile_path: Custom path for profile storage
    
    Returns:
        Creator profile with style patterns, vocabulary, structure analysis
    """
    try:
        logger.info(f"Starting channel style analysis for {channel_id}")
        
        # Get channel videos with transcripts
        videos_response = youtube_get_channel_videos(
            channel_id=channel_id,
            max_results=max_videos,
            include_transcripts=True,
            delay_seconds=10.0  # Conservative delay for analysis
        )
        
        videos_data = json.loads(videos_response.text)
        
        if 'error' in videos_data:
            return types.TextContent(type="text", text=json.dumps(videos_data))
        
        # Analyze patterns
        channel_info = videos_data['channel']
        videos_with_transcripts = [
            v for v in videos_data['videos'] 
            if 'transcript_analysis' in v
        ]
        
        if not videos_with_transcripts:
            return types.TextContent(
                type="text",
                text=json.dumps({
                    "error": "no_transcripts",
                    "message": "No videos with available transcripts found"
                })
            )
        
        # Extract patterns
        intro_phrases = []
        outro_phrases = []
        vocabulary_freq = {}
        total_words = 0
        
        for video in videos_with_transcripts:
            analysis = video['transcript_analysis']
            
            # Collect intro phrases
            if analysis.get('intro'):
                intro_text = ' '.join([e['text'] for e in analysis['intro']])
                intro_phrases.append(intro_text)
            
            # Collect outro phrases
            if analysis.get('outro'):
                outro_text = ' '.join([e['text'] for e in analysis['outro']])
                outro_phrases.append(outro_text)
            
            # Analyze vocabulary from samples
            for sample in analysis.get('main_samples', []):
                words = sample['text'].lower().split()
                total_words += len(words)
                for word in words:
                    # Filter out common words
                    if len(word) > 3:
                        vocabulary_freq[word] = vocabulary_freq.get(word, 0) + 1
        
        # Find common patterns
        common_intro_words = find_common_phrases(intro_phrases)
        common_outro_words = find_common_phrases(outro_phrases)
        
        # Get top vocabulary
        top_vocabulary = sorted(
            vocabulary_freq.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:50]
        
        # Build creator profile
        creator_profile = {
            "channel_id": channel_id,
            "channel_name": channel_info['title'],
            "analyzed_videos": len(videos_with_transcripts),
            "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "style_patterns": {
                "common_intro_phrases": common_intro_words,
                "common_outro_phrases": common_outro_words,
                "vocabulary": {
                    "total_unique_words": len(vocabulary_freq),
                    "total_words_analyzed": total_words,
                    "top_words": dict(top_vocabulary)
                }
            },
            "content_structure": {
                "avg_video_duration": sum(v['duration_seconds'] for v in videos_with_transcripts) / len(videos_with_transcripts),
                "intro_style": "consistent" if len(set(common_intro_words[:3])) < 5 else "varied",
                "outro_style": "consistent" if len(set(common_outro_words[:3])) < 5 else "varied"
            },
            "videos_analyzed": [
                {
                    "id": v['id'],
                    "title": v['title'],
                    "duration": v['duration_seconds']
                }
                for v in videos_with_transcripts
            ]
        }
        
        # Save profile if requested
        if save_profile:
            from pathlib import Path
            if profile_path:
                profile_file = Path(profile_path)
            else:
                profile_dir = Path("creator_profiles")
                profile_dir.mkdir(exist_ok=True)
                profile_file = profile_dir / f"{channel_id}_profile.json"
            
            with open(profile_file, 'w') as f:
                json.dump(creator_profile, f, indent=2)
            
            creator_profile['profile_saved_to'] = str(profile_file)
        
        return types.TextContent(
            type="text",
            text=json.dumps(creator_profile, indent=2)
        )
        
    except Exception as e:
        logger.error(f"Error analyzing channel style: {e}")
        return types.TextContent(
            type="text",
            text=json.dumps(format_error_response(e))
        )

def find_common_phrases(phrases: List[str], min_length: int = 2) -> List[str]:
    """Find common words/phrases across multiple texts"""
    if not phrases:
        return []
    
    # Simple word frequency analysis
    word_freq = {}
    for phrase in phrases:
        words = phrase.lower().split()
        for word in words:
            if len(word) >= min_length:
                word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:20]]