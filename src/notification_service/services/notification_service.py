from notification_service.core import NotificationError

from notification_service.src.notification_service.services.domain import Notification
from notification_service.src.notification_service.repositories.notification_repository import NotificationRepository
from notification_service.src.notification_service.models.notification import NotificationModel
from notification_service.src.notification_service.schemas.notification import NotificationRequest
from notification_service.src.notification_service.senders.base import NotificationSender


class NotificationService:
    def __init__(
        self,
        notification_senders: list[NotificationSender],
        notification_repository: NotificationRepository,
    ):
        self.notification_senders = notification_senders
        self.notification_repository = notification_repository

    def create_notification(self, request: NotificationRequest) -> NotificationModel:
        notification_model = NotificationModel(
            user_id=request.user_id,
            subject=request.subject,
            message=request.message,
            status="PENDING",
        )
        notification_model = self.notification_repository.create_notification(
            notification_model
        )
        print("Notification ID:", notification_model.id)

        unique_channels = set(request.channels)
        for channel in unique_channels:
            self.notification_repository.create_delivery(
                notification_id=notification_model.id, channel=channel
            )

        return notification_model

    @log_execution
    def process_notification(
        self, notification_model: NotificationModel, notification: Notification
    ) -> None:
        deliveries = self.notification_repository.get_deliveries(notification_model.id)

        for sender, delivery in zip(self.notification_senders, deliveries):
            try:
                sender.send(notification)
                self.notification_repository.update_delivery(
                    delivery=delivery, status="SENT"
                )

            except NotificationError as e:
                self.notification_repository.update_delivery(
                    delivery=delivery, status="FAILED", error_message=str(e)
                )

    def send_notification(self, notification: Notification) -> None:
        for n in self.notification_senders:
            try:
                n.send(notification)
            except NotificationError as e:
                print(f"Notification failed: {e}")
