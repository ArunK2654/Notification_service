from notification_service.enums import ChannelEnum
from notification_service.senders.base import NotificationSender
from notification_service.services.domain import Notification


class SMSSender(NotificationSender):
    def __init__(self, number: str):
        self.number = number

    @property
    def channel(self) -> ChannelEnum:
        return ChannelEnum.SMS

    async def send(self, notification: Notification) -> None:
        print(f"Sending subject '{notification.subject}' SMS to {self.number}")
