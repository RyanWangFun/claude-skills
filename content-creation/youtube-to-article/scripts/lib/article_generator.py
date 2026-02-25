"""
Article Generator Module
使用AI将结构化内容转化为正式文章
"""

import sys
import subprocess
import re
from pathlib import Path
from typing import Dict, Optional

# Import frontmatter_generator and title_extractor (handle both package and direct execution)
try:
    from .frontmatter_generator import prepend_frontmatter
    from .title_extractor import extract_and_sanitize_title
except ImportError:
    from frontmatter_generator import prepend_frontmatter
    from title_extractor import extract_and_sanitize_title


def extract_content_section(structured_content: str) -> str:
    """
    从 structured_content.md 中提取 ## Content 部分

    Args:
        structured_content: 完整的 structured_content.md 内容

    Returns:
        只包含 Content 部分的纯文本转录
    """
    # 匹配 ## Content 之后的所有内容
    match = re.search(r'^## Content\s*\n\s*\n(.*)$', structured_content, re.MULTILINE | re.DOTALL)

    if match:
        content_text = match.group(1).strip()
        return content_text
    else:
        # 如果没找到 ## Content section，返回原内容
        print("⚠️  Warning: No ## Content section found in structured_content, using full content", file=sys.stderr)
        return structured_content


class ArticleGenerator:
    """文章生成器：使用AI将结构化内容转化为正式文章"""

    def __init__(self, prompt_template_path: str):
        """
        初始化生成器

        Args:
            prompt_template_path: prompt模板文件路径
        """
        self.prompt_template = self._load_prompt_template(prompt_template_path)

    def _load_prompt_template(self, template_path: str) -> str:
        """加载prompt模板"""
        try:
            template_file = Path(template_path)
            if not template_file.exists():
                raise FileNotFoundError(f"Prompt template not found: {template_path}")

            with open(template_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading prompt template: {e}", file=sys.stderr)
            raise

    def _fill_prompt(self, metadata: Dict, structured_content: str) -> str:
        """
        填充prompt模板

        Args:
            metadata: 视频元数据字典（包含title, uploader, description等）
            structured_content: 结构化内容文本（完整的 structured_content.md）

        Returns:
            填充后的完整prompt
        """
        prompt = self.prompt_template

        # 从 structured_content 中只提取 ## Content 部分
        content_only = extract_content_section(structured_content)

        # 替换占位符
        prompt = prompt.replace('[在此处插入视频标题]', metadata.get('title', '未知标题'))
        prompt = prompt.replace('[在此处插入作者]', metadata.get('uploader', '未知作者'))
        prompt = prompt.replace('[在此处插入视频简介]', metadata.get('description', '无简介'))
        prompt = prompt.replace('[在此处粘贴完整的文字转录稿]', content_only)

        return prompt

    def _call_gemini_cli(self, prompt: str) -> Optional[str]:
        """
        使用Gemini CLI生成文章

        Args:
            prompt: 完整的prompt

        Returns:
            生成的文章内容，失败时返回None
        """
        try:
            print("Generating article using Gemini CLI...", file=sys.stderr)
            result = subprocess.run(
                ['gemini', '-p', prompt],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=300  # 5分钟超时
            )

            if result.returncode == 0:
                print("Gemini CLI generation successful", file=sys.stderr)
                return result.stdout
            else:
                print(f"Gemini CLI failed with code {result.returncode}", file=sys.stderr)
                if result.stderr:
                    print(f"Error: {result.stderr}", file=sys.stderr)
                return None

        except subprocess.TimeoutExpired:
            print("Gemini CLI timed out after 5 minutes", file=sys.stderr)
            return None
        except FileNotFoundError:
            print("Gemini CLI not found. Install with: pip install google-generativeai", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error running Gemini CLI: {e}", file=sys.stderr)
            return None

    def _call_google_ai_api(self, prompt: str) -> str:
        """
        使用Google AI API生成文章（备用方案）

        Args:
            prompt: 完整的prompt

        Returns:
            生成的文章内容

        Raises:
            Exception: 如果API调用失败
        """
        import os
        import requests

        print("Using Google AI API fallback...", file=sys.stderr)

        api_key = os.getenv('GOOGLE_AI_API_KEY')
        if not api_key:
            raise ValueError(
                "GOOGLE_AI_API_KEY environment variable not set. "
                "Please set it or install Gemini CLI."
            )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }

        try:
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()

            result = response.json()
            article = result['candidates'][0]['content']['parts'][0]['text']

            print("Google AI API generation successful", file=sys.stderr)
            return article

        except requests.exceptions.Timeout:
            raise Exception("Google AI API request timed out after 5 minutes")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Google AI API request failed: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to parse Google AI API response: {e}")

    def generate_article(
        self,
        metadata: Dict,
        structured_content: str,
        use_cli_first: bool = True
    ) -> str:
        """
        生成文章

        Args:
            metadata: 视频元数据字典
            structured_content: 结构化内容文本
            use_cli_first: 是否优先使用CLI（默认True）

        Returns:
            生成的完整文章（包含来源标注）

        Raises:
            Exception: 如果所有生成方法都失败
        """
        # 1. 填充prompt模板
        print("Preparing prompt...", file=sys.stderr)
        prompt = self._fill_prompt(metadata, structured_content)

        # 2. 调用AI服务生成文章
        article = None

        if use_cli_first:
            # 优先尝试Gemini CLI
            article = self._call_gemini_cli(prompt)

            # 如果CLI失败，降级到API
            if article is None:
                print("Falling back to Google AI API...", file=sys.stderr)
                article = self._call_google_ai_api(prompt)
        else:
            # 直接使用API
            article = self._call_google_ai_api(prompt)

        if not article:
            raise Exception("Failed to generate article with all available methods")

        # 3. 添加YAML frontmatter（替代旧的末尾来源标注）
        print("Adding YAML frontmatter...", file=sys.stderr)
        article_with_frontmatter = prepend_frontmatter(article, metadata)

        return article_with_frontmatter

    def generate_and_save(
        self,
        metadata: Dict,
        structured_content: str,
        output_path: Path,
        use_cli_first: bool = True
    ) -> Path:
        """
        生成文章并保存到文件（使用提取的中文标题作为文件名）

        Args:
            metadata: 视频元数据字典
            structured_content: 结构化内容文本
            output_path: 输出文件路径（会被替换为{chinese_title}.md）
            use_cli_first: 是否优先使用CLI

        Returns:
            实际保存的文件路径（使用中文标题命名）
        """
        # 1. 生成文章（已包含frontmatter）
        article = self.generate_article(metadata, structured_content, use_cli_first)

        # 2. 从文章中提取H1中文标题
        print("Extracting Chinese title from article...", file=sys.stderr)
        fallback_title = metadata.get('title', 'untitled')
        chinese_title = extract_and_sanitize_title(article, fallback_title)

        # 3. 使用中文标题作为文件名（而非ai_article.md）
        output_dir = output_path.parent
        final_filename = f"{chinese_title}.md"
        final_path = output_dir / final_filename

        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        # 4. 保存文章
        print(f"Saving article to: {final_path}", file=sys.stderr)
        with open(final_path, 'w', encoding='utf-8') as f:
            f.write(article)

        print(f"✅ Article saved: {final_path.name}", file=sys.stderr)
        return final_path


def create_generator(prompt_template_name: str = 'yta-prompt3.0.md') -> ArticleGenerator:
    """
    工厂函数：创建文章生成器实例

    Args:
        prompt_template_name: prompt模板文件名

    Returns:
        ArticleGenerator实例
    """
    # 假设此文件在 scripts/lib/ 目录下
    current_file = Path(__file__)
    skills_dir = current_file.parent.parent.parent  # 回到 skills/youtube-to-article
    prompt_path = skills_dir / 'assets' / prompt_template_name

    return ArticleGenerator(str(prompt_path))
