"""
Enumeration types used across the notification service.

ChannelEnum: Supported notification delivery channels.
NotificationStatusEnum: Overall status of a notification.
DeliveryStatusEnum: Status of an individual channel delivery.
"""

from enum import StrEnum


class ChannelEnum(StrEnum):
    EMAIL = "email"
    SMS = "sms"


class NotificationStatusEnum(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    PARTIALLY_FAILED = "partially_failed"
    FAILED = "failed"


class DeliveryStatusEnum(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class UserRoleEnum(StrEnum):
    ADMIN = "admin"
    USER = "user"
