"""
Title Extractor Module
从生成的markdown文章中提取H1标题

设计原则：
- 从文章内容提取已翻译的中文H1标题（# 标题）
- 不进行翻译，只做提取和清理
- 降级优先：提取失败时返回英文原标题
- Unix哲学：做一件事并做好
"""

import re
import sys
from typing import Optional

# Import FilenameProcessor from utils
try:
    from .utils import FilenameProcessor
except ImportError:
    from utils import FilenameProcessor


def extract_h1_title(markdown_content: str) -> Optional[str]:
    """
    从markdown内容中提取第一个H1标题

    Args:
        markdown_content: markdown文章内容

    Returns:
        提取的H1标题文本（不含#号），如果未找到则返回None

    Examples:
        >>> content = "# 这是标题\\n\\n正文内容..."
        >>> extract_h1_title(content)
        "这是标题"

        >>> content = "正文\\n## 二级标题\\n# 一级标题"
        >>> extract_h1_title(content)
        "一级标题"
    """
    if not markdown_content:
        return None

    # 正则匹配第一个H1标题：行首的 # 后跟空格和标题文本
    # 使用MULTILINE模式，让^匹配每行开头
    pattern = r'^#\s+(.+?)$'
    match = re.search(pattern, markdown_content, re.MULTILINE)

    if match:
        title = match.group(1).strip()
        return title if title else None

    return None


def extract_title_from_article(
    article_content: str,
    fallback_title: str = "untitled"
) -> str:
    """
    从文章中提取H1标题，失败时使用降级标题

    这是最常用的函数，带有降级保护

    Args:
        article_content: 文章markdown内容
        fallback_title: 降级标题（通常是英文原标题）

    Returns:
        提取的中文标题或降级标题，保证非空

    Examples:
        >>> article = "# 使用Claude构建AI智能体\\n\\n正文..."
        >>> extract_title_from_article(article, "Building AI Agents")
        "使用Claude构建AI智能体"

        >>> article = "正文内容，无H1标题"
        >>> extract_title_from_article(article, "Fallback Title")
        "Fallback Title"
    """
    # 尝试提取H1标题
    extracted = extract_h1_title(article_content)

    if extracted:
        print(f"✅ Extracted title: {extracted[:50]}...", file=sys.stderr)
        return extracted
    else:
        print(f"⚠️  No H1 title found, using fallback: {fallback_title[:50]}...", file=sys.stderr)
        return fallback_title


def extract_and_sanitize_title(
    article_content: str,
    fallback_title: str = "untitled",
    max_length: int = 150
) -> str:
    """
    从文章提取H1标题并清理为安全的文件名

    这是推荐使用的高级函数，组合了提取、降级和文件名清理

    Args:
        article_content: 文章markdown内容
        fallback_title: 降级标题（英文原标题）
        max_length: 文件名最大长度

    Returns:
        清理后的安全文件名

    Examples:
        >>> article = "# 如何构建AI智能体？\\n\\n正文..."
        >>> extract_and_sanitize_title(article, "How to build AI agents")
        "如何构建AI智能体"  # 问号被移除
    """
    # 1. 提取标题（带降级）
    title = extract_title_from_article(article_content, fallback_title)

    # 2. 清理为安全文件名
    safe_filename = FilenameProcessor.sanitize_filename(title, max_length)

    print(f"📁 Safe filename: {safe_filename}", file=sys.stderr)
    return safe_filename


# 便捷函数：用于快速测试
def main():
    """命令行测试接口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract H1 title from markdown article'
    )
    parser.add_argument(
        'file',
        help='Markdown file to extract title from'
    )
    parser.add_argument(
        '--fallback',
        default='untitled',
        help='Fallback title if extraction fails'
    )

    args = parser.parse_args()

    # 读取文件
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # 提取并清理标题
    title = extract_and_sanitize_title(content, args.fallback)
    print(title)  # stdout输出结果


if __name__ == "__main__":
    main()
