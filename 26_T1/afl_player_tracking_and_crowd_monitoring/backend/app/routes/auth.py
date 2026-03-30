from fastapi import APIRouter
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse

router = APIRouter()

@router.post("/register", response_model=AuthResponse) # Mock register endpoint
def register(user: RegisterRequest):
    return {
        "access_token": "mock_token",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "username": user.username,
            "email": user.email
        }
    }

@router.post("/login", response_model=AuthResponse) # Mock login endpoint
def login(user: LoginRequest):
    return {
        "access_token": "mock_token",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "username": "test_user",
            "email": user.email
        }
    }