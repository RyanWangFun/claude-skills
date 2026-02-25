#!/usr/bin/env python3
"""
Article Translation Orchestrator

Composes independent Unix-style tools into a complete translation workflow.
Following Unix philosophy: Compose small tools into powerful workflows.

Workflow: detect → fetch → translate → format → save

This script orchestrates the following independent tools:
  - fetcher.py: Fetch content from URL or file
  - translator.py: Translate using Gemini CLI
  - formatter.py: Format and extract metadata
  - file_mgr.py: Save to appropriate location

Usage:
    # Translate URL (expects pre-fetched content via stdin)
    echo '<content>' | python3 translate_article.py --url "https://example.com/article"

    # Translate local file
    python3 translate_article.py --file "/path/to/document.md"

    # Custom save location
    python3 translate_article.py --file "./doc.md" --save-to ~/Desktop/output.md
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_pipe(commands: list) -> str:
    """
    Run commands in a Unix pipe.

    Args:
        commands: List of command lists to pipe together
                 Example: [['cat', 'file.txt'], ['grep', 'foo']]

    Returns:
        Final stdout output as string
    """
    processes = []

    for i, cmd in enumerate(commands):
        if i == 0:
            # First command
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        else:
            # Pipe from previous
            p = subprocess.Popen(
                cmd,
                stdin=processes[-1].stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            processes[-1].stdout.close()

        processes.append(p)

    # Get final output
    stdout, stderr = processes[-1].communicate()

    # Print all stderr outputs
    for p in processes:
        if p.stderr:
            err = p.stderr.read() if hasattr(p.stderr, 'read') else ''
            if err:
                print(err, file=sys.stderr, end='')

    # Check for errors
    if processes[-1].returncode != 0:
        print(f"❌ Pipeline failed with exit code {processes[-1].returncode}", file=sys.stderr)
        sys.exit(1)

    return stdout


def detect_source_type(source: str) -> tuple:
    """
    Detect source type.

    Returns:
        (source_type, validated_source) where source_type is "url" or "file"
    """
    if source.startswith("http://") or source.startswith("https://"):
        # Validate not YouTube
        if "youtube.com" in source.lower() or "youtu.be" in source.lower():
            print("❌ Error: YouTube videos are not supported", file=sys.stderr)
            sys.exit(1)
        return "url", source
    else:
        # Validate file exists
        path = Path(source)
        if not path.exists():
            print(f"❌ Error: File not found: {source}", file=sys.stderr)
            sys.exit(1)
        return "file", str(path.absolute())


def main():
    parser = argparse.ArgumentParser(
        description='Translate English articles to Simplified Chinese',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Examples:
  # URL (expects fetched content from stdin)
  echo "<content>" | translate_article.py --url "https://example.com/article"

  # Local file
  translate_article.py --file "./document.md"

  # Custom save location
  translate_article.py --file "./doc.md" --save-to ~/Desktop/output.md
'''
    )

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument('--url', type=str, help='URL to translate (expects content from stdin)')
    source_group.add_argument('--file', type=str, help='Local file path to translate')

    parser.add_argument('--save-to', type=str, help='Custom output path (optional)')
    parser.add_argument('--timeout', type=int, default=300, help='Translation timeout in seconds (default: 300)')

    args = parser.parse_args()

    # Get script directory
    script_dir = Path(__file__).parent

    # Determine source
    source = args.url if args.url else args.file
    source_type, validated_source = detect_source_type(source)

    print(f"📄 Processing: {validated_source}", file=sys.stderr)
    print(f"🔍 Source type: {source_type}", file=sys.stderr)

    # Build pipeline commands
    python = sys.executable

    # Step 1: Fetch
    if source_type == "url":
        # For URLs, expect content from stdin
        fetch_cmd = [python, str(script_dir / "fetcher.py"), "--url", validated_source]
    else:
        # For files, read directly
        fetch_cmd = [python, str(script_dir / "fetcher.py"), "--file", validated_source]

    # Step 2: Translate
    translate_cmd = [python, str(script_dir / "translator.py"), "--timeout", str(args.timeout)]

    # Step 3: Format
    format_cmd = [python, str(script_dir / "formatter.py"), "--source", validated_source]

    # Step 4: Save
    save_cmd = [python, str(script_dir / "file_mgr.py"), "--source", validated_source, "--type", source_type]
    if args.save_to:
        save_cmd.extend(["--save-to", args.save_to])

    # Execute pipeline
    print("🚀 Starting translation pipeline...", file=sys.stderr)

    try:
        # For URL: stdin → fetch → translate → format → save
        # For file: fetch → translate → format → save
        if source_type == "url":
            # Read from stdin first, then pipe through
            stdin_content = sys.stdin.read()
            if not stdin_content.strip():
                print("❌ Error: No content received from stdin for URL", file=sys.stderr)
                sys.exit(1)

            # Create fetch process with stdin
            p1 = subprocess.Popen(fetch_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            p1_out, p1_err = p1.communicate(input=stdin_content)
            if p1_err:
                print(p1_err, file=sys.stderr, end='')

            # Pipe through remaining commands
            p2 = subprocess.Popen(translate_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            p2_out, p2_err = p2.communicate(input=p1_out)
            if p2_err:
                print(p2_err, file=sys.stderr, end='')

            p3 = subprocess.Popen(format_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            p3_out, p3_err = p3.communicate(input=p2_out)
            if p3_err:
                print(p3_err, file=sys.stderr, end='')

            p4 = subprocess.Popen(save_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            final_path, p4_err = p4.communicate(input=p3_out)
            if p4_err:
                print(p4_err, file=sys.stderr, end='')

        else:
            # File: simpler pipeline
            p1 = subprocess.Popen(fetch_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            p1_out, p1_err = p1.communicate()
            if p1_err:
                print(p1_err, file=sys.stderr, end='')

            p2 = subprocess.Popen(translate_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            p2_out, p2_err = p2.communicate(input=p1_out)
            if p2_err:
                print(p2_err, file=sys.stderr, end='')

            p3 = subprocess.Popen(format_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            p3_out, p3_err = p3.communicate(input=p2_out)
            if p3_err:
                print(p3_err, file=sys.stderr, end='')

            p4 = subprocess.Popen(save_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            final_path, p4_err = p4.communicate(input=p3_out)
            if p4_err:
                print(p4_err, file=sys.stderr, end='')

        # Output final result
        print(f"\n✅ Content saved to: {final_path.strip()}")

    except Exception as e:
        print(f"❌ Pipeline error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
