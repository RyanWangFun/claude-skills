---
name: youtube-to-article
description: Convert YouTube videos to formal articles. Use when user provides YouTube URL, requests "视频转文章", "convert video to article", or mentions YouTube video processing.
---

# YouTube to Article

## Usage

```bash
# Default: outputs to ~/context/00Inbox/
python3 scripts/yta "https://youtube.com/watch?v=VIDEO_ID"

# Custom output directory
python3 scripts/yta "URL" --output-dir ~/Documents/

# Skip article generation (structured content only)
python3 scripts/yta "URL" --no-article
```

## Dependencies

```bash
pip install yt-dlp requests
```

**For AI article generation:**
- Gemini CLI: `pip install google-generativeai`
- OR set `GOOGLE_AI_API_KEY` environment variable

Requires Python 3.10+

## Examples

**Example 1: Convert video to article (default)**
```
User: 把这个视频转成文章 https://youtube.com/watch?v=XuvKFsktX0Q

Execute: python3 scripts/yta "https://youtube.com/watch?v=XuvKFsktX0Q"

Result: ~/context/00Inbox/{中文标题}/{中文标题}.md
```

**Example 2: Custom output directory**
```
User: Save to my project folder

Execute: python3 scripts/yta "URL" --output-dir ~/context/01Projects/my-project/

Result: ~/context/01Projects/my-project/{中文标题}/{中文标题}.md
```

**Example 3: Structured content only**
```
User: 只要字幕整理，不需要AI生成文章

Execute: python3 scripts/yta "URL" --no-article

Result: ~/context/00Inbox/{中文标题}/structured_content.md
```
