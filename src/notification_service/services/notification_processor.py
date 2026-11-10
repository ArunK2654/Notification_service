"""Processes notifications using asynchronous database sessions."""

from notification_service.core.logging import logger
from notification_service.database import AsyncSessionLocal
from notification_service.enums import DeliveryStatusEnum
from notification_service.repositories.async_notification_repository import (
    AsyncNotificationRepository,
)
from notification_service.senders.factory import NotificationSenderFactory
from notification_service.services.async_notification_service import (
    AsyncNotificationService,
)


class NotificationProcessor:
    """Processes persisted notifications outside the HTTP request lifecycle."""

    async def process(self, notification_id: int) -> None:
        """Load and process pending notification deliveries."""

        async with AsyncSessionLocal() as db:
            try:
                repository = AsyncNotificationRepository(db)

                notification = await repository.get_notification(notification_id)

                if notification is None:
                    logger.warning("Notification id=%s not found", notification_id)
                    return

                logger.info("Processing notification id=%s", notification_id)

                deliveries = await repository.get_deliveries(notification_id)

                pending_deliveries = [
                    delivery
                    for delivery in deliveries
                    if delivery.status == DeliveryStatusEnum.PENDING
                ]

                senders = [
                    NotificationSenderFactory.create(
                        channel=delivery.channel,
                        recipient=delivery.recipient,
                    )
                    for delivery in pending_deliveries
                ]

                service = AsyncNotificationService(
                    notification_repository=repository,
                    notification_senders=senders,
                )

                await service.process_notification(
                    notification,
                    pending_deliveries,
                )

                await db.commit()

                logger.info(
                    "Finished processing notification id=%s",
                    notification_id,
                )

            except Exception:
                await db.rollback()
                logger.exception(
                    "Failed processing notification id=%s",
                    notification_id,
                )
                raise