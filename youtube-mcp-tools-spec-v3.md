# YouTube Content Creator MCP Server - Complete Tool Specification v3

## Overview

MCP server providing YouTube data access tools for content creators. All tools fetch raw data without performing analysis. Intelligence and interpretation are handled by AI agents using these tools.

## Tool Specifications

### 1. `youtube_get_video_transcript`

Fetches the transcript for any YouTube video. Does not require API key.

#### Parameters
- `video_id` (string, **required**): YouTube video ID (11 characters) or full YouTube URL
- `use_cache` (boolean, optional, default: `true`): Whether to use cached transcript if available
- `cache_directory` (string, optional, default: `"./transcript_cache"`): Directory where transcripts are cached

#### Returns
```json
{
  "video_id": "dQw4w9WgXcQ",
  "transcript": [
    {
      "text": "Never gonna give you up",
      "start": 0.0,
      "duration": 2.4
    },
    {
      "text": "Never gonna let you down",
      "start": 2.4,
      "duration": 2.2
    }
  ],
  "language": "en",
  "language_code": "en",
  "is_generated": false,
  "is_translatable": true,
  "translation_languages": [
    {"language": "Spanish", "language_code": "es"},
    {"language": "French", "language_code": "fr"}
  ],
  "cached": true,
  "cache_timestamp": "2025-01-27T10:00:00Z",
  "fetch_timestamp": "2025-01-27T10:00:00Z"
}
```

#### Error Responses
- `transcript_disabled`: Video owner disabled transcripts
- `no_transcript_found`: No transcript available in any language
- `video_unavailable`: Video is private, deleted, or region-blocked
- `rate_limit`: Too many requests (retry after delay)

---

### 2. `youtube_get_video_metadata`

Fetches comprehensive metadata for a single YouTube video. Requires API key.

#### Parameters
- `video_id` (string, **required**): YouTube video ID (11 characters) or full YouTube URL

#### Returns
```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "description": "Full video description...",
  "channel": {
    "id": "UCuAXFkgsw1L7xaCfnd5JJOw",
    "title": "Rick Astley",
    "subscriber_count": 3500000
  },
  "published_at": "2009-10-25T06:57:33Z",
  "duration": "PT3M33S",
  "duration_seconds": 213,
  "thumbnail": {
    "default": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
    "medium": "https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg",
    "high": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
    "standard": "https://i.ytimg.com/vi/dQw4w9WgXcQ/sddefault.jpg",
    "maxres": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
  },
  "tags": ["rick astley", "never gonna give you up", "80s"],
  "category_id": "10",
  "category_name": "Music",
  "statistics": {
    "view_count": 1400000000,
    "like_count": 15000000,
    "dislike_count": null,
    "comment_count": 2000000
  },
  "privacy_status": "public",
  "embeddable": true,
  "live_broadcast_content": "none",
  "default_language": "en",
  "default_audio_language": "en",
  "_metadata": {
    "api_quota_cost": 1,
    "fetched_at": "2025-01-27T10:00:00Z"
  }
}
```

#### Error Responses
- `video_not_found`: Video ID doesn't exist
- `api_key_invalid`: Invalid or missing API key
- `quota_exceeded`: YouTube API quota limit reached

---

### 3. `youtube_get_channel_videos`

Lists videos from a YouTube channel with optional transcript fetching.

#### Parameters
- `channel_id` (string, **required**): YouTube channel ID (starts with "UC", 24 characters total)
- `max_results` (integer, optional, default: `25`): Number of videos to return (1-50)
- `include_transcripts` (boolean, optional, default: `false`): Whether to fetch transcripts
- `use_cache` (boolean, optional, default: `true`): Use cached transcripts when include_transcripts is true
- `transcript_delay_seconds` (number, optional, default: `10`): Delay between transcript fetches to avoid rate limits

#### Returns
```json
{
  "channel": {
    "id": "UCuAXFkgsw1L7xaCfnd5JJOw",
    "title": "Rick Astley",
    "description": "Official Rick Astley YouTube Channel",
    "subscriber_count": 3500000,
    "view_count": 1500000000,
    "video_count": 127,
    "created_at": "2009-10-24T21:20:49Z",
    "country": "GB",
    "custom_url": "https://youtube.com/@RickAstley",
    "thumbnail_url": "https://yt3.googleusercontent.com/..."
  },
  "videos": [
    {
      "video_id": "dQw4w9WgXcQ",
      "title": "Rick Astley - Never Gonna Give You Up",
      "description": "The official video...",
      "published_at": "2009-10-25T06:57:33Z",
      "duration": "PT3M33S",
      "duration_seconds": 213,
      "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg",
      "view_count": 1400000000,
      "like_count": 15000000,
      "comment_count": 2000000,
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "transcript": null
    }
  ],
  "_metadata": {
    "api_quota_cost": 3,
    "videos_returned": 25,
    "transcripts_fetched": 0,
    "transcripts_cached": 0,
    "fetched_at": "2025-01-27T10:00:00Z"
  }
}
```

#### Notes
- Videos are returned sorted by upload date (newest first)
- When `include_transcripts` is true, the `transcript` field contains the same structure as `youtube_get_video_transcript`
- Transcript fetching respects the delay to avoid rate limits

---

### 4. `youtube_search_videos`

Searches YouTube videos with advanced filtering options.

#### Parameters
- `query` (string, **required**): Search query text
- `max_results` (integer, optional, default: `25`): Maximum results to return (1-50)
- `order` (string, optional, default: `"relevance"`): Sort order
  - `"date"`: Upload date (newest first)
  - `"rating"`: Highest rating
  - `"relevance"`: Most relevant to query
  - `"title"`: Alphabetical by title
  - `"viewCount"`: Most views
