"""
MIT License

Copyright (c) 2024 KhalidWKhedr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Eww, Notification System - A modern notification daemon for Eww widgets.
"""

__version__ = '1.0.0'

from .notification_queue.notification_queue import NotificationQueue
from .notifier.notification_handler import NotificationHandler
from .spotify.album_art_handler import AlbumArtHandler
from .spotify.spotify_handler import SpotifyHandler

__all__ = [
    'NotificationHandler',
    'NotificationQueue',
    'SpotifyHandler',
    'AlbumArtHandler',
]
