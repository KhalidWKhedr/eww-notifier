"""
Main entry point for the notification system.
"""

import sys
import signal
import logging
from pathlib import Path

from eww_notifier.config import NOTIFICATION_PERMISSION_TEST
from eww_notifier.notifier.notification_handler import NotificationHandler

# Configure logging
logger = logging.getLogger(__name__)

def check_permissions():
    """Check if we have write permissions to required directories."""
    try:
        # Test write permission to /tmp
        test_file = NOTIFICATION_PERMISSION_TEST
        test_file.touch()
        test_file.unlink()
        return True
    except (PermissionError, OSError) as e:
        logger.error(f"Permission check failed: {e}")
        return False

def handle_signal(signum, _frame):
    """Handle system signals for graceful shutdown."""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    sys.exit(0)

def main():
    """Main entry point for the notification system."""
    # Check permissions first
    if not check_permissions():
        logger.error("Failed permission check, exiting")
        sys.exit(1)

    # Set up signal handlers
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        # Initialize and start the notification handler
        handler = NotificationHandler()
        handler.start()
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 