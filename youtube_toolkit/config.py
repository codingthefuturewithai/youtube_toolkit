"""Server configuration for YouTube Toolkit MCP server"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class ServerConfig:
    """Configuration for the MCP server"""
    name: str = "YouTube Toolkit"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # YouTube API Configuration
    youtube_api_key: Optional[str] = os.getenv("YOUTUBE_API_KEY", None)
    transcript_cache_dir: str = os.getenv("TRANSCRIPT_CACHE_DIR", "./transcript_cache")
    default_transcript_delay: float = float(os.getenv("DEFAULT_TRANSCRIPT_DELAY", "10.0"))
    max_cache_age_days: int = int(os.getenv("MAX_CACHE_AGE_DAYS", "30"))


def load_config() -> ServerConfig:
    """Load server configuration from environment or defaults"""
    return ServerConfig(
        name=os.getenv("MCP_SERVER_NAME", "YouTube Toolkit"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        youtube_api_key=os.getenv("YOUTUBE_API_KEY", None),
        transcript_cache_dir=os.getenv("TRANSCRIPT_CACHE_DIR", "./transcript_cache"),
        default_transcript_delay=float(os.getenv("DEFAULT_TRANSCRIPT_DELAY", "10.0")),
        max_cache_age_days=int(os.getenv("MAX_CACHE_AGE_DAYS", "30"))
    )
