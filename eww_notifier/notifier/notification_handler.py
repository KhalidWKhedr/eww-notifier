"""
Main notification handler module that processes and managing system notifications.
"""

import logging
from typing import Dict, Any, List

import dbus

from eww_notifier.notification_queue.notification_queue import NotificationQueue
from eww_notifier.spotify.spotify_handler import SpotifyHandler
from eww_notifier.notifier.dbus_service import DBusService
from eww_notifier.notifier.notification_processor import NotificationProcessor

logger = logging.getLogger(__name__)

class NotificationHandler:
    """Notification handler for processing and managing system notifications."""

    def __init__(self):
        """Initialize notification handler."""
        # Initialize components
        self.notification_queue = NotificationQueue()
        self.spotify_handler = SpotifyHandler()
        self.processor = NotificationProcessor(self.spotify_handler)
        self.dbus_service = DBusService(self)
        logger.info("Notification handler initialized")

    def start(self):
        """Start the notification handler."""
        try:
            logger.info("Starting notification handler")
            self.dbus_service.start()
        except Exception as e:
            logger.error(f"Error in notification handler: {e}")
            raise

    def handle_notification(self, app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout):
        """Handle incoming notification."""
        try:
            # Log all hints for debugging
            if app_name.lower() == 'spotify':
                logger.info(f"Spotify notification received:")
                logger.info(f"Summary: {summary}")
                logger.info(f"Body: {body}")
                if hints and isinstance(hints, dict):
                    for key, value in hints.items():
                        # Skip logging byte arrays and D-Bus variants
                        if isinstance(value, (dbus.Array, dbus.Byte, dbus.ByteArray)):
                            continue
                        if isinstance(value, (str, int, float, bool)):
                            logger.info(f"Hint '{key}': {value} (type: {type(value)})")

            # Process notification data
            notification = self.processor.process_notification_data(
                app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout
            )

            # Add to queue
            self.process_notification(notification)
            return dbus.UInt32(int(notification['notification_id']))
        except Exception as e:
            logger.error(f"Error processing notification: {e}")
            return dbus.UInt32(0)

    def close_notification(self, notification_id):
        """Close a notification."""
        try:
            notification_id = str(notification_id)
            self.remove_notification(notification_id)
            logger.info(f"Closed notification {notification_id}")
        except Exception as e:
            logger.error(f"Error closing notification: {e}")

    def process_notification(self, notification: Dict[str, Any]) -> None:
        """Process a notification dictionary and add it to the queue."""
        try:
            self.notification_queue.add_notification(notification)
            logger.info(f"Processed notification: {notification.get('summary')}")
        except Exception as e:
            logger.error(f"Error processing notification: {e}")

    def remove_notification(self, notification_id: str) -> None:
        """Remove a notification from the queue."""
        self.notification_queue.remove_notification(notification_id)

    def clear_notifications(self) -> None:
        """Clear all notifications from the queue."""
        self.notification_queue.clear()

    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get all notifications from the queue."""
        return self.notification_queue.get_notifications()

    def get_notification(self, notification_id: str) -> Dict[str, Any]:
        """Get a specific notification from the queue."""
        return self.notification_queue.get_notification(notification_id) 