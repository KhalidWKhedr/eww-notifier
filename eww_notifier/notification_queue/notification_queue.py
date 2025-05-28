"""
Notification queue module for managing notification storage and updates.
"""

import json
import logging
import subprocess
import time
from typing import Dict, Any, List, Optional

from eww_notifier.config import NOTIFICATION_CACHE_FILE, MAX_NOTIFICATIONS, UPDATE_COOLDOWN

logger = logging.getLogger(__name__)

# Maximum age of notifications in seconds (1 hour)
MAX_NOTIFICATION_AGE = 3600

class NotificationQueue:
    """Queue for managing notifications with persistence."""

    def __init__(self):
        """Initialize notification queue with cache file."""
        self.cache_file = NOTIFICATION_CACHE_FILE
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.last_update = 0
        self.notifications = []
        self._load_notifications()
        self._cleanup_old_notifications()

    def _load_notifications(self) -> List[Dict[str, Any]]:
        """Load notifications from cache file."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    notifications = json.load(f)
                    # Sort by timestamp, most recent first
                    return sorted(notifications, key=lambda x: x.get('timestamp', 0), reverse=True)
        except Exception as e:
            logger.error(f"Error loading notifications: {e}")
        return []

    def _save_notifications(self) -> None:
        """Save notifications to cache file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.notifications, f, indent=2)
            logger.debug(f"Saved {len(self.notifications)} notifications to cache")
        except Exception as e:
            logger.error(f"Error saving notifications: {e}")

    def _cleanup_old_notifications(self) -> None:
        """Clean up old notifications and ensure we don't exceed MAX_NOTIFICATIONS."""
        current_time = time.time()
        
        # Remove notifications older than MAX_NOTIFICATION_AGE
        self.notifications = [
            n for n in self.notifications 
            if current_time - n.get('timestamp', 0) < MAX_NOTIFICATION_AGE
        ]
        
        # Trim to max size
        if len(self.notifications) > MAX_NOTIFICATIONS:
            self.notifications = self.notifications[:MAX_NOTIFICATIONS]
            logger.info(f"Trimmed notifications to {MAX_NOTIFICATIONS} entries")
        
        self._save_notifications()

    def add_notification(self, notification: Dict[str, Any]) -> None:
        """Add a new notification to the queue."""
        # Add timestamp if not present
        if 'timestamp' not in notification:
            notification['timestamp'] = time.time()

        # Add to beginning of list (most recent first)
        self.notifications.insert(0, notification)

        # Clean up old notifications and trim to max size
        self._cleanup_old_notifications()

        # Update widget
        self.update_eww_widget()

    def remove_notification(self, notification_id: str) -> None:
        """Remove a notification from the queue."""
        initial_count = len(self.notifications)
        self.notifications = [n for n in self.notifications if n.get('id') != notification_id]
        if len(self.notifications) < initial_count:
            logger.info(f"Removed notification {notification_id}")
            self._save_notifications()
            self.update_eww_widget()

    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get all notifications."""
        # Clean up before returning
        self._cleanup_old_notifications()
        return self.notifications

    def clear_notifications(self) -> None:
        """Clear all notifications."""
        self.notifications = []
        self._save_notifications()
        self.update_eww_widget()
        logger.info("Cleared all notifications")

    def should_update(self) -> bool:
        """Check if enough time has passed since last update."""
        current_time = time.time()
        if current_time - self.last_update >= UPDATE_COOLDOWN:
            self.last_update = current_time
            return True
        return False

    def update_eww_widget(self) -> None:
        """Update the Eww widget with current notifications."""
        # Only update if enough time has passed since the last update
        if not self.should_update():
            return

        try:
            # Convert to JSON string
            notifications_json = json.dumps(self.notifications)

            # Update Eww widget variable
            subprocess.run(
                ['eww', 'update', f'notifications={notifications_json}'],
                check=True,
                capture_output=True,
                text=True
            )
            logger.debug("Updated Eww notifications widget")
        except Exception as e:
            logger.error(f"Error updating Eww widget: {e}")

    def get_notification(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific notification by ID."""
        try:
            for notification in self.notifications:
                if notification.get('id') == notification_id:
                    return notification
            return None
        except Exception as e:
            logger.error(f"Error getting notification {notification_id}: {e}")
            return None

    def update_notification(self, notification_id: str, updates: Dict[str, Any]) -> None:
        """Update a specific notification by ID with new data."""
        try:
            for i, notification in enumerate(self.notifications):
                if notification.get('id') == notification_id:
                    self.notifications[i].update(updates)
                    self._save_notifications()
                    self.update_eww_widget()
                    logger.info(f"Updated notification {notification_id}")
                    return
        except Exception as e:
            logger.error(f"Error updating notification {notification_id}: {e}") 