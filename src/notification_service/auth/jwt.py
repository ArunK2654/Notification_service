from datetime import UTC, datetime, timedelta

import jwt
from jwt import InvalidTokenError

from notification_service.auth.models import CurrentUser
from notification_service.core.config import settings
from notification_service.core.exceptions import InvalidJWTError
from notification_service.enums import UserRoleEnum

SECRET_KEY: str = settings.jwt_secret_key
ALGORITHM: str = settings.jwt_algorithm
EXPIRES_IN: int = settings.jwt_access_token_expire_minutes


def create_access_token(user_id: int, role: UserRoleEnum) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=EXPIRES_IN)

    payload = {"sub": str(user_id), "role": role.value, "exp": expires_at}

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> CurrentUser:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError as exc:
        raise InvalidJWTError("Invalid or expired token") from exc

    subject = payload.get("sub")
    role = payload.get("role")

    if not isinstance(subject, str) or not isinstance(role, str):
        raise InvalidJWTError("Invalid token payload")

    try:
        user_id = int(subject)
        user_role = UserRoleEnum(role)
    except (TypeError, ValueError) as exc:
        raise InvalidJWTError("Invalid token payload") from exc

    return CurrentUser(user_id=user_id, role=user_role)
