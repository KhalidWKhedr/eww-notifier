import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional
import requests

# Configure logging
logger = logging.getLogger(__name__)

class AlbumArtHandler:
    """Handler for managing album art downloads and caching."""

    # Constants
    ALBUM_ART_DIR = Path.home() / ".cache/eww/spotify"
    ALBUM_ART_CACHE = ALBUM_ART_DIR / "url_cache.json"
    ALBUM_ART_METADATA = ALBUM_ART_DIR / "metadata.json"

    # Cache settings
    MAX_CACHE_SIZE_MB = 100
    MAX_CACHE_AGE_DAYS = 30
    CLEANUP_INTERVAL_HOURS = 24
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0

    def __init__(self):
        """Initialize the album art handler."""
        self.album_art_cache: Dict[str, str] = {}
        self.album_art_metadata: Dict[str, Dict[str, Any]] = {}
        self.last_cleanup_time: float = 0
        self.setup_cache()

    def setup_cache(self) -> None:
        """Set up the album art cache directory and load existing cache."""
        try:
            self.ALBUM_ART_DIR.mkdir(parents=True, exist_ok=True)
            self.load_album_art_cache()
        except Exception as e:
            logger.error(f"Failed to setup cache: {e}")

    def get_file_size_mb(self, path: Path) -> float:
        """Get file size in megabytes."""
        return path.stat().st_size / (1024 * 1024)

    def get_cache_size(self) -> float:
        """Get total size of album art cache in megabytes."""
        total_size = 0
        for file in self.ALBUM_ART_DIR.glob("*.jpg"):
            total_size += self.get_file_size_mb(file)
        return total_size

    def load_album_art_cache(self) -> None:
        """Load the album art URL cache and metadata from disk."""
        try:
            if self.ALBUM_ART_CACHE.exists():
                with open(self.ALBUM_ART_CACHE, 'r') as f:
                    self.album_art_cache.update(json.load(f))
            if self.ALBUM_ART_METADATA.exists():
                with open(self.ALBUM_ART_METADATA, 'r') as f:
                    self.album_art_metadata.update(json.load(f))
        except Exception as e:
            logger.error(f"Failed to load album art cache: {e}")

    def save_album_art_cache(self) -> None:
        """Save the album art URL cache and metadata to disk."""
        try:
            with open(self.ALBUM_ART_CACHE, 'w') as f:
                json.dump(self.album_art_cache, f, indent=2)
            with open(self.ALBUM_ART_METADATA, 'w') as f:
                json.dump(self.album_art_metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save album art cache: {e}")

    def cleanup_old_files(self) -> None:
        """Remove old and unused album art files."""
        try:
            current_time = time.time()
            cutoff_time = current_time - (self.MAX_CACHE_AGE_DAYS * 24 * 60 * 60)
            
            files_to_remove = []
            for file in self.ALBUM_ART_DIR.glob("*.jpg"):
                if file.stat().st_mtime < cutoff_time:
                    files_to_remove.append(file)
            
            for file in files_to_remove:
                file.unlink()
                for url, path in list(self.album_art_cache.items()):
                    if path == str(file):
                        del self.album_art_cache[url]
                        if url in self.album_art_metadata:
                            del self.album_art_metadata[url]
            
            self.save_album_art_cache()
            logger.info(f"Cleaned up {len(files_to_remove)} old album art files")
        except Exception as e:
            logger.error(f"Failed to cleanup old files: {e}")

    def enforce_cache_size_limit(self) -> None:
        """Ensure cache size doesn't exceed the limit by removing oldest files."""
        try:
            while self.get_cache_size() > self.MAX_CACHE_SIZE_MB:
                oldest_file = min(
                    self.ALBUM_ART_DIR.glob("*.jpg"),
                    key=lambda x: x.stat().st_mtime,
                    default=None
                )
                if oldest_file:
                    for url, path in list(self.album_art_cache.items()):
                        if path == str(oldest_file):
                            del self.album_art_cache[url]
                            if url in self.album_art_metadata:
                                del self.album_art_metadata[url]
                    oldest_file.unlink()
                    logger.info(f"Removed oldest album art to maintain cache size limit: {oldest_file}")
                else:
                    break
            
            self.save_album_art_cache()
        except Exception as e:
            logger.error(f"Failed to enforce cache size limit: {e}")

    def check_cleanup(self) -> None:
        """Check if cleanup is needed and perform it if necessary."""
        current_time = time.time()
        if current_time - self.last_cleanup_time > (self.CLEANUP_INTERVAL_HOURS * 60 * 60):
            self.cleanup_old_files()
            self.enforce_cache_size_limit()
            self.last_cleanup_time = current_time

    def get_album_art_path(self, url_or_data: Any) -> Optional[str]:
        """Get the path to the album art, downloading if necessary."""
        try:
            if not url_or_data:
                return None

            # Handle bytes data
            if isinstance(url_or_data, bytes):
                try:
                    url = url_or_data.decode('utf-8').strip()
                    if url.startswith('file://'):
                        url = url[7:]
                    if os.path.exists(url):
                        return url
                except UnicodeDecodeError:
                    logger.warning("Could not decode bytes as URL")
                    return None

            # Handle URL string
            url = url_or_data
            if isinstance(url, (list, tuple)):
                url = url[0] if url else None
            elif isinstance(url, dict):
                url = url.get('url') or url.get('path')

            if not url or not isinstance(url, str):
                return None

            # Clean up the URL
            url = url.strip()
            if url.startswith('file://'):
                url = url[7:]
            url = url.strip()

            # If it's a local file, use it directly
            if os.path.exists(url):
                return url

            # Check cache
            url_hash = hashlib.md5(url.encode()).hexdigest()
            cache_path = self.ALBUM_ART_DIR / f"{url_hash}.jpg"

            if cache_path.exists():
                return str(cache_path)

            # Download and cache
            for attempt in range(self.MAX_RETRIES):
                try:
                    response = requests.get(url, stream=True, timeout=5)
                    response.raise_for_status()

                    with open(cache_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    self.album_art_cache[url] = str(cache_path)
                    self.album_art_metadata[url] = {
                        'timestamp': time.time(),
                        'size': self.get_file_size_mb(cache_path)
                    }
                    self.save_album_art_cache()
                    self.check_cleanup()

                    return str(cache_path)
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed to download album art: {e}")
                    if attempt < self.MAX_RETRIES - 1:
                        time.sleep(self.RETRY_DELAY)
                    else:
                        return None

        except Exception as e:
            logger.error(f"Error getting album art path: {e}")
            return None 