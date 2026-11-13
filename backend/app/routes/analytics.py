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
    format_player_tracking
)

from app.schemas.jobs import CrowdResponse

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
    
    
def _get_job(
    job_id: str,
    db: Session,
    current_user: dict,
):
    query = db.query(Job).filter(
        Job.job_id == job_id
    )

    if current_user["role"] != "admin":
        query = query.filter(
            Job.user_id == current_user["sub"]
        )

    job = query.first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return job


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
    movement = player_result.get("movement") or {}
    movement_metrics = movement.get("movement_metrics") or {}

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
        "movement": {
            "metric_mode": (
                movement.get("metric_mode")
                or movement_metrics.get("metric_mode")
                ),
                "calibration_available": (
                    movement.get("calibration_available")
                    if movement.get("calibration_available") is not None
                    else movement_metrics.get("calibration_available")
                    ),
                    "exported_tracks": movement_metrics.get("exported_tracks"),
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


@router.get("/analysis/{job_id}")
def get_analysis(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = _get_job(
        job_id,
        db,
        current_user,
    )

    if job.status not in ["done", "partial"]:
        raise HTTPException(
            status_code=409,
            detail="Analysis is not complete",
        )

    return {
        "job_id": str(job.job_id),
        "status": job.status,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "player": player_with_urls(job.player_result),
        "crowd": crowd_with_urls(job.crowd_result),
        "error": job.error,
    }


@router.get("/analytics/{job_id}")
def get_analytics(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = _get_job(
        job_id,
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
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "player": _player_summary(job.player_result),
        "crowd": _crowd_summary(job.crowd_result),
        "error": job.error,
    }


@router.get(
    "/crowd/{job_id}",
    response_model=CrowdResponse,
)
def get_crowd(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = _get_job(
        job_id,
        db,
        current_user,
    )

    if job.status not in ["done", "partial"]:
        raise HTTPException(
            status_code=409,
            detail="Analysis is not complete",
        )

    if not job.crowd_result:
        raise HTTPException(
            status_code=404,
            detail="Crowd analysis is not available for this job",
        )

    return {
        "job_id": str(job.job_id),
        "status": job.status,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "crowd": crowd_with_urls(job.crowd_result),
    }


@router.get("/player-tracking/{job_id}")
def get_player_tracking(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = _get_job(
        job_id,
        db,
        current_user,
    )

    if not job.player_result:
        raise HTTPException(
            status_code=404,
            detail="Player tracking result is not available for this job",
        )

    tracking_result = job.player_result.get("tracking")

    if not tracking_result:
        raise HTTPException(
            status_code=404,
            detail="Player tracking result is not available for this job",
        )

    return {
        "job_id": str(job.job_id),
        "status": job.status,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "player": format_player_tracking(tracking_result),
    }