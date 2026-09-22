"""Application logic for creating and delivering notifications."""

from notification_service.auth.models import CurrentUser
from notification_service.core.exceptions import NotificationError
from notification_service.core.logging import log_execution, logger
from notification_service.enums import (
    ChannelEnum,
    DeliveryStatusEnum,
    NotificationStatusEnum,
    UserRoleEnum,
)
from notification_service.models.notification import (
    NotificationDeliveryModel,
    NotificationModel,
)
from notification_service.repositories.notification_repository import (
    NotificationRepository,
)
from notification_service.schemas.notification import NotificationRequest
from notification_service.senders.base import NotificationSender
from notification_service.services.domain import Notification


class NotificationService:
    """For notification creation, saving and delivery."""

    def __init__(
        self,
        notification_repository: NotificationRepository,
        notification_senders: list[NotificationSender] | None = None,
    ):

        self.notification_senders = notification_senders or []
        self.notification_repository = notification_repository

    @log_execution
    def create_notification(
        self, request: NotificationRequest, current_user_id: int, idempotency_key: str
    ) -> tuple[NotificationModel, bool]:
        """Create a notification and its pending deliveries."""
        try:
            existing_notification = self.notification_repository.get_by_idempotency_key(
                idempotency_key
            )

            if existing_notification is not None:
                return existing_notification, False

            notification_model = NotificationModel(
                user_id=current_user_id,
                subject=request.subject,
                message=request.message,
                status=NotificationStatusEnum.PENDING,
                idempotency_key=idempotency_key,
            )
            notification_model = self.notification_repository.create_notification(
                notification_model
            )

            for channel in request.channels:
                self.notification_repository.create_delivery(
                    notification_id=notification_model.id, channel_request=channel
                )

            self.notification_repository.commit()

            logger.info(
                "Notification created successfully with id=%s", notification_model.id
            )

            return notification_model, True

        except Exception:
            self.notification_repository.rollback()
            raise

    @log_execution
    async def process_notification(
        self,
        notification_model: NotificationModel,
        deliveries: list[NotificationDeliveryModel],
    ) -> None:
        """Deliver a notification through all configured channels."""
        notification = Notification(
            subject=notification_model.subject,
            message=notification_model.message,
        )

        delivery_by_channel: dict[ChannelEnum, NotificationDeliveryModel] = {}

        for delivery in deliveries:
            delivery_by_channel[delivery.channel] = delivery

        for sender in self.notification_senders:
            delivery = delivery_by_channel[sender.channel]

            try:
                await sender.send(notification)

                self.notification_repository.update_delivery(
                    delivery=delivery,
                    status=DeliveryStatusEnum.SENT,
                )

            except NotificationError as exc:
                self.notification_repository.update_delivery(
                    delivery=delivery,
                    status=DeliveryStatusEnum.FAILED,
                    error_message=str(exc),
                )

        notification_status = self.determine_notification_status(deliveries)

        self.notification_repository.update_notification_status(
            notification=notification_model,
            status=notification_status,
        )

    @log_execution
    def determine_notification_status(
        self,
        deliveries: list[NotificationDeliveryModel],
    ) -> NotificationStatusEnum:
        """Determine the overall notification status from delivery status."""

        if not deliveries:
            raise NotificationError("Notification has no deliveries")

        statuses = [delivery.status for delivery in deliveries]

        if any(status == DeliveryStatusEnum.PENDING for status in statuses):
            return NotificationStatusEnum.PENDING

        if all(status == DeliveryStatusEnum.SENT for status in statuses):
            return NotificationStatusEnum.COMPLETED

        if all(status == DeliveryStatusEnum.FAILED for status in statuses):
            return NotificationStatusEnum.FAILED

        return NotificationStatusEnum.PARTIALLY_FAILED

    @log_execution
    def get_notifications(
        self,
        current_user: CurrentUser,
    ) -> list[NotificationModel]:
        if current_user.role == UserRoleEnum.ADMIN:
            return self.notification_repository.get_all_notifications()

        return self.notification_repository.get_notifications_by_user(
            current_user.user_id
        )
