"""SQLAlchemy models for notifications and their channel deliveries."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from notification_service.database import Base
from notification_service.enums import (
    ChannelEnum,
    DeliveryStatusEnum,
    NotificationStatusEnum,
)


class NotificationModel(Base):
    """Persisted representation of a notification request."""

    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    subject: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(String(1000))
    status: Mapped[NotificationStatusEnum] = mapped_column(
        Enum(NotificationStatusEnum),
        default=NotificationStatusEnum.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )


class NotificationDeliveryModel(Base):
    """Persisted representation of deliveries for a specific notification channel."""

    __tablename__ = "notification_deliveries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notification_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("notifications.id")
    )
    channel: Mapped[ChannelEnum] = mapped_column(Enum(ChannelEnum))
    recipient: Mapped[str] = mapped_column(String(250))
    status: Mapped[DeliveryStatusEnum] = mapped_column(
        Enum(DeliveryStatusEnum),
        default=DeliveryStatusEnum.PENDING,
    )
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
