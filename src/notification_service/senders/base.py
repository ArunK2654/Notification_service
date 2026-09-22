from abc import ABC, abstractmethod

from notification_service.enums import ChannelEnum
from notification_service.services.domain import Notification


class NotificationSender(ABC):
    @property
    @abstractmethod
    def channel(self) -> ChannelEnum:
        pass

    @abstractmethod
    async def send(self, notification: Notification) -> None:
        pass
