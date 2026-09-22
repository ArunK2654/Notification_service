import pytest
from unittest.mock import Mock, AsyncMock, patch
from notification_service.repositories.notification_repository import (
    NotificationRepository,
)
from notification_service.models.notification import (
    NotificationModel,
    NotificationDeliveryModel,
)

from notification_service.enums import (
    NotificationStatusEnum,
    ChannelEnum,
    DeliveryStatusEnum,
)

from notification_service.services.notification_processor import NotificationProcessor


@pytest.mark.asyncio
async def test_process_happy_path():
    mock_db = Mock()
    repository = Mock()

    notification_model = NotificationModel(
        id=100,
        user_id=1,
        subject="Test Subject",
        message="Test Message",
        status=NotificationStatusEnum.PENDING,
        idempotency_key="1",
    )
    repository.get_notification.return_value = notification_model

    deliveries = [
        NotificationDeliveryModel(
            id=11,
            notification_id=100,
            channel=ChannelEnum.EMAIL,
            recipient="test@gmail.com",
            status=DeliveryStatusEnum.PENDING,
            attempt_count=0,
            error_message=None,
        )
    ]
    repository.get_deliveries.return_value = deliveries

    mock_sender = Mock()

    mock_service = Mock()
    mock_service.process_notification = AsyncMock()

    with (
        patch(
            "notification_service.services.notification_processor.SessionLocal",
            return_value=mock_db,
        ),
        patch(
            "notification_service.services.notification_processor.NotificationSenderFactory.create",
            return_value=mock_sender,
        ),
        patch(
            "notification_service.services.notification_processor.NotificationRepository",
            return_value=repository,
        ),
        patch(
            "notification_service.services.notification_processor.NotificationService",
            return_value=mock_service,
        ),
    ):
        processor = NotificationProcessor()
        await processor.process(100)

    # Assert
    repository.get_notification.assert_called_once_with(100)
    repository.get_deliveries.assert_called_once_with(100)

    mock_service.process_notification.assert_awaited_once_with(
        notification_model, deliveries
    )

    mock_db.commit.assert_called_once()
    mock_db.close.assert_called_once()
    mock_db.rollback.assert_not_called()


@pytest.mark.asyncio
async def test_process_rollback_due_to_db_error():
    mock_db = Mock()
    repository = Mock()

    notification_model = NotificationModel(
        id=100,
        user_id=1,
        subject="Test Subject",
        message="Test Message",
        status=NotificationStatusEnum.PENDING,
        idempotency_key="1",
    )
    repository.get_notification.return_value = notification_model

    deliveries = [
        NotificationDeliveryModel(
            id=11,
            notification_id=100,
            channel=ChannelEnum.EMAIL,
            recipient="test@gmail.com",
            status=DeliveryStatusEnum.PENDING,
            attempt_count=0,
            error_message=None,
        )
    ]
    repository.get_deliveries.side_effect = Exception("DB Error")

    mock_sender = Mock()

    mock_service = Mock()
    mock_service.process_notification = AsyncMock()

    with (
        patch(
            "notification_service.services.notification_processor.SessionLocal",
            return_value=mock_db,
        ),
        patch(
            "notification_service.services.notification_processor.NotificationSenderFactory.create",
            return_value=mock_sender,
        ),
        patch(
            "notification_service.services.notification_processor.NotificationRepository",
            return_value=repository,
        ),
        patch(
            "notification_service.services.notification_processor.NotificationService",
            return_value=mock_service,
        ),
    ):
        processor = NotificationProcessor()
        with pytest.raises(Exception, match="DB Error"):
            await processor.process(100)

    # Assert
    repository.get_notification.assert_called_once_with(100)
    repository.get_deliveries.assert_called_once_with(100)

    mock_service.process_notification.assert_not_awaited()

    mock_db.commit.assert_not_called()
    mock_db.close.assert_called_once()
    mock_db.rollback.assert_called_once()
