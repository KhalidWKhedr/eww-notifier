"""
D-Bus service module for handling system notifications.
"""

import logging
import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib

logger = logging.getLogger(__name__)

class DBusService(dbus.service.Object):
    """D-Bus service for handling system notifications."""

    def __init__(self, notification_handler):
        """Initialize D-Bus service.
        
        Args:
            notification_handler: The notification handler to delegate to
        """
        # Initialize D-Bus
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        bus_name = dbus.service.BusName('org.freedesktop.Notifications', bus=bus)
        dbus.service.Object.__init__(self, bus_name, '/org/freedesktop/Notifications')
        
        self.notification_handler = notification_handler
        self.mainloop = GLib.MainLoop()
        logger.info("D-Bus service initialized")

    def start(self):
        """Start the D-Bus service."""
        try:
            logger.info("Starting D-Bus service")
            self.mainloop.run()
        except Exception as e:
            logger.error(f"Error in D-Bus service: {e}")
            raise

    @dbus.service.method(dbus_interface='org.freedesktop.Notifications', in_signature='susssasa{sv}i', out_signature='u')
    def Notify(self, app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout):
        """Handle incoming notification."""
        return self.notification_handler.handle_notification(
            app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout
        )

    @dbus.service.method(dbus_interface='org.freedesktop.Notifications', in_signature='u')
    def CloseNotification(self, notification_id):
        """Close a notification."""
        self.notification_handler.close_notification(notification_id)

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
        return "eww-notifier", "eww", "1.0", "1.2" 