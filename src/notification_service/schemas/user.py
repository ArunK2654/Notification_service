from pydantic import BaseModel, EmailStr, Field

from notification_service.enums import UserRoleEnum


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RegisterResponse(BaseModel):
    email: EmailStr
    id: int = Field(gt=0)
    role: UserRoleEnum


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
