# Create YouTube Analysis Slash Commands for Claude Code

## Context

You have access to a YouTube MCP server that provides data-fetching tools. Your task is to create Claude Code slash commands that use these tools to help content creators analyze YouTube channels and research their niche.

## Available MCP Tools

Your commands will use these YouTube MCP tools:
- `youtube_get_video_transcript` - Fetches video transcripts (no API key required)
- `youtube_get_video_metadata` - Gets video statistics and information
- `youtube_get_channel_videos` - Lists videos from any channel
- `youtube_search_videos` - Searches YouTube with filters
- `youtube_get_channel_metadata` - Gets detailed channel information

## Critical Command Style Requirements

### The "I'll" Pattern is MANDATORY

Every action MUST use "I'll" statements. This is how Claude Code executes commands properly. Here's an example of the CORRECT style:

```markdown
---
description: Analyze any YouTube channel's content strategy and performance
usage: /analyze-channel --channel-id "UCxxxxxx" [--is-mine true]
example: /analyze-channel --channel-id "UCBJycsmduvYEL83R_U4JriQ"
---

I'll analyze this YouTube channel to understand its content strategy and performance.

## Step 1: Parse Arguments

I'll extract the channel ID and check if this is marked as your own channel from "$ARGUMENTS".

## Step 2: Fetch Channel Overview

I'll use the youtube_get_channel_metadata tool to get:
- Subscriber count and total views
- Channel age and video count
- Keywords and branding

## Step 3: Analyze Recent Content

I'll use youtube_get_channel_videos to fetch the last 20 videos.

Then I'll identify:
- Publishing frequency patterns
- Average video length
- View and engagement trends

## Step 4: Sample Top Performers

I'll use youtube_get_video_transcript on the top 3 performing videos to understand:
- Content structure patterns
- Speaking style and pacing
- Technical depth

## Step 5: Generate Analysis Report

Based on all this data, I'll create a comprehensive analysis covering:
- Content pillars and themes
- Performance benchmarks
- Publishing strategy
- Audience engagement patterns

## Step 6: Save Report

!mkdir -p youtube-analysis/channels
I'll save the analysis to: youtube-analysis/channels/[channel-name]_analysis.md
```

### Style Rules:
1. **ALWAYS use "I'll"** for actions: "I'll fetch", "I'll analyze", "I'll save"
2. **NO executable code** - Use natural language only
3. **Shell commands use !** prefix: `!mkdir -p reports/analysis`
4. **Reference user input** with "$ARGUMENTS"
5. **Step-by-step structure** with clear headers

## Required Slash Commands to Create

### 1. `/analyze-channel`
Analyzes any YouTube channel (your own or competitors).

**Key features:**
- Accepts `--channel-id` parameter (required)
- Optional `--is-mine true` flag for organizing reports
- Fetches channel stats, recent videos, and sample transcripts
- Generates comprehensive content strategy analysis
- Saves to `youtube-analysis/channels/` or `youtube-analysis/my-channel/`

### 2. `/research-niche`
Researches what content is succeeding in a specific niche.

**Key features:**
- Accepts topic/niche as argument
- Uses youtube_search_videos sorted by viewCount
- Analyzes top 20-30 videos for patterns
- Fetches transcripts of top 5 performers
- Identifies content gaps and opportunities
- Saves to `youtube-analysis/niche-research/`

### 3. `/compare-creators`
Compares teaching/content styles between 2-5 videos.

**Key features:**
- Accepts multiple video URLs as arguments
- Fetches metadata and transcripts for each
- Analyzes differences in approach, pacing, structure
- Creates side-by-side comparison
- Saves to `youtube-analysis/comparisons/`

### 4. `/track-performance`
Tracks channel performance trends over time.

**Key features:**
- Accepts `--channel-id` and optional `--period` (30days, 90days, etc.)
- Fetches videos from specified timeframe
- Calculates performance metrics and trends
- Identifies what content types work best
- Saves to `youtube-analysis/performance/`

### 5. `/find-content-gaps`
Identifies underserved topics in a niche.

**Key features:**
- Accepts broad topic area as argument
- Performs multiple related searches
- Maps what's been covered extensively
- Identifies missing subtopics or angles
- Saves to `youtube-analysis/opportunities/`

## Implementation Requirements

1. **All analysis happens in the command** - MCP tools only fetch data
2. **Every command saves reports** - Both for reference and tracking
3. **Handle missing API keys gracefully** - Offer transcript-only analysis
4. **Include progress updates** - "I'll now fetch...", "I'll analyze..."
5. **Create organized output structure**:
   ```
   youtube-analysis/
   ├── my-channel/
   ├── channels/
   ├── niche-research/
   ├── comparisons/
   ├── performance/
   └── opportunities/
   ```

## Error Handling

Include helpful error messages:
- API key missing: Offer to proceed with transcript-only analysis
- Rate limits: Suggest waiting or using cached data
- Invalid channel ID: Provide format guidance

## Remember

These commands help content creators:
- Understand their own channel performance
- Learn from successful creators
- Find content opportunities
- Improve their content strategy

The MCP tools fetch data. Your commands provide the intelligence.