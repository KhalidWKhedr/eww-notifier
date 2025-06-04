"""
Logging configuration for the notification system.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

from eww_notifier.config import LOG_FILE, LOG_LEVEL


def setup_logging():
    """Set up logging configuration."""
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )

    # Create handlers
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Set specific logger levels for third-party modules
    logging.getLogger('dbus').setLevel(logging.WARNING)
    logging.getLogger('gi').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    # Set specific logger levels for our modules
    logging.getLogger('eww_notifier.notification_queue').setLevel(logging.INFO)
    logging.getLogger('eww_notifier.spotify').setLevel(logging.INFO)
    logging.getLogger('eww_notifier.notifier').setLevel(logging.INFO)
    logging.getLogger('eww_notifier.utils').setLevel(logging.INFO)

    # Log startup message
    logging.info("Logging system initialized")
