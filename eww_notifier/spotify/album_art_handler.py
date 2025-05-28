"""
Album art handler for Spotify notifications.
"""

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional
import requests
from urllib.parse import urlparse

from eww_notifier.config import (
    SPOTIFY_CACHE_DIR,
    SPOTIFY_ALBUM_ART_DIR,
    SPOTIFY_CACHE_MAX_SIZE,
    SPOTIFY_CACHE_MAX_AGE
)
from eww_notifier.utils.file_utils import get_file_size_mb

# Configure logging
logger = logging.getLogger(__name__)


class AlbumArtHandler:
    """Handles album art downloading and caching for Spotify notifications."""

    def __init__(self):
        """Initialize album art handler with cache directory."""
        self.ALBUM_ART_DIR = SPOTIFY_ALBUM_ART_DIR
        self.ALBUM_ART_CACHE = SPOTIFY_CACHE_DIR / "url_cache.json"
        
        # Cache settings from config
        self.MAX_CACHE_SIZE = SPOTIFY_CACHE_MAX_SIZE
        self.MAX_CACHE_AGE = SPOTIFY_CACHE_MAX_AGE
        
        self.album_art_cache: Dict[str, str] = {}
        
        # Set up cache
        self.setup_cache()

    def setup_cache(self) -> None:
        """Set up the album art cache directory and load existing cache."""
        try:
            self.ALBUM_ART_DIR.mkdir(parents=True, exist_ok=True)
            self.load_album_art_cache()
        except Exception as e:
            logger.error(f"Failed to setup cache: {e}")

    def get_cache_size(self) -> float:
        """Get total size of album art cache in megabytes."""
        try:
            total_size = sum(f.stat().st_size for f in self.ALBUM_ART_DIR.glob('*') if f.is_file())
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception as e:
            logger.error(f"Error getting cache size: {e}")
            return 0.0

    def load_album_art_cache(self) -> None:
        """Load the album art URL cache and metadata from disk."""
        try:
            if self.ALBUM_ART_CACHE.exists():
                with open(self.ALBUM_ART_CACHE, 'r') as f:
                    self.album_art_cache.update(json.load(f))
        except Exception as e:
            logger.error(f"Failed to load album art cache: {e}")

    def save_album_art_cache(self) -> None:
        """Save the album art URL cache and metadata to disk."""
        try:
            with open(self.ALBUM_ART_CACHE, 'w') as f:
                json.dump(self.album_art_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save album art cache: {e}")

    def get_album_art_path(self, url: str) -> Optional[str]:
        """Get the local path for an album art URL, downloading if necessary."""
        if not url:
            return None

        try:
            # Generate a hash of the URL for the filename
            url_hash = hashlib.md5(url.encode()).hexdigest()
            
            # Check if we already have this URL cached
            if url in self.album_art_cache:
                cached_path = self.album_art_cache[url]
                if os.path.exists(cached_path):
                    return cached_path
            
            # Download the image
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            # Save to cache
            file_path = self.ALBUM_ART_DIR / f"{url_hash}.jpg"
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Update cache
            self.album_art_cache[url] = str(file_path)
            self.save_album_art_cache()
            
            return str(file_path)
        except Exception as e:
            logger.error(f"Error getting album art: {e}")
            return None

    def cleanup_cache(self) -> None:
        """Clean up old and oversized cache entries."""
        try:
            current_time = time.time()
            
            # Remove old files
            for file_path in self.ALBUM_ART_DIR.glob('*'):
                if not file_path.is_file():
                    continue
                    
                file_age = current_time - file_path.stat().st_mtime
                if file_age > self.MAX_CACHE_AGE:
                    try:
                        file_path.unlink()
                        # Remove from cache
                        self.album_art_cache = {
                            url: path for url, path in self.album_art_cache.items()
                            if path != str(file_path)
                        }
                        logger.info(f"Removed old cache file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error removing old cache file {file_path}: {e}")
            
            # Check total size
            total_size = sum(f.stat().st_size for f in self.ALBUM_ART_DIR.glob('*') if f.is_file())
            if total_size > self.MAX_CACHE_SIZE:
                # Sort files by modification time (oldest first)
                files = sorted(
                    self.ALBUM_ART_DIR.glob('*'),
                    key=lambda x: x.stat().st_mtime
                )
                
                # Remove files until we're under the limit
                for file_path in files:
                    if total_size <= self.MAX_CACHE_SIZE:
                        break
                        
                    try:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        total_size -= file_size
                        # Remove from cache
                        self.album_art_cache = {
                            url: path for url, path in self.album_art_cache.items()
                            if path != str(file_path)
                        }
                        logger.info(f"Removed oversized cache file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error removing oversized cache file {file_path}: {e}")
            
            # Save updated cache
            self.save_album_art_cache()
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}") 