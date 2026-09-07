from notification_service.src.notification_service.senders.sms import SMSSender

from notification_service.src.notification_service.senders.push import PushSender
from notification_service.src.notification_service.senders.base import NotificationSender

from notification_service.src.notification_service.senders.email import EmailSender


class NotificationSenderFactory:
    @staticmethod
    def create(channel: str) -> NotificationSender:
        match channel:
            case "email":
                return EmailSender("arunthamizhanda@gmail.com")
            case "sms":
                return SMSSender(9845678903)
            case "push":
                return PushSender("wewf233en67")
            case _:
                raise ValueError(f"Unsupported channel: {channel}")

