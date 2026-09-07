import os
import smtplib  # Python's built-in library for communicating with an SMTP(Simple Mail Transfer Protocol) server.
from email.message import EmailMessage  # creates an email message object

from dotenv import load_dotenv  # to load the .env file

from notification_service.src.notification_service.services.domain import Notification
from notification_service.src.notification_service.main import EmailDeliveryError
from notification_service.src.notification_service.senders.base import NotificationSender

load_dotenv()


class EmailSender(NotificationSender):
    def __init__(self, email: str):
        self.email = email

    def send(self, notification: Notification) -> None:
        smtp_email = os.getenv("SMTP_EMAIL")
        smtp_password = os.getenv("SMTP_APP_PASSWORD")

        if not smtp_email or not smtp_password:
            raise ValueError("SMTP credentials are not configured")

        message = EmailMessage()
        message["From"] = smtp_email
        message["To"] = self.email
        message["Subject"] = notification.subject
        message.set_content(notification.message)

        try:

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(smtp_email, smtp_password)
                smtp.send_message(message)

        except smtplib.SMTPException as exc:
            raise EmailDeliveryError(
                "Failed to send email"
            ) from exc