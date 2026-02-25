#!/usr/bin/env python3
"""
Article Formatter - Unix-style independent tool

Formats translated content and extracts metadata.
Following Unix philosophy: Do one thing and do it well.

Input: Translated markdown from stdin
Output: JSON with {content, title} to stdout
Errors: To stderr

The JSON output includes:
  - content: Formatted markdown (with preserved frontmatter if exists)
  - title: Extracted H1 title for filename generation (or null)

Usage:
    cat translated.md | python3 formatter.py --source "https://example.com"
"""
import sys
import json
import re
import argparse


def extract_frontmatter(content: str) -> tuple:
    """
    Extract YAML frontmatter from content.

    Returns:
        (frontmatter_block, main_content) or (None, content)
    """
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)

    if match:
        frontmatter_content = match.group(1)
        main_content = match.group(2)
        frontmatter_block = f"---\n{frontmatter_content}\n---\n"
        return frontmatter_block, main_content

    return None, content


def extract_h1_title(content: str) -> str:
    """
    Extract first H1 title from markdown.

    Returns:
        H1 title text (without # symbol), or None
    """
    lines = content.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('# ') and not stripped.startswith('## '):
            return stripped[2:].strip()
    return None


def format_article(content: str, source: str) -> str:
    """
    Format article with frontmatter preservation.

    Args:
        content: Translated content
        source: Original source URL or file path

    Returns:
        Formatted markdown (frontmatter preserved if exists)
    """
    frontmatter, main_content = extract_frontmatter(content)

    if frontmatter:
        # Has frontmatter - preserve it completely
        return frontmatter + main_content
    else:
        # No frontmatter - return as is
        return content


def main():
    parser = argparse.ArgumentParser(
        description='Format article and extract metadata'
    )
    parser.add_argument('--source', type=str, required=True,
                       help='Original source URL or file path')

    args = parser.parse_args()

    # Read content from stdin
    content = sys.stdin.read()
    if not content.strip():
        print("❌ Error: No content to format", file=sys.stderr)
        sys.exit(1)

    print(f"📝 Formatting article...", file=sys.stderr)

    # Format article
    formatted = format_article(content, args.source)

    # Extract H1 title
    title = extract_h1_title(formatted)

    if title:
        print(f"📌 Extracted H1 title: {title}", file=sys.stderr)
    else:
        print(f"⚠️  No H1 title found", file=sys.stderr)

    # Output JSON to stdout
    result = {
        "content": formatted,
        "title": title
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
