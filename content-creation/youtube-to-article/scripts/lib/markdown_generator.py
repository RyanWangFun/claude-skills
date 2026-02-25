"""
Markdown generation with chapter integration
"""

import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from youtube_extractor import VideoMetadata, ChapterInfo
from srt_processor import SrtProcessor

class MarkdownGenerator:
    """Generates structured Markdown from video data"""
    
    def __init__(self):
        self.srt_processor = SrtProcessor()
    
    def generate_structured_markdown(
        self, 
        metadata: VideoMetadata, 
        chapters: List[ChapterInfo],
        transcript_path: Optional[Path] = None
    ) -> str:
        """
        Generate structured Markdown document with chapters and transcript
        
        Args:
            metadata: Video metadata
            chapters: List of chapter information
            transcript_path: Path to transcript file (SRT format)
            
        Returns:
            Structured Markdown content
        """
        markdown_parts = []
        
        # Title
        markdown_parts.append(f"# {metadata.title}")
        markdown_parts.append("")
        
        
        
        # Content section
        if transcript_path and transcript_path.exists():
            if chapters:
                # Generate content with chapters
                content = self._generate_chaptered_content(chapters, transcript_path)
            else:
                # Generate content without chapters
                content = self._generate_simple_content(transcript_path)
            
            markdown_parts.extend(content)
        else:
            markdown_parts.append("## Content")
            markdown_parts.append("")
            markdown_parts.append("*Transcript not available for this video.*")
            markdown_parts.append("")
        
        # Source attribution - removed
        
        return "\n".join(markdown_parts)
    
    def _generate_metadata_section(self, metadata: VideoMetadata) -> List[str]:
        """Generate metadata section"""
        lines = []
        lines.append("## Video Information")
        lines.append("")
        lines.append(f"- **Author**: {metadata.uploader}")
        lines.append(f"- **Duration**: {metadata.duration_string}")
        lines.append(f"- **Views**: {metadata.view_count:,}")
        
        if metadata.upload_date:
            # Format upload date (YYYYMMDD -> readable format)
            try:
                date_str = metadata.upload_date
                formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                lines.append(f"- **Upload Date**: {formatted_date}")
            except:
                lines.append(f"- **Upload Date**: {metadata.upload_date}")
        
        lines.append(f"- **Video URL**: {metadata.webpage_url}")
        lines.append("")
        
        # Description if available
        if metadata.description and len(metadata.description.strip()) > 0:
            lines.append("## Description")
            lines.append("")
            # Truncate very long descriptions
            description = metadata.description.strip()
            if len(description) > 500:
                description = description[:500] + "..."
            lines.append(description)
            lines.append("")
        
        return lines
    
    def _generate_chaptered_content(self, chapters: List[ChapterInfo], transcript_path: Path) -> List[str]:
        """Generate content with chapter integration"""
        lines = []
        lines.append("## Content")
        lines.append("")
        
        # Read and parse transcript
        segments = self.srt_processor.read_srt_file(transcript_path)
        
        if not segments:
            lines.append("*Could not process transcript data.*")
            return lines
        
        # Group segments by chapters
        chapter_segments = self._group_segments_by_chapters(segments, chapters)
        
        for chapter, chapter_segment_list in chapter_segments:
            # Chapter heading
            lines.append(f"### {chapter.title}")
            lines.append("")
            
            if chapter_segment_list:
                # Use the improved segment processing with deduplication
                clean_text = self.srt_processor.segments_to_clean_text(chapter_segment_list)
                
                # Split into paragraphs for better readability
                paragraphs = self._split_into_paragraphs(clean_text)
                for paragraph in paragraphs:
                    if paragraph.strip():  # Only add non-empty paragraphs
                        lines.append(paragraph)
                        lines.append("")
            else:
                lines.append("*No transcript available for this chapter.*")
                lines.append("")
        
        return lines
    
    def _generate_simple_content(self, transcript_path: Path) -> List[str]:
        """Generate content without chapters"""
        lines = []
        lines.append("## Content")
        lines.append("")
        
        # Process transcript
        clean_text = self.srt_processor.process_srt_file(transcript_path)
        
        if clean_text:
            # Split into paragraphs
            paragraphs = self._split_into_paragraphs(clean_text)
            for paragraph in paragraphs:
                if paragraph.strip():  # Only add non-empty paragraphs
                    lines.append(paragraph)
                    lines.append("")
        else:
            lines.append("*Could not process transcript data.*")
            lines.append("")
        
        return lines
    
    def _group_segments_by_chapters(
        self,
        segments,
        chapters: List[ChapterInfo]
    ) -> List[tuple]:
        """
        Group transcript segments by chapters based on timing

        Args:
            segments: List of SRT segments
            chapters: List of chapters

        Returns:
            List of (chapter, segments_list) tuples
        """
        if not chapters:
            return []

        chapter_segments = []

        for chapter in chapters:
            # Find segments that fall within this chapter's time range
            chapter_segment_list = []

            for segment in segments:
                # Convert SRT timestamp strings to seconds for comparison
                segment_start = self._srt_timestamp_to_seconds(segment.start_time)
                segment_end = self._srt_timestamp_to_seconds(segment.end_time)
                chapter_start = chapter.start_time
                chapter_end = chapter.end_time or float('inf')

                # Segment overlaps if it starts before chapter ends and ends after chapter starts
                if segment_start < chapter_end and segment_end > chapter_start:
                    chapter_segment_list.append(segment)

            chapter_segments.append((chapter, chapter_segment_list))

        return chapter_segments

    def _srt_timestamp_to_seconds(self, timestamp: str) -> float:
        """
        Convert SRT timestamp format (HH:MM:SS,mmm) to seconds

        Args:
            timestamp: SRT timestamp string like "00:01:30,500"

        Returns:
            Time in seconds as float
        """
        try:
            # Split time and milliseconds
            time_part, ms_part = timestamp.split(',')
            hours, minutes, seconds = time_part.split(':')

            total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
            total_seconds += int(ms_part) / 1000.0

            return total_seconds
        except (ValueError, IndexError):
            return 0.0

    def _split_into_paragraphs(self, text: str, target_length: int = 300) -> List[str]:
        """
        Split text into readable paragraphs
        
        Args:
            text: Input text to split
            target_length: Target length for each paragraph
            
        Returns:
            List of paragraph strings
        """
        if not text:
            return []
        
        # Split by existing line breaks first
        initial_splits = text.split('\n')
        paragraphs = []
        
        for section in initial_splits:
            section = section.strip()
            if not section:
                continue
                
            # If section is already reasonable length, use as is
            if len(section) <= target_length * 1.5:
                paragraphs.append(section)
                continue
            
            # Split long sections by sentences
            sentences = self._split_by_sentences(section)
            current_paragraph = []
            current_length = 0
            
            for sentence in sentences:
                sentence_length = len(sentence)
                
                # If adding this sentence would exceed target length, start new paragraph
                if current_length > 0 and current_length + sentence_length > target_length:
                    if current_paragraph:
                        paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = [sentence]
                    current_length = sentence_length
                else:
                    current_paragraph.append(sentence)
                    current_length += sentence_length
            
            # Add remaining content
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
        
        return [p for p in paragraphs if p.strip()]
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """Split text by sentences using simple rules"""
        # Simple sentence splitting - can be improved with more sophisticated NLP
        import re
        
        # Split on sentence endings, but preserve the ending punctuation
        sentences = re.split(r'([.!?]+\s*)', text)
        
        result = []
        for i in range(0, len(sentences) - 1, 2):
            sentence = sentences[i]
            if i + 1 < len(sentences):
                sentence += sentences[i + 1]
            sentence = sentence.strip()
            if sentence:
                result.append(sentence)
        
        return result
    
    def _generate_source_attribution(self, metadata: VideoMetadata) -> List[str]:
        """Generate source attribution section"""
        lines = []
        lines.append("---")
        lines.append("")
        lines.append("## Source")
        lines.append("")
        lines.append(
            f"*This article is based on the YouTube video \"{metadata.title}\" "
            f"by {metadata.uploader}. You can watch the original video at the "
            f"following link: {metadata.webpage_url}*"
        )
        lines.append("")
        lines.append(f"*Article generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return lines
    
    def save_markdown(self, content: str, output_path: Path) -> None:
        """Save markdown content to file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')
        print(f"Markdown saved: {output_path}", file=sys.stderr)