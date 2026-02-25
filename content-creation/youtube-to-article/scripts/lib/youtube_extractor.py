"""
YouTube data extraction using yt-dlp
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

from utils import YouTubeURLProcessor, FilenameProcessor, format_duration
from config import config

@dataclass
class VideoMetadata:
    """Data class for YouTube video metadata"""
    video_id: str
    title: str
    uploader: str
    uploader_id: str
    description: str
    duration: int
    duration_string: str
    upload_date: str
    view_count: int
    like_count: Optional[int]
    thumbnail_url: str
    webpage_url: str
    channel_url: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

@dataclass
class ChapterInfo:
    """Data class for video chapter information"""
    title: str
    start_time: float
    end_time: Optional[float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

@dataclass
class ExtractionResult:
    """Data class for complete extraction result"""
    metadata: VideoMetadata
    chapters: List[ChapterInfo]
    transcript_path: Optional[Path]
    thumbnail_path: Optional[Path]
    output_directory: Path
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'metadata': self.metadata.to_dict(),
            'chapters': [chapter.to_dict() for chapter in self.chapters],
            'transcript_path': str(self.transcript_path) if self.transcript_path else None,
            'thumbnail_path': str(self.thumbnail_path) if self.thumbnail_path else None,
            'output_directory': str(self.output_directory),
            'extraction_timestamp': datetime.now(timezone.utc).isoformat()
        }

class YouTubeExtractor:
    """Main class for extracting YouTube video data"""
    
    def __init__(self):
        self.url_processor = YouTubeURLProcessor()
        self.filename_processor = FilenameProcessor()

    def _get_safe_yt_dlp_command(self) -> List[str]:
        """
        Returns a base yt-dlp command with safety features to avoid rate-limiting.
        """
        command = [
            'yt-dlp',
            '--limit-rate', config.yt_dlp_limit_rate,
            '--sleep-interval', str(config.yt_dlp_sleep_interval),
            '--max-sleep-interval', str(config.yt_dlp_max_sleep_interval),
            '--user-agent', config.yt_dlp_user_agent,
        ]
        if config.yt_dlp_cookies_from_browser:
            command.extend(['--cookies-from-browser', config.yt_dlp_cookies_from_browser])
        return command

    def _convert_webp_to_jpg(self, webp_path: Path) -> Optional[Path]:
        """
        Convert webp image to jpg format

        Args:
            webp_path: Path to the webp file

        Returns:
            Path to converted jpg file, or None if conversion failed
        """
        if not PILLOW_AVAILABLE:
            print("Warning: PIL not available, cannot convert webp to jpg", file=sys.stderr)
            return webp_path

        try:
            jpg_path = webp_path.with_suffix('.jpg')

            with Image.open(webp_path) as img:
                # Convert to RGB mode (removes alpha channel if present)
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                img.save(jpg_path, 'JPEG', quality=95, optimize=True)

            # Remove original webp file
            webp_path.unlink()
            print(f"Converted webp to jpg: {jpg_path}", file=sys.stderr)
            return jpg_path

        except Exception as e:
            print(f"Warning: Failed to convert webp to jpg: {e}", file=sys.stderr)
            return webp_path

    def extract_metadata(self, url: str) -> VideoMetadata:
        """
        Extract video metadata using yt-dlp
        
        Args:
            url: YouTube video URL
            
        Returns:
            VideoMetadata object with all extracted information
            
        Raises:
            Exception: If extraction fails
        """
        video_id = self.url_processor.extract_video_id(url)
        normalized_url = self.url_processor.normalize_url(url)
        
        cmd = self._get_safe_yt_dlp_command()
        cmd.extend([
            '--dump-json',
            '--no-download',
            normalized_url
        ])
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=config.timeout_seconds,
                check=True
            )
            
            video_info = json.loads(result.stdout)
            
            metadata = VideoMetadata(
                video_id=video_id,
                title=video_info.get('title', 'Unknown Title'),
                uploader=video_info.get('uploader', 'Unknown Uploader'),
                uploader_id=video_info.get('uploader_id', ''),
                description=video_info.get('description', ''),
                duration=int(video_info.get('duration', 0)),
                duration_string=format_duration(int(video_info.get('duration', 0))),
                upload_date=video_info.get('upload_date', ''),
                view_count=int(video_info.get('view_count', 0)),
                like_count=video_info.get('like_count'),
                thumbnail_url=video_info.get('thumbnail', ''),
                webpage_url=normalized_url,
                channel_url=video_info.get('channel_url', '')
            )
            
            return metadata
            
        except subprocess.TimeoutExpired:
            raise Exception(f"Metadata extraction timed out after {config.timeout_seconds} seconds")
        except subprocess.CalledProcessError as e:
            raise Exception(f"yt-dlp failed with error: {e.stderr}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse yt-dlp output: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error during metadata extraction: {e}")
    
    def extract_chapters(self, url: str) -> List[ChapterInfo]:
        """
        Extract chapter information from video
        
        Args:
            url: YouTube video URL
            
        Returns:
            List of ChapterInfo objects
        """
        normalized_url = self.url_processor.normalize_url(url)
        
        cmd = self._get_safe_yt_dlp_command()
        cmd.extend([
            '--dump-json',
            '--no-download',
            normalized_url
        ])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config.timeout_seconds,
                check=True
            )
            
            video_info = json.loads(result.stdout)
            chapters_data = video_info.get('chapters', [])
            
            chapters = []
            for i, chapter_data in enumerate(chapters_data):
                end_time = None
                if i + 1 < len(chapters_data):
                    end_time = chapters_data[i + 1]['start_time']
                else:
                    end_time = video_info.get('duration')
                
                chapter = ChapterInfo(
                    title=chapter_data.get('title', f'Chapter {i + 1}'),
                    start_time=float(chapter_data.get('start_time', 0)),
                    end_time=float(end_time) if end_time else None
                )
                chapters.append(chapter)
            
            return chapters
            
        except subprocess.TimeoutExpired:
            raise Exception(f"Chapter extraction timed out after {config.timeout_seconds} seconds")
        except subprocess.CalledProcessError as e:
            return []
        except Exception as e:
            print(f"Warning: Failed to extract chapters: {e}", file=sys.stderr)
            return []
    
    def download_transcript(self, url: str, output_dir: Path) -> Optional[Path]:
        """
        Download video transcript/subtitles
        
        Args:
            url: YouTube video URL
            output_dir: Directory to save transcript
            
        Returns:
            Path to downloaded transcript file, or None if not available
        """
        normalized_url = self.url_processor.normalize_url(url)
        
        cmd = self._get_safe_yt_dlp_command()
        cmd.extend([
            '--write-subs',
            '--write-auto-subs',
            '--sub-langs', 'en,en-US,en-GB',
            '--sub-format', 'srt/best',
            '--skip-download',
            '--output', str(output_dir / '%(title)s.%(ext)s'),
            normalized_url
        ])
        
        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config.timeout_seconds,
                check=True
            )
            
            srt_files = list(output_dir.glob('*.srt'))
            if srt_files:
                return srt_files[0]
            
            return None
            
        except subprocess.TimeoutExpired:
            raise Exception(f"Transcript download timed out after {config.timeout_seconds} seconds")
        except subprocess.CalledProcessError:
            return None
        except Exception as e:
            print(f"Warning: Failed to download transcript: {e}", file=sys.stderr)
            return None
    
    def download_thumbnail(self, url: str, output_dir: Path) -> Optional[Path]:
        """
        Download video thumbnail
        
        Args:
            url: YouTube video URL  
            output_dir: Directory to save thumbnail
            
        Returns:
            Path to downloaded thumbnail file, or None if failed
        """
        normalized_url = self.url_processor.normalize_url(url)
        
        cmd = self._get_safe_yt_dlp_command()
        cmd.extend([
            '--write-thumbnail',
            '--skip-download',
            '--output', str(output_dir / '%(title)s.%(ext)s'),
            normalized_url
        ])
        
        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config.timeout_seconds,
                check=True
            )
            
            # First, check for jpg/jpeg files (preferred format)
            for ext in ['jpg', 'jpeg']:
                thumbnails = list(output_dir.glob(f'*.{ext}'))
                if thumbnails:
                    return thumbnails[0]

            # Check for PNG files
            png_files = list(output_dir.glob('*.png'))
            if png_files:
                return png_files[0]

            # Check for webp files and convert to jpg
            webp_files = list(output_dir.glob('*.webp'))
            if webp_files:
                webp_path = webp_files[0]
                converted_path = self._convert_webp_to_jpg(webp_path)
                return converted_path
            
            return None
            
        except subprocess.TimeoutExpired:
            raise Exception(f"Thumbnail download timed out after {config.timeout_seconds} seconds")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to download thumbnail: {e.stderr}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Warning: Unexpected error downloading thumbnail: {e}", file=sys.stderr)
            return None