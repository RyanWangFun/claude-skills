"""
Frontmatter Generator Module
为AI生成的文章添加YAML frontmatter元数据

设计原则：
- 使用标准YAML frontmatter格式（而非末尾文本）
- 符合markdown规范（Jekyll、Hugo、Obsidian等工具兼容）
- 便于程序化解析和处理
- 与article-translator格式保持一致
"""

from typing import Dict, Optional


def generate_yaml_frontmatter(
    metadata: Dict,
    chinese_title: Optional[str] = None
) -> str:
    """
    根据视频元数据生成YAML frontmatter

    Args:
        metadata: 视频元数据字典，包含title、uploader、webpage_url等字段
        chinese_title: 可选的中文标题（从文章H1提取）

    Returns:
        格式化的YAML frontmatter字符串（包含分隔符---）

    Examples:
        >>> metadata = {
        ...     'title': 'Father of RL thinks LLMs are a dead end',
        ...     'uploader': 'Richard Sutton',
        ...     'webpage_url': 'https://youtube.com/watch?v=123'
        ... }
        >>> print(generate_yaml_frontmatter(metadata))
        ---
        author: Richard Sutton
        original_title: Father of RL thinks LLMs are a dead end
        source_url: https://youtube.com/watch?v=123
        ---
        <BLANKLINE>
    """
    try:
        # 提取必要字段
        author = metadata.get('author') or metadata.get('uploader', '未知作者')
        original_title = metadata.get('title', '未知标题')
        source_url = metadata.get('webpage_url') or metadata.get('source_url', '')
        content_type = metadata.get('content_type')
        publish_date = metadata.get('publish_date')
        duration = metadata.get('duration_readable') or metadata.get('duration')
        if not duration and metadata.get('duration_seconds'):
            duration = f"{metadata['duration_seconds']} 秒"
        thumbnail_url = metadata.get('thumbnail_url')

        # 构建YAML frontmatter（追加顺序保持可读）
        frontmatter_lines = ['---']
        if chinese_title:
            frontmatter_lines.append(f"title: {chinese_title}")
        if content_type:
            frontmatter_lines.append(f"content_type: {content_type}")
        frontmatter_lines.append(f"author: {author}")
        frontmatter_lines.append(f"original_title: {original_title}")
        frontmatter_lines.append(f"source_url: {source_url}")

        if publish_date:
            frontmatter_lines.append(f"publish_date: {publish_date}")
        if duration:
            frontmatter_lines.append(f"duration: {duration}")
        if thumbnail_url:
            frontmatter_lines.append(f"thumbnail_url: {thumbnail_url}")

        frontmatter_lines.append('---')
        frontmatter_lines.append('')  # 空行分隔frontmatter和正文

        return '\n'.join(frontmatter_lines)

    except Exception as e:
        # 如果处理失败，返回基础格式
        return "---\nauthor: 未知作者\noriginal_title: 未知标题\nsource_url: \n---\n\n"


def prepend_frontmatter(
    article_content: str,
    metadata: Dict,
    chinese_title: Optional[str] = None
) -> str:
    """
    在文章内容开头添加YAML frontmatter

    Args:
        article_content: 原始文章内容（markdown格式）
        metadata: 视频元数据
        chinese_title: 可选的中文标题

    Returns:
        添加了frontmatter的完整文章内容

    Examples:
        >>> metadata = {'uploader': 'Author', 'title': 'Title', 'webpage_url': 'https://...'}
        >>> article = "# 文章标题\\n\\n正文内容..."
        >>> result = prepend_frontmatter(article, metadata)
        >>> result.startswith('---')
        True
        >>> '# 文章标题' in result
        True
    """
    frontmatter = generate_yaml_frontmatter(metadata, chinese_title)
    return frontmatter + article_content


def prepend_frontmatter_from_video_metadata(
    article_content: str,
    video_metadata,
    chinese_title: Optional[str] = None
) -> str:
    """
    从VideoMetadata对象添加frontmatter（兼容性函数）

    Args:
        article_content: 原始文章内容
        video_metadata: VideoMetadata对象
        chinese_title: 可选的中文标题

    Returns:
        添加了frontmatter的完整文章内容
    """
    # 将VideoMetadata对象转换为字典格式
    metadata_dict = {
        'title': video_metadata.title,
        'uploader': video_metadata.uploader,
        'webpage_url': video_metadata.webpage_url
    }

    return prepend_frontmatter(article_content, metadata_dict, chinese_title)


# 向后兼容：保留旧的source_attribution函数名作为别名
# 这样可以让现有代码继续工作，同时逐步迁移到新API
def generate_source_attribution(metadata: Dict) -> str:
    """
    [已废弃] 旧的末尾文本格式来源标注

    保留此函数是为了向后兼容，但推荐使用generate_yaml_frontmatter()

    Args:
        metadata: 视频元数据字典

    Returns:
        YAML frontmatter字符串（新格式）
    """
    import sys
    print("⚠️  Warning: generate_source_attribution() is deprecated. Use generate_yaml_frontmatter() instead.", file=sys.stderr)
    return generate_yaml_frontmatter(metadata)


def append_source_attribution(article_content: str, metadata: Dict) -> str:
    """
    [已废弃] 旧的末尾追加来源信息函数

    保留此函数是为了向后兼容，但推荐使用prepend_frontmatter()

    Args:
        article_content: 原始文章内容
        metadata: 视频元数据

    Returns:
        添加了frontmatter的文章（开头，而非末尾）
    """
    import sys
    print("⚠️  Warning: append_source_attribution() is deprecated. Use prepend_frontmatter() instead.", file=sys.stderr)
    return prepend_frontmatter(article_content, metadata)
