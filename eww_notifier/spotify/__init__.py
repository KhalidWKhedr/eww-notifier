"""
Spotify integration module for handling notifications and album art.
"""

from .album_art_handler import AlbumArtHandler
from .spotify_handler import SpotifyHandler

__all__ = ['SpotifyHandler', 'AlbumArtHandler'] 