
from fastapi import FastAPI

from notification_service.src.notification_service.services.domain import Notification

from notification_service.src.notification_service.services.notification_service import NotificationService

from notification_service.src.notification_service.senders.factory import NotificationSenderFactory

from notification_service.src.notification_service.repositories.notification_repository import NotificationRepository

from notification_service.src.notification_service.schemas.notification import NotificationRequest
from notification_service.src.notification_service.database import db_dependency

app = FastAPI()

@app.post("/notification")
async def create_notification(
    request: NotificationRequest, db: db_dependency
) -> dict[str, str | int]:
    # 1. Create repository
    repository = NotificationRepository(db)

    # 2. Create delivery strategies
    senders = [
        NotificationSenderFactory.create(channel) for channel in request.channels
    ]

    # 3. Create service with injected dependencies
    service = NotificationService(
        notification_senders=senders, notification_repository=repository
    )

    # 4. Create and save NotificationModel
    notification_model = service.create_notification(request)

    notification = Notification(subject=request.subject, message=request.message)

    service.process_notification(
        notification_model=notification_model, notification=notification
    )

    return {
        "message": "Notification processed",
        "notification_id": notification_model.id,
    }

