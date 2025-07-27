---
description: Identify underserved topics and content opportunities in a YouTube niche
usage: /find-content-gaps "broad topic area"
example: /find-content-gaps "web development"
---

I'll help you find content gaps and underserved topics in this niche by analyzing what's been covered and what's missing.

## Step 1: Define Research Parameters

I'll extract the broad topic area from "$ARGUMENTS" and create a comprehensive search strategy with related subtopics and variations.

## Step 2: Map Current Content Landscape

I'll perform comprehensive searches:
- Use mcp__youtube-toolkit__youtube_search_videos for each query
- Execute multiple strategic searches:

### Broad Coverage Search
- Main topic sorted by relevance (20 results)
- Main topic sorted by view count (20 results)
- Main topic sorted by date (10 recent results)

### Depth Searches
- Topic + "tutorial" (15 results)
- Topic + "explained" (15 results)  
- Topic + "complete guide" (10 results)
- Topic + "for beginners" (15 results)
- Topic + "advanced" (10 results)
- Topic + "tips" (10 results)
- Topic + "mistakes" (10 results)

This gives me ~125 videos to analyze for comprehensive coverage mapping.

## Step 3: Categorize Existing Content

I'll analyze all found videos to map:

### Topic Coverage
- Main concepts covered extensively
- Subtopics with high saturation
- Difficulty levels addressed
- Target audiences served

### Content Formats
- Tutorial styles (step-by-step, overview, deep-dive)
- Video lengths and formats
- Series vs standalone content
- Live streams vs edited content

### Creator Landscape
- Dominant channels in the space
- Channel sizes and authority levels
- Geographic/language coverage
- Community sizes

## Step 4: Identify Potential Gaps

I'll search for gaps by looking for:

### Underserved Combinations
- Beginner content for advanced topics
- Advanced content for seemingly simple topics
- Cross-discipline combinations
- Specific use-case applications

### Format Opportunities
- Missing content lengths (e.g., 2-minute explanations)
- Underused formats (e.g., case studies, live coding)
- Interactive content possibilities
- Visual explanation opportunities

### Audience Gaps
- Underserved skill levels
- Missing prerequisites content
- Language/region opportunities
- Industry-specific applications

## Step 5: Validate Gap Opportunities

For each identified gap, I'll:
- Search specifically for that gap to confirm it's truly underserved
- Estimate search volume potential
- Assess competition difficulty
- Evaluate audience need signals (comments asking for this content)

## Step 6: Deep Analysis of Top Gaps

For the top 5 most promising content gaps, I'll:
- Use mcp__youtube-toolkit__youtube_get_video_transcript on related videos
- Pass video_id and appropriate extract_mode to understand what's missing
- Analyze comments for unaddressed questions
- Identify pain points not being solved
- Find connection opportunities between topics

## Step 7: Generate Content Gap Report

!mkdir -p youtube-analysis/opportunities

I'll create a comprehensive gap analysis report with:

### Executive Summary
- Top 10 content opportunities ranked by potential
- Quick win opportunities (low competition, high demand)
- Long-term content series opportunities
- Niche domination strategies

### Detailed Gap Analysis
For each opportunity:
- Gap description and evidence
- Estimated search volume
- Competition analysis
- Content angle recommendations
- Title and keyword suggestions

### Content Strategy Matrix
- Effort vs Impact matrix
- Content calendar for gap-filling
- Series development opportunities
- Collaboration possibilities

### Implementation Roadmap
- Priority order for content creation
- Resource requirements
- Success metrics to track
- Differentiation strategies

The report will be saved to: youtube-analysis/opportunities/[topic]_content_gaps_[date].md

## Step 8: Create Actionable Content Plan

I'll provide:

### Immediate Opportunities (Next 30 days)
- 5 quick-win video ideas
- Optimal titles and descriptions
- Target keywords and tags
- Expected performance benchmarks

### Medium-term Strategy (30-90 days)
- Content series outline
- Progressive difficulty content ladder
- Cross-promotion opportunities
- Community building tactics

### Long-term Positioning (90+ days)
- Niche authority building plan
- Advanced content roadmap
- Platform expansion opportunities
- Monetization strategies

## Error Handling

If search quota is limited:
- I'll prioritize strategic searches
- I'll use sampling techniques
- I'll focus on highest-impact gaps

If no API key available:
- I'll provide manual research methodology
- I'll suggest tools for gap identification
- I'll create templates for tracking