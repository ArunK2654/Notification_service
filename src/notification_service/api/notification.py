from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Header, status

from notification_service.auth.dependencies import get_current_user
from notification_service.auth.models import CurrentUser
from notification_service.database import db_dependency
from notification_service.repositories.notification_repository import (
    NotificationRepository,
)
from notification_service.schemas.notification import (
    NotificationDetailResponse,
    NotificationListResponse,
    NotificationRequest,
    NotificationResponse,
)
from notification_service.senders.factory import NotificationSenderFactory
from notification_service.services.notification_processor import NotificationProcessor
from notification_service.services.notification_service import NotificationService

router = APIRouter()
user_dependency = Annotated[CurrentUser, Depends(get_current_user)]


@router.post(
    "/notification",
    response_model=NotificationResponse,
)
def create_notification(
    request: NotificationRequest,
    db: db_dependency,
    current_user: user_dependency,
    background_tasks: BackgroundTasks,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
) -> NotificationResponse:
    # 1. Create repository
    repository = NotificationRepository(db)

    # 2. Create delivery strategies
    senders = [
        NotificationSenderFactory.create(channel.channel, channel.recipient)
        for channel in request.channels
    ]

    # 3. Create service with injected dependencies
    service = NotificationService(
        notification_senders=senders, notification_repository=repository
    )

    # 4. Create and save NotificationModel
    notification_model, created = service.create_notification(
        request=request,
        current_user_id=current_user.user_id,
        idempotency_key=idempotency_key,
    )

    if created:
        processor = NotificationProcessor()

        background_tasks.add_task(
            processor.process,
            notification_model.id,
        )

    return NotificationResponse(
        message=("Notification accepted" if created else "Notification already exits"),
        notification_id=notification_model.id,
    )


@router.get(
    "/get_notifications",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
)
def get_notifications(
    current_user: user_dependency, db: db_dependency
) -> NotificationListResponse:

    repository = NotificationRepository(db)
    service = NotificationService(notification_repository=repository)

    notifications = service.get_notifications(current_user)

    return NotificationListResponse(
        notifications=[
            NotificationDetailResponse(
                id=notification.id,
                subject=notification.subject,
                message=notification.message,
                status=notification.status,
                created_at=notification.created_at,
            )
            for notification in notifications
        ]
    )
