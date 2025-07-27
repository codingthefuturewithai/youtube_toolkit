---
description: Track YouTube channel performance trends over time
usage: /track-performance --channel-id "UCxxxxxx" [--period "30days|90days|6months|1year"]
example: /track-performance --channel-id "UCBJycsmduvYEL83R_U4JriQ" --period "90days"
---

I'll track and analyze the performance trends for this YouTube channel over the specified time period.

## Step 1: Parse Arguments

I'll extract the channel ID and time period from "$ARGUMENTS". If no period is specified, I'll default to 90 days of data.

## Step 2: Fetch Channel Overview

I'll fetch channel information:
- Use mcp__youtube-toolkit__youtube_get_channel_metadata
- Pass the channel_id from parsed arguments
- Get:
- Current subscriber count
- Total channel views
- Total video count
- Channel creation date

## Step 3: Fetch Videos from Time Period

I'll fetch videos from the channel:
- Use mcp__youtube-toolkit__youtube_get_channel_videos
- Pass channel_id and appropriate max_results based on the period:
- 30 days: up to 50 most recent videos
- 90 days: up to 100 most recent videos  
- 6 months: up to 150 most recent videos
- 1 year: up to 200 most recent videos

I'll collect videos in batches if needed to cover the full period.

## Step 4: Analyze Performance Metrics

For all videos in the period, I'll calculate:

### Publishing Patterns
- Videos published per week/month
- Most active publishing days
- Publishing time patterns
- Consistency score

### View Performance
- Average views per video
- View velocity (views per day since publish)
- Viral threshold for this channel
- View distribution (median vs mean)

### Engagement Metrics
- Average like/view ratio
- Comment engagement rate
- Like/dislike patterns (where available)
- Engagement trend over time

### Content Performance
- Best performing video types
- Optimal video length correlation
- Title length vs performance
- Topic performance mapping

## Step 5: Identify Trends

I'll analyze the data to identify:

### Growth Trends
- Subscriber growth rate estimation
- View growth trajectory
- Engagement rate changes
- Audience retention patterns

### Content Evolution
- Shifts in video topics
- Changes in video length
- Title strategy evolution
- Production quality improvements

### Performance Patterns
- Seasonal variations
- Day-of-week performance
- Time-of-day optimization
- Series vs standalone performance

## Step 6: Deep Dive Top & Bottom Performers

I'll identify the top 5 and bottom 5 performing videos by views.

For each, I'll analyze their openings:
- Use mcp__youtube-toolkit__youtube_get_video_transcript
- Pass video_id and extract_mode: "intro_only"
- This helps understand:
- What made top videos successful
- Why bottom videos underperformed
- Hook effectiveness correlation
- Title/thumbnail alignment

## Step 7: Generate Performance Report

!mkdir -p youtube-analysis/performance

I'll create a comprehensive performance tracking report with:

### Executive Dashboard
- Key metrics summary
- Growth rate analysis
- Performance health score
- Quick wins identified

### Detailed Analytics
- Publishing frequency charts
- View performance graphs
- Engagement trend lines
- Content type breakdown

### Performance Insights
- What's working well
- What needs improvement
- Emerging opportunities
- Risk factors identified

### Recommendations
- Optimal publishing schedule
- Content types to prioritize
- Title/thumbnail strategies
- Engagement tactics

The report will be saved to: youtube-analysis/performance/[channel-name]_performance_[period]_[date].md

## Step 8: Create Action Plan

Based on the analysis, I'll provide:
- 5 immediate optimizations
- Content calendar suggestions
- A/B testing recommendations
- Growth strategy outline
- Performance benchmarks to track

## Error Handling

If we can't fetch enough historical data:
- I'll work with available videos
- I'll note the actual period analyzed
- I'll adjust projections accordingly

If API quota is exhausted:
- I'll save partial analysis
- I'll prioritize most recent data
- I'll suggest when to continue

If no API key:
- I'll explain limitations
- I'll offer to analyze specific video IDs if provided
- I'll suggest manual tracking methods