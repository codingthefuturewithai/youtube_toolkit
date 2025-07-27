# YouTube Toolkit

MCP server for YouTube content analysis, transcript extraction, and creator style profiling with intelligent caching and rate limit protection.

This toolkit enables AI assistants to:
- Analyze YouTube channels and their content strategies
- Extract video transcripts without rate limit issues (with intelligent caching)
- Search YouTube and analyze trends in specific niches
- Compare creator styles and teaching approaches
- Identify content gaps and opportunities
- Track channel performance over time

## Claude Code Custom Commands

This toolkit includes powerful Claude Code slash commands in the `.claude/commands/` directory that automate common YouTube analysis workflows:

- **/analyze-channel** - Comprehensive channel analysis with metrics, content strategy insights, and growth opportunities
- **/research-niche** - Research successful content in any YouTube niche to understand what works
- **/compare-creators** - Compare teaching styles and content approaches between multiple videos
- **/track-performance** - Track channel performance trends over time with detailed analytics
- **/find-content-gaps** - Identify underserved topics and content opportunities in your niche

To use these commands in Claude Code:
1. Ensure the MCP server is installed and configured (see Quick Start below)
2. Type `/` in Claude Code to see available commands
3. Example: `/analyze-channel "UCBJycsmduvYEL83R_U4JriQ"`

These commands handle all the complexity of data fetching, analysis, and report generation automatically.

## Quick Start for MCP Clients

### 1. Install the MCP server (Recommended)

For the most reliable setup, first install the server as an isolated tool:

```bash
# Install the MCP server
uv tool install youtube_toolkit

# Find the installed binary path
which youtube-toolkit-server  # macOS/Linux
where youtube-toolkit-server  # Windows
```

### 2. Configure your MCP client

#### For Claude Code (Recommended)

Use the Claude Code CLI to add the YouTube toolkit:

```bash
# Using uvx (simplest, but may have dependency conflicts)
claude mcp add youtube-toolkit --uvx youtube_toolkit

# Or with full configuration including API key
claude mcp add-json -s user youtube-toolkit '{"type":"stdio","command":"uvx","args":["youtube_toolkit"],"env":{"YOUTUBE_API_KEY":"your-api-key-here","TRANSCRIPT_CACHE_DIR":"~/youtube-transcript-cache","DEFAULT_TRANSCRIPT_DELAY":"10.0","MAX_CACHE_AGE_DAYS":"30"}}'

# For isolated installation (most reliable)
# First install: uv tool install youtube_toolkit
# Then find path: which youtube-toolkit-server
# Then add with absolute path:
claude mcp add-json -s user youtube-toolkit '{"type":"stdio","command":"/path/to/youtube-toolkit-server","args":[],"env":{"YOUTUBE_API_KEY":"your-api-key-here"}}'
```

#### For Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

#### For Cline

Add to `.vscode/settings.json` in your project

```json
{
  "youtube-toolkit": {
    "command": "/absolute/path/to/youtube-toolkit-server"
  }
}
```

```json
{
  "youtube-toolkit": {
    "command": "/absolute/path/to/youtube-toolkit-server",
    "env": {
      "YOUTUBE_API_KEY": "your-youtube-api-key-here",
      "TRANSCRIPT_CACHE_DIR": "~/youtube-transcript-cache",
      "DEFAULT_TRANSCRIPT_DELAY": "10.0",
      "MAX_CACHE_AGE_DAYS": "30"
    }
  }
}
```

**Alternative: Quick start with uvx** (may have dependency conflicts):
```json
{
  "youtube-toolkit": {
    "command": "uvx",
    "args": ["CTF_Youtube_Toolkit"]
  }
}
```

### 3. Get your credentials (if needed)

