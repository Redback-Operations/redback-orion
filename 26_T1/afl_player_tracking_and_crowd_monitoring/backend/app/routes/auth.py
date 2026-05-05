from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, RefreshToken
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, UserResponse, RefreshRequest, LogoutRequest
from app.auth.hashing import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token, decode_refresh_token
from app.auth.dependencies import get_current_user
from app.config import JWT_EXPIRE_MINUTES

router = APIRouter()


def _issue_tokens(user: User, db: Session) -> dict:
    token_data = {
        "sub": str(user.user_id),
        "email": user.email,
        "role": user.role
    }
    access_token = create_access_token(token_data)
    refresh_token_str, expires_at = create_refresh_token(token_data)

    db_refresh = RefreshToken(
        user_id=user.user_id,
        token=refresh_token_str,
        expires_at=expires_at
    )
    db.add(db_refresh)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRE_MINUTES * 60,
        "user": user
    }


@router.post("/register", response_model=AuthResponse)
def register(user: RegisterRequest, db: Session = Depends(get_db)):
    try:
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=409, detail="Email already registered")
        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(status_code=409, detail="Username already taken")

        new_user = User(
            email=user.email,
            username=user.username,
            password=hash_password(user.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return _issue_tokens(new_user, db)

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error during registration")


@router.post("/login", response_model=AuthResponse)
def login(user: LoginRequest, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user or not verify_password(user.password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        return _issue_tokens(db_user, db)

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error during login")


@router.post("/refresh", response_model=AuthResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_refresh_token(body.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == body.refresh_token,
        RefreshToken.is_active == True
    ).first()

    if not db_token:
        raise HTTPException(status_code=401, detail="Refresh token has been revoked")

    if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        db_token.is_active = False
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token has expired")

    user = db.query(User).filter(User.user_id == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_token.is_active = False
    db.commit()

    return _issue_tokens(user, db)


@router.post("/logout")
def logout(body: LogoutRequest, db: Session = Depends(get_db)):
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == body.refresh_token
    ).first()

    if db_token:
        db_token.is_active = False
        db.commit()

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.user_id == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error retrieving user")