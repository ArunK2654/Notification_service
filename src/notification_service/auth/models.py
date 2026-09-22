from dataclasses import dataclass

from notification_service.enums import UserRoleEnum


@dataclass
class CurrentUser:
    user_id: int
    role: UserRoleEnum
