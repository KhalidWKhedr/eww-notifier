"""
Eww, Notification System - A modern notification daemon for Eww widgets.
"""

__version__ = '1.0.0'

from .notifier.notification_handler import NotificationHandler
from .notification_queue.notification_queue import NotificationQueue
from .spotify.spotify_handler import SpotifyHandler
from .spotify.album_art_handler import AlbumArtHandler

__all__ = [
    'NotificationHandler',
    'NotificationQueue',
    'SpotifyHandler',
    'AlbumArtHandler',
] 