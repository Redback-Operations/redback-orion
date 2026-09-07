from collections import Counter

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user,
)

from app.database import get_db

from app.models import Job

from app.services.result_formatter import (
    crowd_with_urls,
    player_with_urls,
)

router = APIRouter(
    prefix="/api",
    tags=["Analytics"],
)


def _latest_job(
    db: Session,
    current_user: dict,
):
    query = db.query(Job)

    if current_user["role"] != "admin":
        query = query.filter(Job.user_id == current_user["sub"])

    return (
        query.filter(
            Job.status.in_(
                [
                    "done",
                    "partial",
                ]
            )
        )
        .order_by(Job.created_at.desc())
        .first()
    )


def _player_summary(
    player_result: dict | None,
):
    if not player_result:
        return None

    tracking = player_result.get("tracking") or {}

    video_info = tracking.get("video_info") or {}

    frames = tracking.get("tracking_results") or []

    unique_players = set()

    team_counts = Counter()

    players_per_frame = []

    confidence_sum = 0.0
    confidence_count = 0

    for frame in frames:
        frame_players = frame.get("players") or []

        players_per_frame.append(len(frame_players))

        for player in frame_players:
            player_id = player.get("player_id")

            if player_id is not None:
                unique_players.add(player_id)

            team = player.get("team_name") or str(
                player.get(
                    "team_id",
                    "",
                )
            )

            if team:
                team_counts[team] += 1

            confidence = player.get("confidence")

            if isinstance(
                confidence,
                (int, float),
            ):
                confidence_sum += confidence

                confidence_count += 1

    formations = (player_result.get("formation") or {}).get("formations") or []

    tackles = (player_result.get("tackle") or {}).get("tackles") or []

    return {
        "video": video_info,
        "tracking": {
            "frames_with_tracking": (len(frames)),
            "unique_player_ids": (len(unique_players)),
            "total_player_detections": (sum(players_per_frame)),
            "average_players_per_frame": (
                round(
                    (sum(players_per_frame) / len(players_per_frame)),
                    2,
                )
                if players_per_frame
                else 0
            ),
            "peak_players_in_frame": (
                max(players_per_frame) if players_per_frame else 0
            ),
            "average_detection_confidence": (
                round(
                    (confidence_sum / confidence_count),
                    4,
                )
                if confidence_count
                else None
            ),
            "team_detection_counts": (dict(team_counts)),
        },
        "formation": {
            "count": len(formations),
            "data": formations,
        },
        "tackles": {
            "count": len(tackles),
            "data": tackles,
        },
    }


def _crowd_summary(
    crowd_result: dict | None,
):
    if not crowd_result:
        return None

    summary = crowd_result.get("summary") or {}

    peak = crowd_result.get("peak_crowd_frame") or {}

    density = crowd_result.get("density_extremes") or {}

    return {
        "total_frames_processed": (summary.get("total_frames_processed")),
        "peak_person_count": (summary.get("peak_person_count")),
        "crowd_state": (summary.get("crowd_state")),
        "highest_density_zone": (summary.get("highest_density_zone")),
        "highest_risk_zone": (summary.get("highest_risk_zone")),
        "peak_crowd_frame": {
            "frame_id": (peak.get("frame_id")),
            "timestamp": (peak.get("timestamp")),
            "person_count": (peak.get("person_count")),
        },
        "density_extremes": (density),
    }


@router.get("/analysis/latest")
def latest_analysis(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = _latest_job(
        db,
        current_user,
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail=("No completed analysis " "is available"),
        )

    return {
        "job_id": str(job.job_id),
        "status": job.status,
        "created_at": (job.created_at),
        "updated_at": (job.updated_at),
        "player": player_with_urls(job.player_result),
        "crowd": crowd_with_urls(job.crowd_result),
        "error": job.error,
    }


@router.get("/analytics/latest")
def latest_analytics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = _latest_job(
        db,
        current_user,
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail=("No completed analysis " "is available"),
        )

    return {
        "job_id": str(job.job_id),
        "status": job.status,
        "created_at": (job.created_at),
        "updated_at": (job.updated_at),
        "player": _player_summary(job.player_result),
        "crowd": _crowd_summary(job.crowd_result),
        "error": job.error,
    }


@router.get("/crowd/latest")
def latest_crowd(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = _latest_job(
        db,
        current_user,
    )

    if not job or not job.crowd_result:
        raise HTTPException(
            status_code=404,
            detail=("No completed crowd " "analysis is available"),
        )

    return {
        "job_id": str(job.job_id),
        "status": job.status,
        "created_at": (job.created_at),
        "updated_at": (job.updated_at),
        "crowd": crowd_with_urls(job.crowd_result),
        "summary": _crowd_summary(job.crowd_result),
    }


@router.get("/player-tracking/latest")
def latest_player_tracking(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = _latest_job(
        db,
        current_user,
    )

    if not job or not job.player_result:
        raise HTTPException(
            status_code=404,
            detail=("No completed player " "analysis is available"),
        )

    return {
        "job_id": str(job.job_id),
        "status": job.status,
        "created_at": (job.created_at),
        "updated_at": (job.updated_at),
        "player": player_with_urls(job.player_result),
        "summary": _player_summary(job.player_result),
    }
