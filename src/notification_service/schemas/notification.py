from pydantic import BaseModel

class NotificationRequest(BaseModel):
    user_id: int
    channels: list[str]
    subject: str
    message: str