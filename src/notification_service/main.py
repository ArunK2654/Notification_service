from fastapi import FastAPI

from notification_service.api.auth import auth_router
from notification_service.api.notification import router
from notification_service.core.exception_handlers import (
    invalid_credentials_handler,
    unexpected_exception_handler,
    user_already_exists_handler,
)
from notification_service.core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from notification_service.core.logging import configure_logging

configure_logging()
app = FastAPI()

app.include_router(router)
app.include_router(auth_router)
app.add_exception_handler(UserAlreadyExistsError, user_already_exists_handler)
app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)
app.add_exception_handler(
    Exception,
    unexpected_exception_handler,
)
