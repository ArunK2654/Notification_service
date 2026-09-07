from sqlalchemy.orm import Session

from notification_service.src.notification_service.models.notification import NotificationModel, \
    NotificationDeliveryModel


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(self, notification: NotificationModel) -> NotificationModel:
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def create_delivery(
        self, notification_id: int, channel: str
    ) -> NotificationDeliveryModel:
        delivery = NotificationDeliveryModel(
            notification_id=notification_id,
            channel=channel,
            status="PENDING",
            error_message=None,
        )
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def get_deliveries(self, notification_id: int) -> list[NotificationDeliveryModel]:
        deliveries = (
            self.db.query(NotificationDeliveryModel)
            .filter(NotificationDeliveryModel.notification_id == notification_id)
            .all()
        )
        return deliveries

    def update_delivery(
        self,
        delivery: NotificationDeliveryModel,
        status: str,
        error_message: str | None = None,
    ) -> NotificationDeliveryModel:
        delivery.status = status
        delivery.error_message = error_message
        delivery.attempt_count += 1

        self.db.commit()
        self.db.refresh(delivery)

        return delivery