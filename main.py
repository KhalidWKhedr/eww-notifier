"""
Main entry point for the notification system.
"""

import sys
import logging
import signal
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from eww_notifier.config import LOG_FILE
from eww_notifier.notifier.notification_handler import NotificationHandler

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

def handle_signal(signum, frame):
    """Handle system signals for graceful shutdown."""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    sys.exit(0)

def check_permissions():
    """Check if we have necessary permissions to run."""
    try:
        # Check if we can write to cache directory
        cache_dir = Path.home() / ".cache" / "eww"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Test write permissions
        test_file = cache_dir / ".permission_test"
        test_file.touch()
        test_file.unlink()
        
        return True
    except (PermissionError, OSError) as e:
        logger.error(f"Permission error: {e}")
        return False

def main():
    """Main entry point for the notification system."""
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    # Check permissions
    if not check_permissions():
        logger.error("Insufficient permissions to run. Please check file permissions.")
        sys.exit(1)
    
    try:
        logger.info("Starting notification system...")
        handler = NotificationHandler()
        logger.info("Notification system started. Waiting for notifications via D-Bus.")
        handler.run()  # This will block and keep the program running
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Shutdown complete.")

if __name__ == "__main__":
    main() 