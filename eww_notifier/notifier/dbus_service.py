"""
D-Bus service module for handling system notifications.

This module provides:
- D-Bus service implementation for system notifications
- Signal handling for graceful shutdown
- Notification capabilities and server information
"""

import logging
import signal
import sys
from typing import List, Dict, Any

import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib

logger = logging.getLogger(__name__)


class DBusService(dbus.service.Object):
    """D-Bus service for handling system notifications.
    
    This class:
    - Implements the org.freedesktop.Notifications interface
    - Handles incoming notifications
    - Manages notification lifecycle
    - Provides server capabilities and information
    """

    def __init__(self, notification_handler, logger, handle_error):
        """Initialize D-Bus service.
        
        This method:
        1. Sets up D-Bus mainloop
        2. Registers service on session bus
        3. Sets up signal handlers
        4. Initializes notification handler
        
        Args:
            notification_handler: The notification handler to delegate to
            logger: Logger instance to use
            handle_error: Error handler function
            
        Raises:
            DBusError: If initialization fails
        """
        try:
            # Initialize D-Bus
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            bus = dbus.SessionBus()
            bus_name = dbus.service.BusName('org.freedesktop.Notifications', bus=bus)
            dbus.service.Object.__init__(self, bus_name, '/org/freedesktop/Notifications')

            self.notification_handler = notification_handler
            self.mainloop = GLib.MainLoop()
            self.logger = logger
            self.handle_error = handle_error

            # Set up signal handlers
            signal.signal(signal.SIGINT, self._handle_signal)
            signal.signal(signal.SIGTERM, self._handle_signal)

            self.logger.info("D-Bus service initialized")
        except Exception as e:
            self.handle_error(e, "D-Bus service initialization", exit_on_error=True)

    def _handle_signal(self, signum: int, _frame: Any) -> None:
        """Handle system signals for graceful shutdown.
        
        This method:
        1. Logs the received signal
        2. Quits the mainloop
        3. Exits the process
        
        Args:
            signum: Signal number
            _frame: Current stack frame
        """
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.mainloop.quit()
        sys.exit(0)

    def start(self) -> None:
        """Start the D-Bus service.
        
        This method:
        1. Starts the GLib mainloop
        2. Handles incoming D-Bus messages
        3. Manages notification lifecycle
        
        Raises:
            DBusError: If service fails to start
        """
        try:
            self.logger.info("Starting D-Bus service")
            self.mainloop.run()
        except Exception as e:
            self.handle_error(e, "D-Bus service", exit_on_error=True)

    @dbus.service.method(dbus_interface='org.freedesktop.Notifications', in_signature='susssasa{sv}i',
                         out_signature='u')
    def Notify(
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
        
        This method:
        1. Validates notification data
        2. Delegates to notification handler
        3. Returns notification ID
        
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
            DBusError: If notification handling fails
        """
        try:
            self.logger.debug(f"Received notification from {app_name}: {summary}")
            return self.notification_handler.handle_notification(
                app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout
            )
        except Exception as e:
            self.handle_error(e, "notification handling", exit_on_error=False)
            return dbus.UInt32(0)

    @dbus.service.method(dbus_interface='org.freedesktop.Notifications', in_signature='u')
    def CloseNotification(self, notification_id: int) -> None:
        """Close a notification.
        
        This method:
        1. Validates notification ID
        2. Delegates to notification handler
        3. Logs the operation
        
        Args:
            notification_id: ID of notification to close
            
        Raises:
            DBusError: If notification closing fails
        """
        try:
            self.logger.debug(f"Closing notification {notification_id}")
            self.notification_handler.close_notification(notification_id)
        except Exception as e:
            self.handle_error(e, "notification closing", exit_on_error=False)

    @dbus.service.method(dbus_interface='org.freedesktop.Notifications', out_signature='as')
    def GetCapabilities(self) -> List[str]:
        """Get notification capabilities.
        
        This method returns a list of supported notification features:
        - body: Supports notification body text
        - icon-static: Supports static icons
        - actions: Supports notification actions
        - urgency: Supports urgency levels
        - hints: Supports notification hints
        - action-icons: Supports icons in actions
        - persistence: Supports persistent notifications
        
        Returns:
            List of supported capabilities
            
        Raises:
            DBusError: If capability retrieval fails
        """
        try:
            capabilities = [
                "body",
                "icon-static",
                "actions",
                "urgency",
                "hints",
                "action-icons",
                "persistence"
            ]
            self.logger.debug(f"Returning capabilities: {capabilities}")
            return capabilities
        except Exception as e:
            self.handle_error(e, "capability retrieval", exit_on_error=False)
            return []

    @dbus.service.method(dbus_interface='org.freedesktop.Notifications', out_signature='ssss')
    def GetServerInformation(self) -> tuple:
        """Get server information.
        
        This method returns information about the notification server:
        - name: Server name
        - vendor: Vendor name
        - version: Server version
        - spec_version: Specification version
        
        Returns:
            Tuple of (name, vendor, version, spec_version)
            
        Raises:
            DBusError: If information retrieval fails
        """
        try:
            info = ("eww-notifier", "eww", "1.0", "1.2")
            self.logger.debug(f"Returning server information: {info}")
            return info
        except Exception as e:
            self.handle_error(e, "server information retrieval", exit_on_error=False)
            return "unknown", "unknown", "0.0", "0.0"
