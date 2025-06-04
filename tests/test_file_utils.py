from eww_notifier.utils.file_utils import get_file_size_mb, create_directories


def test_get_file_size_mb(tmp_path):
    file = tmp_path / 'test.txt'
    file.write_text('a' * 1024 * 1024)  # 1 MB
    size = get_file_size_mb(file)
    assert 0.99 < size < 1.01


def test_create_directories(monkeypatch, tmp_path):
    # Patch config paths to use temp dirs
    monkeypatch.setattr('eww_notifier.config.SPOTIFY_CACHE_DIR', tmp_path / 'spotify_cache')
    monkeypatch.setattr('eww_notifier.config.SPOTIFY_ALBUM_ART_DIR', tmp_path / 'spotify_cache' / 'album_art')
    create_directories()
    assert (tmp_path / 'spotify_cache').exists()
    assert (tmp_path / 'spotify_cache' / 'album_art').exists()
