"""Async persistence operations for notifications and deliveries."""

from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.enums import (
    DeliveryStatusEnum,
    NotificationStatusEnum,
)
from notification_service.models.notification import (
    NotificationDeliveryModel,
    NotificationModel,
)
from notification_service.schemas.notification import NotificationChannelRequest


class AsyncNotificationRepository:
    """Provides asynchronous database access for notifications."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_notification(
        self,
        notification: NotificationModel,
    ) -> NotificationModel:
        """Save a notification record."""
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def update_notification_status(
        self,
        notification: NotificationModel,
        status: NotificationStatusEnum,
    ) -> NotificationModel:
        """Update a notification's status."""
        notification.status = status
        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def get_notification(
        self,
        notification_id: int,
    ) -> NotificationModel | None:
        """Return a notification by ID."""
        result = await self.db.execute(
            select(NotificationModel).where(
                NotificationModel.id == notification_id
            )
        )
        return result.scalar_one_or_none()

    async def create_delivery(
        self,
        notification_id: int,
        channel_request: NotificationChannelRequest,
    ) -> NotificationDeliveryModel:
        """Save a pending delivery."""
        delivery = NotificationDeliveryModel(
            notification_id=notification_id,
            channel=channel_request.channel,
            recipient=channel_request.recipient,
            status=DeliveryStatusEnum.PENDING,
            error_message=None,
        )
        self.db.add(delivery)
        await self.db.flush()
        await self.db.refresh(delivery)
        return delivery

    async def update_delivery(
        self,
        delivery: NotificationDeliveryModel,
        status: DeliveryStatusEnum,
        error_message: str | None = None,
    ) -> NotificationDeliveryModel:
        """Update a delivery's status."""
        delivery.status = status
        delivery.error_message = error_message
        delivery.attempt_count += 1

        await self.db.flush()
        await self.db.refresh(delivery)
        return delivery

    async def get_deliveries(
        self,
        notification_id: int,
    ) -> list[NotificationDeliveryModel]:
        """Return deliveries for a notification."""
        result = await self.db.execute(
            select(NotificationDeliveryModel).where(
                NotificationDeliveryModel.notification_id
                == notification_id
            )
        )
        return list(result.scalars().all())

    async def get_notifications_by_user(
        self,
        user_id: int,
    ) -> list[NotificationModel]:
        """Return notifications belonging to a user."""
        result = await self.db.execute(
            select(NotificationModel).where(
                NotificationModel.user_id == user_id
            )
        )
        return list(result.scalars().all())

    async def get_all_notifications(self) -> list[NotificationModel]:
        """Return all notifications."""
        result = await self.db.execute(select(NotificationModel))
        return list(result.scalars().all())

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> NotificationModel | None:
        """Find a notification by its idempotency key."""
        result = await self.db.execute(
            select(NotificationModel).where(
                NotificationModel.idempotency_key == idempotency_key
            )
        )
        return result.scalar_one_or_none()

    async def commit(self) -> None:
        """Commit the current transaction."""
        await self.db.commit()

    async def rollback(self) -> None:
        """Roll back the current transaction."""
        await self.db.rollback()

    async def ping(self) -> bool:
        """Check database connectivity."""
        try:
            await self.db.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            await self.db.rollback()
            return False