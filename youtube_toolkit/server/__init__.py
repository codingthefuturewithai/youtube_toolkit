"""MCP server package initialization"""

from youtube_toolkit.config import load_config
from youtube_toolkit.server.app import create_mcp_server

# Create server instance with default configuration
server = create_mcp_server(load_config())

__all__ = ["server", "create_mcp_server"]
