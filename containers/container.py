from dependency_injector import containers, providers
import logging

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    logging_service = providers.Singleton(
        logging.getLogger,
        name='eww_notifier'
    )

    # Add other services and components here 