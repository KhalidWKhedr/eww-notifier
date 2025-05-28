# Eww Notifier

A notification system for [Eww](https://github.com/elkowar/eww) that provides a modern, customizable notification experience.

## Features

- **Modern Design**: Clean, modern notification design with support for icons, actions, and rich text
- **Spotify Integration**: Special handling for Spotify notifications with album art support
- **Customizable**: Easy to customize appearance and behavior through Eww widgets
- **Persistent Storage**: Notifications are stored and can be accessed even after they expire
- **D-Bus Integration**: Native integration with the system's D-Bus notification system

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/eww-notifier.git
cd eww-notifier
```

2. Install the package:
```bash
pip install -e .
```

3. Start the service:
```bash
python -m eww_notifier
```

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

### Configuration

The following environment variables can be used to configure the system:

- `EWW_MAX_NOTIFICATIONS`: Maximum number of notifications to store (default: 50)
- `EWW_DEFAULT_TIMEOUT`: Default notification timeout in milliseconds (default: 5000)
- `EWW_UPDATE_COOLDOWN`: Minimum time between Eww widget updates in seconds (default: 0.1)
- `EWW_LOG_LEVEL`: Logging level (default: INFO)
- `EWW_SPOTIFY_CACHE_MAX_SIZE`: Maximum size of Spotify album art cache in bytes (default: 100MB)
- `EWW_SPOTIFY_CACHE_MAX_AGE`: Maximum age of cached Spotify album art in seconds (default: 7 days)

## Troubleshooting

All events and errors are logged in `/tmp/eww_notifier.log`. You can check the logs using:
```bash
tail -f /tmp/eww_notifier.log
```

Common issues and solutions:

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 