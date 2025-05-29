"""
Main entry point for the notification system.
"""

import logging
import signal
import sys
import json
from pathlib import Path

# Add the project root to Python path
from eww_notifier.config import PROJECT_ROOT, LOG_FILE, NOTIFICATION_PERMISSION_TEST
sys.path.insert(0, str(PROJECT_ROOT))

from eww_notifier.notifier.notification_handler import NotificationHandler
from eww_notifier.notification_queue.notification_queue import NotificationQueue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def handle_signal(signum, _frame):
    """Handle system signals for graceful shutdown."""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    sys.exit(0)

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

def output_notifications():
    """Output current notifications for deflisten."""
    queue = NotificationQueue()
    print(json.dumps(queue.get_notifications()))

def main():
    """Main entry point for the notification system."""
    # Check if we're being called by deflisten
    if len(sys.argv) > 1 and sys.argv[1] == "--output":
        output_notifications()
        return

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