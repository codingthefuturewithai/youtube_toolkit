---
description: Compare teaching and content styles between multiple YouTube videos
usage: /compare-creators "video_url1" "video_url2" ["video_url3" ...]
example: /compare-creators "https://youtube.com/watch?v=abc123" "https://youtube.com/watch?v=def456"
---

I'll compare the teaching and content styles between these videos to help you understand different creator approaches.

## Step 1: Parse Video URLs

I'll extract all video URLs from "$ARGUMENTS" and validate them to ensure they're YouTube videos. I'll support comparing 2-5 videos.

## Step 2: Fetch Video Metadata

For each video, I'll fetch metadata:
- Use mcp__youtube-toolkit__youtube_get_video_metadata
- Extract video_id from each URL
- Collect:
- Video title and channel name
- Duration and publish date
- View count and engagement metrics
- Tags and category
- Channel subscriber count

## Step 3: Fetch Full Transcripts

I'll fetch full transcripts for each video:
- Use mcp__youtube-toolkit__youtube_get_video_transcript
- Pass video_id and extract_mode: "full"
- This provides complete transcripts with timestamps to analyze:
- Total word count and speaking pace
- Content structure and sections
- Technical depth and complexity
- Teaching methodology

## Step 4: Analyze Content Structure

For each video, I'll examine:

### Opening Strategy (First 60 seconds)
- Hook type (question, statement, preview)
- Problem introduction approach
- Viewer retention tactics
- Energy level and tone

### Content Organization
- Linear vs modular structure
- Use of examples and demonstrations
- Conceptual vs practical focus
- Transition strategies between topics

### Teaching Style
- Explanation depth (surface vs comprehensive)
- Pacing (rushed vs deliberate)
- Audience assumptions (beginner vs advanced)
- Use of analogies and metaphors

### Engagement Techniques
- Questions to audience
- Call-to-action frequency and type
- Interactive elements
- Storytelling vs direct instruction

## Step 5: Create Comparative Analysis

I'll create a side-by-side comparison covering:

### Style Differences
- Formal vs casual presentation
- Scripted vs improvisational
- Energy levels and personality
- Production quality approach

### Content Approach
- Depth vs breadth strategy
- Theory vs practice balance
- Example complexity
- Error handling and edge cases

### Audience Engagement
- Speaking pace (words per minute)
- Technical jargon usage
- Assumed knowledge level
- Community interaction style

### Unique Strengths
- What each creator does best
- Distinctive teaching methods
- Production innovations
- Audience connection techniques

## Step 6: Generate Comparison Report

!mkdir -p youtube-analysis/comparisons

I'll create a detailed comparison report with:
- Overview table of all videos
- Side-by-side style analysis
- Strengths and weaknesses of each approach
- Best practices identified across all videos
- Recommendations for your content style

The report will be saved to: youtube-analysis/comparisons/comparison_[date]_[video_count]videos.md

## Step 7: Provide Actionable Insights

Based on the comparison, I'll suggest:
- Elements to incorporate from each creator
- Styles that best match your goals
- Techniques to avoid based on your audience
- Hybrid approaches combining best elements
- Production techniques worth adopting

## Error Handling

If transcripts aren't available:
- I'll note which videos lack transcripts
- I'll proceed with metadata-only analysis for those videos
- I'll focus deeper analysis on videos with transcripts

If videos are very long (>30 minutes):
- I'll sample key sections (intro, 25%, 50%, 75%, outro)
- I'll note that analysis is based on sampling
- I'll identify if full analysis would be valuable