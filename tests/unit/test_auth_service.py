from unittest.mock import Mock, patch

import pytest

from notification_service.core.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
)
from notification_service.models.user import UserModel
from notification_service.repositories.user_repository import UserRepository
from notification_service.services.auth_service import AuthService

from notification_service.enums import UserRoleEnum

from notification_service.auth.hashing import verify_password


def test_register_user_happy_path() -> None:
    # Arrange
    repository = Mock(spec=UserRepository)
    repository.find_by_email.return_value = None
    service = AuthService(user_repository=repository)

    # Act
    result = service.register_user(email="test@gmail.com", password="Test1234")

    # Assert
    assert result.email == "test@gmail.com"
    assert result.password_hash != "Test1234"

    repository.find_by_email.assert_called_once_with("test@gmail.com")
    repository.create.assert_called_once_with(result)
    repository.commit.assert_called_once()
    repository.rollback.assert_not_called()


def test_register_user_when_email_exists() -> None:
    # Arrange
    repository = Mock(spec=UserRepository)
    existing_user = UserModel(email="test@gmail.com", password_hash="hashed_password")
    repository.find_by_email.return_value = existing_user
    service = AuthService(user_repository=repository)

    # Act
    with pytest.raises(UserAlreadyExistsError):
        service.register_user(email="test@gmail.com", password="Test1234")

    # Assert
    repository.find_by_email.assert_called_once_with("test@gmail.com")
    repository.create.assert_not_called()
    repository.commit.assert_not_called()
    repository.rollback.assert_not_called()


def test_register_user_rollback_user_on_db_error() -> None:
    # Arrange
    repository = Mock(spec=UserRepository)
    repository.find_by_email.return_value = None
    service = AuthService(user_repository=repository)
    repository.create.side_effect = Exception("DB error")

    # Act
    with pytest.raises(Exception):
        service.register_user(email="test@gmail.com", password="Test1234")

    # Assert
    repository.find_by_email.assert_called_once_with("test@gmail.com")
    repository.create.assert_called_once()
    repository.commit.assert_not_called()
    repository.rollback.assert_called_once()


def test_login_user_happy_path() -> None:
    repository = Mock(spec=UserRepository)
    user_model = UserModel(
        id=100,
        email="test@gmail.com",
        password_hash="hashed_password",
        role=UserRoleEnum.USER,
        is_active=True,
    )
    repository.find_by_email.return_value = user_model
    service = AuthService(user_repository=repository)

    with patch(
        "notification_service.services.auth_service.verify_password", return_value=True
    ) as mock_verify_password:
        token = service.login_user(email="test@gmail.com", password="test123")

    assert token is not None
    repository.find_by_email.assert_called_once_with("test@gmail.com")
    mock_verify_password.assert_called_once_with("test123", "hashed_password")


def test_login_user_when_password_mismatch() -> None:
    repository = Mock(spec=UserRepository)
    user_model = UserModel(
        id=100,
        email="test@gmail.com",
        password_hash="hashed_password",
        role=UserRoleEnum.USER,
        is_active=True,
    )
    repository.find_by_email.return_value = user_model
    service = AuthService(user_repository=repository)

    with patch(
        "notification_service.services.auth_service.verify_password", return_value=False
    ):
        with pytest.raises(InvalidCredentialsError, match="Invalid email or password"):
            service.login_user(email="test@gmail.com", password="test123")


def test_login_user_when_user_not_exist() -> None:
    repository = Mock(spec=UserRepository)
    repository.find_by_email.return_value = None
    service = AuthService(user_repository=repository)

    with pytest.raises(InvalidCredentialsError, match="Invalid email or password"):
        service.login_user(email="test@gmail.com", password="test123")


def test_login_user_when_user_not_active() -> None:
    repository = Mock(spec=UserRepository)
    user_model = UserModel(
        id=100,
        email="test@gmail.com",
        password_hash="hashed_password",
        role=UserRoleEnum.USER,
        is_active=False,
    )
    repository.find_by_email.return_value = user_model
    service = AuthService(user_repository=repository)

    with patch(
        "notification_service.services.auth_service.verify_password", return_value=True
    ):
        with pytest.raises(InvalidCredentialsError, match="User account is inactive"):
            service.login_user(email="test@gmail.com", password="test123")
