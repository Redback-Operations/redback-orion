from fastapi import APIRouter
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse

router = APIRouter()

@router.post("/register", response_model=AuthResponse)
def register(user: RegisterRequest):
    return {
        "access_token": "mock_token",
        "token_type": "bearer",
        "user": {
            "id": "1",
            "username": user.username,
            "email": user.email
        },
        "expires_in": 3600
    }

@router.post("/login", response_model=AuthResponse)
def login(user: LoginRequest):
    return {
        "access_token": "mock_token",
        "token_type": "bearer",
        "user": {
            "id": "1",
            "username": user.username,
            "email": f"{user.username}@example.com"
        },
        "expires_in": 3600
    }