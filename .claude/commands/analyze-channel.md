---
description: Analyze any YouTube channel's content strategy and performance
usage: /analyze-channel --channel-id "UCxxxxxx" [--is-mine true]
example: /analyze-channel --channel-id "UCBJycsmduvYEL83R_U4JriQ"
---

I'll analyze this YouTube channel to understand its content strategy and performance.

## Step 1: Parse Arguments

I'll extract the channel ID and check if this is marked as your own channel from "$ARGUMENTS".

## Step 2: Fetch Channel Overview

I'll fetch the channel metadata:
- Use mcp__youtube-toolkit__youtube_get_channel_metadata to get channel information
- Pass the channel_id from the parsed arguments

## Step 3: Analyze Recent Content

I'll fetch the channel's recent videos:
- Use mcp__youtube-toolkit__youtube_get_channel_videos to get the video list
- Pass channel_id and max_results: 20

Then I'll identify:
- Publishing frequency patterns (videos per week/month)
- Average video length and duration trends
- View count distribution and engagement rates
- Most successful video types and topics

## Step 4: Sample Top Performers

I'll identify the top 3 performing videos based on view count and engagement.

For each top performer, I'll fetch and analyze transcripts:
- Use mcp__youtube-toolkit__youtube_get_video_transcript for each video
- Pass video_id and extract_mode: "analysis"
- This will provide samples from intro, outro, and main content

From these transcripts, I'll understand:
- Content structure patterns (intro/outro style)
- Speaking style and pacing
- Key topics and technical depth
- Hook strategies and retention techniques

## Step 5: Generate Comprehensive Analysis

Based on all this data, I'll create a detailed analysis covering:

### Content Strategy
- Main content pillars and themes
- Video format preferences (tutorials, reviews, discussions)
- Title and thumbnail patterns
- Publishing schedule consistency

### Performance Metrics
- Average views per video
- Engagement rate benchmarks
- Growth trajectory
- Best performing content types

### Audience Insights
- Peak publishing times
- Content that drives most engagement
- Community interaction patterns

### Competitive Advantages
- Unique content angles
- Production quality observations
- Differentiation factors

## Step 6: Save Analysis Report

!mkdir -p youtube-analysis/channels
!mkdir -p youtube-analysis/my-channel

I'll determine the save location based on the --is-mine flag and save the comprehensive analysis as a markdown report with:
- Executive summary
- Detailed metrics and charts
- Content recommendations
- Growth opportunities

The report will be saved to:
- If --is-mine true: youtube-analysis/my-channel/[channel-name]_analysis_[date].md
- Otherwise: youtube-analysis/channels/[channel-name]_analysis_[date].md

## Error Handling

If the YouTube API key is not configured:
- I'll notify you about the limitation
- I'll offer to proceed with transcript-only analysis if you have specific video IDs
- I'll suggest adding the API key to your .env file for full functionality

If we encounter rate limits:
- I'll work with the data we've collected so far
- I'll note which analyses were incomplete
- I'll suggest optimal times to retry