from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from notification_service.database import db_dependency
from notification_service.repositories.user_repository import UserRepository
from notification_service.schemas.user import (
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from notification_service.services.auth_service import AuthService

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED
)
def register(request: RegisterRequest, db: db_dependency) -> RegisterResponse:
    user_repository = UserRepository(db=db)
    auth_service = AuthService(user_repository=user_repository)
    user = auth_service.register_user(email=request.email, password=request.password)
    return RegisterResponse(email=user.email, id=user.id, role=user.role)


@auth_router.post(
    "/login", response_model=LoginResponse, status_code=status.HTTP_200_OK
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
) -> LoginResponse:
    user_repository = UserRepository(db=db)
    auth_service = AuthService(user_repository=user_repository)
    token = auth_service.login_user(
        email=form_data.username, password=form_data.password
    )
    return LoginResponse(access_token=token)
