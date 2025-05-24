"""
exceptions.py ─────────────────────────────────────────────────────────────
Author : ChatGPT for CBW  ✦ 2025-05-24
Summary: Custom exception classes for JamSplitter
ModLog : 2025-05-24 Initial implementation
"""

class JamSplitterError(Exception):
    """Base class for all JamSplitter exceptions"""
    def __init__(self, message: str, status_code: int = 500, **kwargs):
        """
        Initialize a JamSplitter error
        
        Args:
            message: Error message
            status_code: HTTP status code
            kwargs: Additional error metadata
        """
        super().__init__(message)
        self.status_code = status_code
        self.metadata = kwargs

class InvalidURLException(JamSplitterError):
    """Raised when an invalid YouTube URL is provided"""
    def __init__(self, url: str, message: str = "Invalid YouTube URL"):
        """
        Initialize an invalid URL error
        
        Args:
            url: The invalid URL
            message: Error message
        """
        super().__init__(message, status_code=400, url=url)

class ProcessingError(JamSplitterError):
    """Raised when video processing fails"""
    def __init__(self, message: str, status_code: int = 500, **kwargs):
        """
        Initialize a processing error
        
        Args:
            message: Error message
            status_code: HTTP status code
            kwargs: Additional error metadata
        """
        super().__init__(message, status_code, **kwargs)

class DatabaseError(JamSplitterError):
    """Raised when database operations fail"""
    def __init__(self, message: str, status_code: int = 500, **kwargs):
        """
        Initialize a database error
        
        Args:
            message: Error message
            status_code: HTTP status code
            kwargs: Additional error metadata
        """
        super().__init__(message, status_code, **kwargs)

class ConfigurationError(JamSplitterError):
    """Raised when configuration is invalid"""
    def __init__(self, message: str, status_code: int = 500, **kwargs):
        """
        Initialize a configuration error
        
        Args:
            message: Error message
            status_code: HTTP status code
            kwargs: Additional error metadata
        """
        super().__init__(message, status_code, **kwargs)
