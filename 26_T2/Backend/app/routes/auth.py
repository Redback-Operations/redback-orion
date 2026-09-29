from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, RefreshToken, Player

import os

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    UserResponse,
    RefreshRequest,
    LogoutRequest,
    UpdateRoleRequest,
    AdminCreateUserRequest,
    UpdatePlayerLinkRequest,
    ResetPasswordRequest,
    UserRole,
    AdminCreateRole,
    ForgotPasswordRequest,
    AdminResetPasswordRequest
)

from app.auth.security import (
    create_password_reset_token,
    verify_password_reset_token,
)

from app.auth.email import send_password_reset_email


from app.auth.hashing import hash_password, verify_password
from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.auth.dependencies import get_current_user
from app.config import JWT_EXPIRE_MINUTES


router = APIRouter()


def _issue_tokens(user: User, db: Session) -> dict:
    token_data = {
        "sub": str(user.user_id),
        "email": user.email,
        "role": user.role,
    }

    access_token = create_access_token(token_data)

    refresh_token_str, expires_at = create_refresh_token(token_data)

    db_refresh = RefreshToken(
        user_id=user.user_id,
        token=refresh_token_str,
        expires_at=expires_at,
    )

    db.add(db_refresh)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRE_MINUTES * 60,
        "user": user,
    }


@router.post("/register", response_model=AuthResponse)
def register(
    user: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(
                status_code=409,
                detail="Email already registered",
            )

        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(
                status_code=409,
                detail="Username already taken",
            )

        # Public registration always creates a normal user
        new_user = User(
            email=user.email,
            username=user.username,
            password=hash_password(user.password),
            role=UserRole.USER.value,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return _issue_tokens(new_user, db)

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error during registration",
        )


@router.post("/login", response_model=AuthResponse)
def login(
    user: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        db_user = (
            db.query(User)
            .filter(User.email == user.email)
            .first()
        )

        if not db_user or not verify_password(
            user.password,
            db_user.password,
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )

        return _issue_tokens(db_user, db)

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error during login",
        )


@router.post("/refresh", response_model=AuthResponse)
def refresh(
    body: RefreshRequest,
    db: Session = Depends(get_db),
):
    payload = decode_refresh_token(body.refresh_token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
        )

    db_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == body.refresh_token,
            RefreshToken.is_active == True,
        )
        .first()
    )

    if not db_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token has been revoked",
        )

    if (
        db_token.expires_at.replace(tzinfo=timezone.utc)
        < datetime.now(timezone.utc)
    ):
        db_token.is_active = False
        db.commit()

        raise HTTPException(
            status_code=401,
            detail="Refresh token has expired",
        )

    user = (
        db.query(User)
        .filter(User.user_id == db_token.user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    db_token.is_active = False
    db.commit()

    return _issue_tokens(user, db)


@router.post("/logout")
def logout(
    body: LogoutRequest,
    db: Session = Depends(get_db),
):
    db_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == body.refresh_token)
        .first()
    )

    if db_token:
        db_token.is_active = False
        db.commit()

    return {
        "message": "Logged out successfully"
    }


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        user = (
            db.query(User)
            .filter(User.user_id == current_user["sub"])
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        return user

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error retrieving user",
        )


