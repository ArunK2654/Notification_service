from dataclasses import dataclass


@dataclass
class NotificationEvent:
    event_id: str
    notification_id: int
    channel: str
    recipient: str
    message: str