"""
Eww Notification System - A modern notification daemon for Eww widgets.
"""

__version__ = '0.1.0'

from .notifier import NotificationHandler
from .notification_queue import NotificationQueue
from .spotify import SpotifyHandler, AlbumArtHandler

__all__ = [
    'NotificationHandler',
    'NotificationQueue',
    'SpotifyHandler',
    'AlbumArtHandler',
] 