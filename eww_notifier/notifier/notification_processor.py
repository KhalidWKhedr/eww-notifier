"""
Notification processor module for handling notification processing.

This module provides functionality for:
- Processing raw notification data into a standardized format
- Handling Spotify-specific features
- Managing notification IDs
- Processing icons and images
"""

import hashlib
import logging
import time
from typing import Dict, Any, Optional, Tuple, List

import dbus

from eww_notifier.config import DEFAULT_TIMEOUT
from eww_notifier.icon_config import APP_ICONS
from eww_notifier.notifier.notification_utils import get_urgency, process_actions, process_hints
from eww_notifier.utils import find_icon_path
from eww_notifier.utils.error_handler import handle_error, NotificationError

logger = logging.getLogger(__name__)

class NotificationProcessor:
    """Processor for handling notification data.
    
    This class handles:
    - Converting raw notification data to a standardized format
    - Managing notification IDs
    - Processing icons and images
    - Handling Spotify-specific features
    """

    def __init__(self, spotify_handler):
        """Initialize notification processor.
        
        Args:
            spotify_handler: Handler for Spotify-specific features
            
        Raises:
            NotificationError: If initialization fails
        """
        try:
            self.spotify_handler = spotify_handler
            self.notification_id_counter = 1
            logger.info("Notification processor initialized")
        except Exception as e:
            handle_error(e, "notification processor initialization", exit_on_error=True)

    def generate_notification_id(self, app_name: str, summary: str, body: str) -> int:
        """Generate a unique notification ID within valid D-Bus range.
        
        The ID is generated using a combination of:
        - A counter that resets at max D-Bus value
        - MD5 hash of app name, summary, body, and counter
        
        Args:
            app_name: Name of the application
            summary: Notification summary
            body: Notification body
            
        Returns:
            A unique notification ID in valid D-Bus range
            
        Raises:
            NotificationError: If ID generation fails
        """
        try:
            if self.notification_id_counter >= 4294967295:  # Reset if we reach max
                self.notification_id_counter = 1
                logger.info("Reset notification ID counter")

            # Use a combination of counter and hash for uniqueness
            unique_str = f"{app_name}{summary}{body}{self.notification_id_counter}"
            hash_obj = hashlib.md5(unique_str.encode())
            # Take first 4 bytes of hash and convert to integer
            notification_id = int.from_bytes(hash_obj.digest()[:4], byteorder='big')
            self.notification_id_counter += 1
            logger.debug(f"Generated notification ID: {notification_id}")
            return notification_id
        except Exception as e:
            handle_error(e, "notification ID generation", exit_on_error=False)
            raise NotificationError("Failed to generate notification ID") from e

    def process_notification_data(
        self,
        app_name: str,
        replaces_id: int,
        app_icon: str,
        summary: str,
        body: str,
        actions: List[str],
        hints: Dict[str, Any],
        expire_timeout: int
    ) -> Dict[str, Any]:
        """Process notification data into a standardized format.
        
        This method:
        1. Generates or uses existing notification ID
        2. Processes basic notification data
        3. Handles icons and images
        4. Processes Spotify-specific features
        
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
            Processed notification dictionary with standardized format
            
        Raises:
            NotificationError: If processing fails
        """
        try:
            # Generate a unique ID for this notification
            notif_id = replaces_id if replaces_id else self.generate_notification_id(app_name, summary, body)
            logger.debug(f"Processing notification {notif_id} from {app_name}")

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

            logger.debug(f"Successfully processed notification {notif_id}")
            return notification
        except Exception as e:
            handle_error(e, "notification processing", exit_on_error=False)
            raise NotificationError("Failed to process notification") from e

    def get_icon_and_image(self, app_name: str, app_icon: str, hints: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        """Get both the app icon and any associated image (like album art).
        
        This method:
        1. Gets the default app icon
        2. For Spotify, tries to get album art from:
           - MPRIS metadata
           - Notification hints
        
        Args:
            app_name: Name of the application
            app_icon: Icon name or path
            hints: Dictionary of hints
            
        Returns:
            Tuple of (icon_path, image_path)
            
        Raises:
            NotificationError: If icon/image retrieval fails
        """
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
            handle_error(e, "icon/image retrieval", exit_on_error=False)
            return find_icon_path(APP_ICONS['default']), None

    def handle_spotify_notification(self, notification: Dict[str, Any], hints: Dict[str, Any]) -> None:
        """Handle Spotify-specific notification features.
        
        This method:
        1. Extracts album art URL from hints
        2. Downloads and caches album art
        3. Updates notification with album art path
        4. Updates Spotify metadata
        
        Args:
            notification: The notification dictionary to update
            hints: Dictionary of hints
            
        Raises:
            NotificationError: If Spotify handling fails
        """
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
            handle_error(e, "Spotify notification handling", exit_on_error=False)
            raise NotificationError("Failed to handle Spotify notification") from e 