"""
Configuration module for the notification system.
Contains all constants and configuration settings.
"""

import os
from pathlib import Path
from Testing.icon_config import ICON_DIRS, ICON_SIZES, ICON_EXTENSIONS, APP_ICONS

# Base directories
HOME = Path(os.path.expanduser("~"))
CACHE_DIR = HOME / ".cache" / "eww"
SPOTIFY_CACHE_DIR = CACHE_DIR / "spotify"
SPOTIFY_ALBUM_ART_DIR = SPOTIFY_CACHE_DIR / "album_art"

# Notification cache file
NOTIFICATION_CACHE_FILE = CACHE_DIR / "eww_notifications.json"

# Log file
LOG_FILE = CACHE_DIR / "eww_notifier.log"

# Maximum number of notifications to store
MAX_NOTIFICATIONS = 50

# Notification urgency levels
URGENCY_LEVELS = {
    0: "low",
    1: "normal",
    2: "critical"
}

# Default notification timeout (in milliseconds)
DEFAULT_TIMEOUT = 5000

# Spotify cache settings
SPOTIFY_CACHE_MAX_SIZE = 100 * 1024 * 1024  # 100MB
SPOTIFY_CACHE_MAX_AGE = 7 * 24 * 60 * 60  # 7 days

# Notification settings
UPDATE_COOLDOWN = 0.1  # Minimum time between Eww widget updates in seconds

# Create the necessary directories
CACHE_DIR.mkdir(parents=True, exist_ok=True)
SPOTIFY_CACHE_DIR.mkdir(parents=True, exist_ok=True)
SPOTIFY_ALBUM_ART_DIR.mkdir(parents=True, exist_ok=True) 