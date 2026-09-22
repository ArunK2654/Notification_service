class ApplicationError(Exception):
    """Base exception for expected application errors."""


class NotificationError(ApplicationError):
    pass


class EmailDeliveryError(NotificationError):
    pass


class SMSDeliveryError(NotificationError):
    pass


class PushDeliveryError(NotificationError):
    pass


class UserAlreadyExistsError(ApplicationError):
    """Raised when attempting to create a user with an existing email."""


class InvalidCredentialsError(ApplicationError):
    """Raised when authentication credentials are invalid."""


class InvalidJWTError(ApplicationError):
    """Raised when a JWT cannot be trusted."""
