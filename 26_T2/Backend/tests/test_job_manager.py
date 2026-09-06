from datetime import datetime, timedelta
from types import SimpleNamespace

from app.services.job_manager import (
    MAX_RETRIES,
    can_retry_job,
    get_component_status,
    get_failed_components,
    get_job_health,
    get_processing_time,
    is_job_stuck,
    mark_job_complete,
    mark_job_failed,
    mark_job_partial,
    prepare_retry
)


def make_job():
    now = datetime.utcnow()

    return SimpleNamespace(
        status="processing",

        retry_count=0,
        progress=0,

        video_path="uploads/test.mp4",

        player_result=None,
        crowd_result=None,

        started_at=now,
        completed_at=None,

        failure_reason=None,
        error=None,

        updated_at=now
    )


def test_failed_components():
    job = make_job()

    failed = get_failed_components(
        job
    )

    assert "player" in failed
    assert "crowd" in failed


def test_player_component_done():
    job = make_job()

    job.player_result = {
        "tracking": {}
    }

    status = get_component_status(
        job
    )

    assert status["player"] == "done"


def test_processing_job_health():
    job = make_job()

    assert (
        get_job_health(job)
        == "processing"
    )


def test_partial_job_health():
    job = make_job()

    job.status = "partial"

    assert (
        get_job_health(job)
        == "needs_retry"
    )


def test_done_job_health():
    job = make_job()

    job.status = "done"

    assert (
        get_job_health(job)
        == "healthy"
    )


def test_stuck_job_detection():
    job = make_job()

    job.started_at = (
        datetime.utcnow()
        - timedelta(minutes=40)
    )

    assert is_job_stuck(job)


def test_stuck_job_health():
    job = make_job()

    job.started_at = (
        datetime.utcnow()
        - timedelta(minutes=40)
    )

    assert (
        get_job_health(job)
        == "stuck"
    )


def test_retry_allowed():
    job = make_job()

    assert can_retry_job(job)


def test_retry_limit():
    job = make_job()

    job.retry_count = MAX_RETRIES

    assert not can_retry_job(job)


def test_prepare_retry():
    job = make_job()

    job.status = "partial"
    job.progress = 100

    result = prepare_retry(job)

    assert result is True
    assert job.retry_count == 1
    assert job.status == "processing"
    assert job.progress == 0


def test_mark_complete():
    job = make_job()

    mark_job_complete(job)

    assert job.status == "done"
    assert job.progress == 100
    assert job.failure_reason is None


def test_mark_partial():
    job = make_job()

    job.player_result = {
        "tracking": {}
    }

    mark_job_partial(job)

    assert job.status == "partial"
    assert job.progress == 100
    assert "crowd" in job.failure_reason


def test_mark_failed():
    job = make_job()

    mark_job_failed(
        job,
        "Processing error"
    )

    assert job.status == "failed"
    assert job.progress == 100

    assert (
        job.failure_reason
        == "Processing error"
    )


def test_processing_duration():
    job = make_job()

    job.started_at = datetime.utcnow()

    job.completed_at = (
        job.started_at
        + timedelta(seconds=20)
    )

    assert (
        get_processing_time(job)
        == 20
    )