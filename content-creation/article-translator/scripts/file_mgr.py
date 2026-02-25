#!/usr/bin/env python3
"""
File Manager - Unix-style independent tool

Determines save path and saves content to file.
Following Unix philosophy: Do one thing and do it well.

Input: JSON from stdin with {content, title}
Output: Saved file path to stdout
Errors: To stderr

Usage:
    echo '{"content":"...","title":"..."}' | python3 file_mgr.py --source "https://example.com" --type url
    cat formatted.json | python3 file_mgr.py --source "/path/to/file.md" --type file
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime


INBOX_PATH = Path.home() / "context" / "00Inbox"


def clean_filename(name: str) -> str:
    """
    Clean string to be a valid filename.

    Args:
        name: String to clean

    Returns:
        Cleaned filename-safe string
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')

    # Limit length
    if len(name) > 50:
        name = name[:50]

    return name.rstrip('. ') or "untitled"


def determine_save_path(source: str, source_type: str, title: str = None, custom_path: str = None) -> Path:
    """
    Determine where to save the output file.

    Args:
        source: Original source path or URL
        source_type: "url" or "file"
        title: Optional title for filename
        custom_path: Optional custom output path

    Returns:
        Path object for output file
    """
    if custom_path:
        return Path(custom_path)

    # Generate filename from title
    if title:
        filename = f"{clean_filename(title)}.md"
    else:
        # Fallback filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"translated_{timestamp}.md"

    # Determine directory
    if source_type == "file":
        # Save in same directory as source file
        save_dir = Path(source).parent.absolute()
    else:
        # Save URL content to inbox
        save_dir = INBOX_PATH
        save_dir.mkdir(parents=True, exist_ok=True)

    return save_dir / filename


def save_content(content: str, output_path: Path) -> str:
    """
    Save content to file.

    Args:
        content: Content to save
        output_path: Path to save to

    Returns:
        Saved file path as string
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')
        return str(output_path)
    except Exception as e:
        print(f"❌ Error saving file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Save formatted article to file'
    )
    parser.add_argument('--source', type=str, required=True,
                       help='Original source URL or file path')
    parser.add_argument('--type', type=str, required=True, choices=['url', 'file'],
                       help='Source type: url or file')
    parser.add_argument('--save-to', type=str,
                       help='Custom output path (optional)')

    args = parser.parse_args()

    # Read JSON from stdin
    try:
        input_data = sys.stdin.read()
        data = json.loads(input_data)
        content = data['content']
        title = data.get('title')
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyError:
        print("❌ Error: Missing 'content' field in JSON", file=sys.stderr)
        sys.exit(1)

    print(f"💾 Determining save location...", file=sys.stderr)

    # Determine save path
    output_path = determine_save_path(
        args.source,
        args.type,
        title=title,
        custom_path=args.save_to
    )

    # Save file
    saved_path = save_content(content, output_path)

    print(f"✅ Saved to: {saved_path}", file=sys.stderr)

    # Output path to stdout
    print(saved_path)


if __name__ == "__main__":
    main()
