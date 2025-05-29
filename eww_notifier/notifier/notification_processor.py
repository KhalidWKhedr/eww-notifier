"""
Notification processor module for handling notification processing.
"""

import hashlib
import logging
import time
from typing import Dict, Any, Optional, Tuple

import dbus

from eww_notifier.config import DEFAULT_TIMEOUT
from eww_notifier.notifier.notification_utils import get_urgency, process_actions, process_hints
from eww_notifier.utils import find_icon_path
from eww_notifier.icon_config import APP_ICONS

logger = logging.getLogger(__name__)

class NotificationProcessor:
    """Processor for handling notification data."""

    def __init__(self, spotify_handler):
        """Initialize notification processor.
        
        Args:
            spotify_handler: Handler for Spotify-specific features
        """
        self.spotify_handler = spotify_handler
        self.notification_id_counter = 1

    def generate_notification_id(self, app_name: str, summary: str, body: str) -> int:
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

    def process_notification_data(
        self,
        app_name: str,
        replaces_id: int,
        app_icon: str,
        summary: str,
        body: str,
        actions: list,
        hints: Dict[str, Any],
        expire_timeout: int
    ) -> Dict[str, Any]:
        """Process notification data into a standardized format.
        
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
            Processed notification dictionary
        """
        # Generate a unique ID for this notification
        notif_id = replaces_id if replaces_id else self.generate_notification_id(app_name, summary, body)

        # Process notification data
        notification = {
            'notification_id': str(notif_id),
            'app': app_name,
            'summary': summary,
            'body': body,
            'icon': find_icon_path(app_icon or app_name.lower()),
            'image': None,
            'urgency': get_urgency(hints),
            'actions': process_actions(actions),
            'hints': process_hints(hints),
            'timestamp': time.time(),
            'expire_timeout': expire_timeout if expire_timeout > 0 else DEFAULT_TIMEOUT
        }

        # Get icon and image
        notification['icon'], notification['image'] = self.get_icon_and_image(app_name, app_icon, hints)

        # Handle Spotify notifications specially
        if app_name.lower() == 'spotify':
            self.handle_spotify_notification(notification, hints)

        return notification

    def get_icon_and_image(self, app_name: str, app_icon: str, hints: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        """Get both the app icon and any associated image (like album art)."""
        try:
            # Default values
            icon = find_icon_path(app_icon or app_name.lower())
            image = None

            # Handle Spotify album art
            if app_name.lower() == 'spotify':
                # Try MPRIS first
                try:
                    from pydbus import SessionBus
                    bus = SessionBus()
                    spotify = bus.get("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
                    metadata = spotify.Metadata
                    url = metadata.get("mpris:artUrl", "")
                    if url.startswith("https://"):
                        logger.info(f"Got album art URL from MPRIS: {url}")
                        album_art_path = self.spotify_handler.get_album_art_path("mpris")
                        if album_art_path:
                            logger.info(f"Using album art from MPRIS: {album_art_path}")
                            image = album_art_path
                except Exception as e:
                    logger.warning(f"Failed to get album art from MPRIS: {e}")

                # Fallback to notification hints if MPRIS fails
                if not image and hints:
                    # Try to get album art from hints
                    for key, value in hints.items():
                        if isinstance(value, str) and value.startswith('https://'):
                            album_art_path = self.spotify_handler.get_album_art_path(value)
                            if album_art_path:
                                logger.info(f"Using album art from hints: {album_art_path}")
                                image = album_art_path
                                break

            return icon, image

        except Exception as e:
            logger.error(f"Error getting icon and image: {e}")
            return find_icon_path(APP_ICONS['default']), None

    def handle_spotify_notification(self, notification: Dict[str, Any], hints: Dict[str, Any]) -> None:
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
                album_art_path = self.spotify_handler.get_album_art_path(album_art_url)
                if album_art_path:
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
            self.spotify_handler.update_metadata(notification['notification_id'], metadata)

        except Exception as e:
            logger.error(f"Error handling Spotify notification: {e}") 