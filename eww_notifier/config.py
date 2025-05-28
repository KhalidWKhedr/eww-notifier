"""
Configuration module for the notification system.
Contains all constants and configuration settings.
"""

import os
from pathlib import Path

# Base directories
HOME = Path(os.path.expanduser("~"))
CACHE_DIR = Path(os.getenv("EWW_CACHE_DIR", str(HOME / ".cache" / "eww")))
SPOTIFY_CACHE_DIR = CACHE_DIR / "spotify"
SPOTIFY_ALBUM_ART_DIR = SPOTIFY_CACHE_DIR / "album_art"

# Notification cache file
NOTIFICATION_CACHE_FILE = CACHE_DIR / "eww_notifications.json"

# Log file
LOG_FILE = CACHE_DIR / "eww_notifier.log"

# Maximum number of notifications to store
MAX_NOTIFICATIONS = int(os.getenv("EWW_MAX_NOTIFICATIONS", "50"))

# Notification urgency levels
URGENCY_LEVELS = {
    0: "low",
    1: "normal",
    2: "critical"
}

# Default notification timeout (in milliseconds)
DEFAULT_TIMEOUT = int(os.getenv("EWW_DEFAULT_TIMEOUT", "5000"))

# Spotify cache settings
SPOTIFY_CACHE_MAX_SIZE = int(os.getenv("EWW_SPOTIFY_CACHE_MAX_SIZE", str(100 * 1024 * 1024)))  # 100MB
SPOTIFY_CACHE_MAX_AGE = int(os.getenv("EWW_SPOTIFY_CACHE_MAX_AGE", str(7 * 24 * 60 * 60)))  # 7 days

# Notification settings
UPDATE_COOLDOWN = float(os.getenv("EWW_UPDATE_COOLDOWN", "0.1"))  # Minimum time between Eww widget updates in seconds

# Log level
LOG_LEVEL = os.getenv("EWW_LOG_LEVEL", "INFO").upper()

def create_directories():
    """Create necessary directories with proper error handling."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        SPOTIFY_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        SPOTIFY_ALBUM_ART_DIR.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        raise RuntimeError(f"Failed to create cache directories: {e}")

# Create the necessary directories
create_directories() 