from email.message import EmailMessage

from aiosmtplib import SMTP, SMTPException
from dotenv import load_dotenv

from notification_service.core.config import settings
from notification_service.core.exceptions import EmailDeliveryError
from notification_service.core.logging import log_execution
from notification_service.enums import ChannelEnum
from notification_service.senders.base import NotificationSender
from notification_service.services.domain import Notification

load_dotenv()


class EmailSender(NotificationSender):
    def __init__(self, email: str):
        self.email = email

    @property
    def channel(self) -> ChannelEnum:
        return ChannelEnum.EMAIL

    @log_execution
    async def send(self, notification: Notification) -> None:
        message = EmailMessage()
        message["From"] = settings.smtp_email
        message["To"] = self.email
        message["Subject"] = notification.subject
        message.set_content(notification.message)

        if not settings.smtp_email or not settings.smtp_app_password:
            raise EmailDeliveryError("SMTP credentials are not configured")

        try:
            smtp = SMTP(hostname="smtp.gmail.com", port=465, use_tls=True)
            await smtp.connect()
            await smtp.login(settings.smtp_email, settings.smtp_app_password)
            await smtp.send_message(message)
            await smtp.quit()

        except SMTPException as exc:
            raise EmailDeliveryError("Failed to send email") from exc
