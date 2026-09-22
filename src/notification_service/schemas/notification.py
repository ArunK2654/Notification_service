from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, Field, ValidationError, model_validator

from notification_service.enums import ChannelEnum, NotificationStatusEnum


class EmailChannelRequest(BaseModel):
    channel: Literal[ChannelEnum.EMAIL]
    recipient: EmailStr


class SMSChannelRequest(BaseModel):
    channel: Literal[ChannelEnum.SMS]
    recipient: str = Field(pattern=r"^\d{10}$")


NotificationChannelRequest = Annotated[
    EmailChannelRequest | SMSChannelRequest,
    Field(discriminator="channel"),
]


class NotificationRequest(BaseModel):
    channels: list[NotificationChannelRequest] = Field(min_length=1, max_length=2)
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def validate_unique_channels(self) -> "NotificationRequest":
        channels = [channel.channel for channel in self.channels]
        if len(channels) != len(set(channels)):
            raise ValidationError("Duplicate channels are not allowed")
        return self


class NotificationResponse(BaseModel):
    notification_id: int = Field(gt=0)
    message: str = Field(min_length=1, max_length=200)


class NotificationDetailResponse(BaseModel):
    id: int
    subject: str
    message: str
    status: NotificationStatusEnum
    created_at: datetime


class NotificationListResponse(BaseModel):
    notifications: list[NotificationDetailResponse]