- **YouTube API Key** (optional but recommended): Get from [Google Cloud Console](https://console.cloud.google.com/)
  1. Create a new project or select existing
  2. Enable YouTube Data API v3
  3. Create credentials (API Key)
  4. Restrict key to YouTube Data API v3 for security

**Note**: The toolkit works without an API key by using transcript-only features, but channel/video metadata requires the API key.

### 4. Start using the tools

Once configured, you can ask your AI assistant to:
- "Analyze the YouTube channel UCBJycsmduvYEL83R_U4JriQ"
- "Research what content is succeeding in the Python programming niche"
- "Compare teaching styles between these 3 YouTube videos: [URLs]"
- "Find content gaps in the AI coding tools niche"
- "Track performance trends for channel UCxxxxxx over the last 90 days"

## Features

- YouTube channel analysis with comprehensive metrics
- Transcript extraction with intelligent caching and rate limit protection
- Video metadata fetching (views, likes, duration, etc.)
- YouTube search with multiple sort options
- Content gap identification and opportunity analysis
- Support for both stdio and SSE transports
- Comprehensive logging with automatic rotation
- Cross-platform compatibility (Linux, macOS, Windows)

## Available Tools

### youtube_get_video_transcript

Fetches and caches video transcripts with flexible extraction modes.

**Parameters:**
- `video_id` (required): YouTube video ID or URL
- `extract_mode` (optional, default: 'full'): 'full', 'analysis', 'intro_only', or 'outro_only'
- `use_cache` (optional, default: true): Use cached transcript if available
- `delay_seconds` (optional): Seconds to wait before scraping

**Returns:**
- Transcript text with timing data and metadata including cache status

### youtube_get_video_metadata

Fetches comprehensive metadata for a YouTube video.

**Parameters:**
- `video_id` (required): YouTube video ID or full URL
- `include_statistics` (optional, default: true): Include view/like/comment counts

**Returns:**
- Video title, description, channel info, duration, statistics, and more

### youtube_get_channel_videos

Lists recent videos from a YouTube channel with detailed metadata.

**Parameters:**
- `channel_id` (required): YouTube channel ID (must start with 'UC')
- `max_results` (optional, default: 10): Number of videos to return (1-50)
- `include_transcripts` (optional, default: false): Fetch transcript for each video
- `use_cache` (optional, default: true): Use cached transcripts when available
- `delay_seconds` (optional): Seconds between transcript fetches

**Returns:**
- Channel info with subscriber count, array of videos with metadata

### youtube_search_videos

Searches YouTube videos with sorting options.

**Parameters:**
- `query` (required): Search terms
- `max_results` (optional, default: 10): Number of results (1-50)
- `order` (optional, default: 'relevance'): Sort by 'relevance', 'date', 'viewCount', or 'rating'
- `published_after` (optional): ISO 8601 date string

**Returns:**
- Array of video results with metadata

### youtube_get_channel_metadata

Fetches comprehensive channel information.

**Parameters:**
- `channel_id` (required): Channel ID, username, or handle

**Returns:**
- Channel title, statistics, branding, and configuration

## Alternative Configuration Methods

### Using a different MCP client

The configuration above works for Claude Desktop and Cline. For other MCP clients:

1. Use `uvx youtube_toolkit-server` as the command
2. Set any required environment variables
3. Consult your MCP client's documentation for specific configuration format

### Using uv tool (Recommended for AI Assistants)

For isolated installation that avoids dependency conflicts:

```bash
# Install as an isolated tool
uv tool install youtube_toolkit

# Find the installed binary location
uv tool list | grep youtube_toolkit
# Or on macOS/Linux:
which youtube-toolkit-server
# Or on Windows:
where youtube-toolkit-server
```

Then use this configuration with the absolute path:
```json
{
  "youtube_toolkit": {
    "command": "/path/to/youtube_toolkit-server"
  }
}
```

**Note**: Replace `/path/to/` with the actual path from the commands above.

### Running from source

For development or testing from source code:

```json
{
  "youtube_toolkit": {
    "command": "python",
    "args": ["-m", "youtube_toolkit.server.app"],
    "env": {
      "PYTHONPATH": "/path/to/youtube_toolkit"
    }
  }
}
```

## Installation Options

### Quick Start with uvx (Simplest)

The configuration above using `uvx` will automatically download and run the server without installation. This is the simplest option but may have conflicts if you have other Python packages installed globally.

### Isolated Installation with uv tool (Most Reliable)

For a clean, isolated installation that prevents dependency conflicts:

```bash
# Install the MCP server as an isolated tool
uv tool install youtube_toolkit

# Verify installation and find the binary path
uv tool list | grep youtube_toolkit

# Platform-specific path discovery:
# macOS/Linux:
which youtube-toolkit-server
# Example output: /Users/username/.local/bin/youtube_toolkit-server

# Windows:
where youtube-toolkit-server
# Example output: C:\Users\username\.local\bin\youtube_toolkit-server.exe
```

**Important**: After installation, update your MCP client configuration to use the absolute path returned by the `which` or `where` command.

### Install from Source (Development)

For development or testing from source code:

```bash
git clone <repository-url>
cd youtube_toolkit

# Create and activate virtual environment
uv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
uv pip install -e .
```

Note: This requires the package to be published to PyPI. See [DEVELOPMENT.md](DEVELOPMENT.md#publishing-to-pypi) for publishing instructions.

## Troubleshooting

### Common Issues

1. **"Tool not found" error**
   - Ensure the server is running and properly configured
   - Check that the tool name is spelled correctly (e.g., `youtube_get_video_transcript`)
   - Verify your MCP client is connected to the server

2. **No YouTube API key configured**
   - The toolkit will still work but only transcript features will be available
   - Channel and video metadata tools will return an error
   - Add `YOUTUBE_API_KEY` to your environment configuration

3. **Rate limit errors**
   - Transcript fetching includes built-in delays to prevent rate limiting
   - If you still hit limits, increase `DEFAULT_TRANSCRIPT_DELAY`
   - Cached transcripts are used automatically when available

4. **Cache directory issues**
   - Ensure `TRANSCRIPT_CACHE_DIR` exists and is writable
   - Default is `~/youtube-transcript-cache`
   - Cache files older than `MAX_CACHE_AGE_DAYS` are automatically cleaned

### Dependency Conflicts

If you encounter dependency conflicts when using `uvx`:

1. **Use isolated installation instead**:
   ```bash
   # Install as an isolated tool to avoid conflicts
   uv tool install youtube_toolkit
   
   # Find the binary path
   which youtube-toolkit-server  # macOS/Linux
   where youtube-toolkit-server  # Windows
   ```

2. **Update your MCP client configuration** to use the absolute path from step 1

3. **If conflicts persist**, check for conflicting global packages:
   ```bash
   # List all globally installed packages
   uv pip list
   
   # Consider using a virtual environment for development
   ```

## Requirements

- Python 3.11 or 3.12
- Operating Systems: Linux, macOS, Windows

- YouTube Data API v3 key (optional, for full functionality)
- Internet access for YouTube API and transcript fetching
- Write access to cache directory for transcript storage

## Logging

The server logs all activity to both stderr and a rotating log file. Log files are stored in OS-specific locations:

- **macOS**: `~/Library/Logs/mcp-servers/youtube_toolkit.log`
- **Linux**: `~/.local/state/mcp-servers/logs/youtube_toolkit.log`
- **Windows**: `%LOCALAPPDATA%\mcp-servers\logs\youtube_toolkit.log`

Logs rotate at 10MB with 5 backups kept. Control verbosity with `LOG_LEVEL`:

```bash
LOG_LEVEL=DEBUG uvx youtube_toolkit-server
```

## Development

For development setup, testing, and contribution guidelines, see [DEVELOPMENT.md](DEVELOPMENT.md).

## AI Assistant Configuration

For detailed setup instructions for AI coding assistants (Claude, Cline, etc.), see [SETUP_PROMPT.md](SETUP_PROMPT.md).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

Tim Kitchens - timkitch@codingthefuture.ai

