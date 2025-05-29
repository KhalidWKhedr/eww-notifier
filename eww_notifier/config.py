"""
Configuration module for the notification system.
Contains all constants and configuration settings.
"""

import os
import logging
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Base directories
HOME = Path(os.path.expanduser("~"))
TMP_DIR = Path('/tmp')
USR_SHARE = Path('/usr/share')
USR_LOCAL = Path('/usr/local/share')

# Eww widget settings
EWW_WIDGET_VAR = "notifications"  # Name of the Eww variable to update

# System paths
SYSTEM_ICON_DIRS = [
    USR_SHARE / "icons/Papirus",
    USR_SHARE / "icons/Papirus-Dark",
    USR_SHARE / "icons/Adwaita",
    USR_SHARE / "icons/Numix",
    USR_SHARE / "icons/Numix-Circle",
    USR_SHARE / "icons/Numix-Square",
    USR_SHARE / "icons/Numix-Square-Light",
    USR_SHARE / "icons/Numix-Square-Dark",
    USR_SHARE / "icons/Arc",
    USR_SHARE / "icons/Arc-Dark",
    USR_SHARE / "icons/Mint-X",
    USR_SHARE / "icons/Mint-Y",
    USR_SHARE / "icons/Mint-Y-Dark",
    USR_SHARE / "icons/Mint-Y-Aqua",
    USR_SHARE / "icons/Mint-Y-Aqua-Dark",
    USR_SHARE / "icons/Mint-Y-Blue",
    USR_SHARE / "icons/Mint-Y-Blue-Dark",
    USR_SHARE / "icons/Mint-Y-Brown",
    USR_SHARE / "icons/Mint-Y-Brown-Dark",
    USR_SHARE / "icons/Mint-Y-Grey",
    USR_SHARE / "icons/Mint-Y-Grey-Dark",
    USR_SHARE / "icons/Mint-Y-Orange",
    USR_SHARE / "icons/Mint-Y-Orange-Dark",
    USR_SHARE / "icons/Mint-Y-Pink",
    USR_SHARE / "icons/Mint-Y-Pink-Dark",
    USR_SHARE / "icons/Mint-Y-Purple",
    USR_SHARE / "icons/Mint-Y-Purple-Dark",
    USR_SHARE / "icons/Mint-Y-Red",
    USR_SHARE / "icons/Mint-Y-Red-Dark",
    USR_SHARE / "icons/Mint-Y-Sand",
    USR_SHARE / "icons/Mint-Y-Sand-Dark",
    USR_SHARE / "icons/Mint-Y-Teal",
    USR_SHARE / "icons/Mint-Y-Teal-Dark",
    USR_SHARE / "icons/Mint-Y-Yellow",
    USR_SHARE / "icons/Mint-Y-Yellow-Dark",
    USR_SHARE / "icons/hicolor",
    USR_SHARE / "pixmaps",
    USR_SHARE / "icons",
    USR_SHARE / "applications",
]

# Desktop file directories
DESKTOP_DIRS = [
    HOME / ".local/share/applications",
    USR_SHARE / "applications",
    USR_LOCAL / "applications"
]

# Default icon paths
DEFAULT_ICON = USR_SHARE / "icons/hicolor/scalable/apps/dialog-information.svg"

# Spotify paths
SPOTIFY_CACHE_DIR = TMP_DIR / "eww_spotify"
SPOTIFY_ALBUM_ART_DIR = SPOTIFY_CACHE_DIR / "album_art"

# Notification file paths
NOTIFICATION_FILE = TMP_DIR / "eww_notifications.json"
NOTIFICATION_FILE_STR = str(NOTIFICATION_FILE)  # For use in shell commands
NOTIFICATION_TEMP_FILE = TMP_DIR / "eww_notifications.tmp"
NOTIFICATION_PERMISSION_TEST = TMP_DIR / "eww_notifier_permission_test"

# Log file
LOG_FILE = TMP_DIR / "eww_notifier.log"

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
        SPOTIFY_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        SPOTIFY_ALBUM_ART_DIR.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        raise RuntimeError(f"Failed to create cache directories: {e}")

# Create the necessary directories
create_directories() 