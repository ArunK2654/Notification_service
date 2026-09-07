from notification_service.src.notification_service.services.domain import Notification
from notification_service.src.notification_service.senders.base import NotificationSender


class PushSender(NotificationSender):
    def __init__(self, device_token: str):
        self.device_token = device_token

    def send(self, notification: Notification) -> None:
        print(
            f"Sending subject '{notification.subject}' push notification to {self.device_token}"
        )