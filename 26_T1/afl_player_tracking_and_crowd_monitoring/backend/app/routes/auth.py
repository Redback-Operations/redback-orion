from datetime import datetime, timezone
import json
import secrets
from urllib.parse import urlencode

import httpx
import jwt as pyjwt
from jwt import PyJWKClient
from pydantic import BaseModel

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, RefreshToken
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    UserResponse,
    RefreshRequest,
    LogoutRequest,
)
from app.auth.hashing import (
    hash_password,
    verify_password,
)
from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.auth.dependencies import get_current_user
from app.config import (
    JWT_EXPIRE_MINUTES,
    FRONTEND_URL,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_CALLBACK_URL,
    MICROSOFT_CLIENT_ID,
    MICROSOFT_JWKS_URL,
)


router = APIRouter()


# =========================================================
# MICROSOFT REQUEST MODEL
# =========================================================

class MicrosoftAuthRequest(BaseModel):
    id_token: str


# =========================================================
# MICROSOFT ID TOKEN VERIFICATION
# =========================================================

def _verify_microsoft_id_token(
    id_token: str,
) -> dict:
    """
    Verify a Microsoft Entra ID / Microsoft account
    v2.0 ID token using Microsoft's public signing keys.

    The unverified payload is read only to obtain the
    tenant ID needed to construct the expected issuer.
    Authentication decisions are made only after full
    signature, audience, issuer and expiry validation.
    """

    if not MICROSOFT_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail=(
                "MICROSOFT_CLIENT_ID "
                "is not configured"
            ),
        )

    try:
        unverified_claims = pyjwt.decode(
            id_token,
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_iss": False,
            },
        )

        tenant_id = unverified_claims.get(
            "tid"
        )

        if not tenant_id:
            raise HTTPException(
                status_code=401,
                detail=(
                    "Microsoft token does not "
                    "contain a tenant ID"
                ),
            )

        expected_issuer = (
            "https://login.microsoftonline.com/"
            f"{tenant_id}/v2.0"
        )

        jwks_client = PyJWKClient(
            MICROSOFT_JWKS_URL,
            cache_keys=True,
        )

        signing_key = (
            jwks_client.get_signing_key_from_jwt(
                id_token
            )
        )

        claims = pyjwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=MICROSOFT_CLIENT_ID,
            issuer=expected_issuer,
            options={
                "require": [
                    "exp",
                    "iat",
                    "aud",
                    "iss",
                    "sub",
                ]
            },
        )

        return claims

    except HTTPException:
        raise

    except pyjwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Microsoft ID token has expired",
        )

    except pyjwt.InvalidAudienceError:
        raise HTTPException(
            status_code=401,
            detail=(
                "Microsoft ID token has an "
                "invalid audience"
            ),
        )

    except pyjwt.InvalidIssuerError:
        raise HTTPException(
            status_code=401,
            detail=(
                "Microsoft ID token has an "
                "invalid issuer"
            ),
        )

    except pyjwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Microsoft ID token",
        )

    except Exception:
        raise HTTPException(
            status_code=401,
            detail=(
                "Unable to verify Microsoft "
                "ID token"
            ),
        )


# =========================================================
# TOKEN CREATION
# =========================================================

def _issue_tokens(
    user: User,
    db: Session,
) -> dict:
    token_data = {
        "sub": str(user.user_id),
        "email": user.email,
        "role": user.role,
    }

    access_token = create_access_token(
        token_data,
    )

    refresh_token_str, expires_at = (
        create_refresh_token(
            token_data,
        )
    )

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
        "expires_in":
            JWT_EXPIRE_MINUTES * 60,
        "user": user,
    }


# =========================================================
# REGISTER
# =========================================================

