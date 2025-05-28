"""
Icon utility functions.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from eww_notifier.icon_config import ICON_DIRS, ICON_SIZES, ICON_EXTENSIONS, APP_ICONS

logger = logging.getLogger(__name__)


def get_theme_icon(icon_name: str) -> Optional[str]:
    """Get the path to a theme icon.
    
    Args:
        icon_name: Name of the icon to find
        
    Returns:
        Optional[str]: Path to the icon if found, None otherwise
    """
    for base_dir in ICON_DIRS:
        base_path = Path(base_dir)

        for size in ICON_SIZES:
            for subdir in ["apps", "actions", "devices", "places", "status", "mimetypes", "categories"]:
                search_path = base_path / size / subdir
                if not search_path.is_dir():
                    continue

                for ext in ICON_EXTENSIONS:
                    icon_file = search_path / f"{icon_name}{ext}"
                    if icon_file.is_file():
                        return str(icon_file)

        for ext in ICON_EXTENSIONS:
            flat_icon = base_path / f"{icon_name}{ext}"
            if flat_icon.is_file():
                return str(flat_icon)

    return None


def get_desktop_icon(app_id: str) -> Optional[str]:
    """Get the icon path from a desktop file.
    
    Args:
        app_id: The application ID to find the desktop file for
        
    Returns:
        Optional[str]: Path to the icon if found, None otherwise
    """
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
                            icon_name = line.strip().split('=', 1)[1]
                            return find_icon_path(icon_name, True)
    except Exception as e:
        logger.debug(f"Failed to get desktop icon for {app_id}: {e}")
    return None


def find_icon_path(icon_name: str, is_recursive: bool = False) -> str:
    """Find the path to an icon file.
    
    Args:
        icon_name: Name of the icon to find
        is_recursive: Whether this is a recursive call (to avoid infinite recursion)
        
    Returns:
        str: Path to the icon file
    """
    try:
        if os.path.isabs(icon_name) and os.path.exists(icon_name):
            return icon_name

        theme_icon = get_theme_icon(icon_name)
        if theme_icon:
            return theme_icon

        if '.' in icon_name:
            desktop_icon = get_desktop_icon(icon_name)
            if desktop_icon:
                return desktop_icon

        for icon_dir in ICON_DIRS:
            if not os.path.exists(icon_dir):
                continue

            for ext in ICON_EXTENSIONS:
                file_path = os.path.join(icon_dir, icon_name + ext)
                if os.path.exists(file_path):
                    return str(file_path)

            for size in ICON_SIZES:
                for ext in ICON_EXTENSIONS:
                    for subdir in ["apps", "status", "mimetypes", ""]:
                        path = os.path.join(icon_dir, size, subdir, f"{icon_name}{ext}") if subdir else os.path.join(icon_dir, size, f"{icon_name}{ext}")
                        if os.path.exists(path):
                            return str(path)

                    path = os.path.join(icon_dir, f"{icon_name}{ext}")
                    if os.path.exists(path):
                        return path

            for root, _, files in os.walk(icon_dir):
                for ext in ICON_EXTENSIONS:
                    if f"{icon_name}{ext}" in files:
                        return os.path.join(root, f"{icon_name}{ext}")

        if not is_recursive and icon_name != APP_ICONS['default']:
            logger.warning(f"Icon not found: {icon_name}, using default")
            return find_icon_path(APP_ICONS['default'], True)

        return "/usr/share/icons/hicolor/scalable/apps/dialog-information.svg"

    except Exception as e:
        logger.error(f"Error finding icon path for {icon_name}: {e}")
        return "/usr/share/icons/hicolor/scalable/apps/dialog-information.svg" 