@router.put(
    "/users/{user_id}/role",
    response_model=UserResponse,
)
def update_user_role(
    user_id: str,
    request: UpdateRoleRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user role - admin only."""

    admin = (
        db.query(User)
        .filter(User.user_id == current_user["sub"])
        .first()
    )

    if not admin or admin.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=403,
            detail="Only admins can update user roles",
        )

    target_user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not target_user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    target_user.role = request.role.value

    db.commit()
    db.refresh(target_user)

    return target_user


# ---------------------------------------------------------
# TASK 3 - ADMIN CREATE PLAYER / COACH ACCOUNT
# ---------------------------------------------------------

@router.post(
    "/admin/users",
    response_model=UserResponse,
    status_code=201,
)
def admin_create_user(
    request: AdminCreateUserRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Admin-only endpoint for creating Player or Coach accounts.
    """

    # Check that requester exists and is an admin
    admin = (
        db.query(User)
        .filter(User.user_id == current_user["sub"])
        .first()
    )

    if not admin or admin.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=403,
            detail="Only admins can create player or coach accounts",
        )

    # Check email uniqueness
    existing_email = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    # Check username uniqueness
    existing_username = (
        db.query(User)
        .filter(User.username == request.username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=409,
            detail="Username already taken",
        )

    player_id = None

    # Player accounts must be linked to an existing player
    if request.role == AdminCreateRole.PLAYER:

        player = (
            db.query(Player)
            .filter(Player.id == request.player_id)
            .first()
        )

        if not player:
            raise HTTPException(
                status_code=404,
                detail="Player not found",
            )

        player_id = request.player_id

        # Prevent the same player from being linked
        # to multiple user accounts
        existing_player_account = (
            db.query(User)
            .filter(User.player_id == request.player_id)
            .first()
        )

        if existing_player_account:
            raise HTTPException(
                status_code=409,
                detail="This player is already linked to a user account",
            )

    try:
        new_user = User(
            username=request.username,
            email=request.email,
            password=hash_password(request.password),
            role=request.role.value,
            player_id=player_id,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Internal server error while creating user",
        )


@router.get("/users")
def list_users(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all users - admin only."""

    admin = (
        db.query(User)
        .filter(User.user_id == current_user["sub"])
        .first()
    )

    if not admin or admin.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=403,
            detail="Only admins can view all users",
        )

    users = db.query(User).all()

    return {
        "users": users,
        "total": len(users),
    }


@router.get("/users/{user_id}")
def get_user_by_id(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Users can view themselves.
    Admins can view any user.
    """

    if current_user["sub"] != user_id:

        requester = (
            db.query(User)
            .filter(User.user_id == current_user["sub"])
            .first()
        )

        if not requester or requester.role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized",
            )

    target_user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not target_user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return target_user


@router.put("/admin/users/{user_id}/reset-password")
def admin_reset_password(
    user_id: str,
    request: AdminResetPasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Admin-only endpoint to reset another user's password.
    """

    # Check requester is an admin
    admin = (
        db.query(User)
        .filter(User.user_id == current_user["sub"])
        .first()
    )

    if not admin or admin.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=403,
            detail="Only admins can reset user passwords",
        )

    # Find target user
    target_user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not target_user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    try:
        # Never store the raw password
        target_user.password = hash_password(request.new_password)

        db.commit()

        return {
            "message": "Password reset successfully",
            "user_id": str(target_user.user_id),
        }

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Internal server error while resetting password",
        )

@router.put("/admin/users/{user_id}/player-link", response_model=UserResponse)
def update_player_link(
    user_id: str,
    request: UpdatePlayerLinkRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check requester is admin
    admin = (
        db.query(User)
        .filter(User.user_id == current_user["sub"])
        .first()
    )

    if not admin or admin.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=403,
            detail="Only admins can update player linkage",
        )

    # Find target user
    target_user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not target_user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # If linking to a player, verify player exists
    if request.player_id is not None:
        player = (
            db.query(Player)
            .filter(Player.id == request.player_id)
            .first()
        )

        if not player:
            raise HTTPException(
                status_code=404,
                detail="Player not found",
            )

        # Prevent same player being linked to another account
        existing_link = (
            db.query(User)
            .filter(
                User.player_id == request.player_id,
                User.user_id != target_user.user_id,
            )
            .first()
        )

        if existing_link:
            raise HTTPException(
                status_code=409,
                detail="This player is already linked to another user",
            )

    target_user.player_id = request.player_id

    db.commit()
    db.refresh(target_user)

    return target_user

@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    # Important:
    # don't tell people whether an email exists in the database
    if not user:
        return {
            "message": (
                "If an account exists with this email, "
                "a password reset link has been sent."
            )
        }

    token = create_password_reset_token(
        str(user.user_id)
    )

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000",
    )

    reset_link = (
        f"{frontend_url}/reset-password"
        f"?token={token}"
    )

    try:
        send_password_reset_email(
            email=user.email,
            reset_link=reset_link,
        )

    except Exception as e:
        print("Password reset email error:", e)

        raise HTTPException(
            status_code=500,
            detail="Unable to send password reset email",
        )

    return {
        "message": (
            "If an account exists with this email, "
            "a password reset link has been sent."
        )
    }

@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        user_id = verify_password_reset_token(
            request.token
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Reset link is invalid or has expired",
        )

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    try:
        user.password = hash_password(
            request.new_password
        )

        db.commit()

        return {
            "message": "Password reset successfully"
        }

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to reset password",
        )