@router.post(
    "/register",
    response_model=AuthResponse,
)
def register(
    user: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        if (
            db.query(User)
            .filter(
                User.email == user.email
            )
            .first()
        ):
            raise HTTPException(
                status_code=409,
                detail=
                    "Email already registered",
            )

        if (
            db.query(User)
            .filter(
                User.username ==
                user.username
            )
            .first()
        ):
            raise HTTPException(
                status_code=409,
                detail=
                    "Username already taken",
            )

        new_user = User(
            email=user.email,
            username=user.username,
            password=hash_password(
                user.password
            ),
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return _issue_tokens(
            new_user,
            db,
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Internal server error "
                "during registration"
            ),
        )


# =========================================================
# LOGIN
# =========================================================

@router.post(
    "/login",
    response_model=AuthResponse,
)
def login(
    user: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        db_user = (
            db.query(User)
            .filter(
                User.email == user.email
            )
            .first()
        )

        if (
            not db_user
            or not verify_password(
                user.password,
                db_user.password,
            )
        ):
            raise HTTPException(
                status_code=401,
                detail=
                    "Invalid email or password",
            )

        return _issue_tokens(
            db_user,
            db,
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Internal server error "
                "during login"
            ),
        )


# =========================================================
# MICROSOFT OAUTH
# =========================================================

@router.post(
    "/microsoft",
    response_model=AuthResponse,
)
async def microsoft_login(
    body: MicrosoftAuthRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user with a Microsoft ID token
    obtained by the React/MSAL frontend.

    Existing Project Orion users are matched by email.
    A new Project Orion user is created automatically
    when the Microsoft email has not been used before.
    """

    if not body.id_token.strip():
        raise HTTPException(
            status_code=400,
            detail="Microsoft ID token is required",
        )

    claims = _verify_microsoft_id_token(
        body.id_token.strip()
    )

    email = (
        claims.get("email")
        or claims.get("preferred_username")
        or claims.get("upn")
    )

    if not email:
        raise HTTPException(
            status_code=401,
            detail=(
                "Microsoft account did not "
                "return an email address"
            ),
        )

    email = str(email).strip().lower()

    display_name = (
        claims.get("name")
        or email.split("@")[0]
    )

    # Microsoft object/account identifier.
    microsoft_user_id = (
        claims.get("oid")
        or claims.get("sub")
    )

    # Find an existing Project Orion account.
    db_user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )

    # Create a Project Orion account the first time
    # this Microsoft identity is used.
    if not db_user:
        base_username = (
            str(display_name).strip()
            or email.split("@")[0]
        )

        username = base_username
        counter = 1

        while (
            db.query(User)
            .filter(
                User.username == username
            )
            .first()
        ):
            username = (
                f"{base_username}_{counter}"
            )
            counter += 1

        # OAuth users do not need a Project Orion
        # password. The current User model requires
        # one, so store a strong random unusable value.
        oauth_password = (
            secrets.token_urlsafe(48)
        )

        db_user = User(
            email=email,
            username=username,
            password=hash_password(
                oauth_password
            ),
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    # Issue the same Project Orion access/refresh
    # tokens used by normal email/password login.
    auth_data = _issue_tokens(
        db_user,
        db,
    )

    # Keep these values available for logging/debugging
    # without changing the AuthResponse contract.
    _ = microsoft_user_id

    return auth_data


# =========================================================
# GOOGLE OAUTH - START
# =========================================================

@router.get("/google")
async def google_login():
    """
    Redirect the browser to Google's
    OAuth authorization page.
    """

    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail=(
                "GOOGLE_CLIENT_ID "
                "is not configured"
            ),
        )

    if not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail=(
                "GOOGLE_CLIENT_SECRET "
                "is not configured"
            ),
        )

    state = secrets.token_urlsafe(32)

    params = {
        "client_id":
            GOOGLE_CLIENT_ID,
        "redirect_uri":
            GOOGLE_CALLBACK_URL,
        "response_type":
            "code",
        "scope":
            "openid email profile",
        "access_type":
            "offline",
        "prompt":
            "select_account",
        "state":
            state,
    }

    google_auth_url = (
        "https://accounts.google.com/"
        "o/oauth2/v2/auth?"
        + urlencode(params)
    )

    response = RedirectResponse(
        url=google_auth_url,
        status_code=302,
    )

    response.set_cookie(
        key="google_oauth_state",
        value=state,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=600,
    )

    return response


# =========================================================
# GOOGLE OAUTH - CALLBACK
# =========================================================

@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Google redirects here after the user
    approves authentication.
    """

    frontend_login_url = (
        FRONTEND_URL.rstrip("/")
        + "/login"
    )

    error = request.query_params.get(
        "error"
    )

    if error:
        redirect_url = (
            frontend_login_url
            + "?"
            + urlencode(
                {
                    "auth": "error",
                    "message":
                        "Google authentication "
                        "was cancelled.",
                }
            )
        )

        return RedirectResponse(
            redirect_url,
            status_code=302,
        )

    code = request.query_params.get(
        "code"
    )

    returned_state = (
        request.query_params.get(
            "state"
        )
    )

    stored_state = request.cookies.get(
        "google_oauth_state"
    )

    if (
        not returned_state
        or not stored_state
        or returned_state != stored_state
    ):
        redirect_url = (
            frontend_login_url
            + "?"
            + urlencode(
                {
                    "auth": "error",
                    "message":
                        "Invalid Google OAuth "
                        "state.",
                }
            )
        )

        return RedirectResponse(
            redirect_url,
            status_code=302,
        )

    if not code:
        redirect_url = (
            frontend_login_url
            + "?"
            + urlencode(
                {
                    "auth": "error",
                    "message":
                        "Google did not return "
                        "an authorization code.",
                }
            )
        )

        return RedirectResponse(
            redirect_url,
            status_code=302,
        )

    try:
        # =============================================
        # 1. Exchange authorization code for tokens
        # =============================================

        async with httpx.AsyncClient(
            timeout=20.0
        ) as client:

            token_response = (
                await client.post(
                    (
                        "https://oauth2."
                        "googleapis.com/token"
                    ),
                    data={
                        "code":
                            code,
                        "client_id":
                            GOOGLE_CLIENT_ID,
                        "client_secret":
                            GOOGLE_CLIENT_SECRET,
                        "redirect_uri":
                            GOOGLE_CALLBACK_URL,
                        "grant_type":
                            "authorization_code",
                    },
                )
            )

            if (
                token_response.status_code
                != 200
            ):
                raise RuntimeError(
                    "Google token exchange "
                    "failed"
                )

            google_tokens = (
                token_response.json()
            )

            google_access_token = (
                google_tokens.get(
                    "access_token"
                )
            )

            if not google_access_token:
                raise RuntimeError(
                    "Google access token "
                    "was not returned"
                )

            # =========================================
            # 2. Retrieve Google profile
            # =========================================

            user_response = (
                await client.get(
                    (
                        "https://"
                        "openidconnect."
                        "googleapis.com/"
                        "v1/userinfo"
                    ),
                    headers={
                        "Authorization":
                            (
                                "Bearer "
                                + google_access_token
                            )
                    },
                )
            )

            if (
                user_response.status_code
                != 200
            ):
                raise RuntimeError(
                    "Unable to retrieve "
                    "Google user information"
                )

            google_user = (
                user_response.json()
            )

        # =============================================
        # 3. Validate Google profile
        # =============================================

        email = google_user.get(
            "email"
        )

        email_verified = (
            google_user.get(
                "email_verified"
            )
        )

        if not email:
            raise RuntimeError(
                "Google account did not "
                "return an email address"
            )

        if email_verified is False:
            raise RuntimeError(
                "Google email address "
                "is not verified"
            )

        display_name = (
            google_user.get("name")
            or email.split("@")[0]
        )

        picture = google_user.get(
            "picture"
        )

        google_id = google_user.get(
            "sub"
        )

        # =============================================
        # 4. Find existing Project Orion user
        # =============================================

        db_user = (
            db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )

        # =============================================
        # 5. Create account when this Google email
        #    has never been used before
        # =============================================

        if not db_user:
            base_username = (
                display_name.strip()
                or email.split("@")[0]
            )

            username = base_username

            counter = 1

            while (
                db.query(User)
                .filter(
                    User.username ==
                    username
                )
                .first()
            ):
                username = (
                    f"{base_username}"
                    f"_{counter}"
                )

                counter += 1

            # OAuth accounts do not need a
            # password for Google login.
            #
            # Store a strong random unusable
            # application password because the
            # current User model expects one.

            oauth_password = (
                secrets.token_urlsafe(48)
            )

            db_user = User(
                email=email,
                username=username,
                password=hash_password(
                    oauth_password
                ),
            )

            db.add(db_user)
            db.commit()
            db.refresh(db_user)

        # =============================================
        # 6. Generate Project Orion JWT
        # =============================================

        token_data = {
            "sub":
                str(db_user.user_id),
            "email":
                db_user.email,
            "role":
                db_user.role,
        }

        access_token = (
            create_access_token(
                token_data
            )
        )

        # =============================================
        # 7. Build frontend user profile
        # =============================================

        frontend_user = {
            "id":
                google_id
                or str(
                    db_user.user_id
                ),
            "email":
                db_user.email,
            "name":
                display_name,
            "picture":
                picture,
            "provider":
                "google",
        }

        # =============================================
        # 8. Redirect back to Vercel Login.tsx
        # =============================================

        redirect_url = (
            frontend_login_url
            + "?"
            + urlencode(
                {
                    "auth":
                        "success",
                    "token":
                        access_token,
                    "user":
                        json.dumps(
                            frontend_user
                        ),
                }
            )
        )

        response = RedirectResponse(
            redirect_url,
            status_code=302,
        )

        response.delete_cookie(
            "google_oauth_state"
        )

        return response

    except Exception:
        redirect_url = (
            frontend_login_url
            + "?"
            + urlencode(
                {
                    "auth":
                        "error",
                    "message":
                        (
                            "Google "
                            "authentication "
                            "failed."
                        ),
                }
            )
        )

        response = RedirectResponse(
            redirect_url,
            status_code=302,
        )

        response.delete_cookie(
            "google_oauth_state"
        )

        return response


# =========================================================
# REFRESH TOKEN
# =========================================================

@router.post(
    "/refresh",
    response_model=AuthResponse,
)
def refresh(
    body: RefreshRequest,
    db: Session = Depends(get_db),
):
    payload = decode_refresh_token(
        body.refresh_token
    )

    if not payload:
        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid or expired "
                "refresh token"
            ),
        )

    db_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token ==
                body.refresh_token,
            RefreshToken.is_active ==
                True,
        )
        .first()
    )

    if not db_token:
        raise HTTPException(
            status_code=401,
            detail=(
                "Refresh token has "
                "been revoked"
            ),
        )

    if (
        db_token.expires_at.replace(
            tzinfo=timezone.utc
        )
        < datetime.now(
            timezone.utc
        )
    ):
        db_token.is_active = False
        db.commit()

        raise HTTPException(
            status_code=401,
            detail=(
                "Refresh token "
                "has expired"
            ),
        )

    user = (
        db.query(User)
        .filter(
            User.user_id ==
                db_token.user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    db_token.is_active = False
    db.commit()

    return _issue_tokens(
        user,
        db,
    )


# =========================================================
# LOGOUT
# =========================================================

@router.post("/logout")
def logout(
    body: LogoutRequest,
    db: Session = Depends(get_db),
):
    db_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token ==
                body.refresh_token
        )
        .first()
    )

    if db_token:
        db_token.is_active = False
        db.commit()

    return {
        "message":
            "Logged out successfully"
    }


# =========================================================
# CURRENT USER
# =========================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: dict = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    try:
        user = (
            db.query(User)
            .filter(
                User.user_id ==
                    current_user["sub"]
            )
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
            detail=(
                "Internal server error "
                "retrieving user"
            ),
        )