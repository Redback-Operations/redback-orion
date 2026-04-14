from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_valid_file():
    response = client.post("/upload", files={"file": ("test.csv", b"dummy,data", "text/csv")})
    assert response.status_code == 200
    assert "message" in response.json()

def test_upload_invalid_file_type():
    response = client.post("/upload", files={"file": ("text.txt", b"dummy,data", "text/plain")})
    assert response.status_code == 400
    assert "invalid" in str(response.json()).lower()

def test_missing_file():
    response = client.post("/upload", files={})
    assert response.status_code == 422
    assert "file" in str(response.json())