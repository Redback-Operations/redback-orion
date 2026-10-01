"""End-to-end service flow for the full crowd monitoring pipeline."""

from pathlib import Path

import matplotlib.pyplot as plt

from .crowd_analytics_service import process_analytics
from .crowd_detection_service import process_detection
from shared.crowd_safety_detection_service import ENABLE_STAMPEDE, process_safety_detection
from data_aggregation.main import aggregate_stadium_data
from crowd_allocation_risk_zone.main import assess_risk
from crowd_behaviour_analytics.main import analyze_behaviour
from shared.timing import timed as _timed

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _safe_round(value, digits=2):
    if value is None:
        return None
    return round(float(value), digits)


_REPORT_WIDTH = 54


def _report_section(title: str, seconds: float | None = None) -> str:
    """Section heading, with the section's total time right-aligned if known."""
    if seconds is None:
        return title
    return f"{title:<{_REPORT_WIDTH - 8}}{seconds:6.2f} s"


def _report_row(label: str, value, note: str = "") -> str:
    """One indented report line: label, value, then an optional note."""
    return f"  {label:<19}{value!s:<9}{note}".rstrip()


def _report_count(count: int, total: int) -> str:
    return f"{count} of {total} ({count / total:.0%})" if total else f"{count} of {total}"


def _print_benchmark_report(
    detection_result: dict,
    timings: dict,
    fire_result: dict | None = None,
    stampede_result: dict | None = None,
) -> None:
    """One combined report for the whole run, printed once at the end,
    instead of each stage printing its own piece as it finishes."""
    vt = detection_result.get("video_processing_timings") or {}
    ds = detection_result.get("detection_summary") or {}
    stage_ms = detection_result.get("stage_timings_ms") or {}
    vs = vt.get("video_stats") or {}
    total_s = sum(timings.values()) / 1000

    lines = ["", " PIPELINE BENCHMARK ".center(_REPORT_WIDTH, "=")]

    overview = []
    if vs.get("duration") is not None:
        overview.append(f"{vs['duration']} s")
    if vt:
        overview.append(f"{vt.get('frames_read', 0)} frames read, {vt.get('processed_frames', 0)} processed")
    if overview:
        lines.append(f"Video: {', '.join(overview)}")
    lines.append(f"Total: {total_s:.2f} s")

    if vt:
        stats_note = (
            f"{vs.get('statistics_samples')} samples, blur threshold {vs.get('threshold')}"
            if vs and vs.get("note") is None else ""
        )
        lines += [
            "",
            _report_section("VIDEO PROCESSING", vt.get("total_seconds", 0)),
            _report_row("Video stats", f"{vt.get('stats_seconds', 0):.2f} s", stats_note),
            _report_row(
                "Decoding", f"{vt.get('decoding_seconds', 0):.2f} s",
                f"main {vt.get('main_read_seconds', 0):.2f} s, "
                f"blur recovery {vt.get('recovery_read_seconds', 0):.2f} s",
            ),
            _report_row("Blur detection", f"{vt.get('blur_seconds', 0):.2f} s"),
            _report_row("CLAHE", f"{vt.get('clahe_seconds', 0):.2f} s", f"{vt.get('clahe_frames', 0)} frames"),
            _report_row("Tiling", f"{vt.get('tiling_seconds', 0):.2f} s", f"{vt.get('tiles_generated', 0):,} tiles"),
            _report_row("JPEG writing", f"{vt.get('jpeg_write_seconds', 0):.2f} s"),
        ]

    if ds:
        detect_ms = stage_ms.get("crowd_detection")
        summary_path = ds.get("summary_json_path") or ""
        try:
            summary_path = Path(summary_path).resolve().relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            pass
        lines += [
            "",
            _report_section("CROWD DETECTION", detect_ms / 1000 if detect_ms is not None else None),
            _report_row("Model", f"{ds.get('model')} ({ds.get('backend')} on {ds.get('device')})"),
            _report_row("Model load", f"{ds.get('model_load_seconds', 0):.2f} s"),
            _report_row(
                "Inference", f"{ds.get('total_detection_seconds', 0):.2f} s",
                f"{ds.get('frames_detected', 0)} of {ds.get('frames_processed', 0)} frames "
                f"(stride {ds.get('detect_stride')}), {ds.get('ms_per_detected_frame', 0):,.0f} ms each",
            ),
            _report_row("Frame I/O", f"{ds.get('frame_io_seconds', 0):.2f} s"),
            _report_row("Peak people", ds.get("peak_people_per_frame", 0)),
            _report_row("Summary", summary_path),
        ]

    if fire_result is not None:
        fire_dets = fire_result.get("detections") or []
        fire_frames = [d for d in fire_dets if d.get("fire_detected")]
        smoke_count = sum(1 for d in fire_dets if d.get("smoke_detected"))
        peak = max(fire_frames, key=lambda d: d.get("confidence") or 0, default=None)
        peak_text = (
            f"{peak.get('confidence') or 0:.2f} {peak.get('severity')} at "
            f"{peak.get('timestamp')} s (frame {peak.get('frame_id')})"
            if peak else "none"
        )
        lines += [
            "",
            _report_section("FIRE DETECTION"),
            _report_row("Fire frames", _report_count(len(fire_frames), len(fire_dets))),
            _report_row("Smoke frames", _report_count(smoke_count, len(fire_dets))),
            _report_row("Peak", peak_text),
        ]

    if stampede_result is not None:
        lines.append("")
        if not ENABLE_STAMPEDE:
            lines.append(f"{'STAMPEDE DETECTION':<21}skipped (CROWD_ENABLE_STAMPEDE=false)")
        else:
            events = stampede_result.get("detections") or []
            stampede_events = [e for e in events if e.get("stampede_detected")]
            peak = max(stampede_events, key=lambda e: e.get("confidence") or 0, default=None)
            peak_text = (
                f"{peak.get('confidence') or 0:.2f} {peak.get('severity')} at "
                f"{peak.get('timestamp')} s, {peak.get('crowd_count')} people moving "
                f"{peak.get('movement_direction')} at {peak.get('movement_speed')}"
                if peak else "none"
            )
            lines += [
                _report_section("STAMPEDE DETECTION"),
                _report_row("Events", len(events)),
                _report_row("Stampede events", len(stampede_events)),
                _report_row("Peak", peak_text),
            ]

    stage_labels = {"safety_detection": "safety_detection (fire + stampede)"}

    def timing_row(label: str, ms: float, indent: int) -> str:
        pct = f"{ms / 1000 / total_s:.0%}" if total_s else "-"
        return f"{' ' * indent}{label:<{40 - indent}}{ms / 1000:7.2f}{pct:>7}"

    lines += ["", f"{'STAGE TIMINGS':<40}{'s':>7}{'%':>7}"]
    # Sub-stages recorded inside "detection" are shown indented beneath it, so
    # they don't read as extra time on top of it.
    for label, ms in timings.items():
        lines.append(timing_row(stage_labels.get(label, label), ms, 2))
        if label == "detection":
            for sub_label, sub_ms in stage_ms.items():
                lines.append(timing_row(sub_label, sub_ms, 4))
    lines += [
        "  " + "-" * (_REPORT_WIDTH - 2),
        f"  {'TOTAL':<38}{total_s:7.2f}{'100%':>7}",
        "=" * _REPORT_WIDTH,
    ]

    print("\n".join(lines))


