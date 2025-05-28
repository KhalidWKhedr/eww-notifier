"""
Utility functions package.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from eww_notifier.icon_config import ICON_DIRS, ICON_SIZES, ICON_EXTENSIONS, APP_ICONS
from eww_notifier.utils.icon_utils import get_theme_icon, get_desktop_icon, find_icon_path
from eww_notifier.utils.file_utils import get_file_size_mb

logger = logging.getLogger(__name__)

__all__ = [
    'get_theme_icon',
    'get_desktop_icon',
    'find_icon_path',
    'get_file_size_mb'
] 