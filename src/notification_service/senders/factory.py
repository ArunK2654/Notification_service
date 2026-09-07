from notification_service.senders.base import NotificationSender
from notification_service.senders.email import EmailSender
from notification_service.senders.push import PushSender
from notification_service.senders.sms import SMSSender


class NotificationSenderFactory:
    @staticmethod
    def create(channel: str) -> NotificationSender:
        match channel:
            case "email":
                return EmailSender("arunthamizhanda@gmail.com")
            case "sms":
                return SMSSender(9876543210)
            case "push":
                return PushSender("")
            case _:
                raise ValueError(f"Unsupported channel: {channel}")
