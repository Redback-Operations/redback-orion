from datetime import datetime, timedelta, timezone

from app.database import SessionLocal
from app.models import Job
from app.services.player_client import get_player_data
from app.services.crowd_client import get_crowd_data


MAX_RETRIES = 3
STUCK_JOB_MINUTES = 30


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_processing_time(job: Job):
    started_at = getattr(job, "started_at", None)
    completed_at = getattr(job, "completed_at", None)

    if started_at and completed_at:
        return (completed_at - started_at).total_seconds()

    return None


def get_failed_components(job: Job):
    failed = []

    if not getattr(job, "player_result", None):
        failed.append("player")

    if not getattr(job, "crowd_result", None):
        failed.append("crowd")

    return failed


def get_component_status(job: Job):
    if getattr(job, "player_result", None):
        player_status = "done"
    elif job.status in ("partial", "failed"):
        player_status = "failed"
    else:
        player_status = "processing"

    if getattr(job, "crowd_result", None):
        crowd_status = "done"
    elif job.status in ("partial", "failed"):
        crowd_status = "failed"
    else:
        crowd_status = "processing"

    return {
        "player": player_status,
        "crowd": crowd_status
    }


def is_job_stuck(job: Job):
    if job.status != "processing":
        return False

    started_at = getattr(job, "started_at", None)

    if not started_at:
        return False

    stuck_limit = _now() - timedelta(
        minutes=STUCK_JOB_MINUTES
    )

    return started_at < stuck_limit


def get_job_health(job: Job):
    if is_job_stuck(job):
        return "stuck"

    if job.status == "failed":
        return "failed"

    if job.status == "partial":
        return "needs_retry"

    if job.status == "processing":
        return "processing"

    if job.status == "done":
        return "healthy"

    return "unknown"


def can_retry_job(job: Job):
    retry_count = getattr(
        job,
        "retry_count",
        0
    )

    if retry_count >= MAX_RETRIES:
        return False

    if not getattr(job, "video_path", None):
        return False

    return True


def prepare_retry(job: Job):
    if not can_retry_job(job):
        return False

    job.retry_count = getattr(
        job,
        "retry_count",
        0
    ) + 1

    job.status = "processing"
    job.progress = 0

    job.started_at = _now()
    job.completed_at = None

    job.failure_reason = None
    job.error = None

    job.updated_at = _now()

    return True


def mark_job_complete(job: Job):
    job.status = "done"
    job.progress = 100

    job.failure_reason = None
    job.error = None

    job.completed_at = _now()
    job.updated_at = _now()


def mark_job_partial(job: Job):
    failed = get_failed_components(job)

    job.status = "partial"
    job.progress = 100

    if failed:
        job.failure_reason = (
            "Failed components: "
            + ", ".join(failed)
        )
    else:
        job.failure_reason = (
            "One or more processing components failed"
        )

    job.error = job.failure_reason

    job.completed_at = _now()
    job.updated_at = _now()


def mark_job_failed(
    job: Job,
    error_message: str
):
    job.status = "failed"
    job.progress = 100

    job.failure_reason = error_message
    job.error = error_message

    job.completed_at = _now()
    job.updated_at = _now()


async def process_retry(
    job_id: str,
    db=None
):
    own_session = False

    # Production creates its own database session.
    # Tests can provide a mocked database session.
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        job = db.query(Job).filter(
            Job.job_id == job_id
        ).first()

        if not job:
            return

        try:
            # Only retry components that
            # do not already have results.

            if not getattr(
                job,
                "player_result",
                None
            ):
                job.player_result = (
                    await get_player_data(
                        job.video_path
                    )
                )

            if not getattr(
                job,
                "crowd_result",
                None
            ):
                job.crowd_result = (
                    await get_crowd_data(
                        job.video_path
                    )
                )

            if (
                job.player_result
                and job.crowd_result
            ):
                mark_job_complete(job)

            else:
                mark_job_partial(job)

        except Exception as error:
            failed = get_failed_components(job)

            if failed:
                job.status = "partial"
                job.progress = 100

                job.failure_reason = str(error)
                job.error = str(error)

                job.completed_at = _now()
                job.updated_at = _now()

            else:
                mark_job_failed(
                    job,
                    str(error)
                )

        db.commit()

    finally:
        if own_session:
            db.close()