from notification_service.senders.base import NotificationSender
from notification_service.services.domain import Notification


class PushSender(NotificationSender):
    def __init__(self, device_token: str):
        self.device_token = device_token

    def send(self, notification: Notification) -> None:
        print(
            f"Sending subject '{notification.subject}' push notification to {self.device_token}"
        )
