"""
Utility functions for the notification system.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from gi.repository import Gio
from eww_notifier.icon_config import ICON_DIRS, ICON_SIZES, ICON_EXTENSIONS, APP_ICONS

logger = logging.getLogger(__name__)

def get_theme_icon(icon_name: str) -> Optional[str]:
    """Get icon path using Gio's theme icon lookup."""
    try:
        theme = Gio.IconTheme.get_default()
        icon = theme.lookup_icon(icon_name, 48, 0)
        if icon:
            return icon.get_filename()
    except Exception as e:
        logger.debug(f"Failed to get theme icon for {icon_name}: {e}")
    return None

def get_desktop_icon(app_id: str) -> Optional[str]:
    """Get icon from desktop file."""
    try:
        desktop_paths = [
            Path.home() / ".local/share/applications",
            Path("/usr/share/applications"),
            Path("/usr/local/share/applications")
        ]
        
        for path in desktop_paths:
            desktop_file = path / f"{app_id}.desktop"
            if desktop_file.exists():
                with open(desktop_file, 'r') as f:
                    for line in f:
                        if line.startswith('Icon='):
                            icon_name = line.strip().split('=')[1]
                            return find_icon_path(icon_name, True)
    except Exception as e:
        logger.debug(f"Failed to get desktop icon for {app_id}: {e}")
    return None

def find_icon_path(icon_name: str, is_recursive: bool = False) -> str:
    """Find the actual path of an icon given its name."""
    try:
        # If it's already a full path, return it
        if os.path.isabs(icon_name) and os.path.exists(icon_name):
            return icon_name

        # Try theme icon lookup first
        theme_icon = get_theme_icon(icon_name)
        if theme_icon:
            return theme_icon

        # Try desktop file lookup for application icons
        if '.' in icon_name:  # Likely an application ID
            desktop_icon = get_desktop_icon(icon_name)
            if desktop_icon:
                return desktop_icon

        # Try to find the icon in the search paths
        for icon_dir in ICON_DIRS:
            if not os.path.exists(icon_dir):
                continue

            # First try exact match
            for ext in ICON_EXTENSIONS:
                file_name = icon_name + ext
                if os.path.exists(os.path.join(icon_dir, file_name)):
                    return os.path.join(icon_dir, file_name)

            # Then try with sizes
            for size in ICON_SIZES:
                for ext in ICON_EXTENSIONS:
                    # Try in apps directory
                    path = os.path.join(icon_dir, size, "apps", f"{icon_name}{ext}")
                    if os.path.exists(path):
                        return path
                    
                    # Try in status directory
                    path = os.path.join(icon_dir, size, "status", f"{icon_name}{ext}")
                    if os.path.exists(path):
                        return path
                    
                    # Try in mimetypes directory
                    path = os.path.join(icon_dir, size, "mimetypes", f"{icon_name}{ext}")
                    if os.path.exists(path):
                        return path
                    
                    # Try directly in size directory
                    path = os.path.join(icon_dir, size, f"{icon_name}{ext}")
                    if os.path.exists(path):
                        return path
                    
                    # Try without size directory
                    path = os.path.join(icon_dir, f"{icon_name}{ext}")
                    if os.path.exists(path):
                        return path

            # Finally, search recursively
            for root, _, files in os.walk(icon_dir):
                for ext in ICON_EXTENSIONS:
                    file_name = icon_name + ext
                    if file_name in files:
                        return os.path.join(root, file_name)

        # If not found and not already in a recursive call, try the default icon
        if not is_recursive and icon_name != APP_ICONS['default']:
            logger.warning(f"Icon not found: {icon_name}, using default")
            return find_icon_path(APP_ICONS['default'], True)
        
        # If we're already looking for the default icon and can't find it,
        # return a hardcoded fallback path
        return "/usr/share/icons/hicolor/scalable/apps/dialog-information.svg"

    except Exception as e:
        logger.error(f"Error finding icon path for {icon_name}: {e}")
        return "/usr/share/icons/hicolor/scalable/apps/dialog-information.svg" 