- `published_after` (string, optional): ISO 8601 date (e.g., "2025-01-01T00:00:00Z")
- `published_before` (string, optional): ISO 8601 date
- `video_duration` (string, optional): Duration filter
  - `"short"`: Under 4 minutes
  - `"medium"`: 4-20 minutes
  - `"long"`: Over 20 minutes
- `channel_id` (string, optional): Limit results to specific channel
- `region_code` (string, optional): ISO 3166-1 alpha-2 country code (e.g., "US")
- `relevance_language` (string, optional): ISO 639-1 two-letter language code

#### Returns
```json
{
  "query": "React hooks tutorial",
  "results": [
    {
      "video_id": "dpw9EHDh2bM",
      "title": "React Hooks Tutorial - Complete Guide",
      "channel": {
        "id": "UC8butISFwT-Wl7EV0hUK0BQ",
        "title": "freeCodeCamp.org"
      },
      "description": "Learn React Hooks in this complete tutorial...",
      "published_at": "2023-03-15T16:00:10Z",
      "duration": "PT1H23M45S",
      "duration_seconds": 5025,
      "view_count": 245000,
      "like_count": 8900,
      "thumbnail_url": "https://i.ytimg.com/vi/dpw9EHDh2bM/mqdefault.jpg",
      "url": "https://www.youtube.com/watch?v=dpw9EHDh2bM"
    }
  ],
  "_metadata": {
    "api_quota_cost": 100,
    "total_results": 1000000,
    "returned_results": 25,
    "next_page_token": "CAoQAA",
    "fetched_at": "2025-01-27T10:00:00Z"
  }
}
```

#### Notes
- Results include a snippet of the description (not full text)
- Use `next_page_token` for pagination (not implemented in base version)
- High API quota cost (100 units) - use sparingly

---

### 5. `youtube_get_channel_metadata`

Fetches detailed metadata for a YouTube channel.

#### Parameters
- `channel_id` (string, **required**): YouTube channel ID (starts with "UC") or username or handle

#### Returns
```json
{
  "channel": {
    "id": "UCBJycsmduvYEL83R_U4JriQ",
    "title": "Marques Brownlee",
    "handle": "@mkbhd",
    "custom_url": "https://youtube.com/@mkbhd",
    "description": "Tech reviews, cars, and more...",
    "published_at": "2008-03-21T23:10:38Z",
    "country": "US",
    "statistics": {
      "subscriber_count": 18700000,
      "subscriber_count_hidden": false,
      "view_count": 3900000000,
      "video_count": 1654
    },
    "branding": {
      "keywords": ["technology", "reviews", "tech", "gadgets"],
      "banner_url": "https://yt3.googleusercontent.com/...",
      "thumbnail_url": "https://yt3.googleusercontent.com/..."
    },
    "content_details": {
      "related_playlists": {
        "uploads": "UUBJycsmduvYEL83R_U4JriQ",
        "likes": "LLBJycsmduvYEL83R_U4JriQ"
      }
    },
    "status": {
      "privacy_status": "public",
      "is_linked": true,
      "long_uploads_status": "longUploadsUnspecified",
      "made_for_kids": false
    }
  },
  "_metadata": {
    "api_quota_cost": 3,
    "fetched_at": "2025-01-27T10:00:00Z"
  }
}
```

#### Error Responses
- `channel_not_found`: Channel doesn't exist
- `api_key_invalid`: Invalid or missing API key
- `quota_exceeded`: YouTube API quota limit reached

---

## Configuration

### Environment Variables

#### Required
- `YOUTUBE_API_KEY`: YouTube Data API v3 key (required for all tools except `youtube_get_video_transcript`)

#### Optional
- `TRANSCRIPT_CACHE_DIR`: Directory for transcript cache (default: `"./transcript_cache"`)
- `DEFAULT_TRANSCRIPT_DELAY`: Default delay between transcript fetches in seconds (default: `10`)
- `MAX_CACHE_SIZE_MB`: Maximum cache size in megabytes (default: `500`)
- `CACHE_EXPIRY_DAYS`: Days before cached transcripts expire (default: `30`)

### Rate Limiting

1. **Transcript Fetching**: 
   - Default 10-second delay between requests
   - No official rate limit documentation
   - Can be hours to days if limit hit

2. **YouTube Data API v3**:
   - Default quota: 10,000 units per day
   - Cost per operation varies (1-100 units)
   - Resets at midnight Pacific Time

### Error Response Format

All tools return consistent error structures:

```json
{
  "error": {
    "type": "rate_limit",
    "message": "Rate limit exceeded. Please retry after delay.",
    "retry_after": 3600,
    "details": {
      "requests_made": 100,
      "time_window": "1 hour"
    }
  }
}
```

Error types:
- `rate_limit`: Too many requests
- `not_found`: Resource doesn't exist
- `api_error`: YouTube API error
- `network_error`: Connection issues
- `invalid_parameter`: Bad input
- `quota_exceeded`: Daily API limit reached
- `authentication_error`: Invalid or missing API key

## Implementation Notes

1. **Channel ID Format**: Always 24 characters starting with "UC"
2. **Video ID Format**: Always 11 characters
3. **URL Handling**: Tools should accept both IDs and full YouTube URLs
4. **Cache Strategy**: Transcripts should be cached indefinitely with metadata
5. **Quota Awareness**: Return API costs in metadata for quota tracking
6. **Timezone**: All timestamps in UTC using ISO 8601 format

## Cache File Structure

Transcript cache files should be stored as:
```
transcript_cache/
├── dQw4w9WgXcQ.json
├── 9bZkp7q19f0.json
└── cache_metadata.json
```

Each cache file contains the full response from `youtube_get_video_transcript`.