def _build_summary(detection_result: dict, behaviour_result: dict, risk_result: dict, analytics_result: dict) -> dict:
    frames = detection_result.get("frames", [])
    counts = [frame.get("person_count", 0) for frame in frames]
    zone_densities = analytics_result.get("zones", [])
    flagged_zones = [zone for zone in risk_result.get("zones", []) if zone.get("flagged")]

    highest_density_zone = max(zone_densities, key=lambda zone: zone.get("density", 0), default=None)
    highest_risk_zone = flagged_zones[0] if flagged_zones else None

    return {
        "total_frames_processed": len(frames),
        "peak_person_count": max(counts, default=0),
        "crowd_state": behaviour_result.get("crowd_state", "unknown"),
        "highest_density_zone": highest_density_zone.get("zone_id") if highest_density_zone else None,
        "highest_risk_zone": highest_risk_zone.get("zone_id") if highest_risk_zone else None,
    }


def _build_peak_crowd_frame(detection_result: dict) -> dict:
    frames = detection_result.get("frames", [])
    peak_frame = max(frames, key=lambda frame: frame.get("person_count", 0), default=None)
    if not peak_frame:
        return {}

    return {
        "frame_id": peak_frame.get("frame_id"),
        "timestamp": peak_frame.get("timestamp"),
        "person_count": peak_frame.get("person_count", 0),
        "people_annotated_frame_path": peak_frame.get("people_annotated_frame_path"),
    }


