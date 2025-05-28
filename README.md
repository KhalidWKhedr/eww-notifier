# eww-notifier

A custom DBus notification service for Linux desktops, designed to capture, store, and enhance notifications for use with [eww](https://elkowar.github.io/eww/) (the ElKowar Widget Wayland window system).

> **Author:** [KhalidWKhedr](https://github.com/KhalidWKhedr)  
> **Language:** Python  
> **License:** _Not specified_  
> **Repo:** [KhalidWKhedr/eww-notifier](https://github.com/KhalidWKhedr/eww-notifier)

---

## Features

- Implements `org.freedesktop.Notifications` DBus API.
- Captures all system notifications and stores them in a JSON cache.
- Automatic notification icon resolution from system themes, application `.desktop` files, or fallback search.
- Special support for Spotify: fetches and caches album art for Spotify notifications.
- Configurable number of notifications to keep.
- Efficient album art caching with size and age limits, automatic cleanup, and metadata tracking.
- Logging to both file and console for easy debugging.
- Designed to integrate out-of-the-box with eww widgets.
- Modular code organization with separate utility modules for better maintainability.
- Robust error handling and graceful shutdown support.
- Clean separation of concerns with dedicated utility modules for file operations, icon handling, and notification processing.

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
   _Dependencies include: `pydbus`, `PyGObject`, `requests`._

4. **Make the script executable (if needed)**:
   ```sh
   chmod +x eww-notifier
   ```

---

## Usage

```sh
./eww-notifier [MAX_NOTIFS]
```

- `MAX_NOTIFS` (optional): Maximum number of notifications to store (default: 5).

The service listens for notifications on DBus and writes them to `~/.cache/eww_notifications.json`. Spotify album art is cached in `~/.cache/spotify_album_arts/`.

---

## Integration with eww

You can use eww's scripting and JSON widget capabilities to read and display notifications from `~/.cache/eww_notifications.json`.

---

## Advanced Features

- **Icon Lookup:** Tries multiple methods and directories to resolve notification icons, providing nice visuals for notifications.
- **Spotify Support:** Fetches album art for Spotify via MPRIS, caches it, and manages cache size/age automatically.
- **Logging:** All events and errors are logged in `~/.cache/eww_notifier.log`.
- **Code Organization:** Modular design with separate utility modules:
  - `notification_utils.py`: Core notification processing functions
  - `file_utils.py`: File and cache management utilities
  - `icon_utils.py`: Icon resolution and management
- **Error Handling:** Comprehensive error handling with graceful shutdown support and detailed logging.
- **Signal Handling:** Proper handling of system signals (SIGINT, SIGTERM) for clean shutdown.

---

## Troubleshooting

- Ensure you have DBus and the required dependencies available.
- The script must be running to capture notifications.
- For Spotify album art, Spotify must be running and accessible over MPRIS.

---

## Contributing

Contributions, bug reports, and feature requests are welcome via [issues](https://github.com/KhalidWKhedr/eww-notifier/issues) and pull requests.

---

## License

_This project currently does not specify a license. Consider adding one!_

---

## Credits

- Inspired by the needs of eww/Wayland users.
- Uses Python, pydbus, PyGObject, and requests.

## Project Structure

```
eww-notifier/
├── eww_notifier/
│   ├── __init__.py
│   ├── __main__.py
│   ├── notifier/
│   │   ├── __init__.py
│   │   ├── notification_handler.py
│   │   └── spotify_handler.py
│   └── utils/
│       ├── __init__.py
│       ├── notification_utils.py
│       ├── file_utils.py
│       └── icon_utils.py
├── main.py
├── setup.py
├── requirements.txt
└── README.md
```
