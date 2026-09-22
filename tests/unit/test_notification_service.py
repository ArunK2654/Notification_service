from unittest.mock import Mock, ANY, AsyncMock, call

import pytest

from notification_service.repositories.notification_repository import (
    NotificationRepository,
)
from notification_service.services.notification_service import NotificationService

from notification_service.models.notification import NotificationModel

from notification_service.schemas.notification import (
    EmailChannelRequest,
    NotificationRequest,
    NotificationChannelRequest,
)

from notification_service.enums import (
    ChannelEnum,
    NotificationStatusEnum,
    DeliveryStatusEnum,
)
from pydantic import ValidationError

from notification_service.services.domain import Notification

from notification_service.senders.email import EmailSender

from notification_service.senders.sms import SMSSender
from notification_service.models.notification import NotificationDeliveryModel
from notification_service.enums import DeliveryStatusEnum

from notification_service.senders.base import NotificationSender

from notification_service.core.exceptions import NotificationError


def test_create_notification_happy_path() -> None:
    # Arrange
    repository = Mock(spec=NotificationRepository)

    service = NotificationService(
        notification_repository=repository, notification_senders=[]
    )
    repository.get_by_idempotency_key.return_value = None

    request = NotificationRequest(
        channels=[
            {"channel": "email", "recipient": "test@gmail.com"},
            {"channel": "sms", "recipient": "9876543210"},
        ],
        subject="Test Subject",
        message="Test Message",
    )

    def fake_create_notification(model):
        model.id = 100
        return model

    repository.create_notification.side_effect = fake_create_notification

    # Act
    (model_value, boolean_value) = service.create_notification(
        request=request, current_user_id=1, idempotency_key="1"
    )

    # Assert
    assert model_value.user_id == 1
    assert model_value.subject == "Test Subject"
    assert model_value.message == "Test Message"
    assert model_value.status == NotificationStatusEnum.PENDING
    assert model_value.idempotency_key == "1"
    assert boolean_value is True

    repository.get_by_idempotency_key.assert_called_once_with("1")
    repository.create_notification.assert_called_once()
    assert repository.create_delivery.call_count == 2
    repository.create_delivery.assert_any_call(
        notification_id=100, channel_request=request.channels[0]
    )
    repository.commit.assert_called_once()
    repository.rollback.assert_not_called()


def test_create_notification_with_invalid_channel() -> None:
    # Assert request Validation
    with pytest.raises(ValidationError):
        NotificationRequest(
            channels=[{"channel": "Whatsapp", "recipient": "9876543210"}],
            subject="Test Subject",
            message="Test Message",
        )


def test_create_notification_with_duplicate_channel() -> None:
    # Assert request Validation
    with pytest.raises(ValidationError):
        NotificationRequest(
            channels=[
                {"channel": "SMS", "recipient": "9876543210"},
                {"channel": "SMS", "recipient": "9876543210"},
            ],
            subject="Test Subject",
            message="Test Message",
        )


def test_create_notification_with_existing_idempotency_key() -> None:
    # Arrange
    repository = Mock(spec=NotificationRepository)
    service = NotificationService(
        notification_repository=repository, notification_senders=[]
    )

    existing_notification = NotificationModel(
        id=100,
        user_id=1,
        subject="Test Subject",
        message="Test Message",
        status=NotificationStatusEnum.PENDING,
        idempotency_key="1",
    )

    repository.get_by_idempotency_key.return_value = existing_notification

    request = NotificationRequest(
        channels=[{"channel": "email", "recipient": "test@gmail.com"}],
        subject="Test Subject",
        message="Test Message",
    )

    # Act
    (model_value, boolean_value) = service.create_notification(
        request=request, current_user_id=1, idempotency_key="1"
    )

    # Assert
    assert model_value.id == 100
    assert model_value.subject == "Test Subject"
    assert model_value.message == "Test Message"
    assert model_value.status == NotificationStatusEnum.PENDING
    assert model_value.idempotency_key == "1"
    assert boolean_value is False
    repository.get_by_idempotency_key.assert_called_once_with("1")
    repository.create_notification.assert_not_called()
    repository.create_delivery.assert_not_called()
    repository.rollback.assert_not_called()


