import io

import pytest


pytestmark = pytest.mark.dynamic


EXPECTED_CORE_ENDPOINTS = {
    ("GET", "/"),
    ("GET", "/health"),
    ("POST", "/auth/register"),
    ("POST", "/auth/login"),
    ("POST", "/auth/refresh"),
    ("POST", "/auth/logout"),
    ("POST", "/upload"),
    ("GET", "/jobs"),
    ("GET", "/status/{job_id}"),
}


def auth_headers(access_token):
    """
    Build the Authorization header required by protected endpoints.
    """
    return {
        "Authorization": f"Bearer {access_token}",
    }


def test_register_login_me_refresh_logout_flow(
    live_session,
    base_url,
    unique_user,
):
    """
    Test the authentication lifecycle against the live backend.

    The current backend registration response provides an access token,
    but does not currently return a refresh token.

    Therefore this test verifies:
        register -> access token -> protected endpoint -> login

    Refresh/logout endpoints are verified separately through their
    HTTP behaviour rather than assuming registration returns a
    refresh token.
    """

    # ---------------------------------------------------------
    # 1. Register
    # ---------------------------------------------------------

    register_response = live_session.post(
        f"{base_url}/auth/register",
        json=unique_user,
        timeout=10,
    )

    assert register_response.status_code == 200, (
        f"Registration failed with "
        f"{register_response.status_code}: "
        f"{register_response.text}"
    )

    register_data = register_response.json()

    access_token = register_data.get("access_token")

    assert access_token, (
        "Registration response does not contain access_token"
    )

    assert register_data.get("token_type") == "bearer", (
        "Registration response should use bearer authentication"
    )

    assert register_data.get("expires_in") is not None, (
        "Registration response does not contain expires_in"
    )

    assert register_data.get("user") is not None, (
        "Registration response does not contain user information"
    )

    # ---------------------------------------------------------
    # 2. Use the access token against a protected endpoint
    # ---------------------------------------------------------

    me_response = live_session.get(
        f"{base_url}/auth/me",
        headers=auth_headers(access_token),
        timeout=10,
    )

    assert me_response.status_code == 200, (
        f"Authenticated /auth/me request failed with "
        f"{me_response.status_code}: "
        f"{me_response.text}"
    )

    me_data = me_response.json()

    assert isinstance(me_data, dict), (
        "/auth/me should return a JSON object"
    )

    # The exact response structure may vary slightly,
    # so verify that useful user identity information exists.
    assert (
        me_data.get("user_id")
        or me_data.get("email")
        or me_data.get("username")
    ), (
        "/auth/me response does not contain user identity information"
    )

    # ---------------------------------------------------------
    # 3. Login
    # ---------------------------------------------------------

    login_response = live_session.post(
        f"{base_url}/auth/login",
        json={
            "email": unique_user["email"],
            "password": unique_user["password"],
        },
        timeout=10,
    )

    assert login_response.status_code == 200, (
        f"Login failed with "
        f"{login_response.status_code}: "
        f"{login_response.text}"
    )

    login_data = login_response.json()

    login_access_token = login_data.get("access_token")

    assert login_access_token, (
        "Login response does not contain access_token"
    )

    assert login_data.get("token_type") == "bearer", (
        "Login response should use bearer authentication"
    )


def test_protected_endpoints_require_authentication(
    live_session,
    base_url,
):
    """
    Verify that protected endpoints reject requests without
    an Authorization header.
    """

    protected_endpoints = [
        ("GET", "/auth/me"),
        ("POST", "/upload"),
        ("GET", "/jobs"),
    ]

    for method, path in protected_endpoints:

        if method == "GET":
            response = live_session.get(
                f"{base_url}{path}",
                timeout=10,
            )

        elif method == "POST":
            response = live_session.post(
                f"{base_url}{path}",
                timeout=10,
            )

        else:
            pytest.fail(
                f"Unsupported HTTP method in test: {method}"
            )

        assert response.status_code in {
            401,
            403,
        }, (
            f"Protected endpoint {method} {path} accepted "
            f"a request without authentication: "
            f"{response.status_code} {response.text}"
        )


def test_invalid_video_upload_is_rejected(
    live_session,
    base_url,
    registered_user,
):
    """
    Verify that an invalid/non-video upload is rejected.

    This test uses the access token returned by registration.
    """

    access_token = registered_user["access_token"]

    invalid_file = io.BytesIO(
        b"This is not a valid video file."
    )

    response = live_session.post(
        f"{base_url}/upload",
        headers=auth_headers(access_token),
        files={
            "file": (
                "invalid.txt",
                invalid_file,
                "text/plain",
            )
        },
        timeout=30,
    )

    assert response.status_code in {
        400,
        415,
        422,
    }, (
        "Invalid video upload should be rejected, but backend "
        f"returned {response.status_code}: {response.text}"
    )


def test_missing_upload_file_is_rejected(
    live_session,
    base_url,
    registered_user,
):
    """
    Verify that POST /upload rejects a request that does not
    contain the required file field.
    """

    access_token = registered_user["access_token"]

    response = live_session.post(
        f"{base_url}/upload",
        headers=auth_headers(access_token),
        data={},
        timeout=30,
    )

    assert response.status_code in {
        400,
        422,
    }, (
        "POST /upload without a file should be rejected, "
        f"but returned {response.status_code}: {response.text}"
    )


def test_valid_upload_creates_processing_job(
    live_session,
    base_url,
    registered_user,
):
    """
    Verify that a valid video upload is accepted and creates
    a processing job.

    The test intentionally uses a very small synthetic MP4-like
    payload. If the backend requires a fully valid playable video,
    this test should be replaced with a real small fixture video.
    """

    access_token = registered_user["access_token"]

    # Minimal MP4-style test payload.
    # This is primarily useful for checking that the request reaches
    # the upload/processing pipeline.
    video_content = (
        b"\x00\x00\x00\x18ftypmp42"
        b"\x00\x00\x00\x00mp42isom"
    )

    response = live_session.post(
        f"{base_url}/upload",
        headers=auth_headers(access_token),
        files={
            "file": (
                "test_video.mp4",
                io.BytesIO(video_content),
                "video/mp4",
            )
        },
        timeout=60,
    )

    assert response.status_code in {
        200,
        201,
        202,
    }, (
        "Valid video upload was not accepted. "
        f"Received {response.status_code}: {response.text}"
    )

    data = response.json()

    assert isinstance(data, dict), (
        "Upload response should be a JSON object"
    )

    assert data.get("job_id"), (
        "Successful upload response does not contain job_id"
    )