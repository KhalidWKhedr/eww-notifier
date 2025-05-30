class NotificationProcessorService:
    def __init__(self, logger):
        self.logger = logger
        self.logger.info("Notification processor service initialized")

    def process_notification(self, notification):
        # Process notification logic here
        self.logger.info(f"Processing notification: {notification}") 