"""
SRT subtitle processing functionality
Simple and efficient alternative to complex VTT processing
"""

import re
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class SrtSegment:
    """Represents an SRT subtitle segment"""
    index: int
    start_time: str
    end_time: str
    text: str

class SrtProcessor:
    """Handles SRT subtitle file processing - simple and efficient"""

    def __init__(self):
        # Minimal filler patterns for SRT (much simpler than VTT)
        self.filler_patterns = [
            r'\[.*?\]',  # Remove bracketed content like [Music], [Applause]
            r'\(.*?\)',  # Remove parenthetical content
            r'♪.*?♪',    # Remove music notation
            r'>>\s*',    # Remove speaker indicators
        ]

    def read_srt_file(self, srt_path: Path) -> List[SrtSegment]:
        """
        Parse SRT subtitle file into segments

        Args:
            srt_path: Path to SRT subtitle file

        Returns:
            List of SrtSegment objects
        """
        if not srt_path.exists():
            raise FileNotFoundError(f"SRT file not found: {srt_path}")

        segments = []
        content = srt_path.read_text(encoding='utf-8')

        # Split into subtitle blocks by double newlines
        blocks = content.strip().split('\n\n')

        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    # Line 1: Index number
                    index = int(lines[0])

                    # Line 2: Timestamps
                    timestamp_line = lines[1]
                    if ' --> ' in timestamp_line:
                        start_time, end_time = timestamp_line.split(' --> ')
                        start_time = start_time.strip()
                        end_time = end_time.strip()

                        # Lines 3+: Text content
                        text_lines = lines[2:]
                        text = ' '.join(text_lines).strip()

                        if text:  # Only add non-empty segments
                            segments.append(SrtSegment(
                                index=index,
                                start_time=start_time,
                                end_time=end_time,
                                text=text
                            ))

                except (ValueError, IndexError):
                    # Skip malformed blocks
                    continue

        return segments

    def clean_srt_text(self, text: str) -> str:
        """
        Clean SRT text by removing filler words and formatting artifacts

        Args:
            text: Raw SRT text

        Returns:
            Cleaned text
        """
        cleaned = text

        # Remove filler patterns
        for pattern in self.filler_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        # Clean up whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)  # Multiple spaces to single
        cleaned = re.sub(r'\n+', ' ', cleaned)  # Newlines to spaces
        cleaned = cleaned.strip()

        return cleaned

    def segments_to_clean_text(self, segments: List[SrtSegment]) -> str:
        """
        Convert SRT segments to clean continuous text
        Simple approach - SRT has minimal overlap issues

        Args:
            segments: List of SrtSegment objects

        Returns:
            Clean continuous transcript text
        """
        # Extract all text segments
        all_texts = []
        prev_text = ""

        for segment in segments:
            current_text = self.clean_srt_text(segment.text)

            if current_text and current_text != prev_text:
                # Simple duplicate removal - exact match only
                # SRT format has much less overlap than VTT
                all_texts.append(current_text)
                prev_text = current_text

        # Join with periods for natural sentence flow
        return '. '.join(all_texts) + '.' if all_texts else ""

    def process_srt_file(self, srt_path: Path, output_path: Optional[Path] = None) -> str:
        """
        Process an SRT file and return clean transcript text

        Args:
            srt_path: Path to input SRT file
            output_path: Optional path to save cleaned transcript

        Returns:
            Clean transcript text
        """
        # Read and parse SRT file
        segments = self.read_srt_file(srt_path)

        # Convert to clean text
        clean_text = self.segments_to_clean_text(segments)

        # Save to file if output path provided
        if output_path:
            output_path.write_text(clean_text, encoding='utf-8')

        return clean_text

    def get_srt_statistics(self, segments: List[SrtSegment]) -> dict:
        """
        Get statistics about the SRT subtitle file

        Args:
            segments: List of SrtSegment objects

        Returns:
            Dictionary with statistics
        """
        if not segments:
            return {
                'total_segments': 0,
                'total_duration': '00:00:00,000',
                'average_segment_length': 0,
                'total_words': 0
            }

        # Calculate basic statistics
        total_segments = len(segments)
        total_words = sum(len(segment.text.split()) for segment in segments)
        average_length = total_words / total_segments if total_segments > 0 else 0

        # Get duration from first and last segments
        first_start = segments[0].start_time if segments else '00:00:00,000'
        last_end = segments[-1].end_time if segments else '00:00:00,000'

        return {
            'total_segments': total_segments,
            'first_timestamp': first_start,
            'last_timestamp': last_end,
            'average_segment_length': round(average_length, 1),
            'total_words': total_words
        }