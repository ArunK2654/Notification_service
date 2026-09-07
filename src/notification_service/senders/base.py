from abc import ABC, abstractmethod

from notification_service.services.domain import Notification


class NotificationSender(ABC):
    @abstractmethod
    def send(self, notification: Notification) -> None:
        pass
