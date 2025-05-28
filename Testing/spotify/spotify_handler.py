"""
Spotify integration module for handling Spotify notifications and album art.
"""

import os
import json
import logging
import requests
from pathlib import Path
from Testing.config import SPOTIFY_CACHE_DIR, SPOTIFY_ALBUM_ART_DIR, SPOTIFY_CACHE_MAX_SIZE, SPOTIFY_CACHE_MAX_AGE
import time
from typing import Dict, Any, Optional
from urllib.parse import urlparse, unquote
import hashlib

logger = logging.getLogger(__name__)

class SpotifyHandler:
    """Handler for Spotify-specific notification features and album art caching."""

    def __init__(self):
        """Initialize Spotify handler with cache directories and cleanup."""
        self.metadata_cache_file = SPOTIFY_CACHE_DIR / "metadata.json"
        self.album_art_dir = SPOTIFY_ALBUM_ART_DIR
        self._ensure_directories()
        self.metadata_cache = self._load_metadata_cache()
        self._cleanup_cache()

    def _ensure_directories(self):
        """Ensure cache directories exist."""
        self.metadata_cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.album_art_dir.mkdir(parents=True, exist_ok=True)

    def _load_metadata_cache(self) -> Dict[str, Dict[str, Any]]:
        """Load metadata cache from file."""
        try:
            if self.metadata_cache_file.exists():
                with open(self.metadata_cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading Spotify metadata cache: {e}")
        return {}

    def _save_metadata_cache(self) -> None:
        """Save metadata cache to file."""
        try:
            with open(self.metadata_cache_file, 'w') as f:
                json.dump(self.metadata_cache, f, indent=2)
            logger.info(f"Saved {len(self.metadata_cache)} metadata entries to cache")
        except Exception as e:
            logger.error(f"Error saving metadata cache: {e}")

    def update_metadata(self, notification_id: str, metadata: Dict[str, Any]) -> None:
        """Update metadata for a notification."""
        try:
            self.metadata_cache[notification_id] = {
                **metadata,
                'timestamp': time.time()
            }
            self._save_metadata_cache()
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")

    def get_metadata(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a notification."""
        return self.metadata_cache.get(notification_id)

    def get_album_art_path(self, notification_id: str, url: str) -> Optional[str]:
        """Get album art path for a notification, downloading if necessary."""
        try:
            # Check if we already have the album art cached
            # Use a hash of the URL as the key to handle different notifications for the same track
            url_hash = hashlib.md5(url.encode()).hexdigest()
            if url_hash in self.metadata_cache and 'album_art_path' in self.metadata_cache[url_hash]:
                 return self.metadata_cache[url_hash]['album_art_path']

            # Download and cache album art
            album_art_path = self._download_album_art(url_hash, url)
            if album_art_path:
                self.update_metadata(url_hash, {'album_art_path': album_art_path})
                return album_art_path

            return None
        except Exception as e:
            logger.error(f"Error getting album art path: {e}")
            return None

    def _download_album_art(self, file_id: str, url: str) -> Optional[str]:
        """Download album art and save to cache directory."""
        try:
            # Create cache path with the given file_id and jpg extension
            cache_path = self.album_art_dir / f"{file_id}.jpg"

            # Download image
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Save image
            with open(cache_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"Downloaded album art to {cache_path}")
            return str(cache_path)
        except Exception as e:
            logger.error(f"Error downloading album art: {e}")
            return None

    def _cleanup_cache(self) -> None:
        """Clean up old and oversized cache entries."""
        try:
            current_time = time.time()
            total_size = 0
            files_to_remove = []

            # Check each file in the album art directory
            for file_path in self.album_art_dir.glob("*"):
                if file_path.is_file():
                    # Check file age
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > SPOTIFY_CACHE_MAX_AGE:
                        files_to_remove.append(file_path)
                        continue

                    # Add to total size
                    total_size += file_path.stat().st_size

            # Remove old files
            for file_path in files_to_remove:
                try:
                    file_path.unlink()
                    logger.info(f"Removed old cache file: {file_path}")
                except Exception as e:
                    logger.error(f"Error removing old cache file {file_path}: {e}")

            # If still over size limit, remove oldest files
            if total_size > SPOTIFY_CACHE_MAX_SIZE:
                files_by_age = sorted(
                    self.album_art_dir.glob("*"),
                    key=lambda x: x.stat().st_mtime
                )
                for file_path in files_by_age:
                    if total_size <= SPOTIFY_CACHE_MAX_SIZE:
                        break
                    try:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        total_size -= file_size
                        logger.info(f"Removed oversized cache file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error removing oversized cache file {file_path}: {e}")

            # Clean up metadata cache - remove entries pointing to non-existent files
            current_metadata = {}
            for url_hash, metadata in list(self.metadata_cache.items()): # Iterate over a copy
                 if 'album_art_path' in metadata and Path(metadata['album_art_path']).exists():
                     current_metadata[url_hash] = metadata
                 else:
                     logger.info(f"Removing metadata for non-existent album art: {url_hash}")
            self.metadata_cache = current_metadata
            self._save_metadata_cache()

        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}") 