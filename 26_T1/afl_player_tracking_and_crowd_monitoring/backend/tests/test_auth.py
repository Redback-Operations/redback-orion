import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock
from app.auth.hashing import hash_password
from app.auth.jwt import create_access_token
from app.models import User


REGISTER_PAYLOAD = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}

LOGIN_PAYLOAD = {
    "email": "test@example.com",
    "password": "password123"
}


def make_mock_user(**kwargs):
    user = MagicMock(spec=User)
    user.user_id = kwargs.get("user_id", uuid.uuid4())
    user.email = kwargs.get("email", "test@example.com")
    user.username = kwargs.get("username", "testuser")
    user.password = kwargs.get("password", hash_password("password123"))
    user.role = kwargs.get("role", "user")
    user.created_at = kwargs.get("created_at", datetime.now(timezone.utc))
    return user


# --- Register ---

def test_register_success(client, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    response = client.post("/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == REGISTER_PAYLOAD["email"]


def test_register_duplicate_email(client, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = make_mock_user()
    response = client.post("/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_register_missing_fields(client, mock_db):
    response = client.post("/auth/register", json={"email": "test@example.com"})
    assert response.status_code == 422


# --- Login ---

def test_login_success(client, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = make_mock_user()
    response = client.post("/auth/login", json=LOGIN_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = make_mock_user()
    response = client.post("/auth/login", json={"email": "test@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_user_not_found(client, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    response = client.post("/auth/login", json=LOGIN_PAYLOAD)
    assert response.status_code == 401


# --- GET /auth/me ---

def test_get_me_success(client, mock_db):
    mock_user = make_mock_user()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    token = create_access_token({
        "sub": str(mock_user.user_id),
        "email": mock_user.email,
        "role": mock_user.role
    })
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == mock_user.email


def test_get_me_no_token(client, mock_db):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_get_me_invalid_token(client, mock_db):
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
