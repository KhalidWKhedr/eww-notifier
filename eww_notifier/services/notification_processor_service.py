class NotificationProcessorService:
    def __init__(self, container):
        self.container = container
        self.logger = container.logging_service()
        self.logger.info("Notification processor service initialized")

    def process_notification(self, notification):
        # Process notification logic here
        self.logger.info(f"Processing notification: {notification}") 