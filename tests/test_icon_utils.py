from unittest.mock import patch

from eww_notifier.utils import icon_utils


def test_get_theme_icon_found(monkeypatch):
    with patch('pathlib.Path.is_dir', return_value=True), \
         patch('pathlib.Path.is_file', return_value=True):
        result = icon_utils.get_theme_icon('testicon')
        assert isinstance(result, str)

def test_get_theme_icon_not_found():
    result = icon_utils.get_theme_icon('nonexistenticon')
    assert result is None

def test_find_icon_path_absolute(tmp_path):
    icon_file = tmp_path / 'icon.svg'
    icon_file.write_text('data')
    result = icon_utils.find_icon_path(str(icon_file))
    assert result == str(icon_file)

def test_find_icon_path_default(monkeypatch):
    # Simulate all lookups failing, should return DEFAULT_ICON
    monkeypatch.setattr(icon_utils, 'get_theme_icon', lambda x: None)
    monkeypatch.setattr(icon_utils, 'get_desktop_icon', lambda x, y=False: None)
    with patch('os.path.exists', return_value=False):
        result = icon_utils.find_icon_path('nonexistenticon')
        assert result.endswith('.svg') 