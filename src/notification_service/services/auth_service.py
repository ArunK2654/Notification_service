from notification_service.auth.hashing import hash_password, verify_password
from notification_service.auth.jwt import create_access_token
from notification_service.core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from notification_service.core.logging import log_execution, logger
from notification_service.models.user import UserModel
from notification_service.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    @log_execution
    def register_user(self, email: str, password: str) -> UserModel:
        existing_user = self.user_repository.find_by_email(email)

        if existing_user:
            raise UserAlreadyExistsError(f"User with email {email} already exists")

        user = UserModel(email=email, password_hash=hash_password(password))
        logger.info("Registering new user")
        try:
            self.user_repository.create(user)
            self.user_repository.commit()

            logger.info("User registered successfully with id=%s", user.id)
        except Exception:
            self.user_repository.rollback()
            raise

        return user

    @log_execution
    def login_user(self, email: str, password: str) -> str:
        user = self.user_repository.find_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        if not user.is_active:
            raise InvalidCredentialsError("User account is inactive")

        return create_access_token(user_id=user.id, role=user.role)
