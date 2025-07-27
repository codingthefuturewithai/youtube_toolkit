"""MCP server implementation with Echo tool"""

import asyncio
import sys
import click
from typing import Optional

from mcp import types
from mcp.server.fastmcp import FastMCP

from youtube_toolkit.config import ServerConfig, load_config
from youtube_toolkit.logging_config import setup_logging, logger
from youtube_toolkit.tools.echo import echo

# YouTube tool imports
from youtube_toolkit.tools.youtube_video import (
    youtube_get_video_info,
    youtube_get_video_transcript
)
from youtube_toolkit.tools.youtube_channel import (
    youtube_get_channel_videos,
    youtube_analyze_channel_style
)
from youtube_toolkit.tools.youtube_search import youtube_search_videos
from youtube_toolkit.tools.youtube_cache import (
    youtube_get_transcript_cache_info,
    youtube_clear_transcript_cache
)


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

    @mcp_server.tool(
        name="echo",
        description="Echo back the input text with optional case transformation",
    )
    def echo_tool(text: str, transform: Optional[str] = None) -> types.TextContent:
        """Wrapper around the echo tool implementation"""
        return echo(text, transform)

    # YouTube Video Tools
    @mcp_server.tool(
        name="youtube_get_video_info",
        description="Fetch metadata for a single YouTube video including title, channel, duration, and statistics"
    )
    def youtube_get_video_info_tool(
        video_id: str,
        include_statistics: bool = True
    ) -> types.TextContent:
        """Fetch YouTube video metadata"""
        return youtube_get_video_info(video_id, include_statistics)

    @mcp_server.tool(
        name="youtube_get_video_transcript",
        description="Fetch and cache video transcript with smart extraction options (full, analysis, intro_only, outro_only)"
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
        description="List recent videos from a YouTube channel with optional transcript fetching"
    )
    def youtube_get_channel_videos_tool(
        channel_id: str,
        max_results: int = 10,
        include_transcripts: bool = False,
        delay_seconds: Optional[float] = None
    ) -> types.TextContent:
        """List videos from a YouTube channel"""
        return youtube_get_channel_videos(channel_id, max_results, include_transcripts, delay_seconds)

    @mcp_server.tool(
        name="youtube_analyze_channel_style",
        description="Perform comprehensive channel analysis for content style profiling"
    )
    def youtube_analyze_channel_style_tool(
        channel_id: str,
        max_videos: int = 5,
        save_profile: bool = True,
        profile_path: Optional[str] = None
    ) -> types.TextContent:
        """Analyze channel content style and patterns"""
        return youtube_analyze_channel_style(channel_id, max_videos, save_profile, profile_path)

    # YouTube Search Tools
    @mcp_server.tool(
        name="youtube_search_videos",
        description="Search YouTube videos by query with sorting and filtering options"
    )
    def youtube_search_videos_tool(
        query: str,
        max_results: int = 10,
        order: str = "relevance",
        published_after: Optional[str] = None
    ) -> types.TextContent:
        """Search YouTube videos"""
        return youtube_search_videos(query, max_results, order, published_after)

    # YouTube Cache Management Tools
    @mcp_server.tool(
        name="youtube_get_transcript_cache_info",
        description="Get information about cached transcripts"
    )
    def youtube_get_transcript_cache_info_tool(
        video_id: Optional[str] = None
    ) -> types.TextContent:
        """Get transcript cache information"""
        return youtube_get_transcript_cache_info(video_id)

    @mcp_server.tool(
        name="youtube_clear_transcript_cache",
        description="Clear transcript cache for one or all videos"
    )
    def youtube_clear_transcript_cache_tool(
        video_id: Optional[str] = None,
        older_than_days: Optional[int] = None
    ) -> types.TextContent:
        """Clear transcript cache entries"""
        return youtube_clear_transcript_cache(video_id, older_than_days)


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