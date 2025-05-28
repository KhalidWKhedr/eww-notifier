"""
Configuration module for the notification system.
Contains all constants and configuration settings.
"""

import os
from pathlib import Path

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

# Icon search paths
ICON_DIRS = [
    "/usr/share/icons/Papirus/",
    "/usr/share/icons/hicolor/",
    "/usr/share/pixmaps/",
    "/usr/share/icons/",
    str(Path.home() / ".local/share/icons/"),
    str(Path.home() / ".icons/"),
    "/usr/share/applications/",
]

# Icon extensions and sizes
ICON_EXTENSIONS = [".svg", ".png", ".xpm"]
ICON_SIZES = ["scalable", "512", "256", "128", "96", "64", "48", "32", "24", "16"]

# Default icons for common applications
APP_ICONS = {
    'default': 'dialog-information',
    'spotify': 'spotify',
    'firefox': 'firefox',
    'chrome': 'google-chrome',
    'telegram': 'telegram',
    'discord': 'discord',
    'slack': 'slack',
    'thunderbird': 'thunderbird',
    'evolution': 'evolution',
    'notify-send': 'dialog-information',
    'system': 'system',
    'update': 'system-software-update',
    'error': 'dialog-error',
    'warning': 'dialog-warning',
    'success': 'dialog-ok',
    'info': 'dialog-information'
}

# Create the necessary directories
CACHE_DIR.mkdir(parents=True, exist_ok=True)
SPOTIFY_CACHE_DIR.mkdir(parents=True, exist_ok=True) 