def _build_anomaly_visual(behaviour_result: dict) -> dict:
    artifact_paths = behaviour_result.get("artifact_paths") or []
    event_flags = behaviour_result.get("event_flags") or []
    activity_series = behaviour_result.get("frame_movement_summary") or behaviour_result.get("frame_activity_series", [])
    motion_artifacts = [
        path for path in artifact_paths
        if "motion_frame_" in path.replace("\\", "/")
    ]
    artifact_by_frame = {}
    for path in motion_artifacts:
        normalized_path = path.replace("\\", "/")
        frame_name = normalized_path.rsplit("/", 1)[-1]
        frame_token = frame_name.replace("motion_frame_", "").replace(".jpg", "")
        try:
            artifact_by_frame[int(frame_token)] = path
        except ValueError:
            continue

    preferred_frame = max(
        activity_series,
        key=lambda entry: (
            entry.get("walking_count", 0),
            entry.get("running_count", 0),
            entry.get("active_count", 0),
        ),
        default=None,
    )
    selected_path = None
    if preferred_frame:
        selected_path = artifact_by_frame.get(preferred_frame.get("frame_id"))
    if not selected_path:
        selected_path = motion_artifacts[0] if motion_artifacts else (artifact_paths[-1] if artifact_paths else None)
    if not selected_path:
        return {}

    if preferred_frame and preferred_frame.get("running_count", 0) > 0:
        event_type = "running_activity"
    elif preferred_frame and preferred_frame.get("walking_count", 0) > 0:
        event_type = "walking_or_running_activity"
    else:
        event_type = event_flags[0] if event_flags else "movement_alert"

    return {
        "event_type": event_type,
        "image_path": selected_path,
    }


