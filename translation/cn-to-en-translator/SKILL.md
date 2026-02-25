---
name: cn-to-en-translator
description: |
  Translate Chinese markdown articles to English while preserving original writing style, formatting, and structure.

  Use when users request "翻译文章", "translate article", "中译英", or provide a Chinese markdown file path for translation. Produces English markdown in the same directory with translated title as filename.
---

# Chinese to English Article Translator

Translate Chinese markdown articles to English while faithfully preserving the original writing style, tone, and structure.

## Core Workflow

1. **Read** the source Chinese markdown file
2. **Translate** all text content to English
3. **Preserve** original writing style (narrative, technical, academic, etc.)
4. **Save** to same directory with English title as filename

## Translation Principles

### Style Fidelity

**Preserve the original article's style completely:**
- Narrative essays → maintain storytelling flow and personal voice
- Technical documentation → keep technical precision and structure
- Academic writing → preserve formal tone and argumentation
- Conversational pieces → retain casual, engaging tone

**Do NOT impose a generic translation style.** Adapt to match the source material.

### Content Handling Rules

**YAML Frontmatter:**
- Keep key names unchanged (e.g., `tags:`, `themes:`)
- Translate only the values
- Example: `tags: ["情绪解离"]` → `tags: ["emotional dissociation"]`

**Images:**
- Preserve completely: `![[image.png]]`, `![](path/to/image.jpg)`
- Do NOT translate filenames or paths

**Code Blocks:**
- Keep code unchanged
- Translate only comments and surrounding explanatory text
- Example:
  ```python
  # 计算总和
  def sum(a, b):
      return a + b
  ```
  →
  ```python
  # Calculate sum
  def sum(a, b):
      return a + b
  ```

**Terminology:**
- Use standard academic/industry English terms
- Examples:
  - "依恋理论" → "attachment theory"
  - "PARA 系统" → "PARA system"
  - "心理解离" → "dissociation"

**Chinese Scholars & Original Concepts:**
- Preserve pinyin for Chinese names
- Add clarification on first mention if needed
- Example: "武志红的'深度关系理论'" → "Wu Zhihong's 'Deep Relationship Theory'"

**Culture-Specific Expressions:**
- Use equivalent English expressions, not literal translations
- Example: "兜兜转转" → "going in circles"

**Links & References:**
- External URLs: Keep unchanged
- Internal links: Translate link text, preserve structure
- Example: `[查看详情](./guide.md)` → `[View Details](./guide.md)`

**Markdown Structure:**
- Preserve all heading levels (`#`, `##`, `###`)
- Keep list structures (`-`, `1.`, `>`)
- Maintain table formatting
- Preserve line breaks and spacing

## Quality Control

**Mandatory Requirements:**
- ❌ Do NOT skip any paragraphs
- ❌ Do NOT alter the original meaning
- ❌ Do NOT add content not in the source
- ✅ Ensure terminology consistency throughout the document

## Output Specification

**File Format:** Markdown (.md)

**Save Location:** Same directory as source file

**Filename Convention:**
1. Extract the translated H1 title (`# Title`) from translated content
2. Use translated title as filename
3. Example:
   - Source: `用Claude Code构建个人心理成长追踪系统.md`
   - Output: `Building a Personal Psychological Growth Tracking System with Claude Code.md`

## Execution Steps

When user requests translation:

1. **Read** the source file using Read tool
2. **Translate** the complete content following all rules above
3. **Extract** the H1 title from translated content for filename
4. **Write** the translated content to same directory using Write tool
5. **Confirm** completion with the output file path

## Example Usage

**Input:**
```
User: 翻译文章 /path/to/article/我的文章.md
```

**Process:**
1. Read `/path/to/article/我的文章.md`
2. Translate content (preserving style, images, code, formatting)
3. Extract English H1 title: "My Article"
4. Write `/path/to/article/My Article.md`

**Output:**
```
Translation completed: /path/to/article/My Article.md
```
