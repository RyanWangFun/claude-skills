"""
Utility functions for YouTube to WeChat Article Assistant
"""

import re

class YouTubeURLProcessor:
    """Handles YouTube URL validation and processing"""
    
    # YouTube URL patterns
    YOUTUBE_PATTERNS = [
        r'^https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'^https?://(?:www\.)?youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
        r'^https?://youtu\.be/([a-zA-Z0-9_-]{11})',
        r'^https?://(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'^https?://(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})',
    ]
    
    @classmethod
    def extract_video_id(cls, url: str) -> str:
        """
        Extract YouTube video ID from various URL formats
        
        Args:
            url: YouTube URL string
            
        Returns:
            Video ID string (11 characters)
            
        Raises:
            ValueError: If URL is invalid or video ID cannot be extracted
        """
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")
        
        # Try each pattern
        for pattern in cls.YOUTUBE_PATTERNS:
            match = re.match(pattern, url.strip())
            if match:
                return match.group(1)
        
        raise ValueError(f"Invalid YouTube URL: {url}")
    
    @classmethod
    def validate_url(cls, url: str) -> bool:
        """
        Validate if the given URL is a valid YouTube URL
        
        Args:
            url: URL string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            cls.extract_video_id(url)
            return True
        except ValueError:
            return False
    
    @classmethod
    def normalize_url(cls, url: str) -> str:
        """
        Normalize YouTube URL to standard format
        
        Args:
            url: YouTube URL in any supported format
            
        Returns:
            Normalized YouTube URL (youtube.com/watch?v=VIDEO_ID)
        """
        video_id = cls.extract_video_id(url)
        return f"https://www.youtube.com/watch?v={video_id}"

class FilenameProcessor:
    """Handles filename sanitization and processing"""
    
    # Characters not allowed in filenames (cross-platform)
    INVALID_CHARS = '<>:"/\\|?*'
    
    @classmethod
    def sanitize_filename(cls, filename: str, max_length: int = 200) -> str:
        """
        Sanitize filename by removing invalid characters and limiting length
        
        Args:
            filename: Original filename
            max_length: Maximum length for the filename
            
        Returns:
            Sanitized filename safe for filesystem use
        """
        if not filename:
            return "untitled"
        
        # Remove or replace invalid characters
        sanitized = filename
        for char in cls.INVALID_CHARS:
            sanitized = sanitized.replace(char, '')
        
        # Replace multiple spaces with single space
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Remove leading/trailing whitespace and dots
        sanitized = sanitized.strip(' .')
        
        # Limit length while preserving file extension if present
        if len(sanitized) > max_length:
            if '.' in sanitized:
                name, ext = sanitized.rsplit('.', 1)
                max_name_length = max_length - len(ext) - 1
                sanitized = name[:max_name_length] + '.' + ext
            else:
                sanitized = sanitized[:max_length]
        
        # Ensure we have a valid filename
        if not sanitized or sanitized in ['.', '..']:
            sanitized = "untitled"
        
        return sanitized
    
    @classmethod
    def create_safe_directory_name(cls, title: str) -> str:
        """
        Create a safe directory name from video title
        
        Args:
            title: Video title
            
        Returns:
            Safe directory name
        """
        # Sanitize and convert to lowercase
        safe_name = cls.sanitize_filename(title, max_length=150).lower()
        
        # Replace spaces with hyphens for directory names
        safe_name = re.sub(r'\s+', '-', safe_name)
        
        # Remove any trailing hyphens
        safe_name = safe_name.strip('-')
        
        return safe_name or "video"

def format_duration(seconds: int) -> str:
    """
    Format duration from seconds to human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "1h 23m 45s")
    """
    if seconds < 60:
        return f"{seconds}s"
    
    minutes = seconds // 60
    seconds = seconds % 60
    
    if minutes < 60:
        return f"{minutes}m {seconds}s" if seconds > 0 else f"{minutes}m"
    
    hours = minutes // 60
    minutes = minutes % 60
    
    result = f"{hours}h"
    if minutes > 0:
        result += f" {minutes}m"
    if seconds > 0:
        result += f" {seconds}s"
    
    return result