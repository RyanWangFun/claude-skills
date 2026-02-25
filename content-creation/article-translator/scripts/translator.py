#!/usr/bin/env python3
"""
Content Translator - Unix-style independent tool

Translates content using Gemini CLI.
Following Unix philosophy: Do one thing and do it well.

Input: Content from stdin
Output: Translated content to stdout
Errors: To stderr

Usage:
    cat article.md | python3 translator.py
    echo "Hello world" | python3 translator.py --target "Simplified Chinese"
"""
import sys
import subprocess
from pathlib import Path


def detect_language(content: str) -> str:
    """
    Detect if content is Chinese or English.

    Returns:
        "zh" for Chinese, "en" for English
    """
    chinese_chars = sum(1 for char in content if '\u4e00' <= char <= '\u9fff')
    total_chars = len([c for c in content if c.isalpha()])

    if total_chars == 0:
        return "en"

    chinese_ratio = chinese_chars / total_chars
    return "zh" if chinese_ratio > 0.3 else "en"


def load_prompt_template() -> str:
    """Load translation prompt template from assets."""
    skill_dir = Path(__file__).parent.parent
    template_path = skill_dir / "assets" / "translation-prompt.md"

    if not template_path.exists():
        print(f"❌ Error: Prompt template not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    return template_path.read_text(encoding='utf-8')


def build_prompt(content: str, source_lang: str, target_lang: str) -> str:
    """Build translation prompt from template."""
    template = load_prompt_template()

    # Replace template variables
    prompt = template.replace('{{Original Language}}', source_lang)
    prompt = prompt.replace('{{Target Language}}', target_lang)
    prompt = prompt.replace('{{Article Topic}}', 'Technical Article')
    prompt = prompt.replace('{{Audience Description}}', 'Technical professionals and developers')
    prompt = prompt.replace('{{Source Text}}', content)

    return prompt


def call_gemini_cli(prompt: str, timeout: int = 120) -> str:
    """
    Call Gemini CLI via subprocess.

    Args:
        prompt: Translation prompt
        timeout: Timeout in seconds

    Returns:
        Translated content
    """
    try:
        result = subprocess.run(
            ['gemini', '-p', '/dev/stdin'],
            input=prompt,
            text=True,
            capture_output=True,
            check=True,
            timeout=timeout
        )
        return result.stdout.strip()

    except FileNotFoundError:
        print("❌ Error: Gemini CLI not found", file=sys.stderr)
        print("   Install: pip install google-generativeai-cli", file=sys.stderr)
        print("   Configure: gemini config", file=sys.stderr)
        sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"❌ Gemini CLI error: {e.stderr}", file=sys.stderr)
        sys.exit(1)

    except subprocess.TimeoutExpired:
        print(f"❌ Translation timeout ({timeout}s)", file=sys.stderr)
        sys.exit(1)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Translate content using Gemini CLI')
    parser.add_argument('--target', type=str, default='Simplified Chinese',
                       help='Target language (default: Simplified Chinese)')
    parser.add_argument('--timeout', type=int, default=300,
                       help='Timeout in seconds (default: 300)')

    args = parser.parse_args()

    # Read content from stdin
    content = sys.stdin.read()
    if not content.strip():
        print("❌ Error: No content to translate", file=sys.stderr)
        sys.exit(1)

    # Detect language
    lang = detect_language(content)
    source_lang = "Simplified Chinese" if lang == "zh" else "English"
    target_lang = args.target

    print(f"🔍 Detected language: {source_lang}", file=sys.stderr)

    # Skip if same language
    if source_lang == target_lang:
        print("ℹ️  Source and target languages are the same, skipping translation", file=sys.stderr)
        print(content)
        return

    # Translate
    print(f"🌐 Translating: {source_lang} → {target_lang}...", file=sys.stderr)
    prompt = build_prompt(content, source_lang, target_lang)
    translated = call_gemini_cli(prompt, args.timeout)

    print(f"✅ Translation completed ({len(translated)} chars)", file=sys.stderr)

    # Output to stdout
    print(translated)


if __name__ == "__main__":
    main()
