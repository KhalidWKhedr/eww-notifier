"""
Error handling utilities for the notification system.
"""

import logging
import sys
from typing import Optional, Type, Callable
import time

logger = logging.getLogger(__name__)

class NotificationError(Exception):
    """Base exception for notification system errors."""
    pass

class DBusError(NotificationError):
    """Exception for DBus-related errors."""
    pass

class CacheError(NotificationError):
    """Exception for cache-related errors."""
    pass

class PermissionError(NotificationError):
    """Exception for permission-related errors."""
    pass

def handle_error(error: Exception, context: str, exit_on_error: bool = False) -> None:
    """Handle an error with proper logging and optional exit.
    
    Args:
        error: The exception to handle
        context: Description of where the error occurred
        exit_on_error: Whether to exit the program after handling the error
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    logger.error(f"Error in {context}: {error_type}: {error_msg}")
    
    if exit_on_error:
        sys.exit(1)

def retry_on_error(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """Decorator for retrying functions on error.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry on
        
    Returns:
        Decorated function that will retry on specified exceptions
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_retries} attempts failed. Last error: {str(e)}"
                        )
                        raise last_exception
            
            raise last_exception
        return wrapper
    return decorator 