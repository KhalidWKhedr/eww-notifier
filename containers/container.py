from dependency_injector import containers, providers
import logging
from eww_notifier.notification_queue.notification_queue import NotificationQueue
from eww_notifier.notifier.dbus_service import DBusService

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    logging_service = providers.Singleton(
        logging.getLogger,
        name='eww_notifier'
    )

    notification_queue = providers.Singleton(NotificationQueue)
    dbus_service = providers.Singleton(DBusService)  # Will need handler passed at runtime

    # Add other services and components here 