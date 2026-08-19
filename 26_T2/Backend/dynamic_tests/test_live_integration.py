import pytest


pytestmark = pytest.mark.dynamic


def test_register_login_me_refresh_logout_flow(
    live_session,
    base_url,
    unique_user,
):
    """
    Test the complete authentication lifecycle against the live backend.
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
        f"Registration failed: {register_response.text}"
    )

    register_data = register_response.json()

    assert register_data.get("access_token")
    assert register_data.get("refresh_token")

    assert register_data.get("token_type") == "bearer"

    access_token = register_data["access_token"]
    refresh_token = register_data["refresh_token"]

    # ---------------------------------------------------------
    # 2. Authenticate against /auth/me
    # ---------------------------------------------------------

    auth_headers = {
        "Authorization": f"Bearer {access_token}",
    }

    me_response = live_session.get(
        f"{base_url}/auth/me",
        headers=auth_headers,
        timeout=10,
    )

    assert me_response.status_code == 200, (
        f"/auth/me failed: {me_response.text}"
    )

    me_data = me_response.json()

    assert me_data["email"] == unique_user["email"]
    assert me_data["username"] == unique_user["username"]

    # ---------------------------------------------------------
    # 3. Refresh token
    # ---------------------------------------------------------

    refresh_response = live_session.post(
        f"{base_url}/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
        timeout=10,
    )

    assert refresh_response.status_code == 200, (
        f"Token refresh failed: {refresh_response.text}"
    )

    refresh_data = refresh_response.json()

    assert refresh_data.get("access_token")
    assert refresh_data.get("refresh_token")

    new_access_token = refresh_data["access_token"]
    new_refresh_token = refresh_data["refresh_token"]

    # The refresh operation should produce usable credentials.
    assert new_access_token != access_token
    assert new_refresh_token != refresh_token

    # ---------------------------------------------------------
    # 4. Use the refreshed access token
    # ---------------------------------------------------------

    refreshed_headers = {
        "Authorization": f"Bearer {new_access_token}",
    }

    refreshed_me_response = live_session.get(
        f"{base_url}/auth/me",
        headers=refreshed_headers,
        timeout=10,
    )

    assert refreshed_me_response.status_code == 200

    # ---------------------------------------------------------
    # 5. Logout
    # ---------------------------------------------------------

    logout_response = live_session.post(
        f"{base_url}/auth/logout",
        json={
            "refresh_token": new_refresh_token,
        },
        timeout=10,
    )

    assert logout_response.status_code == 200

    logout_data = logout_response.json()

    assert logout_data.get("message")

    # ---------------------------------------------------------
    # 6. Reuse of revoked refresh token should fail
    # ---------------------------------------------------------

    revoked_response = live_session.post(
        f"{base_url}/auth/refresh",
        json={
            "refresh_token": new_refresh_token,
        },
        timeout=10,
    )

    assert revoked_response.status_code == 401

    assert "detail" in revoked_response.json()


def test_protected_endpoints_require_authentication(
    live_session,
    base_url,
):
    """
    Check that protected routes reject requests without JWT credentials.
    """

    protected_routes = [
        ("GET", "/auth/me"),
        ("GET", "/jobs"),
        ("POST", "/upload"),
        (
            "GET",
            "/status/11111111-1111-1111-1111-111111111111",
        ),
        (
            "GET",
            "/jobs/11111111-1111-1111-1111-111111111111",
        ),
        (
            "POST",
            "/jobs/11111111-1111-1111-1111-111111111111/retry",
        ),
        (
            "DELETE",
            "/jobs/11111111-1111-1111-1111-111111111111",
        ),
        (
            "GET",
            "/jobs/11111111-1111-1111-1111-111111111111/heatmap",
        ),
    ]

    for method, path in protected_routes:
        response = live_session.request(
            method,
            f"{base_url}{path}",
            timeout=5,
        )

        assert response.status_code == 401, (
            f"{method} {path} returned {response.status_code} "
            "without authentication"
        )

        assert "detail" in response.json()


def test_invalid_video_upload_is_rejected(
    live_session,
    base_url,
    registered_user,
):
    """
    Verify upload validation without starting a real processing job.
    """

    token = registered_user["data"]["access_token"]

    response = live_session.post(
        f"{base_url}/upload",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": (
                "not_a_video.txt",
                b"not a video",
                "text/plain",
            )
        },
        timeout=10,
    )

    assert response.status_code == 400

    data = response.json()

    assert "detail" in data

    assert "invalid" in data["detail"].lower()


def test_missing_upload_file_is_rejected(
    live_session,
    base_url,
    registered_user,
):
    token = registered_user["data"]["access_token"]

    response = live_session.post(
        f"{base_url}/upload",
        headers={
            "Authorization": f"Bearer {token}",
        },
        timeout=10,
    )

    assert response.status_code == 422

    assert "detail" in response.json()


def test_valid_upload_creates_processing_job(
    live_session,
    base_url,
    registered_user,
):
    """
    Verify that a syntactically valid video upload creates a job.

    The test intentionally does not require the expensive processing
    pipeline to complete.
    """

    token = registered_user["data"]["access_token"]

    response = live_session.post(
        f"{base_url}/upload",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": (
                "dynamic_test.mp4",
                b"fake video payload",
                "video/mp4",
            )
        },
        timeout=10,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data.get("job_id")
    assert data.get("status") == "processing"

    # Verify that the returned job ID can be used immediately.
    status_response = live_session.get(
        f"{base_url}/status/{data['job_id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        timeout=10,
    )

    assert status_response.status_code in {
        200,
        404,
    }

    if status_response.status_code == 200:
        status_data = status_response.json()

        assert status_data["job_id"] == data["job_id"]
        assert status_data["status"] in {
            "processing",
            "done",
            "partial",
            "failed",
        }