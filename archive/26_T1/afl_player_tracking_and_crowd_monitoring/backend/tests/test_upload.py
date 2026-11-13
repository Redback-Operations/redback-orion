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
    response = client.post("/upload", files={"file": ("test.mp4", b"fake video content", "video/mp4")})
    assert response.status_code == 200
    assert response.json()["job_id"] == "11111111-1111-1111-1111-111111111111"
    assert response.json()["status"] == "processing"

def test_upload_invalid_file_type(client):
    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.post("/upload", files={"file": ("text.txt", b"dummy,data", "text/plain")})
    assert response.status_code == 400
    assert "invalid" in str(response.json()).lower()

def test_missing_file(client):
    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.post("/upload", files={})
    assert response.status_code == 422
    assert "file" in str(response.json())

def test_upload_invalid_mime_type(client):
    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.post("/upload", files={"file": ("test.mp4", b"fake video content", "text/plain")})
    assert response.status_code == 400
    assert "Invalid video format" in response.json()["detail"]