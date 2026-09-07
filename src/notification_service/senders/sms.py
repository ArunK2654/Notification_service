from notification_service.senders.base import NotificationSender
from notification_service.services.domain import Notification


class SMSSender(NotificationSender):
    def __init__(self, number: int):
        self.number = number

    def send(self, notification: Notification) -> None:
        print(f"Sending subject '{notification.subject}' SMS to {self.number}")
