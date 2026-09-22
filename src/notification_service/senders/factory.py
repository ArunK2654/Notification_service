from notification_service.enums import ChannelEnum
from notification_service.senders.base import NotificationSender
from notification_service.senders.email import EmailSender
from notification_service.senders.sms import SMSSender


class NotificationSenderFactory:
    @staticmethod
    def create(channel: str, recipient: str) -> NotificationSender:
        match channel:
            case ChannelEnum.EMAIL:
                return EmailSender(recipient)
            case ChannelEnum.SMS:
                return SMSSender(recipient)
            case _:
                raise ValueError(f"Unsupported channel: {channel}")
