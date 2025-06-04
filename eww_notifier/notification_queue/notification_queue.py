"""
Notification queue module for managing notification storage and updates.
"""

import json
import logging
import subprocess
import threading
import time
from typing import Dict, Any, List, Optional

from eww_notifier.config import (
    NOTIFICATION_FILE,
    NOTIFICATION_TEMP_FILE,
    MAX_NOTIFICATIONS,
    UPDATE_COOLDOWN,
    DEFAULT_TIMEOUT,
    EWW_WIDGET_VAR
)
from eww_notifier.utils.error_handler import handle_error

logger = logging.getLogger(__name__)


class NotificationQueue:
    """Queue for managing notifications with persistence.
    
    This class handles:
    - Notification storage and retrieval
    - Cache file management
    - Periodic cleanup of expired notifications
    - Eww widget updates
    """

    def __init__(self):
        """Initialize notification queue with cache file.
        
        Raises:
            CacheError: If cache initialization fails
        """
        try:
            self.cache_file = NOTIFICATION_FILE
            self.temp_file = NOTIFICATION_TEMP_FILE
            # No need to create directory since /tmp always exists
            self.last_update = 0
            self.notifications = []
            self._load_notifications()
            self._cleanup_old_notifications()

            # Start periodic cleanup
            self.cleanup_thread = threading.Thread(target=self._periodic_cleanup, daemon=True)
            self.cleanup_thread.start()
            logger.info("Notification queue initialized")
        except Exception as e:
            handle_error(e, "notification queue initialization", exit_on_error=True)

    def _periodic_cleanup(self):
        """Periodically clean up expired notifications."""
        while True:
            try:
                time.sleep(1)  # Check every second
                self._cleanup_old_notifications()
                if self.notifications:  # Only update widget if there are notifications
                    self.update_eww_widget()
            except Exception as e:
                handle_error(e, "periodic cleanup", exit_on_error=False)

    def _load_notifications(self) -> List[Dict[str, Any]]:
        """Load notifications from cache file.
        
        Returns:
            List of valid notifications
            
        Raises:
            CacheError: If loading fails
        """
        try:
            if not self.cache_file.exists():
                logger.debug("No cache file exists, starting with empty notifications")
                return []

            with open(self.cache_file, 'r') as f:
                try:
                    notifications = json.load(f)
                    if not isinstance(notifications, list):
                        logger.error("Invalid notification cache format: expected list")
                        return []

                    # Validate each notification has required fields
                    valid_notifications = []
                    current_time = time.time()
                    for n in notifications:
                        if not isinstance(n, dict):
                            logger.warning(f"Skipping invalid notification: {n}")
                            continue

                        # Add missing fields
                        if 'timestamp' not in n:
                            n['timestamp'] = current_time
                            logger.warning(f"Added missing timestamp to notification: {n}")
                        if 'expire_timeout' not in n:
                            n['expire_timeout'] = DEFAULT_TIMEOUT
                            logger.warning(f"Added missing expire_timeout to notification: {n}")

                        # Check if notification has expired
                        if current_time - n['timestamp'] > n['expire_timeout'] / 1000:  # Convert ms to s
                            logger.debug(f"Skipping expired notification: {n}")
                            continue

                        valid_notifications.append(n)

                    # Sort by timestamp, most recent first
                    notifications = sorted(valid_notifications, key=lambda x: x.get('timestamp', 0), reverse=True)

                    # Enforce MAX_NOTIFICATIONS limit
                    if len(notifications) > MAX_NOTIFICATIONS:
                        notifications = notifications[:MAX_NOTIFICATIONS]
                        logger.info(f"Trimmed loaded notifications to {MAX_NOTIFICATIONS} entries")

                    return notifications
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in cache file: {e}")
                    return []
        except Exception as e:
            handle_error(e, "notification loading", exit_on_error=False)
            return []

    def _save_notifications(self) -> None:
        """Save notifications to cache file.
        
        Raises:
            CacheError: If saving fails
        """
        try:
            # Ensure we don't exceed MAX_NOTIFICATIONS before saving
            if len(self.notifications) > MAX_NOTIFICATIONS:
                self.notifications = self.notifications[:MAX_NOTIFICATIONS]
                logger.info(f"Trimmed notifications to {MAX_NOTIFICATIONS} entries before saving")

            # Save to temporary file first
            with open(self.temp_file, 'w') as f:
                json.dump(self.notifications, f, indent=2)

            # Atomic rename to ensure file consistency
            self.temp_file.replace(self.cache_file)

            logger.debug(f"Saved {len(self.notifications)} notifications to cache")
        except Exception as e:
            handle_error(e, "notification saving", exit_on_error=False)

    def _cleanup_old_notifications(self) -> None:
        """Clean up old notifications and ensure we don't exceed MAX_NOTIFICATIONS.
        
        Raises:
            NotificationError: If cleanup fails
        """
        try:
            current_time = time.time()

            # Remove expired notifications
            initial_count = len(self.notifications)
            self.notifications = [
                n for n in self.notifications
                if current_time - n.get('timestamp', 0) <= n.get('expire_timeout', DEFAULT_TIMEOUT) / 1000
                # Convert ms to s
            ]

            if len(self.notifications) < initial_count:
                logger.info(f"Removed {initial_count - len(self.notifications)} expired notifications")
                for n in self.notifications:
                    time_passed = current_time - n.get('timestamp', 0)
                    timeout = n.get('expire_timeout', DEFAULT_TIMEOUT) / 1000
                    logger.debug(
                        f"Notification {n.get('notification_id')}: {time_passed:.1f}s passed, {timeout:.1f}s timeout")

                # Always update widget when notifications change
                self._save_notifications()
                self.update_eww_widget()
                return

            # Trim to max size
            if len(self.notifications) > MAX_NOTIFICATIONS:
                self.notifications = self.notifications[:MAX_NOTIFICATIONS]
                logger.info(f"Trimmed notifications to {MAX_NOTIFICATIONS} entries")
                self._save_notifications()
                self.update_eww_widget()
        except Exception as e:
            handle_error(e, "notification cleanup", exit_on_error=False)

    def add_notification(self, notification: Dict[str, Any]) -> None:
        """Add a new notification to the queue.
        
        Args:
            notification: Notification dictionary to add
            
        Raises:
            NotificationError: If adding fails
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in notification:
                notification['timestamp'] = time.time()

            # Add expire_timeout if not present
            if 'expire_timeout' not in notification:
                notification['expire_timeout'] = DEFAULT_TIMEOUT

            # Add to beginning of list (most recent first)
            self.notifications.insert(0, notification)

            # Ensure we don't exceed MAX_NOTIFICATIONS
            if len(self.notifications) > MAX_NOTIFICATIONS:
                self.notifications = self.notifications[:MAX_NOTIFICATIONS]
                logger.info(f"Trimmed notifications to {MAX_NOTIFICATIONS} entries after adding new notification")

            # Clean up old notifications
            self._cleanup_old_notifications()

            # Update widget
            self.update_eww_widget()
        except Exception as e:
            handle_error(e, "notification addition", exit_on_error=False)

    def remove_notification(self, notification_id: str) -> None:
        """Remove a notification from the queue.
        
        Args:
            notification_id: ID of notification to remove
            
        Raises:
            NotificationError: If removal fails
        """
        try:
            initial_count = len(self.notifications)
            self.notifications = [n for n in self.notifications if n.get('notification_id') != notification_id]
            if len(self.notifications) < initial_count:
                logger.info(f"Removed notification {notification_id}")
                self._save_notifications()
                self.update_eww_widget()
        except Exception as e:
            handle_error(e, "notification removal", exit_on_error=False)

    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get all notifications.
        
        Returns:
            List of all notifications
            
        Raises:
            NotificationError: If retrieval fails
        """
        try:
            # Clean up before returning
            self._cleanup_old_notifications()
            return self.notifications
        except Exception as e:
            handle_error(e, "notification retrieval", exit_on_error=False)
            return []

    def clear(self) -> None:
        """Clear all notifications.
        
        Raises:
            NotificationError: If clearing fails
        """
        try:
            self.notifications = []
            self._save_notifications()
            self.update_eww_widget()
            logger.info("Cleared all notifications")
        except Exception as e:
            handle_error(e, "notification clearing", exit_on_error=False)

    def should_update(self) -> bool:
        """Check if enough time has passed since last update.
        
        Returns:
            True if enough time has passed, False otherwise
        """
        current_time = time.time()
        if current_time - self.last_update >= UPDATE_COOLDOWN:
            self.last_update = current_time
            return True
        return False

    def update_eww_widget(self) -> None:
        """Update the Eww widget with current notifications.
        
        This method updates the Eww widget variable with the current notifications.
        It includes error handling for:
        - Eww not running
        - Invalid JSON
        - Command execution failures
        
        Raises:
            NotificationError: If update fails
        """
        # Only update if enough time has passed since the last update
        if not self.should_update():
            return

        try:
            # Convert to JSON string
            notifications_json = json.dumps(self.notifications)

            # Update Eww widget variable
            result = subprocess.run(
                ['eww', 'update', f'{EWW_WIDGET_VAR}={notifications_json}'],
                check=True,
                capture_output=True,
                text=True
            )
            logger.debug("Updated Eww notifications widget")
        except subprocess.CalledProcessError as e:
            handle_error(e, "Eww widget update", exit_on_error=False)
            if e.stderr:
                logger.error(f"Eww error output: {e.stderr}")
        except Exception as e:
            handle_error(e, "Eww widget update", exit_on_error=False)

    def get_notification(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific notification by ID.
        
        Args:
            notification_id: The ID of the notification to retrieve
            
        Returns:
            The notification dictionary if found, None otherwise
            
        Raises:
            NotificationError: If retrieval fails
        """
        try:
            for notification in self.notifications:
                if notification.get('notification_id') == notification_id:
                    return notification
            return None
        except Exception as e:
            handle_error(e, "notification retrieval", exit_on_error=False)
            return None
