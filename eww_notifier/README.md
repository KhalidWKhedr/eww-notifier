# Eww Notification System

A modern notification daemon for Eww widgets with enhanced features like Spotify integration and improved icon handling.

## Features

- **Modern Notification Handling**: Process and display system notifications with rich metadata
- **Spotify Integration**: Special handling for Spotify notifications with album art support
- **Icon Management**: Robust icon finding system using Gio theme lookup and desktop files
- **Notification Queue**: Efficient storage and retrieval of notifications
- **Configurable**: Easy to customize through configuration files

## Project Structure

```
Testing/
├── __init__.py          # Main package initialization
├── config.py           # General configuration settings
├── icon_config.py      # Icon-related configuration
├── utils.py            # Utility functions
├── main.py             # Main entry point
├── notifier/           # Notification handling
│   ├── __init__.py
│   └── notification_handler.py
├── notification_queue/ # Notification storage
│   ├── __init__.py
│   └── notification_queue.py
└── spotify/           # Spotify integration
    ├── __init__.py
    ├── spotify_handler.py
    └── album_art_handler.py
```

## Components

### Notification Handler
The core component that processes incoming notifications and manages their lifecycle.

### Spotify Integration
Special handling for Spotify notifications, including:
- Album art caching
- MPRIS metadata support
- Rich media controls

### Icon Management
Advanced icon finding system that:
- Uses Gio theme lookup
- Searches desktop files
- Supports multiple icon themes
- Handles fallbacks gracefully

### Notification Queue
Efficient storage system for notifications with:
- JSON-based persistence
- Size limits
- Automatic cleanup
- Priority handling

## Usage

```python
from Testing import NotificationHandler, NotificationQueue, SpotifyHandler

# Initialize components
queue = NotificationQueue()
spotify = SpotifyHandler()
handler = NotificationHandler(queue, spotify)

# Start handling notifications
handler.start()
```

## Configuration

Configuration is managed through several files:
- `config.py`: General settings
- `icon_config.py`: Icon-related settings

## Dependencies

- Python 3.8+
- PyGObject (for Gio support)
- pydbus (for MPRIS support)
- requests (for album art downloading)

## License

MIT License 