"""
Main notification handler module that processes and managing system notifications.
"""

import logging
import signal
import sys
import time
import hashlib
from typing import Dict, Any, List, Optional
from pathlib import Path
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

from Testing.config import APP_ICONS, URGENCY_LEVELS, DEFAULT_TIMEOUT
from Testing.spotify.spotify_handler import SpotifyHandler
from Testing.notification_queue.notification_queue import NotificationQueue

logger = logging.getLogger(__name__)

class NotificationHandler(dbus.service.Object):
    """Notification handler for processing and managing system notifications."""

    def __init__(self):
        """Initialize notification handler with D-Bus service."""
        # Initialize D-Bus
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        bus_name = dbus.service.BusName('org.freedesktop.Notifications', bus=bus)
        dbus.service.Object.__init__(self, bus_name, '/org/freedesktop/Notifications')

        # Initialize components
        self.notification_queue = NotificationQueue()
        self.spotify_handler = SpotifyHandler()
        self.notification_id_counter = 1

        # Set up main loop
        self.mainloop = GLib.MainLoop()
        logger.info("Notification handler initialized")

    def _generate_notification_id(self, app_name: str, summary: str, body: str) -> int:
        """Generate a unique notification ID within valid D-Bus range."""
        if self.notification_id_counter >= 4294967295:  # Reset if we reach max
            self.notification_id_counter = 1

        # Use a combination of counter and hash for uniqueness
        unique_str = f"{app_name}{summary}{body}{self.notification_id_counter}"
        hash_obj = hashlib.md5(unique_str.encode())
        # Take first 4 bytes of hash and convert to integer
        notification_id = int.from_bytes(hash_obj.digest()[:4], byteorder='big')
        self.notification_id_counter += 1
        return notification_id

    @dbus.service.method(dbus_interface='org.freedesktop.Notifications', in_signature='susssasa{sv}i', out_signature='u')
    def Notify(self, app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout):
        """Handle incoming notification."""
        try:
            # Generate a unique ID for this notification
            notif_id = replaces_id if replaces_id else self._generate_notification_id(app_name, summary, body)

            # Process urgency level
            urgency = self._get_urgency(hints)

            # Process actions
            processed_actions = self._process_actions(actions)

            # Process hints
            processed_hints = self._process_hints(hints)

            # Get icon
            icon = self._get_icon(app_name, app_icon, hints)

            notification = {
                'id': str(notif_id),
                'app': app_name,
                'summary': summary,
                'body': body,
                'icon': icon,
                'urgency': urgency,
                'actions': processed_actions,
                'hints': processed_hints,
                'timestamp': time.time(),
                'expire_timeout': expire_timeout if expire_timeout > 0 else DEFAULT_TIMEOUT
            }

            # Handle Spotify notifications specially
            if app_name.lower() == 'spotify':
                self._handle_spotify_notification(notification, hints)

            self.process_notification(notification)
            return dbus.UInt32(notif_id)
        except Exception as e:
            logger.error(f"Error processing notification: {e}")
            return dbus.UInt32(0)

    @dbus.service.method(dbus_interface='org.freedesktop.Notifications', in_signature='u')
    def CloseNotification(self, id):
        """Close a notification."""
        try:
            notification_id = str(id)
            self.remove_notification(notification_id)
            logger.info(f"Closed notification {notification_id}")
        except Exception as e:
            logger.error(f"Error closing notification: {e}")

    @dbus.service.method(dbus_interface='org.freedesktop.Notifications', out_signature='as')
    def GetCapabilities(self):
        """Get notification capabilities."""
        return [
            "body",
            "icon-static",
            "actions",
            "urgency",
            "hints",
            "action-icons",
            "persistence"
        ]

    @dbus.service.method(dbus_interface='org.freedesktop.Notifications', out_signature='ssss')
    def GetServerInformation(self):
        """Get server information."""
        return ("eww-notifier", "eww", "1.0", "1.2")

    def _get_urgency(self, hints: Dict[str, Any]) -> str:
        """Get the urgency level from hints."""
        if hints and isinstance(hints, dict):
            urgency = hints.get('urgency')
            if urgency is not None:
                return URGENCY_LEVELS.get(urgency, 'normal')
        return 'normal'

    def _process_actions(self, actions: List[str]) -> List[Dict[str, str]]:
        """Process notification actions into a list of dictionaries."""
        processed_actions = []
        if actions and isinstance(actions, list):
            for i in range(0, len(actions), 2):
                if i + 1 < len(actions):
                    processed_actions.append({
                        'id': actions[i],
                        'label': actions[i + 1]
                    })
        return processed_actions

    def _process_hints(self, hints: Dict[str, Any]) -> Dict[str, Any]:
        """Process notification hints into a clean dictionary."""
        processed_hints = {}
        if hints and isinstance(hints, dict):
            for key, value in hints.items():
                if isinstance(value, (str, int, float, bool)):
                    processed_hints[key] = value
                elif hasattr(value, 'unpack'):
                    processed_hints[key] = value.unpack() # Assuming this is a D-Bus variant
        return processed_hints

    def _get_icon(self, app_name: str, app_icon: str, hints: Dict[str, Any]) -> str:
        """Get the appropriate icon for the notification."""
        # Try hints first (image-path or image-data)
        if hints and isinstance(hints, dict):
            image_path = hints.get('image-path')
            if image_path:
                # Handle file:// URIs
                if image_path.startswith('file://'):
                    return Path(image_path[len('file://'):]).resolve().as_posix()
                return image_path

            image_data = hints.get('image-data')
            if image_data:
                # Handle image-data hint (requires further processing, maybe save to temp file)
                # For now, we'll just return a placeholder or default icon
                logger.warning("image-data hint received, but not fully supported yet.")
                return APP_ICONS.get(app_name.lower(), APP_ICONS['default'])

        # Try app icon string (can be a name or a path)
        if app_icon:
             # Check if it's a full path
            if Path(app_icon).is_absolute():
                return Path(app_icon).resolve().as_posix()
             # Otherwise assume it's an icon name
            return app_icon

        # Try app name mapping
        app_icon = APP_ICONS.get(app_name.lower())
        if app_icon:
            return app_icon

        # Fallback to default
        return APP_ICONS['default']

    def _handle_spotify_notification(self, notification: Dict[str, Any], hints: Dict[str, Any]) -> None:
        """Handle Spotify-specific notification features."""
        if hints and isinstance(hints, dict):
            # Get album art URL from hints (check both image-path and image_url)
            album_art_url = hints.get('image-path') or hints.get('image_url')

            if album_art_url:
                # Use the spotify_handler to download and cache album art as a path
                # Pass the notification ID and the album art URL to the spotify handler
                album_art_path = self.spotify_handler.get_album_art_path(notification.get('id'), album_art_url)
                if album_art_path:
                    notification['icon'] = album_art_path # Update notification icon to the cached path

            # Get additional Spotify metadata from hints
            metadata = {
                'artist': hints.get('xesam:artist', ''),
                'album': hints.get('xesam:album', ''),
                'title': hints.get('xesam:title', ''),
                'track_id': hints.get('track-id', '')
            }
            # Add spotify_metadata to the notification dictionary if any metadata was found
            if any(metadata.values()):
                 notification['spotify_metadata'] = metadata

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
        """Clear all notifications."""
        self.notification_queue.clear_notifications()

    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get all notifications."""
        return self.notification_queue.get_notifications()

    def get_notification(self, notification_id: str) -> Dict[str, Any]:
        """Get a specific notification."""
        return self.notification_queue.get_notification(notification_id)

    def run(self):
        """Run the notification handler."""
        try:
            logger.info("Starting notification handler main loop")
            self.mainloop.run()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
            self.mainloop.quit()
        except Exception as e:
            logger.error(f"Error in notification handler: {e}")
            self.mainloop.quit()
        finally:
            logger.info("Stopping notification handler") 