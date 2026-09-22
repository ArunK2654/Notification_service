from notification_service.auth.hashing import (
    hash_password,
    verify_password,
)


def test_password_hash_is_not_plain_text() -> None:
    password = "TestPassword123"

    hashed_password = hash_password(password)

    assert hashed_password != password


def test_verify_password_with_correct_password() -> None:
    password = "TestPassword123"

    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password) is True


def test_verify_password_with_wrong_password() -> None:
    password = "TestPassword123"

    hashed_password = hash_password(password)

    assert verify_password("WrongPassword123", hashed_password) is False
