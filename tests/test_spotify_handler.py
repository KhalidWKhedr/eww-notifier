import os
import tempfile
import pytest
import time
from unittest.mock import MagicMock, patch
from eww_notifier.spotify.spotify_handler import SpotifyHandler
from eww_notifier.spotify.album_art_handler import AlbumArtHandler

def test_metadata_cache(tmp_path):
    album_art_handler = MagicMock(spec=AlbumArtHandler)
    handler = SpotifyHandler(album_art_handler)
    handler.metadata_cache_file = tmp_path / "metadata.json"
    handler.metadata_cache = {}
    handler.update_metadata('notif1', {'foo': 'bar'})
    assert 'notif1' in handler.metadata_cache
    loaded = handler._load_metadata_cache()
    assert isinstance(loaded, dict)

def test_get_album_art_path_url():
    album_art_handler = MagicMock(spec=AlbumArtHandler)
    album_art_handler.get_album_art_path.return_value = '/tmp/art.png'
    handler = SpotifyHandler(album_art_handler)
    result = handler.get_album_art_path('https://example.com/art.png')
    assert result == '/tmp/art.png'

def test_get_album_art_path_mpris(monkeypatch):
    album_art_handler = MagicMock(spec=AlbumArtHandler)
    album_art_handler.get_album_art_path.return_value = '/tmp/art.png'
    handler = SpotifyHandler(album_art_handler)
    with patch('pydbus.SessionBus') as MockBus:
        mock_spotify = MagicMock()
        mock_spotify.Metadata = {'mpris:artUrl': 'https://example.com/art.png'}
        MockBus.return_value.get.return_value = mock_spotify
        result = handler.get_album_art_path('mpris')
        assert result == '/tmp/art.png'

def test_cleanup_cache(tmp_path, monkeypatch):
    album_art_handler = MagicMock(spec=AlbumArtHandler)
    handler = SpotifyHandler(album_art_handler)
    handler.album_art_dir = tmp_path
    # Patch cache max age to 1 second
    monkeypatch.setattr('eww_notifier.spotify.spotify_handler.SPOTIFY_CACHE_MAX_AGE', 1)
    # Create a fake old file
    old_file = tmp_path / 'old.png'
    old_file.write_text('data')
    os.utime(old_file, (time.time() - 100000, time.time() - 100000))
    handler._cleanup_cache()
    # File should be removed if too old
    assert not old_file.exists() 