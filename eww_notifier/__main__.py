"""
Main entry point for the notification system.
"""

import sys
import signal
import logging
from eww_notifier.notifier.notification_handler import NotificationHandler

# Configure logging
logger = logging.getLogger(__name__)

def handle_signal(signum, _frame):
    """Handle system signals for graceful shutdown."""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    sys.exit(0)

def main():
    """Main entry point for the notification system."""
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