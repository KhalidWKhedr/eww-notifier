from dependency_injector import containers, providers
import logging
from eww_notifier.notification_queue.notification_queue import NotificationQueue
from eww_notifier.notifier.dbus_service import DBusService
from eww_notifier.config import Config
from eww_notifier.notification_service import NotificationService
from eww_notifier.notification_processor_service import NotificationProcessorService
from eww_notifier.notification_queue_service import NotificationQueueService

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    app_config = providers.Singleton(Config)

    logging_service = providers.Singleton(
        logging.getLogger,
        name='eww_notifier'
    )

    notification_queue = providers.Singleton(NotificationQueue)
    dbus_service = providers.Singleton(DBusService)  # Will need handler passed at runtime
    notification_service = providers.Singleton(NotificationService)  # New service
    notification_processor_service = providers.Singleton(NotificationProcessorService)  # New service
    notification_queue_service = providers.Singleton(NotificationQueueService)  # New service

    # Add other services and components here 