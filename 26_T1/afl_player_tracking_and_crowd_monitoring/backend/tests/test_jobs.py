from datetime import datetime, timezone
from types import SimpleNamespace

from app.main import app
from app.auth.dependencies import get_current_user

# Bypass authentication
def override_get_current_user():
    return {"sub": "test_user", "role": "admin"}

# Mock DB record
def make_job(
        job_id="11111111-1111-1111-1111-111111111111",
        status="done",
        user_id="test_user",
        player_result=None,
        crowd_result=None,
        error=None,
        video_path="uploads/test.mp4",   
    ):
        now = datetime.now(timezone.utc)

        return SimpleNamespace(
              job_id=job_id,
              status=status,
              user_id=user_id,
              player_result=player_result,
              crowd_result=crowd_result,
              error=error,
              video_path=video_path,
              created_at=now,
              updated_at=now,
        )

# Test: Get job status (success)
def test_get_status_success(client, mock_db):
    app.dependency_overrides[get_current_user] = override_get_current_user
    fake_job = make_job(
            status="done",
            player_result={"players": 10},
            crowd_result={"crowd": 50},
            )
    mock_db.query.return_value.filter.return_value.first.return_value = fake_job # Mock DB query to return fake job
    response = client.get("/status/11111111-1111-1111-1111-111111111111") # Send GET request to endpoint
    assert response.status_code == 200 
    data = response.json()
    assert data["job_id"] == "11111111-1111-1111-1111-111111111111"
    assert data["status"] == "done"
    assert "results" in data

# Test: Job status not found
def test_get_status_not_found(client, mock_db):
    app.dependency_overrides[get_current_user] = override_get_current_user

    mock_db.query.return_value.filter.return_value.first.return_value = None

    response = client.get("/status/missing-job")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"

# Test: List jobs (pagination)
def test_list_jobs_with_pagination(client, mock_db):
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Create fake jobs list
    jobs = [
        make_job(job_id="11111111-1111-1111-1111-111111111111"),
        make_job(job_id="22222222-2222-2222-2222-222222222222"),
        make_job(job_id="33333333-3333-3333-3333-333333333333"),
    ]

    mock_db.query.return_value.count.return_value = 3
    mock_db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = jobs[:2]

    response = client.get("/jobs?page=1&limit=2")
    assert response.status_code == 200
    data = response.json()

    # Check pagination fields
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["limit"] == 2
    assert len(data["jobs"]) == 2  # only 2 returned

# Test: Get job details
def test_get_job_success(client, mock_db):
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Fake completed job
    fake_job = make_job(
        status="done",
        player_result={"players": 10},
        crowd_result={"crowd": 50},
    )

    mock_db.query.return_value.filter.return_value.first.return_value = fake_job

    response = client.get("/jobs/11111111-1111-1111-1111-111111111111")
    assert response.status_code == 200
    data = response.json()
    # Validate job data
    assert data["job_id"] == "11111111-1111-1111-1111-111111111111"
    assert data["status"] == "done"
    assert "results" in data

# Test Get job not found
def test_get_job_not_found(client, mock_db):
    app.dependency_overrides[get_current_user] = override_get_current_user

    # No job returned
    mock_db.query.return_value.filter.return_value.first.return_value = None

    response = client.get("/jobs/missing-job")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"

# Test: Retry job (success case)
def test_retry_job_success(client, mock_db, monkeypatch):
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Partial job (only one result missing)
    fake_job = make_job(
        status="partial",
        player_result=None,
        crowd_result={"crowd": 50},
    )

    mock_db.query.return_value.filter.return_value.first.return_value = fake_job

    # Mock async player service response
    async def fake_player_data(video_path):
        return {"players": 12}

    # Replace real service call with fake one
    monkeypatch.setattr("app.routes.jobs.get_player_data", fake_player_data)

    response = client.post("/jobs/11111111-1111-1111-1111-111111111111/retry")
    assert response.status_code == 200
    data = response.json()

    # Job should now be completed
    assert data["job_id"] == "11111111-1111-1111-1111-111111111111"
    assert data["status"] == "done"

# Test: Retry invalid job
def test_retry_job_not_partial(client, mock_db):
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Job already complete
    fake_job = make_job(
        status="done",
        player_result={"players": 10},
        crowd_result={"crowd": 50},
    )

    mock_db.query.return_value.filter.return_value.first.return_value = fake_job

    response = client.post("/jobs/11111111-1111-1111-1111-111111111111/retry")

    # Should fail
    assert response.status_code == 400
    assert response.json()["detail"] == "Only partial jobs can be retried"

# Test: Delete job
def test_delete_job_success(client, mock_db):
    app.dependency_overrides[get_current_user] = override_get_current_user

    fake_job = make_job()

    # Mock DB returning a job
    mock_db.query.return_value.filter.return_value.first.return_value = fake_job

    response = client.delete("/jobs/11111111-1111-1111-1111-111111111111")
    assert response.status_code == 200
    assert response.json()["message"] == "job deleted"

    # Ensure DB methods were called
    mock_db.delete.assert_called_once_with(fake_job)
    mock_db.commit.assert_called()

# When attempting to delete a job that does not exist
def test_delete_job_not_found(client, mock_db):
    app.dependency_overrides[get_current_user] = override_get_current_user

    mock_db.query.return_value.filter.return_value.first.return_value = None

    response = client.delete("/jobs/missing-job")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"

# When attempting to retry a job that does not exist
def test_retry_job_not_found(client, mock_db):
    app.dependency_overrides[get_current_user] = override_get_current_user

    mock_db.query.return_value.filter.return_value.first.return_value = None

    response = client.post("/jobs/missing-job/retry")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"