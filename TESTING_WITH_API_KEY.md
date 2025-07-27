# Testing with YouTube API Key

## Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your YouTube API key:
   ```
   YOUTUBE_API_KEY=your_actual_api_key_here
   ```

3. Install dependencies (if not already done):
   ```bash
   uv pip install -e .
   uv pip install pytest
   ```

## Running Tests

### Tests without API key (always run):
```bash
pytest tests/test_youtube_tools.py -v
```

### Tests with API key (only run when API key is set):
```bash
pytest tests/test_youtube_api_tools.py -v
```

### Run all tests:
```bash
pytest tests/ -v
```

## Security Notes

- The `.env` file is gitignored and will never be committed to the repository
- Your API key is only loaded into environment variables when the tests run
- The API key is never logged or displayed in test output

## Test Coverage

### Without API Key:
- Video ID parsing from various URL formats
- Duration parsing (ISO 8601)
- Transcript extraction utilities
- Cache management
- Error response formatting

### With API Key:
- `youtube_get_video_metadata` - Fetches video details
- `youtube_get_channel_videos` - Lists channel videos
- `youtube_get_channel_metadata` - Gets channel info
- `youtube_search_videos` - Searches for videos

## API Quota Usage

Be aware that running API tests will consume your YouTube API quota:
- Video metadata: 3 units per call
- Channel videos: 101+ units (search + details)
- Channel metadata: 3-103 units (depending on lookup method)
- Search: 100 units per call

Daily quota limit is typically 10,000 units for free tier.