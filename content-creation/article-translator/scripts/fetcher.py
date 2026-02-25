#!/usr/bin/env python3
"""
Content Fetcher - Unix-style independent tool

Fetches content from URL or local file and outputs to stdout.
Following Unix philosophy: Do one thing and do it well.

Input:
  - URL: reads from stdin (expects pre-fetched markdown from mcp__fetch__fetch)
  - File path: reads directly from filesystem

Output:
  - Raw content to stdout
  - Errors to stderr

Usage:
    # For URL (expects fetched content via stdin)
    echo "<content>" | python3 fetcher.py --url "https://example.com"

    # For local file
    python3 fetcher.py --file "/path/to/document.md"
"""
import sys
import argparse
from pathlib import Path


def fetch_url_content() -> str:
    """
    Fetch URL content from stdin.

    For URLs, we expect content to be pre-fetched via mcp__fetch__fetch
    and piped to this script.
    """
    content = sys.stdin.read()
    if not content.strip():
        print("❌ Error: No content received from stdin", file=sys.stderr)
        sys.exit(1)
    return content


def fetch_file_content(file_path: str) -> str:
    """
    Fetch local file content.

    Args:
        file_path: Path to local file

    Returns:
        File content as string
    """
    path = Path(file_path)

    if not path.exists():
        print(f"❌ Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    if path.suffix.lower() not in [".md", ".markdown"]:
        print(f"❌ Error: Only markdown files supported (got {path.suffix})", file=sys.stderr)
        sys.exit(1)

    try:
        return path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ Error reading file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Fetch content from URL or file',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', type=str, help='URL to fetch (expects content from stdin)')
    group.add_argument('--file', type=str, help='Local file path to read')

    args = parser.parse_args()

    # Fetch content
    if args.url:
        print(f"📥 Fetching URL content from stdin...", file=sys.stderr)
        content = fetch_url_content()
        print(f"✅ Received {len(content)} characters", file=sys.stderr)
    else:
        print(f"📄 Reading file: {args.file}", file=sys.stderr)
        content = fetch_file_content(args.file)
        print(f"✅ Read {len(content)} characters", file=sys.stderr)

    # Output to stdout
    print(content)


if __name__ == "__main__":
    main()
