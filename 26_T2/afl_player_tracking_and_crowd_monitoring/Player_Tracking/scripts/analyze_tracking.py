#!/usr/bin/env python3
"""Create a lightweight quality report from a tracking CSV.

The report surfaces likely problem sections without requiring someone to watch
an entire broadcast. Metrics that depend on ground-truth player identity are
labelled as proxies; this tool does not claim to measure true ID switches.

It also flags suspected track re-associations where the same track ID
disappears for one or more frames and later returns with a different class.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = {"frame", "track_id", "class", "confidence"}


@dataclass
class TrackStats:
    first_frame: int
    last_frame: int
    detections: int = 0
    confidence_sum: float = 0.0
    min_confidence: float = 1.0

    def add(self, frame: int, confidence: float) -> None:
        self.first_frame = min(self.first_frame, frame)
        self.last_frame = max(self.last_frame, frame)
        self.detections += 1
        self.confidence_sum += confidence
        self.min_confidence = min(self.min_confidence, confidence)


def timestamp(frame: int, fps: float) -> str:
    total_seconds = max(0, int(frame / fps))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def percentile(values: list[float], percent: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * percent
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - index) + ordered[upper] * (index - lower)


def detect_suspected_reassociations(
    rows_by_track: dict[str, list[dict[str, str]]],
    *,
    fps: float,
) -> list[dict[str, Any]]:
    """Find class changes that occur after the same track ID disappears.

    These events are review candidates only. Without ground-truth player
    identities they cannot be treated as confirmed ID switches.
    """
    events: list[dict[str, Any]] = []

    for track_id, track_rows in rows_by_track.items():
        ordered = sorted(track_rows, key=lambda row: int(row["frame"]))

        for previous, current in zip(ordered, ordered[1:]):
            previous_frame = int(previous["frame"])
            current_frame = int(current["frame"])

            frame_gap = current_frame - previous_frame

            # Consecutive detections are normal tracking behaviour.
            if frame_gap <= 1:
                continue

            previous_class = previous["class"].strip()
            current_class = current["class"].strip()

            # We are specifically interested in a class change after a gap.
            if previous_class == current_class:
                continue

            missing_frames = frame_gap - 1

            events.append({
                "track_id": track_id,
                "last_seen_frame": previous_frame,
                "reappeared_frame": current_frame,
                "missing_frames": missing_frames,
                "gap_seconds": round(missing_frames / fps, 3),
                "previous_class": previous_class,
                "new_class": current_class,
                "previous_confidence": round(float(previous["confidence"]), 3),
                "new_confidence": round(float(current["confidence"]), 3),
            })

    events.sort(
        key=lambda event: (
            -event["missing_frames"],
            event["last_seen_frame"],
        )
    )
    return events


def analyze_csv(
    csv_path: Path,
    *,
    fps: float,
    class_name: str | None,
    short_track_seconds: float,
    low_confidence: float,
    count_jump: int,
    worst_limit: int,
) -> dict[str, Any]:
    tracks: dict[tuple[str, str], TrackStats] = {}
    rows_by_track: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    frame_counts: Counter[int] = Counter()
    frame_confidence_sum: defaultdict[int, float] = defaultdict(float)
    frame_low_confidence: Counter[int] = Counter()
    class_counts: Counter[str] = Counter()
    first_frame: int | None = None
    last_frame: int | None = None
    rows = 0

    with csv_path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"Missing required CSV columns: {', '.join(sorted(missing))}")

        for line_number, row in enumerate(reader, start=2):
            try:
                frame = int(row["frame"])
                confidence = float(row["confidence"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid frame/confidence at CSV line {line_number}") from exc

            detected_class = row["class"].strip()
            if class_name and detected_class.casefold() != class_name.casefold():
                continue

            track_id = row["track_id"].strip()
            key = (detected_class, track_id)
            if key not in tracks:
                tracks[key] = TrackStats(frame, frame)
            tracks[key].add(frame, confidence)

            # Keep observations grouped by ByteTrack ID so that gaps followed
            # by class changes can be reviewed as possible re-associations.
            rows_by_track[track_id].append(row)

            rows += 1
            class_counts[detected_class] += 1
            frame_counts[frame] += 1
            frame_confidence_sum[frame] += confidence
            if confidence < low_confidence:
                frame_low_confidence[frame] += 1
            first_frame = frame if first_frame is None else min(first_frame, frame)
            last_frame = frame if last_frame is None else max(last_frame, frame)

    if not rows or first_frame is None or last_frame is None:
        raise ValueError("No tracking rows matched the selected class filter")

    suspected_reassociations = detect_suspected_reassociations(
        rows_by_track,
        fps=fps,
    )

    short_limit_frames = max(1, round(short_track_seconds * fps))
    spans = [stats.last_frame - stats.first_frame + 1 for stats in tracks.values()]
    short_tracks = {
        key: stats for key, stats in tracks.items()
        if stats.last_frame - stats.first_frame + 1 <= short_limit_frames
    }
    duration_frames = last_frame - first_frame + 1
    duration_minutes = duration_frames / fps / 60

    count_events = []
    previous_count = frame_counts.get(first_frame, 0)
    for frame in range(first_frame + 1, last_frame + 1):
        current_count = frame_counts.get(frame, 0)
        difference = current_count - previous_count
        if abs(difference) >= count_jump:
            count_events.append({
                "frame": frame,
                "timestamp": timestamp(frame, fps),
                "previous_count": previous_count,
                "count": current_count,
                "change": difference,
            })
        previous_count = current_count
    count_events.sort(key=lambda event: (-abs(event["change"]), event["frame"]))

    second_windows: dict[int, dict[str, float]] = defaultdict(
        lambda: {"detections": 0, "confidence_sum": 0.0, "low": 0, "min_count": math.inf,
                 "max_count": 0, "short_starts": 0}
    )
    for frame in range(first_frame, last_frame + 1):
        second = int(frame / fps)
        count = frame_counts.get(frame, 0)
        bucket = second_windows[second]
        bucket["detections"] += count
        bucket["confidence_sum"] += frame_confidence_sum.get(frame, 0.0)
        bucket["low"] += frame_low_confidence.get(frame, 0)
        bucket["min_count"] = min(bucket["min_count"], count)
        bucket["max_count"] = max(bucket["max_count"], count)
    for stats in short_tracks.values():
        second_windows[int(stats.first_frame / fps)]["short_starts"] += 1

    worst_windows = []
    for second, bucket in second_windows.items():
        detections = int(bucket["detections"])
        mean_confidence = bucket["confidence_sum"] / detections if detections else 0.0
        low_rate = bucket["low"] / detections if detections else 1.0
        count_range = int(bucket["max_count"] - bucket["min_count"])
        # Transparent triage score, not a model accuracy metric.
        score = 3 * bucket["short_starts"] + 2 * low_rate + count_range / max(1, count_jump)
        worst_windows.append({
            "second": second,
            "timestamp": timestamp(round(second * fps), fps),
            "score": round(score, 3),
            "mean_confidence": round(mean_confidence, 3),
            "low_confidence_rate": round(low_rate, 3),
            "player_count_range": count_range,
            "short_track_starts": int(bucket["short_starts"]),
        })
    worst_windows.sort(key=lambda window: (-window["score"], window["second"]))

    frame_mean_confidences = [
        frame_confidence_sum[frame] / count
        for frame, count in frame_counts.items() if count
    ]

    report = {
        "input": str(csv_path),
        "settings": {
            "fps": fps,
            "class_filter": class_name,
            "short_track_seconds": short_track_seconds,
            "low_confidence_threshold": low_confidence,
            "count_jump_threshold": count_jump,
        },
        "summary": {
            "first_frame": first_frame,
            "last_frame": last_frame,
            "duration_seconds": round(duration_frames / fps, 3),
            "detections": rows,
            "unique_tracks": len(tracks),
            "tracks_per_minute_proxy": round(len(tracks) / duration_minutes, 3),
            "short_lived_tracks": len(short_tracks),
            "short_lived_track_rate": round(len(short_tracks) / len(tracks), 4),
            "mean_frame_confidence": round(statistics.fmean(frame_mean_confidences), 4),
            "count_jump_events": len(count_events),
            "suspected_reassociations": len(suspected_reassociations),
        },
        "classes": dict(class_counts.most_common()),
        "track_span_frames": {
            "median": round(percentile([float(value) for value in spans], 0.5), 1),
            "p10": round(percentile([float(value) for value in spans], 0.1), 1),
            "p90": round(percentile([float(value) for value in spans], 0.9), 1),
        },
        "largest_count_jumps": count_events[:worst_limit],
        "worst_timestamps": worst_windows[:worst_limit],
        "suspected_reassociations": suspected_reassociations[:worst_limit],
        "notes": [
            "Short-lived tracks and tracks-per-minute are fragmentation proxies, not true ID-switch counts.",
            "Suspected re-associations are class changes after a tracking gap and require visual confirmation.",
            "Camera cuts, replays and graphics can produce legitimate player-count changes.",
            "Use the worst timestamps and suspected re-associations as a review queue.",
        ],
    }
    return report


def format_markdown(reports: list[dict[str, Any]]) -> str:
    lines = ["# Tracking quality report", ""]
    for report in reports:
        summary = report["summary"]
        lines.extend([
            f"## {Path(report['input']).name}", "",
            f"Class filter: `{report['settings']['class_filter'] or 'all'}`  ",
            f"Analysed: `{timestamp(summary['first_frame'], report['settings']['fps'])}` to "
            f"`{timestamp(summary['last_frame'], report['settings']['fps'])}`  ",
            "",
            "| Metric | Value |", "| --- | ---: |",
            f"| Detections | {summary['detections']:,} |",
            f"| Unique track IDs | {summary['unique_tracks']:,} |",
            f"| Tracks/minute (fragmentation proxy) | {summary['tracks_per_minute_proxy']:.2f} |",
            f"| Short-lived tracks | {summary['short_lived_tracks']:,} "
            f"({summary['short_lived_track_rate']:.1%}) |",
            f"| Mean frame confidence | {summary['mean_frame_confidence']:.3f} |",
            f"| Sudden count-change events | {summary['count_jump_events']:,} |",
            f"| Suspected re-associations | {summary['suspected_reassociations']:,} |",
            "", "### Suspected re-associations", "",
            "| Track ID | Last seen | Reappeared | Missing frames | Previous class | New class |",
            "| --- | ---: | ---: | ---: | --- | --- |",
        ])

        for event in report["suspected_reassociations"]:
            lines.append(
                f"| {event['track_id']} | {event['last_seen_frame']} | "
                f"{event['reappeared_frame']} | {event['missing_frames']} | "
                f"{event['previous_class']} | {event['new_class']} |"
            )

        lines.extend([
            "", "### Worst timestamps", "",
            "| Timestamp | Triage score | Mean confidence | Low-confidence rate | "
            "Count range | Short-track starts |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ])
        for item in report["worst_timestamps"]:
            lines.append(
                f"| {item['timestamp']} | {item['score']:.3f} | {item['mean_confidence']:.3f} | "
                f"{item['low_confidence_rate']:.1%} | {item['player_count_range']} | "
                f"{item['short_track_starts']} |"
            )
        lines.extend(["", "### Interpretation", ""])
        lines.extend(f"- {note}" for note in report["notes"])
        lines.append("")

    if len(reports) == 2:
        baseline, candidate = reports
        lines.extend([
            "## Baseline vs candidate", "",
            "Positive changes below mean the candidate produced a larger value.", "",
            "| Metric | Baseline | Candidate | Change |", "| --- | ---: | ---: | ---: |",
        ])
        for key, label in [
            ("unique_tracks", "Unique track IDs"),
            ("tracks_per_minute_proxy", "Tracks/minute proxy"),
            ("short_lived_track_rate", "Short-lived track rate"),
            ("mean_frame_confidence", "Mean frame confidence"),
            ("count_jump_events", "Count-change events"),
            ("suspected_reassociations", "Suspected re-associations"),
        ]:
            before = baseline["summary"][key]
            after = candidate["summary"][key]
            lines.append(f"| {label} | {before:.4g} | {after:.4g} | {after - before:+.4g} |")
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="candidate tracking CSV")
    parser.add_argument("--baseline", type=Path, help="optional baseline CSV for comparison")
    parser.add_argument("--fps", type=float, default=25.0)
    parser.add_argument("--class-name", default="PLAYER",
                        help="case-insensitive class filter; use ALL to disable")
    parser.add_argument("--short-track-seconds", type=float, default=1.0)
    parser.add_argument("--low-confidence", type=float, default=0.25)
    parser.add_argument("--count-jump", type=int, default=8)
    parser.add_argument("--worst-limit", type=int, default=20)
    parser.add_argument("--output-prefix", type=Path, default=Path("tracking_quality"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.fps <= 0 or args.short_track_seconds <= 0 or args.count_jump <= 0:
        raise SystemExit("fps, short-track-seconds and count-jump must be positive")

    class_name = None if args.class_name.casefold() == "all" else args.class_name
    inputs = ([args.baseline] if args.baseline else []) + [args.csv]

    reports = [
        analyze_csv(
            path,
            fps=args.fps,
            class_name=class_name,
            short_track_seconds=args.short_track_seconds,
            low_confidence=args.low_confidence,
            count_jump=args.count_jump,
            worst_limit=args.worst_limit,
        )
        for path in inputs
    ]

    json_path = args.output_prefix.with_suffix(".json")
    markdown_path = args.output_prefix.with_suffix(".md")
    json_path.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(
        json.dumps({"reports": reports}, indent=2) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(
        format_markdown(reports),
        encoding="utf-8",
    )

    print(f"Wrote {markdown_path}")
    print(f"Wrote {json_path}")


if __name__ == "__main__":
    main()