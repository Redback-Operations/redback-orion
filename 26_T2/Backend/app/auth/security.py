import os
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError

PASSWORD_RESET_SECRET = os.getenv("PASSWORD_RESET_SECRET")
if not PASSWORD_RESET_SECRET:
    raise RuntimeError(
        "PASSWORD_RESET_SECRET environment variable is not configured"
    )

ALGORITHM = "HS256"

print("PASSWORD_RESET_SECRET loaded:", bool(PASSWORD_RESET_SECRET))


def create_password_reset_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    payload = {
        "sub": str(user_id),
        "purpose": "password_reset",
        "exp": expire,
    }

    return jwt.encode(
        payload,
        PASSWORD_RESET_SECRET,
        algorithm=ALGORITHM,
    )


def verify_password_reset_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            PASSWORD_RESET_SECRET,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")
        purpose = payload.get("purpose")

        if not user_id:
            raise ValueError("Missing user ID")

        if purpose != "password_reset":
            raise ValueError("Invalid token purpose")

        return user_id

    except JWTError:
        raise ValueError("Invalid or expired reset token")