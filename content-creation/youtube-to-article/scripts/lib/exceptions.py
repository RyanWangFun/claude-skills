"""
Custom exceptions for YouTube to WeChat Article Assistant
"""

class YouTubeExtractorError(Exception):
    """Base exception for YouTube extraction errors"""
    pass

class InvalidURLError(YouTubeExtractorError):
    """Raised when YouTube URL is invalid"""
    pass

class VideoNotFoundError(YouTubeExtractorError):
    """Raised when video cannot be found or is not accessible"""
    pass

class TranscriptNotAvailableError(YouTubeExtractorError):
    """Raised when video transcript/subtitles are not available"""
    pass

class NetworkTimeoutError(YouTubeExtractorError):
    """Raised when network requests timeout"""
    pass

class ConfigurationError(YouTubeExtractorError):
    """Raised when configuration is invalid or missing"""
    pass

class ProcessingError(YouTubeExtractorError):
    """Raised when processing fails unexpectedly"""
    pass

class AIProcessorError(Exception):
    """Raised for errors related to the AI Processor"""
    pass

class WeChatPublisherError(Exception):
    """Base exception for WeChat publishing errors"""
    pass

class WeChatAuthError(WeChatPublisherError):
    """Raised when WeChat authentication fails"""
    pass

class WeChatAPIError(WeChatPublisherError):
    """Raised when WeChat API calls fail"""
    pass

class WeChatMediaUploadError(WeChatPublisherError):
    """Raised when media upload to WeChat fails"""
    pass

class WeChatContentFormatError(WeChatPublisherError):
    """Raised when content formatting for WeChat fails"""
    pass