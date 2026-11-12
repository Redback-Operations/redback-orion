from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, model_validator


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    PLAYER = "player"
    COACH = "coach"


# Only roles that can be created using the admin create-user endpoint
class AdminCreateRole(str, Enum):
    PLAYER = "player"
    COACH = "coach"


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[UserRole] = UserRole.USER


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    username: str
    email: EmailStr
    role: UserRole
    player_id: Optional[int] = None
    created_at: datetime


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: Optional[UserResponse] = None
    expires_in: int


class UpdateRoleRequest(BaseModel):
    role: UserRole


class AdminCreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: AdminCreateRole
    player_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_player_id(self):
        if self.role == AdminCreateRole.PLAYER and self.player_id is None:
            raise ValueError("player_id is required when role is player")

        return self

class AdminResetPasswordRequest(BaseModel):
    new_password: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class UpdatePlayerLinkRequest(BaseModel):
    player_id: Optional[int] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr
