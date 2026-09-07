from abc import ABC, abstractmethod

from notification_service.src.notification_service.services.domain import Notification


class NotificationSender(ABC):

    @property
    @abstractmethod
    def channel(self) -> str:
        pass

    @abstractmethod
    def send(self, notification: Notification) -> None:
        pass