"""MCP server implementation for YouTube toolkit"""

import asyncio
import sys
import click
from typing import Optional

from mcp import types
from mcp.server.fastmcp import FastMCP

from youtube_toolkit.config import ServerConfig, load_config
from youtube_toolkit.logging_config import setup_logging, logger
# YouTube tool imports
from youtube_toolkit.tools.youtube_video import (
    youtube_get_video_metadata,
    youtube_get_video_transcript
)
from youtube_toolkit.tools.youtube_channel import (
    youtube_get_channel_videos,
    youtube_get_channel_metadata
)
from youtube_toolkit.tools.youtube_search import youtube_search_videos


def create_mcp_server(config: Optional[ServerConfig] = None) -> FastMCP:
    """Create and configure the MCP server instance"""
    if config is None:
        config = load_config()
    
    # Set up logging first
    setup_logging(config)
    
    server = FastMCP(config.name)

    # Register all tools with the server
    register_tools(server)

    return server


def register_tools(mcp_server: FastMCP) -> None:
    """Register all MCP tools with the server"""

    # YouTube Video Tools
    @mcp_server.tool(
        name="youtube_get_video_metadata",
        description="""Fetch comprehensive metadata for a YouTube video.

Parameters:
- video_id (required): YouTube video ID or full URL (e.g., 'dQw4w9WgXcQ' or 'https://youtube.com/watch?v=dQw4w9WgXcQ')
- include_statistics (optional, default: true): Include view/like/comment counts

Returns: Video title, description, channel info with subscriber count, duration, thumbnails, tags, category, privacy status, and statistics
API quota cost: 3 units"""
    )
    def youtube_get_video_metadata_tool(
        video_id: str,
        include_statistics: bool = True
    ) -> types.TextContent:
        """Fetch YouTube video metadata"""
        return youtube_get_video_metadata(video_id, include_statistics)

    @mcp_server.tool(
        name="youtube_get_video_transcript",
        description="""Fetch and intelligently cache video transcripts with flexible extraction modes.

Parameters:
- video_id (required): YouTube video ID or URL
- extract_mode (optional, default: 'full'): 
  * 'full': Complete transcript with timestamps
  * 'analysis': Intro (first 60s) + outro (last 60s) + 3 main content samples
  * 'intro_only': First 60 seconds only
  * 'outro_only': Last 60 seconds only
- use_cache (optional, default: true): Use cached transcript if available
- delay_seconds (optional, default: 10): Seconds to wait before scraping (minimum 1s recommended to avoid IP blocking)

Returns: Transcript text with timing data, metadata including cache status
Note: Uses web scraping; delays prevent IP blocking by YouTube"""
    )
    def youtube_get_video_transcript_tool(
        video_id: str,
        extract_mode: str = "full",
        use_cache: bool = True,
        delay_seconds: Optional[float] = None
    ) -> types.TextContent:
        """Get video transcript with various extraction modes"""
        return youtube_get_video_transcript(video_id, extract_mode, use_cache, delay_seconds)

    # YouTube Channel Tools
    @mcp_server.tool(
        name="youtube_get_channel_videos",
        description="""List recent videos from a YouTube channel with detailed metadata.

Parameters:
- channel_id (required): YouTube channel ID (must start with 'UC', e.g., 'UCuAXFkgsw1L7xaCfnd5JJOw')
- max_results (optional, default: 10): Number of videos to return (1-50)
- include_transcripts (optional, default: false): Fetch transcript for each video
- use_cache (optional, default: true): Use cached transcripts when available
- delay_seconds (optional, default: 10): Seconds to wait between transcript fetches (minimum 1s recommended to avoid IP blocking)

Returns: Channel info with subscriber count, array of videos with metadata, transcript data if requested
Note: Including transcripts significantly increases processing time. First video has no delay, subsequent videos use delay_seconds.
API quota cost: 101+ units (1 channel + 100 search + details)"""
    )
    def youtube_get_channel_videos_tool(
        channel_id: str,
        max_results: int = 10,
        include_transcripts: bool = False,
        use_cache: bool = True,
        delay_seconds: Optional[float] = None
    ) -> types.TextContent:
        """List videos from a YouTube channel"""
        return youtube_get_channel_videos(channel_id, max_results, include_transcripts, use_cache, delay_seconds)


    # YouTube Search Tools
    @mcp_server.tool(
        name="youtube_search_videos",
        description="""Search YouTube videos with sorting options.

Parameters:
- query (required): Search terms (e.g., 'python tutorial')
- max_results (optional, default: 10): Number of results (1-50)
- order (optional, default: 'relevance'): Sort by 'relevance', 'date', 'viewCount', or 'rating'
- published_after (optional): ISO 8601 date string (e.g., '2024-01-01T00:00:00Z')

Returns: Search query echo, array of video results with metadata including title, description, channel, duration, view count
API quota cost: 100 units per search"""
    )
    def youtube_search_videos_tool(
        query: str,
        max_results: int = 10,
        order: str = "relevance",
        published_after: Optional[str] = None
    ) -> types.TextContent:
        """Search YouTube videos"""
        return youtube_search_videos(query, max_results, order, published_after)

    @mcp_server.tool(
        name="youtube_get_channel_metadata",
        description="""Fetch comprehensive channel information including statistics, branding, and configuration.

Parameters:
- channel_id (required): Channel ID, username, or handle (e.g., 'UCBJycsmduvYEL83R_U4JriQ', 'mkbhd', '@mkbhd')

Returns: Channel title, handle, custom URL, description, country, creation date, statistics (subscribers, views, video count), branding (keywords, banner URL), content playlists, and channel status

API quota cost: 3 units (direct ID) or 103 units (username/handle lookup requires search)"""
    )
    def youtube_get_channel_metadata_tool(
        channel_id: str
    ) -> types.TextContent:
        """Get detailed channel metadata"""
        return youtube_get_channel_metadata(channel_id)


# Create a server instance that can be imported by the MCP CLI
server = create_mcp_server()


@click.command()
@click.option("--port", default=3001, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type (stdio or sse)",
)
def main(port: int, transport: str) -> int:
    """Run the server with specified transport."""
    try:
        if transport == "stdio":
            asyncio.run(server.run_stdio_async())
        else:
            server.settings.port = port
            asyncio.run(server.run_sse_async())
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())