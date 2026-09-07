from app.main import app
from datetime import datetime, timezone
from app.auth.dependencies import get_current_user


def override_get_current_user():
    return {"sub": "test_user", "role": "admin"}


async def fake_process_video(job_id, file_path):
    return "11111111-1111-1111-1111-111111111111"


def test_upload_valid_file(client, monkeypatch, mock_db):
    app.dependency_overrides[get_current_user] = override_get_current_user
    monkeypatch.setattr("app.routes.upload.process_video", fake_process_video)

    def fake_refresh(job):
        job.job_id = "11111111-1111-1111-1111-111111111111"
        job.created_at = datetime.now(timezone.utc)

    mock_db.refresh.side_effect = fake_refresh

    valid_mp4_header = b"\x00\x00\x00\x18ftypisom"

    response = client.post(
        "/upload",
        files={"file": ("test.mp4", valid_mp4_header, "video/mp4")}
    )

    assert response.status_code == 200
    assert response.json()["job_id"] == "11111111-1111-1111-1111-111111111111"
    assert response.json()["status"] == "processing"


def test_upload_invalid_file_header(client):
    app.dependency_overrides[get_current_user] = override_get_current_user

    response = client.post(
        "/upload",
        files={"file": ("test.mp4", b"not a real mp4 file", "video/mp4")}
    )

    assert response.status_code == 400
    assert "invalid .mp4 file header" in response.json()["detail"].lower()


def test_upload_invalid_avi_header(client):
    app.dependency_overrides[get_current_user] = override_get_current_user

    response = client.post(
        "/upload",
        files={"file": ("test.avi", b"not a real avi file", "video/x-msvideo")}
    )

    assert response.status_code == 400
    assert "invalid .avi file header" in response.json()["detail"].lower()


def test_upload_invalid_mov_header(client):
    app.dependency_overrides[get_current_user] = override_get_current_user

    response = client.post(
        "/upload",
        files={"file": ("test.mov", b"not a real mov file", "video/quicktime")}
    )

    assert response.status_code == 400
    assert "invalid .mov file header" in response.json()["detail"].lower()


def test_upload_invalid_file_type(client):
    app.dependency_overrides[get_current_user] = override_get_current_user

    response = client.post(
        "/upload",
        files={"file": ("text.txt", b"dummy,data", "text/plain")}
    )

    assert response.status_code == 400
    assert "invalid" in str(response.json()).lower()


def test_missing_file(client):
    app.dependency_overrides[get_current_user] = override_get_current_user

    response = client.post("/upload", files={})

    assert response.status_code == 422
    assert "file" in str(response.json())


def test_upload_invalid_mime_type(client):
    app.dependency_overrides[get_current_user] = override_get_current_user

    response = client.post(
        "/upload",
        files={"file": ("test.mp4", b"fake video content", "text/plain")}
    )

    assert response.status_code == 400
    assert "Invalid video format" in response.json()["detail"]
