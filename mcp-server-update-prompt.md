# Prompt for Updating YouTube MCP Server Implementation

## Context

You previously implemented a YouTube MCP server based on the initial specification in `youtube-mcp-tools-spec.md`. The server is working and has been tested successfully. Now we need to update it to match a refined specification that better serves content creators.

## Your Task

Update the existing YouTube MCP server implementation to match the new specification located at: `docs/youtube-mcp-tools-spec-v3.md`

## Required Changes

### 1. Remove Intelligence-Implying Tools
- **REMOVE**: `youtube_analyze_channel_style` - This tool implies AI analysis. Analysis should happen in AI agents, not MCP tools.

### 2. Update Existing Tools

#### `youtube_get_channel_videos`
Add this missing parameter:
- `use_cache` (boolean, optional, default: `true`): Use cached transcripts when `include_transcripts` is true

This parameter should work exactly like the `use_cache` in `youtube_get_video_transcript` - check cache first before fetching.

### 3. Verify Tool Naming
Ensure your tools are named exactly as in the spec:
- `youtube_get_video_transcript` (no API key required)
- `youtube_get_video_metadata` (requires API key)
- `youtube_get_channel_videos` (requires API key)
- `youtube_search_videos` (requires API key)
- `youtube_get_channel_metadata` (requires API key) - **NEW TOOL**

### 4. Implement New Tool

#### `youtube_get_channel_metadata`
This is a new tool that fetches detailed channel information. See the v3 spec for complete parameter and response details. Key features:
- Accepts channel ID, username, or @handle
- Returns comprehensive channel statistics
- Includes branding information (banner, keywords)
- Shows channel creation date and country

### 5. Response Structure Compliance

Ensure ALL tools return responses exactly as specified in v3, particularly:
- Include `_metadata` objects with API quota costs
- Use consistent error response format
- Include cache indicators where applicable
- Match the exact JSON structure shown in examples

### 6. Error Handling

Implement the standardized error format for all tools:
```json
{
  "error": {
    "type": "error_type_here",
    "message": "Human-readable description",
    "retry_after": 3600,  // optional
    "details": {}  // optional
  }
}
```

### 7. Cache Implementation

For `youtube_get_video_transcript`:
- Cache files should be stored as `{video_id}.json` in the cache directory
- Include cache metadata in responses (`cached`, `cache_timestamp`)
- Respect the `use_cache` parameter

## Testing Your Updates

After making changes, verify:

1. **Removed Tool**: Calling `youtube_analyze_channel_style` should return an error
2. **Cache Parameter**: Test `youtube_get_channel_videos` with `include_transcripts: true` and `use_cache: false` to verify it bypasses cache
3. **New Tool**: Test `youtube_get_channel_metadata` with a known channel ID like `UCBJycsmduvYEL83R_U4JriQ` (MKBHD)
4. **Error Format**: Trigger an error (e.g., invalid video ID) and verify it matches the spec format
5. **Metadata**: Verify all responses include `_metadata` with API quota costs

## Important Notes

- The core functionality you implemented is good - we're mainly cleaning up naming and adding one new tool
- Keep your existing transcript caching logic - it's working well
- The YouTube Data API integration you built is solid - no changes needed there
- Focus on matching the v3 spec exactly for consistency

Please proceed with these updates and let me know if you encounter any issues or need clarification on the specification.