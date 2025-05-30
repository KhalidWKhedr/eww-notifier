"""
Main notification handler module that processes and managing system notifications.
"""

import logging
from typing import Dict, Any, List, Optional

import dbus

from eww_notifier.utils.error_handler import handle_error

logger = logging.getLogger(__name__)

class NotificationHandler:
    """Notification handler for processing and managing system notifications.
    
    This class coordinates between different components:
    - DBusService: Handles D-Bus communication
    - NotificationProcessor: Processes notification data
    - NotificationQueue: Manages notification storage
    - SpotifyHandler: Handles Spotify-specific features
    """

    def __init__(self, notification_queue, spotify_handler, processor, dbus_service, logger, config):
        """Initialize notification handler.
        
        Raises:
            NotificationError: If initialization fails
        """
        try:
            self.notification_queue = notification_queue
            self.spotify_handler = spotify_handler
            self.processor = processor
            self.dbus_service = dbus_service
            self.logger = logger
            self.config = config
            logger.info("Notification handler initialized")
        except Exception as e:
            handle_error(e, "notification handler initialization", exit_on_error=True)

    def start(self):
        """Start the notification handler.
        
        Raises:
            NotificationError: If starting fails
        """
        try:
            logger.info("Starting notification handler")
            self.dbus_service.start()
        except Exception as e:
            handle_error(e, "notification handler", exit_on_error=True)

    def handle_notification(
        self,
        app_name: str,
        replaces_id: int,
        app_icon: str,
        summary: str,
        body: str,
        actions: List[str],
        hints: Dict[str, Any],
        expire_timeout: int
    ) -> dbus.UInt32:
        """Handle incoming notification.
        
        Args:
            app_name: Name of the application
            replaces_id: ID of notification to replace
            app_icon: Icon name or path
            summary: Notification summary
            body: Notification body
            actions: List of actions
            hints: Dictionary of hints
            expire_timeout: Timeout in milliseconds
            
        Returns:
            Notification ID as D-Bus UInt32
            
        Raises:
            NotificationError: If handling fails
        """
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
            handle_error(e, "notification handling", exit_on_error=False)
            return dbus.UInt32(0)

    def close_notification(self, notification_id: int) -> None:
        """Close a notification.
        
        Args:
            notification_id: ID of notification to close
            
        Raises:
            NotificationError: If closing fails
        """
        try:
            notification_id = str(notification_id)
            self.remove_notification(notification_id)
            logger.info(f"Closed notification {notification_id}")
        except Exception as e:
            handle_error(e, "notification closing", exit_on_error=False)

    def process_notification(self, notification: Dict[str, Any]) -> None:
        """Process a notification dictionary and add it to the queue.
        
        Args:
            notification: Notification dictionary to process
            
        Raises:
            NotificationError: If processing fails
        """
        try:
            self.notification_queue.add_notification(notification)
            logger.info(f"Processed notification: {notification.get('summary')}")
        except Exception as e:
            handle_error(e, "notification processing", exit_on_error=False)

    def remove_notification(self, notification_id: str) -> None:
        """Remove a notification from the queue.
        
        Args:
            notification_id: ID of notification to remove
            
        Raises:
            NotificationError: If removal fails
        """
        try:
            self.notification_queue.remove_notification(notification_id)
        except Exception as e:
            handle_error(e, "notification removal", exit_on_error=False)

    def clear_notifications(self) -> None:
        """Clear all notifications from the queue.
        
        Raises:
            NotificationError: If clearing fails
        """
        try:
            self.notification_queue.clear()
        except Exception as e:
            handle_error(e, "notification clearing", exit_on_error=False)

    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get all notifications from the queue.
        
        Returns:
            List of notification dictionaries
            
        Raises:
            NotificationError: If retrieval fails
        """
        try:
            return self.notification_queue.get_notifications()
        except Exception as e:
            handle_error(e, "notification retrieval", exit_on_error=False)
            return []

    def get_notification(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific notification from the queue.
        
        Args:
            notification_id: ID of notification to get
            
        Returns:
            Notification dictionary or None if not found
            
        Raises:
            NotificationError: If retrieval fails
        """
        try:
            return self.notification_queue.get_notification(notification_id)
        except Exception as e:
            handle_error(e, "notification retrieval", exit_on_error=False)
            return None 