---
description: Research what content is succeeding in a specific YouTube niche
usage: /research-niche "topic or niche"
example: /research-niche "python programming tutorials for beginners"
---

I'll research what content is succeeding in this niche to help you understand the landscape and opportunities.

## Step 1: Define Research Scope

I'll extract the niche/topic from "$ARGUMENTS" and prepare multiple search variations to get comprehensive coverage.

## Step 2: Search for Top Performing Content

I'll perform multiple searches:
- Use mcp__youtube-toolkit__youtube_search_videos for each query
- First search: Direct topic search sorted by viewCount (max_results: 20)
- Second search: Same topic sorted by date to find recent trends (max_results: 10)
- Third search: Topic + "tutorial" or "guide" sorted by viewCount (max_results: 10)
- Fourth search: Topic + "for beginners" sorted by viewCount (max_results: 10)

This gives me ~50 videos to analyze for patterns.

## Step 3: Analyze Video Performance Patterns

For all videos found, I'll analyze:
- View count distribution (what constitutes "viral" in this niche)
- Average video duration for successful content
- Upload frequency of top creators
- Title patterns and keyword usage
- Channel size correlation with video performance

## Step 4: Deep Dive into Top Performers

I'll identify the top 5 performing videos across all searches.

For each top performer, I'll:
- Use mcp__youtube-toolkit__youtube_get_video_metadata to get detailed statistics
- Use mcp__youtube-toolkit__youtube_get_video_transcript with extract_mode="analysis" to understand:
  - Content structure and pacing
  - Unique angles or approaches
  - Production style (scripted vs casual)
  - Call-to-action strategies

## Step 5: Identify Content Patterns

I'll analyze the collected data to identify:

### Successful Content Formats
- Video length sweet spots
- Common video structures
- Title formulas that work
- Thumbnail style patterns

### Topic Coverage
- Most popular subtopics
- Difficulty levels addressed
- Common pain points solved
- Recurring themes

### Creator Strategies
- Publishing frequency of successful channels
- Series vs standalone content
- Collaboration patterns
- Community engagement tactics

## Step 6: Find Opportunities

Based on the analysis, I'll identify:
- Underserved subtopics with high search volume
- Content gaps in existing coverage
- Emerging trends with low competition
- Unique angles not yet explored
- Optimal video lengths and formats

## Step 7: Generate Niche Research Report

!mkdir -p youtube-analysis/niche-research

I'll create a comprehensive report including:
- Executive summary of the niche landscape
- Top performing content analysis
- Successful creator strategies
- Content opportunity matrix
- Recommended content calendar
- Title and thumbnail insights
- SEO keyword opportunities

The report will be saved to: youtube-analysis/niche-research/[niche-name]_research_[date].md

## Step 8: Create Actionable Recommendations

I'll provide specific recommendations for:
- First 10 video ideas with highest potential
- Optimal posting schedule
- Target video length and format
- Title templates based on what works
- Differentiation strategies

## Error Handling

If we hit API quota limits:
- I'll work with the data collected so far
- I'll prioritize analyzing the highest performing content
- I'll note which analyses are incomplete

If no API key is available:
- I'll explain the limitations
- I'll offer alternative research methods using video IDs if you have them
- I'll suggest manual research strategies