# EWW Notifier

A robust notification system for EWW widgets with dependency injection, caching, and comprehensive testing.

## Features

- **Dependency Injection**: Modular architecture with clean separation of concerns
- **Caching System**: Efficient icon and metadata caching
- **Spotify Integration**: Special handling for Spotify notifications with album art
- **Error Handling**: Comprehensive error handling and logging
- **Testing**: Unit and integration tests with mock implementations

## Architecture

### Core Components

- **NotificationHandler**: Main coordinator for notification processing
- **NotificationProcessor**: Processes raw notification data
- **NotificationQueue**: Manages notification storage and retrieval
- **SpotifyHandler**: Handles Spotify-specific features
- **AlbumArtHandler**: Manages album art caching and retrieval

### Interfaces

- `IFileSystem`: File system operations
- `ICache`: Caching operations
- `ILogger`: Logging operations
- `IConfig`: Configuration management
- `INotification`: Notification object interface
- `INotificationQueue`: Queue management
- `INotificationHandler`: Notification handling
- `INotificationProcessor`: Notification processing

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/eww-notifier.git
cd eww-notifier

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the notification system
python -m eww_notifier
```

## Testing

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests/test_notification_system.py
```

## Dependencies

See `requirements.txt` for full list of dependencies.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 