# eww-notifier

A custom DBus notification service for Linux desktops, designed to capture, store, and enhance notifications for use with [eww](https://elkowar.github.io/eww/) (the ElKowar Widget Wayland window system).

> **Author:** [KhalidWKhedr](https://github.com/KhalidWKhedr)  
> **Language:** Python  
> **License:** MIT  
> **Repo:** [KhalidWKhedr/eww-notifier](https://github.com/KhalidWKhedr/eww-notifier)

---

## Features

- Implements `org.freedesktop.Notifications` DBus API
- Captures all system notifications and stores them in a JSON file
- Automatic notification icon resolution from system themes
- Special support for Spotify with album art caching
- Configurable notification limits and timeouts
- Efficient album art caching with size and age limits
- Comprehensive logging system
- Designed to integrate with eww widgets
- Modular code organization
- Robust error handling and graceful shutdown
- Type-safe code with comprehensive type hints

---

## Project Structure

```
eww-notifier/
├── eww_notifier/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Entry point
│   ├── config.py            # Configuration settings
│   ├── icon_config.py       # Icon configuration
│   ├── notifier/            # Core notification handling
│   │   ├── __init__.py
│   │   ├── dbus_service.py      # D-Bus service implementation
│   │   ├── notification_handler.py  # Main notification handler
│   │   ├── notification_processor.py # Notification processing
│   │   └── notification_utils.py    # Utility functions
│   ├── notification_queue/  # Notification storage
│   │   ├── __init__.py
│   │   └── notification_queue.py
│   ├── spotify/            # Spotify integration
│   │   ├── __init__.py
│   │   └── spotify_handler.py
│   └── utils/              # Utility modules
│       ├── __init__.py
│       └── error_handler.py
├── setup.py                # Package setup
├── requirements.txt        # Dependencies
└── README.md              # This file
```

---

## Dependencies

### Core Dependencies
- `dbus-python>=1.2.18`: D-Bus communication
- `PyGObject>=3.42.0`: GLib integration
- `pydbus>=0.6.0`: D-Bus handling

### Image Handling
- `Pillow>=9.5.0`: Image processing
- `requests>=2.31.0`: HTTP requests for album art

### Development Tools
- `mypy>=1.5.1`: Static type checking
- `black>=23.7.0`: Code formatting
- `flake8>=6.1.0`: Linting
- `pytest>=7.4.0`: Testing
- `pytest-cov>=4.1.0`: Test coverage

---

## Installation

1. **Clone the repository**:
   ```sh
   git clone https://github.com/KhalidWKhedr/eww-notifier.git
   cd eww-notifier
   ```

2. **Create a Python virtual environment** (recommended):
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Install the package** (development mode):
   ```sh
   pip install -e .
   ```

5. **Start the service**:
   ```sh
   python -m eww_notifier
   ```

---

## Configuration

The following environment variables can be used to configure the system:

- `EWW_MAX_NOTIFICATIONS`: Maximum number of notifications to store (default: 50)
- `EWW_DEFAULT_TIMEOUT`: Default notification timeout in milliseconds (default: 5000)
- `EWW_UPDATE_COOLDOWN`: Minimum time between Eww widget updates in seconds (default: 0.1)
- `EWW_LOG_LEVEL`: Logging level (default: INFO)
- `EWW_SPOTIFY_CACHE_MAX_SIZE`: Maximum size of Spotify album art cache in bytes (default: 100MB)
- `EWW_SPOTIFY_CACHE_MAX_AGE`: Maximum age of cached Spotify album art in seconds (default: 7 days)

---

## Usage

The service listens for notifications on DBus and writes them to `/tmp/eww_notifications.json`. Spotify album art is cached in `/tmp/eww_spotify/album_art/`.

### Eww Integration

You can use eww's scripting and JSON widget capabilities to read and display notifications from `/tmp/eww_notifications.json`.

Example Eww widget:
```yuck
(defwidget notifications []
  (box :orientation "v" :spacing 10
    (for n in (eww-notifier-get-notifications)
      (notification-card n))))
```

---

## Development

### Type Checking
```sh
mypy eww_notifier
```

### Code Formatting
```sh
black eww_notifier
```

### Linting
```sh
flake8 eww_notifier
```

### Testing
```sh
pytest
```

### Test Coverage
```sh
pytest --cov=eww_notifier
```

---

## Troubleshooting

### Common Issues

1. **Notifications not appearing**:
   - Check the logs: `tail -f /tmp/eww_notifier.log`
   - Verify D-Bus is running: `systemctl --user status dbus`
   - Check if the service is running: `ps aux | grep eww_notifier`

2. **Spotify album art not showing**:
   - Check if the cache directory exists: `ls -l /tmp/eww_spotify/album_art/`
   - Verify the notification file exists: `cat /tmp/eww_notifications.json`
   - Check file permissions: `ls -l /tmp/eww_notifications.json`

3. **Permission issues**:
   - Check file permissions: `ls -l /tmp/eww_notifications.json`
   - Verify user has write access to `/tmp`
   - Check if the service is running as the correct user

### Logging

All events and errors are logged in `/tmp/eww_notifier.log`. You can check the logs using:
```bash
tail -f /tmp/eww_notifier.log
```

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure to:
- Add tests for new features
- Update documentation
- Follow the existing code style
- Add type hints
- Run all tests before submitting

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Credits

- Inspired by the needs of eww/Wayland users
- Uses Python, pydbus, PyGObject, and requests
- Special thanks to the eww community
