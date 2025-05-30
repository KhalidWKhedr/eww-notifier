"""
File system utility functions.
"""

from pathlib import Path


def get_file_size_mb(path: Path) -> float:
    """Get file size in megabytes.
    
    Args:
        path: Path to the file
        
    Returns:
        float: File size in megabytes
    """
    return path.stat().st_size / (1024 * 1024)

def create_directories():
    """Create necessary directories with proper error handling."""
    from eww_notifier.config import SPOTIFY_CACHE_DIR, SPOTIFY_ALBUM_ART_DIR
    try:
        SPOTIFY_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        SPOTIFY_ALBUM_ART_DIR.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        raise RuntimeError(f"Failed to create cache directories: {e}") 