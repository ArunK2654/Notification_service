from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from notification_service.auth.jwt import decode_access_token
from notification_service.auth.models import CurrentUser
from notification_service.enums import UserRoleEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> CurrentUser:
    try:
        return decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        ) from exc


def ensure_notification_access(
    current_user: CurrentUser,
    notification_user_id: int,
) -> None:
    if current_user.role == UserRoleEnum.ADMIN:
        return

    if current_user.user_id != notification_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this notification",
        )
