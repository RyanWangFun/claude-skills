---
name: article-translator
description: |
  Translate English articles to Simplified Chinese markdown with automatic formatting.

  This skill should be used when users request "translate article", "翻译文章", provide an English article URL, or provide a local markdown file path for translation. It orchestrates a complete workflow: fetch → translate → format → save, producing structured Chinese markdown in the appropriate location.
---

# Article Translator

## Overview

Translate English web articles or local markdown files into high-quality Simplified Chinese markdown with automatic formatting, metadata preservation, and intelligent file naming.

## When to Use This Skill

Trigger this skill when users:
- Request "translate this article" or "翻译这篇文章"
- Provide an English article URL (e.g., `https://example.com/post`)
- Provide a local markdown file path (e.g., `./README.md` or `/path/to/doc.md`)
- Want structured Chinese markdown output (not plain text translation)

## Core Workflow

This skill provides a **single-command translation pipeline** that replicates the MCP universal_reader workflow:

```
Source → Detect → Fetch → Translate → Format → Save
```

Execute using the `translate_article.py` script, which handles the complete workflow automatically.

## Usage Patterns

### Pattern 1: Translate URL Article

When user provides a URL:

1. **Fetch content using MCP tool:**
   ```
   mcp__fetch__fetch(url="https://example.com/article")
   ```

2. **Pipe content to translation script:**
   ```bash
   echo '<fetched_content>' | python3 scripts/translate_article.py "https://example.com/article"
   ```

The script will:
- Receive markdown content from stdin
- Translate to Simplified Chinese using Gemini CLI
- Extract H1 title from translated content
- Save to `~/context/00Inbox/{中文标题}.md`

**Output:** Path to saved file

### Pattern 2: Translate Local Markdown File

When user provides a local file path:

```bash
python3 scripts/translate_article.py --file "/path/to/document.md"
```

The script will:
- Read file content directly
- Translate to Simplified Chinese
- Extract H1 title from translated content
- Save to same directory: `/path/to/{中文标题}.md`

**Output:** Path to saved file

### Pattern 3: Custom Save Location

Specify custom output path:

```bash
python3 scripts/translate_article.py <source> --save-to "/custom/path/output.md"
```

## Technical Details

### Dependencies

**Required:**
- Python 3.10+
- Gemini CLI (`pip install google-generativeai-cli`)
- Gemini API key configured (`gemini config`)

**MCP Tools Used:**
- `mcp__fetch__fetch` - For fetching URL content (converts HTML to clean markdown)

### Translation Quality

- Uses **Deverbalisation** principle (internalize meaning → regenerate in target language)
- Preserves markdown structure (headings, lists, code blocks, links)
- Maintains author's tone and style
- Handles technical terminology appropriately

### Frontmatter Handling

- **Preserves existing YAML frontmatter completely** (including English title field)
- **Does not modify frontmatter** during translation
- Extracts H1 title (`# Title`) from translated body for filename generation

### File Naming Convention

- **URL articles:** `~/context/00Inbox/{中文H1标题}.md`
- **Local files:** `{原目录}/{中文H1标题}.md`
- If no H1 title found: Falls back to `translated_{timestamp}.md`

## Error Handling

The script handles errors gracefully:
- **Missing Gemini CLI:** Exits with installation instructions
- **Translation failure:** Falls back to original content with warning
- **Unsupported content:** YouTube videos, non-markdown files → clear error message
- **Network issues:** User-friendly error reporting

## Implementation Notes

This skill uses a **single-script architecture** (`translate_article.py`) that:
- Accepts one parameter (source URL/path) + optional `--save-to`
- Executes the complete workflow internally
- Returns final file path on success

This design ensures:
- ✅ Stable input/output interface
- ✅ Reduced call overhead (one script invocation)
- ✅ Deterministic behavior
- ✅ Easy error handling

## Resources

### scripts/

This skill follows Unix philosophy with **5 independent CLI tools** composed into a workflow:

1. **fetcher.py** - Content fetching engine
   - Input: `--url <url>` (expects content from stdin) OR `--file <path>`
   - Output: Raw content to stdout
   - Purpose: Fetch from URL or read local file

2. **translator.py** - Translation engine
   - Input: Content from stdin
   - Output: Translated content to stdout
   - Purpose: Translate using Gemini CLI with Deverbalisation prompt

3. **formatter.py** - Article formatting engine
   - Input: Translated content from stdin + `--source <original>`
   - Output: JSON `{content, title}` to stdout
   - Purpose: Preserve frontmatter, extract H1 title

4. **file_mgr.py** - File management engine
   - Input: JSON from stdin + `--source <original>` + `--type url|file`
   - Output: Saved file path to stdout
   - Purpose: Determine save location and write file

5. **translate_article.py** - Main orchestrator
   - Composes the above 4 tools into complete pipeline
   - Input: `--url <url>` OR `--file <path>` + optional `--save-to <path>`
   - Output: Final file path
   - Pipeline: fetch → translate → format → save

**Each script is independently testable and reusable**, following Unix principles of small, focused tools.

### assets/

- **translation-prompt.md** - Gemini translation prompt template
  - Implements Deverbalisation principle
  - Preserves markdown structure
  - Maintains stylistic fidelity
  - Variables: `{{Original Language}}`, `{{Target Language}}`, `{{Source Text}}`

## Examples

### Example 1: Web Article Translation

```
User: 翻译这篇文章 https://simonwillison.net/2024/Oct/17/video-scraping/

Claude Process:
1. Call mcp__fetch__fetch(url="https://simonwillison.net/2024/Oct/17/video-scraping/")
   → Receives markdown content
2. Execute: echo '<content>' | python3 scripts/translate_article.py --url "https://simonwillison.net/2024/Oct/17/video-scraping/"
   → Script outputs: ✅ Content saved to: ~/context/00Inbox/视频抓取-从35秒屏幕录制中提取JSON数据.md
```

### Example 2: Local File Translation

```
User: 翻译这个文件 /Users/ryan/docs/README.md

Claude Process:
1. Execute: python3 scripts/translate_article.py --file "/Users/ryan/docs/README.md"
   → Script outputs: ✅ Content saved to: /Users/ryan/docs/快速开始指南.md
```

### Example 3: Custom Save Path

```
User: 翻译这篇文章并保存到桌面 https://example.com/post

Claude Process:
1. Fetch content via mcp__fetch__fetch
2. Execute: echo '<content>' | python3 scripts/translate_article.py --url "https://example.com/post" --save-to ~/Desktop/article.md
   → Script outputs: ✅ Content saved to: ~/Desktop/article.md
```
