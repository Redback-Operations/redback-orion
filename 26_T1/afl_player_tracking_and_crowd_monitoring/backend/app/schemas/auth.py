from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    username: str
    email: EmailStr
    role: str
    created_at: datetime


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: Optional[UserResponse] = None
    expires_in: int







