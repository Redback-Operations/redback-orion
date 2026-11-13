import os
import uuid

import pytest
import requests


BASE_URL = os.getenv(
    "ORION_BASE_URL",
    "http://localhost:8000",
).rstrip("/")


@pytest.fixture(scope="session")
def base_url():
    """Return the live Orion backend base URL"""
    return BASE_URL


@pytest.fixture(scope="session")
def live_session(base_url):
    """
    Create one HTTP session for the dynamic test suite.

    The tests intentionally communicate with the real HTTP server rather
    than FastAPI's TestClient because these tests are intended to verify
    the running backend stack.
    """
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
        }
    )

    try:
        response = session.get(f"{base_url}/", timeout=5)
        response.raise_for_status()
    except requests.RequestException as exc:
        pytest.skip(
            f"Orion backend is not reachable at {base_url}. "
            f"Start the Orion backend Docker stack first. Cause: {exc}"
        )

    yield session
    session.close()


@pytest.fixture(scope="session")
def openapi(live_session, base_url):
    """Fetch and return the live OpenAPI document."""
    response = live_session.get(
        f"{base_url}/openapi.json",
        timeout=10,
    )

    assert response.status_code == 200, (
        f"GET /openapi.json failed with "
        f"{response.status_code}: {response.text}"
    )

    payload = response.json()

    assert isinstance(payload, dict), (
        "OpenAPI response must be a JSON object"
    )

    assert isinstance(payload.get("paths"), dict), (
        "OpenAPI document does not contain a valid paths object"
    )

    return payload


@pytest.fixture
def unique_user():
    """
    Generate credentials that should not collide with previous test runs.
    """
    suffix = uuid.uuid4().hex[:12]

    return {
        "username": f"dynamic_test_{suffix}",
        "email": f"dynamic_test_{suffix}@example.com",
        "password": "DynamicTestPassword123!",
    }


@pytest.fixture
def registered_user(live_session, base_url, unique_user):
    """
    Register a fresh test account against the running backend.

    The current backend returns an access token during registration.
    """

    response = live_session.post(
        f"{base_url}/auth/register",
        json=unique_user,
        timeout=10,
    )

    assert response.status_code == 200, (
        f"Registration failed with {response.status_code}: "
        f"{response.text}"
    )

    data = response.json()

    assert "access_token" in data, (
        "Registration response does not contain access_token"
    )

    return {
        "access_token": data["access_token"],
        "token_type": data.get("token_type", "bearer"),
        "user": data.get("user"),
        "credentials": unique_user,
    }


@pytest.fixture
def authenticated_session(
    live_session,
    base_url,
    registered_user,
):
    """
    Return a session authenticated as a newly-created test user.
    """
    access_token = registered_user["data"]["access_token"]

    session = requests.Session()

    session.headers.update(
        {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
    )

    yield session

    session.close()