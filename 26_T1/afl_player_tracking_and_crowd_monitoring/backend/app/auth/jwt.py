from datetime import (
    datetime,
    timedelta,
    timezone,
)

from fastapi import (
    HTTPException,
    status,
)

from jose import (
    JWTError,
    jwt,
)

from app.config import (
    JWT_ALGORITHM,
    JWT_EXPIRE_MINUTES,
    JWT_SECRET_KEY,
)

REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(
    data: dict,
) -> str:
    payload = data.copy()

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=(JWT_EXPIRE_MINUTES))

    payload.update(
        {
            "exp": expires_at,
            "type": "access",
        }
    )

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def create_refresh_token(
    data: dict,
) -> tuple[
    str,
    datetime,
]:
    payload = data.copy()

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=(REFRESH_TOKEN_EXPIRE_DAYS)
    )

    payload.update(
        {
            "exp": expires_at,
            "type": "refresh",
        }
    )

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    return (
        token,
        expires_at.replace(tzinfo=None),
    )


def decode_access_token(
    token: str,
) -> dict:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

    except JWTError as exc:
        raise HTTPException(
            status_code=(status.HTTP_401_UNAUTHORIZED),
            detail=("Could not validate " "access token"),
        ) from exc

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=(status.HTTP_401_UNAUTHORIZED),
            detail=("Invalid access token"),
        )

    return payload


def decode_refresh_token(
    token: str,
) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

    except JWTError:
        return None

    if payload.get("type") != "refresh":
        return None

    return payload
