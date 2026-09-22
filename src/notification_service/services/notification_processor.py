from notification_service.core.logging import logger
from notification_service.database import SessionLocal
from notification_service.enums import DeliveryStatusEnum
from notification_service.repositories.notification_repository import (
    NotificationRepository,
)
from notification_service.senders.factory import NotificationSenderFactory
from notification_service.services.notification_service import (
    NotificationService,
)


class NotificationProcessor:
    """Processes persisted notifications outside the HTTP request lifecycle."""

    async def process(self, notification_id: int) -> None:
        """Load a notification and process its pending deliveries."""

        db = SessionLocal()

        try:
            repository = NotificationRepository(db)

            notification = repository.get_notification(notification_id)

            if notification is None:
                logger.warning("Notification id=%s not found", notification_id)
                return

            logger.info("Processing notification id=%s", notification_id)

            deliveries = repository.get_deliveries(notification_id)

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

            service = NotificationService(
                notification_senders=senders,
                notification_repository=repository,
            )

            await service.process_notification(notification, pending_deliveries)
            db.commit()
            logger.info("Finished processing notification id=%s", notification_id)

        except Exception:
            db.rollback()
            logger.exception(
                "Failed processing notification id=%s",
                notification_id,
            )
            raise

        finally:
            db.close()
