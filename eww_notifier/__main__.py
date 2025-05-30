"""
Main entry point for the notification system.
"""

import logging
import signal
import sys

import eww_notifier.config as config
from eww_notifier.config import NOTIFICATION_PERMISSION_TEST
from eww_notifier.factories import (
    get_logger,
    get_handle_error,
    get_notification_queue,
    get_dbus_service,
)
from eww_notifier.notifier.notification_handler import NotificationHandler
from eww_notifier.notifier.notification_processor import NotificationProcessor
from eww_notifier.spotify.album_art_handler import AlbumArtHandler
from eww_notifier.spotify.spotify_handler import SpotifyHandler
from eww_notifier.utils.error_handler import handle_error, PermissionError
from eww_notifier.utils.file_utils import create_directories
from eww_notifier.utils.logging_config import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

def check_permissions():
    """Check if we have write permissions to required directories."""
    try:
        # Test write permission to /tmp
        test_file = NOTIFICATION_PERMISSION_TEST
        test_file.touch()
        test_file.unlink()
        return True
    except (PermissionError, OSError) as e:
        handle_error(e, "permission check", exit_on_error=True)
        return False

def handle_signal(signum, _frame):
    """Handle system signals for graceful shutdown."""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    sys.exit(0)

def main():
    """Main entry point for the notification system."""
    try:
        create_directories()
        # Check permissions first
        if not check_permissions():
            raise PermissionError("Failed permission check")

        # Set up signal handlers
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

        # Manual DI wiring
        logger = get_logger()
        handle_error = get_handle_error()
        notification_queue = get_notification_queue()
        album_art_handler = AlbumArtHandler()
        spotify_handler = SpotifyHandler(album_art_handler)
        processor = NotificationProcessor(logger, spotify_handler)
        # dbus_service needs notification_handler, so we create it after
        dbus_service = None  # placeholder
        handler = NotificationHandler(
            notification_queue,
            spotify_handler,
            processor,
            None,  # dbus_service, will be set after
            logger,
            config  # pass the config module itself if needed
        )
        dbus_service = get_dbus_service(handler)
        handler.dbus_service = dbus_service
        handler.start()
    except Exception as e:
        handle_error(e, "main", exit_on_error=True)

if __name__ == "__main__":
    main() 