def test_create_notification_rollback_due_to_db_error() -> None:
    # Arrange
    repository = Mock(spec=NotificationRepository)
    service = NotificationService(
        notification_repository=repository, notification_senders=[]
    )
    repository.get_by_idempotency_key.return_value = None
    request = NotificationRequest(
        channels=[
            {"channel": "email", "recipient": "test@gmail.com"},
            {"channel": "sms", "recipient": "9876543210"},
        ],
        subject="Test Subject",
        message="Test Message",
    )

    repository.create_notification.side_effect = Exception("DB Error")

    # Act
    with pytest.raises(Exception, match="DB Error"):
        service.create_notification(
            request=request, current_user_id=1, idempotency_key="1"
        )

    # Assert
    repository.get_by_idempotency_key.assert_called_once_with("1")
    repository.create_notification.assert_called_once()
    repository.create_delivery.assert_not_called()
    repository.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_process_notification_happy_path() -> None:
    # Arrange
    repository = Mock(spec=NotificationRepository)
    email_sender = Mock(spec=NotificationSender)
    email_sender.channel = ChannelEnum.EMAIL
    email_sender.send = AsyncMock()

    sms_sender = Mock(spec=NotificationSender)
    sms_sender.channel = ChannelEnum.SMS
    sms_sender.send = AsyncMock()

    notification_senders = [email_sender, sms_sender]
    notification_model = NotificationModel(
        id=100,
        user_id=1,
        subject="Test Subject",
        message="Test Message",
        status=NotificationStatusEnum.PENDING,
        idempotency_key="1",
    )
    deliveries = [
        NotificationDeliveryModel(
            id=11,
            notification_id=100,
            channel=ChannelEnum.EMAIL,
            recipient="test@gmail.com",
            status=DeliveryStatusEnum.PENDING,
            attempt_count=0,
            error_message=None,
        ),
        NotificationDeliveryModel(
            id=12,
            notification_id=100,
            channel=ChannelEnum.SMS,
            recipient="9876543210",
            status=DeliveryStatusEnum.PENDING,
            attempt_count=0,
            error_message=None,
        ),
    ]
    service = NotificationService(
        notification_repository=repository, notification_senders=notification_senders
    )

    def fake_update_delivery(
        delivery: NotificationDeliveryModel,
        status: DeliveryStatusEnum,
        error_message: str | None = None,
    ) -> NotificationDeliveryModel:
        delivery.status = status
        delivery.error_message = error_message
        return delivery

    repository.update_delivery.side_effect = fake_update_delivery

    # Act
    await service.process_notification(
        notification_model=notification_model, deliveries=deliveries
    )

    # Assert
    email_sender.send.assert_awaited_once()
    sms_sender.send.assert_awaited_once()

    assert repository.update_delivery.call_count == 2
    repository.update_delivery.assert_has_calls(
        [
            call(delivery=deliveries[0], status=DeliveryStatusEnum.SENT),
            call(delivery=deliveries[1], status=DeliveryStatusEnum.SENT),
        ]
    )

    repository.update_notification_status.assert_called_once()


@pytest.mark.asyncio
async def test_process_notification_failure_due_to_notification_error() -> None:
    repository = Mock(spec=NotificationRepository)
    email_sender = Mock(spec=NotificationSender)
    email_sender.channel = ChannelEnum.EMAIL
    email_sender.send = AsyncMock(
        side_effect=NotificationError("Email Delivery Failed")
    )

    notification_senders = [email_sender]
    notification_model = NotificationModel(
        id=100,
        user_id=1,
        subject="Test Subject",
        message="Test Message",
        status=NotificationStatusEnum.PENDING,
        idempotency_key="1",
    )
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
    service = NotificationService(
        notification_repository=repository, notification_senders=notification_senders
    )

    def fake_update_delivery(
        delivery: NotificationDeliveryModel,
        status: DeliveryStatusEnum,
        error_message: str | None = None,
    ) -> NotificationDeliveryModel:
        delivery.status = status
        delivery.error_message = error_message
        return delivery

    repository.update_delivery.side_effect = fake_update_delivery

    # Act
    await service.process_notification(
        notification_model=notification_model, deliveries=deliveries
    )

    # Assert
    email_sender.send.assert_awaited_once()
    assert repository.update_delivery.call_count == 1
    repository.update_delivery.assert_called_once_with(
        delivery=deliveries[0],
        status=DeliveryStatusEnum.FAILED,
        error_message="Email Delivery Failed",
    )
    repository.update_notification_status.assert_called_once_with(
        notification=notification_model, status=NotificationStatusEnum.FAILED
    )


