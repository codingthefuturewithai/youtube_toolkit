# AI Assistant Setup Instructions for YouTube Toolkit

This document provides instructions for AI coding assistants to properly configure and use the YouTube Toolkit MCP server.

## Installation Method

**IMPORTANT**: Use `uvx` for running the MCP server. This creates ephemeral environments that prevent "works then breaks" stability issues.

### Step 1: Verify Prerequisites

```bash
# Install uv if not already installed
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell):
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Restart your terminal after installation
```

### Step 2: Configure Your MCP Client

**For Claude Code:**
```bash
# Quick setup
claude mcp add youtube-toolkit --uvx youtube-toolkit

# Or with full configuration including API key:
claude mcp add-json -s user youtube-toolkit '{"type":"stdio","command":"uvx","args":["--from","youtube-toolkit","youtube-toolkit-server"],"env":{"YOUTUBE_API_KEY":"your-api-key-here"}}'
```

**For Claude Desktop:**
Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "youtube-toolkit": {
      "command": "uvx",
      "args": ["--from", "youtube-toolkit", "youtube-toolkit-server"],
      "env": {
        "YOUTUBE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**For Cline (VS Code):**
Add to `.vscode/settings.json`:

```json
{
  "cline.MCP.mcpServers": {
    "youtube-toolkit": {
      "command": "uvx",
      "args": ["--from", "youtube-toolkit", "youtube-toolkit-server"],
      "env": {
        "YOUTUBE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Verification

After configuration:

1. Restart your MCP client
2. Test the server directly:
   ```bash
   uvx --from youtube-toolkit youtube-toolkit-server --version
   # Should output: "YouTube Toolkit MCP Server running"
   ```
3. In your MCP client, test with: "List the available YouTube tools"
4. If it fails, check:
   - `uvx` is installed and in PATH
   - The package name is correct: `youtube-toolkit`
   - MCP client logs for specific errors

## Troubleshooting

### "spawn uvx ENOENT" Error
- **Problem**: MCP client can't find `uvx` command
- **Solution**: 
  ```bash
  # Find where uvx is installed
  which uvx  # macOS/Linux
  where uvx  # Windows
  
  # If not found, reinstall uv:
  curl -LsSf https://astral.sh/uv/install.sh | sh
  
  # For macOS GUI apps, you may need to create a symlink:
  sudo ln -s ~/.local/bin/uvx /usr/local/bin/uvx
  ```

### Server Fails to Start
- Test the command directly in terminal:
  ```bash
  uvx --from youtube-toolkit youtube-toolkit-server
  ```
- Check for Python version compatibility (requires 3.11 or 3.12)
- Ensure no firewall blocking the connection

### Environment Variables
- Replace `your-api-key-here` with actual YouTube API key
- API key is optional - server works without it (transcript-only mode)
- Get API key from [Google Cloud Console](https://console.cloud.google.com/)

## Why uvx?

`uvx` creates ephemeral (temporary) environments for each execution, which:
- Prevents dependency conflicts
- Avoids "works then breaks" stability issues
- Ensures clean execution every time
- Automatically handles package updates

This is why we recommend `uvx` over `uv tool install` or `pip install` for MCP servers.