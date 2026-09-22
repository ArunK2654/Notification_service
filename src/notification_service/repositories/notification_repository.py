"""Persistence operations for notifications and delivery records."""

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from notification_service.enums import DeliveryStatusEnum, NotificationStatusEnum
from notification_service.models.notification import (
    NotificationDeliveryModel,
    NotificationModel,
)
from notification_service.schemas.notification import NotificationChannelRequest


class NotificationRepository:
    """Provides database access for notifications and deliveries."""

    def __init__(self, db: Session):
        self.db = db

    def create_notification(self, notification: NotificationModel) -> NotificationModel:
        """Saves a notification record"""
        self.db.add(notification)
        self.db.flush()
        self.db.refresh(notification)
        return notification

    def update_notification_status(
        self,
        notification: NotificationModel,
        status: NotificationStatusEnum,
    ) -> NotificationModel:
        """Update the status of a notification."""
        notification.status = status

        self.db.commit()
        self.db.refresh(notification)

        return notification

    def get_notification(
        self,
        notification_id: int,
    ) -> NotificationModel | None:
        """Return a notification by ID."""

        return (
            self.db.query(NotificationModel)
            .filter(NotificationModel.id == notification_id)
            .first()
        )

    def create_delivery(
        self, notification_id: int, channel_request: NotificationChannelRequest
    ) -> NotificationDeliveryModel:
        """Saves a pending delivery for a notification."""

        delivery = NotificationDeliveryModel(
            notification_id=notification_id,
            channel=channel_request.channel,
            recipient=channel_request.recipient,
            status=DeliveryStatusEnum.PENDING,
            error_message=None,
        )
        self.db.add(delivery)
        self.db.flush()
        self.db.refresh(delivery)
        return delivery

    def update_delivery(
        self,
        delivery: NotificationDeliveryModel,
        status: DeliveryStatusEnum,
        error_message: str | None = None,
    ) -> NotificationDeliveryModel:
        """Update the status of a delivery."""
        delivery.status = status
        delivery.error_message = error_message
        delivery.attempt_count += 1

        self.db.flush()
        self.db.refresh(delivery)

        return delivery

    def get_deliveries(self, notification_id: int) -> list[NotificationDeliveryModel]:
        """Return all channel deliveries associated with a notification."""
        deliveries = (
            self.db.query(NotificationDeliveryModel)
            .filter(NotificationDeliveryModel.notification_id == notification_id)
            .all()
        )
        return deliveries

    def get_notifications_by_user(
        self,
        user_id: int,
    ) -> list[NotificationModel]:
        return (
            self.db.query(NotificationModel)
            .filter(NotificationModel.user_id == user_id)
            .all()
        )

    def get_all_notifications(self) -> list[NotificationModel]:
        return self.db.query(NotificationModel).all()

    def commit(self) -> None:
        """Commit the current transaction."""

        self.db.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""

        self.db.rollback()

    def ping(self) -> bool:
        try:
            self.db.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            return False

    def get_by_idempotency_key(self, idempotency_key: str) -> NotificationModel | None:
        return (
            self.db.query(NotificationModel)
            .filter(NotificationModel.idempotency_key == idempotency_key)
            .first()
        )