def _build_time_series_chart(detection_result: dict, behaviour_result: dict, video_id: str | None) -> dict:
    frames = detection_result.get("frames", [])
    if not frames:
        return {}

    person_timestamps = [frame.get("timestamp", 0.0) for frame in frames]
    person_counts = [frame.get("person_count", 0) for frame in frames]

    output_dir = PROJECT_ROOT / "analytics_output" / "charts"
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_video_id = video_id or detection_result.get("video_id") or "unknown_video"
    output_path = output_dir / f"{safe_video_id}_crowd_activity_chart.png"

    figure, axis = plt.subplots(figsize=(10, 4.5))
    axis.plot(person_timestamps, person_counts, color="#1f77b4", linewidth=2.4)
    axis.set_xlabel("Time (s)")
    axis.set_ylabel("Person count")
    axis.grid(True, linestyle="--", alpha=0.35)

    figure.suptitle("Person Count Over Time")
    figure.tight_layout()
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)

    return {
        "image_path": str(output_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    }


def _build_density_extremes(analytics_result: dict, risk_result: dict) -> dict:
    risk_by_zone = {
        zone.get("zone_id"): zone
        for zone in risk_result.get("zones", [])
    }

    zone_insights = []
    for zone in analytics_result.get("zones", []):
        risk = risk_by_zone.get(zone.get("zone_id"), {})
        zone_insights.append({
            "zone_id": zone.get("zone_id"),
            "person_count": zone.get("person_count", 0),
            "density": _safe_round(zone.get("density", 0.0), 4),
            "risk_level": risk.get("risk_level", "unknown"),
            "flagged": risk.get("flagged", False),
        })

    if not zone_insights:
        return {
            "highest_density_zone": {},
            "lowest_density_zone": {},
        }

    highest_density_zone = max(zone_insights, key=lambda zone: zone.get("density", 0.0))
    lowest_density_zone = min(zone_insights, key=lambda zone: zone.get("density", 0.0))
    return {
        "highest_density_zone": highest_density_zone,
        "lowest_density_zone": lowest_density_zone,
    }


def process_crowd_detection(data: dict):
    """Run detection, analytics, and intelligence as one frontend-facing flow."""
    timings: dict[str, float] = {}

    with _timed("detection", timings, verbose=False):
        detection_result = process_detection(data)

    with _timed("analytics", timings, verbose=False):
        analytics_result = process_analytics(detection_result)

    with _timed("safety_detection", timings, verbose=False):
        safety_result = process_safety_detection(
            video_data=data,
            frame_data=detection_result,
            camera_id=data.get("camera_id", "CAM_02"),
            zone_id=data.get("zone_id", "ZONE_B"),
        )

    fire_result = safety_result["fire"]
    stampede_result = safety_result["stampede"]

    intelligence_input = {
        "video_id": data.get("video_id"),
        "zones": analytics_result.get("zones", []),
        "heatmap": analytics_result.get("heatmap", {}),
        "frames": detection_result.get("frames", []),
    }
    with _timed("behaviour", timings, verbose=False):
        behaviour_result = analyze_behaviour(intelligence_input)
    with _timed("risk", timings, verbose=False):
        risk_result = assess_risk(behaviour_result)

    with _timed("assemble", timings, verbose=False):
        payload = {
            "video_id": data.get("video_id"),
            "summary": _build_summary(detection_result, behaviour_result, risk_result, analytics_result),
            "peak_crowd_frame": _build_peak_crowd_frame(detection_result),
            "anomaly_visual": _build_anomaly_visual(behaviour_result),
            "heatmap": analytics_result.get("heatmap", {}),
            "time_series_chart": _build_time_series_chart(detection_result, behaviour_result, data.get("video_id")),
            "density_extremes": _build_density_extremes(analytics_result, risk_result),
        }

    with _timed("aggregation", timings, verbose=False):
        aggregated_result = aggregate_stadium_data(
            crowd_data=payload,
            fire_data=fire_result,
            stampede_data=stampede_result,
            stadium_id=data.get("stadium_id", "STADIUM_01"),
        )

    _print_benchmark_report(detection_result, timings, fire_result, stampede_result)
    payload["stage_timings_ms"] = timings

    return payload

def process_stadium_monitoring(data: dict):
    """Run crowd, fire, stampede, and stadium aggregation."""

    crowd_result = process_crowd_detection(data)

    detection_result = process_detection(data)

    safety_result = process_safety_detection(
        video_data=data,
        frame_data=detection_result,
        camera_id=data.get("camera_id", "CAM_02"),
        zone_id=data.get("zone_id", "ZONE_B"),
    )

    aggregated_result = aggregate_stadium_data(
        crowd_data=crowd_result,
        fire_data=safety_result["fire"],
        stampede_data=safety_result["stampede"],
        stadium_id=data.get("stadium_id", "STADIUM_01"),
    )

    return aggregated_result
