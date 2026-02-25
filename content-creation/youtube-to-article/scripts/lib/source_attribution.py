"""
Source Attribution Module
为AI生成的文章添加视频来源信息的工具模块
"""

def generate_source_attribution(metadata):
    """
    根据视频元数据生成标准格式的来源信息

    Args:
        metadata: 视频元数据字典，包含title、uploader、webpage_url等字段

    Returns:
        str: 格式化的来源信息字符串
    """
    try:
        title = metadata.get('title', '未知标题')
        uploader = metadata.get('uploader', '未知作者')
        webpage_url = metadata.get('webpage_url', '')

        # 构建来源信息
        attribution_text = f"\n\n---\n\n**本文基于 {uploader} 的视频《{title}》写作，原视频链接：{webpage_url}**"

        return attribution_text

    except Exception as e:
        # 如果处理失败，返回基础格式
        return "\n\n---\n\n**本文基于YouTube视频写作**"

def append_source_attribution(article_content, metadata):
    """
    在文章内容末尾追加来源信息

    Args:
        article_content (str): 原始文章内容
        metadata: 视频元数据

    Returns:
        str: 追加了来源信息的完整文章内容
    """
    attribution = generate_source_attribution(metadata)
    return article_content + attribution

# 兼容性函数：支持VideoMetadata对象
def append_source_attribution_from_video_metadata(article_content, video_metadata):
    """
    从VideoMetadata对象追加来源信息（兼容ai_processor.py）

    Args:
        article_content (str): 原始文章内容
        video_metadata: VideoMetadata对象

    Returns:
        str: 追加了来源信息的完整文章内容
    """
    # 将VideoMetadata对象转换为字典格式
    metadata_dict = {
        'title': video_metadata.title,
        'uploader': video_metadata.uploader,
        'webpage_url': video_metadata.webpage_url
    }

    return append_source_attribution(article_content, metadata_dict)