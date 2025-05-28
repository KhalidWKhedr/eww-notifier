"""
Main notification handler module that processes and managing system notifications.
"""

import hashlib
import logging
import os
import time
from typing import Dict, Any, List, Optional, Tuple

import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib
from pydbus import SessionBus

from eww_notifier.icon_config import APP_ICONS
from eww_notifier.config import URGENCY_LEVELS, DEFAULT_TIMEOUT
from eww_notifier.notification_queue.notification_queue import NotificationQueue
from eww_notifier.spotify.spotify_handler import SpotifyHandler
from eww_notifier.utils import find_icon_path

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

            # Generate a unique ID for this notification
            notif_id = replaces_id if replaces_id else self._generate_notification_id(app_name, summary, body)

            # Process urgency level
            urgency = self._get_urgency(hints)

            # Process actions
            processed_actions = self._process_actions(actions)

            # Process hints
            processed_hints = self._process_hints(hints)

            # Get icon and image
            icon, image = self._get_icon_and_image(app_name, app_icon, hints)

            notification = {
                'id': str(notif_id),
                'app': app_name,
                'summary': summary,
                'body': body,
                'icon': icon,  # App icon (24x24)
                'image': image,  # Full-size image (like album art)
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
                # Skip byte arrays and D-Bus variants
                if isinstance(value, (dbus.Array, dbus.Byte, dbus.ByteArray)):
                    continue
                if isinstance(value, (str, int, float, bool)):
                    processed_hints[key] = value
                elif hasattr(value, 'unpack'):
                    unpacked = value.unpack()
                    # Skip byte arrays in unpacked values too
                    if not isinstance(unpacked, (dbus.Array, dbus.Byte, dbus.ByteArray)):
                        processed_hints[key] = unpacked
        return processed_hints

    def _get_icon_and_image(self, app_name: str, app_icon: str, hints: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        """Get both the app icon and any associated image (like album art)."""
        try:
            # Default values
            icon = find_icon_path(app_icon or app_name.lower())
            image = None

            # Handle Spotify album art
            if app_name.lower() == 'spotify':
                # Try MPRIS first
                try:
                    bus = SessionBus()
                    spotify = bus.get("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
                    metadata = spotify.Metadata
                    url = metadata.get("mpris:artUrl", "")
                    if url.startswith("https://"):
                        logger.info(f"Got album art URL from MPRIS: {url}")
                        album_art_path = self.spotify_handler.get_album_art_path("mpris", url)
                        if album_art_path and os.path.exists(album_art_path):
                            logger.info(f"Using album art from MPRIS: {album_art_path}")
                            image = album_art_path
                except Exception as e:
                    logger.warning(f"Failed to get album art from MPRIS: {e}")

                # Fallback to notification hints if MPRIS fails
                if not image and hints:
                    # Try to get album art from hints
                    for key, value in hints.items():
                        if isinstance(value, str) and value.startswith('https://'):
                            album_art_path = self.spotify_handler.get_album_art_path("hint", value)
                            if album_art_path and os.path.exists(album_art_path):
                                logger.info(f"Using album art from hints: {album_art_path}")
                                image = album_art_path
                                break

            return icon, image

        except Exception as e:
            logger.error(f"Error getting icon and image: {e}")
            return find_icon_path(APP_ICONS['default']), None

    def _handle_spotify_notification(self, notification: Dict[str, Any], hints: Dict[str, Any]) -> None:
        """Handle Spotify-specific notification features."""
        try:
            # Extract album art URL from hints
            album_art_url = None
            if hints and isinstance(hints, dict):
                # Skip byte arrays and only process string values
                for key, value in hints.items():
                    if isinstance(value, (dbus.Array, dbus.Byte, dbus.ByteArray)):
                        continue
                    if key == 'image-path' and isinstance(value, str):
                        album_art_url = value
                        logger.debug(f"Found album art URL in image-path: {album_art_url}")
                        break
                    elif key in ['image_url', 'image'] and isinstance(value, str):
                        album_art_url = value
                        logger.debug(f"Found album art URL in hint '{key}': {album_art_url}")
                        break

            if album_art_url:
                # Add image URL to notification
                notification['image'] = album_art_url
                logger.info(f"Added image URL to notification: {album_art_url}")

                # Get album art path
                album_art_path = self.spotify_handler.get_album_art_path(notification['id'], album_art_url)
                if album_art_path and os.path.exists(album_art_path):
                    # Update notification with album art path
                    notification['image'] = album_art_path
                    logger.info(f"Updated Spotify notification with album art: {album_art_path}")
                else:
                    logger.warning(f"Failed to get album art path for URL: {album_art_url}")

            # Update metadata
            metadata = {
                'track_id': hints.get('track-id', 'unknown') if isinstance(hints.get('track-id'), str) else 'unknown',
                'album_art_url': album_art_url,
                'album_art_path': notification['image']
            }
            self.spotify_handler.update_metadata(notification['id'], metadata)

        except Exception as e:
            logger.error(f"Error handling Spotify notification: {e}")

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