def test_determine_notification_status_pending() -> None:
    repository = Mock(spec=NotificationRepository)
    service = NotificationService(
        notification_repository=repository, notification_senders=[]
    )
    deliveries = [
        NotificationDeliveryModel(
            id=11,
            notification_id=100,
            channel=ChannelEnum.EMAIL,
            recipient="test@gmail.com",
            status=DeliveryStatusEnum.PENDING,
            attempt_count=0,
            error_message=None,
        ),
        NotificationDeliveryModel(
            id=12,
            notification_id=100,
            channel=ChannelEnum.SMS,
            recipient="9876543210",
            status=DeliveryStatusEnum.SENT,
            attempt_count=0,
            error_message=None,
        ),
    ]
    result = service.determine_notification_status(deliveries=deliveries)
    assert result == NotificationStatusEnum.PENDING


def test_determine_notification_status_completed() -> None:
    repository = Mock(spec=NotificationRepository)
    service = NotificationService(
        notification_repository=repository, notification_senders=[]
    )
    deliveries = [
        NotificationDeliveryModel(
            id=11,
            notification_id=100,
            channel=ChannelEnum.EMAIL,
            recipient="test@gmail.com",
            status=DeliveryStatusEnum.SENT,
            attempt_count=0,
            error_message=None,
        ),
        NotificationDeliveryModel(
            id=12,
            notification_id=100,
            channel=ChannelEnum.SMS,
            recipient="9876543210",
            status=DeliveryStatusEnum.SENT,
            attempt_count=0,
            error_message=None,
        ),
    ]
    result = service.determine_notification_status(deliveries=deliveries)
    assert result == NotificationStatusEnum.COMPLETED


def test_determine_notification_status_failed() -> None:
    repository = Mock(spec=NotificationRepository)
    service = NotificationService(
        notification_repository=repository, notification_senders=[]
    )
    deliveries = [
        NotificationDeliveryModel(
            id=11,
            notification_id=100,
            channel=ChannelEnum.EMAIL,
            recipient="test@gmail.com",
            status=DeliveryStatusEnum.FAILED,
            attempt_count=0,
            error_message=None,
        ),
        NotificationDeliveryModel(
            id=12,
            notification_id=100,
            channel=ChannelEnum.SMS,
            recipient="9876543210",
            status=DeliveryStatusEnum.FAILED,
            attempt_count=0,
            error_message=None,
        ),
    ]
    result = service.determine_notification_status(deliveries=deliveries)
    assert result == NotificationStatusEnum.FAILED


def test_determine_notification_status_partially_failed() -> None:
    repository = Mock(spec=NotificationRepository)
    service = NotificationService(
        notification_repository=repository, notification_senders=[]
    )
    deliveries = [
        NotificationDeliveryModel(
            id=11,
            notification_id=100,
            channel=ChannelEnum.EMAIL,
            recipient="test@gmail.com",
            status=DeliveryStatusEnum.SENT,
            attempt_count=0,
            error_message=None,
        ),
        NotificationDeliveryModel(
            id=12,
            notification_id=100,
            channel=ChannelEnum.SMS,
            recipient="9876543210",
            status=DeliveryStatusEnum.FAILED,
            attempt_count=0,
            error_message=None,
        ),
    ]
    result = service.determine_notification_status(deliveries=deliveries)
    assert result == NotificationStatusEnum.PARTIALLY_FAILED


def test_determine_notification_status_with_no_deliveries() -> None:
    repository = Mock(spec=NotificationRepository)
    service = NotificationService(
        notification_repository=repository, notification_senders=[]
    )
    deliveries = []
    with pytest.raises(NotificationError):
        service.determine_notification_status(deliveries=deliveries)
