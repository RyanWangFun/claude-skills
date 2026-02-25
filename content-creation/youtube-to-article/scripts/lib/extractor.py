"""
Main orchestrator for YouTube video data extraction
"""

import json
import sys
import traceback
from pathlib import Path
from typing import Optional

from youtube_extractor import YouTubeExtractor, ExtractionResult
from utils import FilenameProcessor
from config import config
from exceptions import (
    YouTubeExtractorError,
    InvalidURLError,
    VideoNotFoundError,
    NetworkTimeoutError,
    ProcessingError
)
from markdown_generator import MarkdownGenerator

class VideoDataExtractor:
    """
    Main orchestrator class that coordinates all extraction operations
    """

    def __init__(self):
        self.youtube_extractor = YouTubeExtractor()
        self.filename_processor = FilenameProcessor()
        self.markdown_generator = MarkdownGenerator()

    def extract_all_data(self, url: str) -> ExtractionResult:
        """
        Extract all available data from a YouTube video with comprehensive error handling

        Args:
            url: YouTube video URL

        Returns:
            ExtractionResult containing all extracted data and file paths

        Raises:
            YouTubeExtractorError: If extraction fails
        """
        print(f"Starting extraction for: {url}", file=sys.stderr)

        try:
            # Step 1: Validate URL
            print("Validating URL...", file=sys.stderr)
            if not self.youtube_extractor.url_processor.validate_url(url):
                raise InvalidURLError(f"Invalid YouTube URL: {url}")

            # Step 2: Extract metadata with retry
            print("Extracting metadata...", file=sys.stderr)
            metadata = self._extract_with_retry(
                lambda: self.youtube_extractor.extract_metadata(url),
                "metadata extraction"
            )

            # Step 3: Create output directory
            safe_title = self.filename_processor.create_safe_directory_name(metadata.title)
            output_dir = config.download_dir / safe_title

            try:
                output_dir.mkdir(parents=True, exist_ok=True)
                print(f"Created output directory: {output_dir}", file=sys.stderr)
            except OSError as e:
                raise ProcessingError(f"Failed to create output directory {output_dir}: {e}")

            # Step 4: Extract chapters (non-critical)
            print("Extracting chapters...", file=sys.stderr)
            try:
                chapters = self._extract_with_retry(
                    lambda: self.youtube_extractor.extract_chapters(url),
                    "chapter extraction"
                )
                if chapters:
                    print(f"Found {len(chapters)} chapters", file=sys.stderr)
                else:
                    print("No chapters found", file=sys.stderr)
            except Exception as e:
                print(f"Warning: Chapter extraction failed: {e}", file=sys.stderr)
                chapters = []

            # Step 5: Download transcript (non-critical but important)
            print("Downloading transcript...", file=sys.stderr)
            transcript_path = None
            try:
                transcript_path = self._extract_with_retry(
                    lambda: self.youtube_extractor.download_transcript(url, output_dir),
                    "transcript download"
                )
                if transcript_path:
                    print(f"Transcript downloaded: {transcript_path}", file=sys.stderr)
                else:
                    print("No transcript available", file=sys.stderr)
            except Exception as e:
                print(f"Warning: Transcript download failed: {e}", file=sys.stderr)

            # Step 6: Download thumbnail (non-critical)
            print("Downloading thumbnail...", file=sys.stderr)
            thumbnail_path = None
            try:
                thumbnail_path = self._extract_with_retry(
                    lambda: self.youtube_extractor.download_thumbnail(url, output_dir),
                    "thumbnail download"
                )
                if thumbnail_path:
                    print(f"Thumbnail downloaded: {thumbnail_path}", file=sys.stderr)
                else:
                    print("Thumbnail download failed", file=sys.stderr)
            except Exception as e:
                print(f"Warning: Thumbnail download failed: {e}", file=sys.stderr)

            # Step 7: Markdown generation is now handled by yta-format

            # Step 8: Create extraction result
            result = ExtractionResult(
                metadata=metadata,
                chapters=chapters,
                transcript_path=transcript_path,
                thumbnail_path=thumbnail_path,
                output_directory=output_dir
            )

            # Step 9: Save extraction summary
            self._save_extraction_summary(result)

            print(f"Extraction completed successfully!", file=sys.stderr)
            print(f"Output directory: {output_dir}", file=sys.stderr)

            return result

        except YouTubeExtractorError:
            # Re-raise known errors
            raise
        except Exception as e:
            # Wrap unexpected errors
            error_msg = f"Unexpected error during extraction: {e}"
            print(f"Error: {error_msg}", file=sys.stderr)
            print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)
            raise ProcessingError(error_msg) from e

    def _extract_with_retry(self, func, operation_name: str):
        """
        Execute function with retry logic

        Args:
            func: Function to execute
            operation_name: Name of operation for error messages

        Returns:
            Result of function execution

        Raises:
            Exception after max retries exceeded
        """
        last_exception = None

        for attempt in range(config.retry_attempts + 1):
            try:
                return func()
            except Exception as e:
                last_exception = e

                if attempt < config.retry_attempts:
                    print(f"Warning: {operation_name} failed (attempt {attempt + 1}), retrying...", file=sys.stderr)
                else:
                    print(f"Error: {operation_name} failed after {config.retry_attempts + 1} attempts", file=sys.stderr)

        # If we get here, all retries failed
        if "timeout" in str(last_exception).lower():
            raise NetworkTimeoutError(f"{operation_name} timed out after {config.retry_attempts + 1} attempts")
        else:
            raise ProcessingError(f"{operation_name} failed: {last_exception}") from last_exception

    def _save_extraction_summary(self, result: ExtractionResult) -> None:
        """
        Save extraction summary to JSON file

        Args:
            result: ExtractionResult to save
        """
        summary_path = result.output_directory / 'extraction_summary.json'

        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

        print(f"Extraction summary saved: {summary_path}", file=sys.stderr)

    def get_video_info(self, url: str) -> dict:
        """
        Quick method to get basic video information without downloading files

        Args:
            url: YouTube video URL

        Returns:
            Dictionary containing basic video information
        """
        metadata = self.youtube_extractor.extract_metadata(url)
        chapters = self.youtube_extractor.extract_chapters(url)

        return {
            'title': metadata.title,
            'uploader': metadata.uploader,
            'duration': metadata.duration_string,
            'view_count': metadata.view_count,
            'chapter_count': len(chapters),
            'has_chapters': len(chapters) > 0,
            'video_id': metadata.video_id,
            'description_length': len(metadata.description),
        }
