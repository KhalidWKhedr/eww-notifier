import logging

from eww_notifier.notification_queue.notification_queue import NotificationQueue
from eww_notifier.notifier.dbus_service import DBusService
from eww_notifier.services.notification_processor_service import NotificationProcessorService
from eww_notifier.services.notification_queue_service import NotificationQueueService
from eww_notifier.services.notification_service import NotificationService
from eww_notifier.utils.error_handler import handle_error


def get_logger():
    return logging.getLogger('eww_notifier')

def get_handle_error():
    return handle_error

def get_notification_queue():
    return NotificationQueue()

def get_dbus_service(notification_handler):
    return DBusService(
        notification_handler,
        get_logger(),
        get_handle_error()
    )

def get_notification_service():
    return NotificationService(get_logger())

def get_notification_processor_service():
    return NotificationProcessorService(get_logger())

def get_notification_queue_service():
    return NotificationQueueService(get_logger())

# Add other service factories as needed

