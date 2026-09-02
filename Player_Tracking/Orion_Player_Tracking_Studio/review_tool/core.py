from __future__ import annotations

import csv
import json
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Iterable


@dataclass
class TrackRow:
    frame: int
    track_id: str
    class_name: str
    confidence: float
    x1: float = 0
    y1: float = 0
    x2: float = 0
    y2: float = 0


@dataclass
class TrackSummary:
    track_id: str
    first_frame: int
    last_frame: int
    detections: int
    mean_confidence: float
    class_name: str
    team: str = "Unassigned"
    jumper: str = ""
    stable_id: str = ""
    status: str = "Needs review"


@dataclass
class ReviewEvent:
    kind: str
    frame: int
    timestamp: str
    detail: str
    status: str = "Needs review"


@dataclass
class ReviewProject:
    video_path: str = ""
    annotated_video_path: str = ""
    csv_path: str = ""
    model_path: str = ""
    fps: float = 25.0
    rows: list[TrackRow] = field(default_factory=list)
    tracks: dict[str, TrackSummary] = field(default_factory=dict)
    events: list[ReviewEvent] = field(default_factory=list)
    manual_merges: dict[str, str] = field(default_factory=dict)

    def load_csv(self, path: str | Path) -> None:
        csv_path = Path(path)
        self.csv_path = str(csv_path)
        self.rows = read_tracking_csv(csv_path)
        self.tracks = summarise_tracks(self.rows)
        self.events = find_review_events(self.rows, self.fps)
        self.resolve_identities()

    def set_track_value(self, track_id: str, field_name: str, value: str) -> None:
        track = self.tracks[track_id]
        if field_name == "team":
            track.team = value.strip() or "Unassigned"
        elif field_name == "jumper":
            track.jumper = value.strip()
        elif field_name == "status":
            track.status = value
        else:
            raise ValueError(f"Unsupported field: {field_name}")
        self.resolve_identities()

    def merge_tracks(self, track_ids: Iterable[str], stable_id: str) -> None:
        chosen = stable_id.strip()
        if not chosen:
            raise ValueError("Enter an identity name first")
        for track_id in track_ids:
            self.manual_merges[track_id] = chosen
        self.resolve_identities()

    def resolve_identities(self) -> None:
        groups: defaultdict[tuple[str, str], list[TrackSummary]] = defaultdict(list)
        for track in self.tracks.values():
            if track.jumper and track.team != "Unassigned":
                groups[(track.team, track.jumper)].append(track)

        for track in self.tracks.values():
            if track.track_id in self.manual_merges:
                track.stable_id = self.manual_merges[track.track_id]
                continue
            if track.jumper and track.team != "Unassigned":
                candidate = f"{track.team} {track.jumper}".strip()
                peers = groups[(track.team, track.jumper)]
                has_overlap = any(
                    peer.track_id != track.track_id
                    and not (peer.last_frame < track.first_frame or track.last_frame < peer.first_frame)
                    for peer in peers
                )
                track.stable_id = f"{candidate} review" if has_overlap else candidate
            else:
                track.stable_id = f"Track {track.track_id}"

    def export(self, folder: str | Path) -> dict[str, Path]:
        target = Path(folder)
        target.mkdir(parents=True, exist_ok=True)
        tracks_path = target / "reviewed_tracks.csv"
        events_path = target / "review_events.csv"
        project_path = target / "review_project.json"

        with tracks_path.open("w", newline="", encoding="utf-8") as handle:
            fields = list(TrackSummary.__dataclass_fields__)
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(asdict(track) for track in self.tracks.values())

        with events_path.open("w", newline="", encoding="utf-8") as handle:
            fields = list(ReviewEvent.__dataclass_fields__)
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(asdict(event) for event in self.events)

        data = {
            "video_path": self.video_path,
            "annotated_video_path": self.annotated_video_path,
            "csv_path": self.csv_path,
            "model_path": self.model_path,
            "fps": self.fps,
            "manual_merges": self.manual_merges,
            "tracks": [asdict(track) for track in self.tracks.values()],
            "events": [asdict(event) for event in self.events],
        }
        project_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return {"tracks": tracks_path, "events": events_path, "project": project_path}


def _pick(row: dict[str, str], *names: str, default: str = "") -> str:
    lowered = {key.casefold(): value for key, value in row.items() if key}
    for name in names:
        if name.casefold() in lowered and lowered[name.casefold()] not in (None, ""):
            return str(lowered[name.casefold()])
    return default


def read_tracking_csv(path: Path) -> list[TrackRow]:
    rows: list[TrackRow] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for line_number, source in enumerate(reader, start=2):
            try:
                rows.append(TrackRow(
                    frame=int(float(_pick(source, "frame", "frame_id", "frame_number"))),
                    track_id=_pick(source, "track_id", "player_id", "id"),
                    class_name=_pick(source, "class", "class_name", "label", default="PLAYER"),
                    confidence=float(_pick(source, "confidence", "conf", default="1")),
                    x1=float(_pick(source, "x1", default="0")),
                    y1=float(_pick(source, "y1", default="0")),
                    x2=float(_pick(source, "x2", default="0")),
                    y2=float(_pick(source, "y2", default="0")),
                ))
            except ValueError as exc:
                raise ValueError(f"Invalid tracking value on CSV line {line_number}") from exc
    if not rows:
        raise ValueError("The tracking CSV has no detections")
    if any(not row.track_id for row in rows):
        raise ValueError("The tracking CSV is missing a track ID")
    return rows


def summarise_tracks(rows: list[TrackRow]) -> dict[str, TrackSummary]:
    grouped: defaultdict[str, list[TrackRow]] = defaultdict(list)
    for row in rows:
        grouped[row.track_id].append(row)
    summaries: dict[str, TrackSummary] = {}
    for track_id, items in grouped.items():
        classes = Counter(item.class_name for item in items)
        class_name = classes.most_common(1)[0][0]
        team = class_name if class_name.upper() not in {"PLAYER", "PERSON", "REF", "REFEREE", "UMPIRE"} else "Unassigned"
        summaries[track_id] = TrackSummary(
            track_id=track_id,
            first_frame=min(item.frame for item in items),
            last_frame=max(item.frame for item in items),
            detections=len(items),
            mean_confidence=statistics.fmean(item.confidence for item in items),
            class_name=class_name,
            team=team,
        )
    return summaries


def format_timestamp(frame: int, fps: float) -> str:
    seconds = max(0, int(frame / max(fps, 1)))
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def find_review_events(rows: list[TrackRow], fps: float) -> list[ReviewEvent]:
    events: list[ReviewEvent] = []
    grouped: defaultdict[str, list[TrackRow]] = defaultdict(list)
    counts: Counter[int] = Counter()
    confidences: defaultdict[int, list[float]] = defaultdict(list)
    for row in rows:
        grouped[row.track_id].append(row)
        counts[row.frame] += 1
        confidences[row.frame].append(row.confidence)

    short_limit = max(1, round(fps))
    for track_id, items in grouped.items():
        ordered = sorted(items, key=lambda item: item.frame)
        span = ordered[-1].frame - ordered[0].frame + 1
        if span <= short_limit:
            frame = ordered[0].frame
            events.append(ReviewEvent("Short track", frame, format_timestamp(frame, fps), f"Track {track_id} lasted {span} frames"))
        for previous, current in zip(ordered, ordered[1:]):
            if current.frame - previous.frame > 1 and current.class_name != previous.class_name:
                events.append(ReviewEvent(
                    "Possible reassociation", current.frame, format_timestamp(current.frame, fps),
                    f"Track {track_id} returned as {current.class_name}",
                ))

    ordered_frames = sorted(counts)
    for previous, current in zip(ordered_frames, ordered_frames[1:]):
        if current != previous + 1:
            continue
        change = counts[current] - counts[previous]
        if abs(change) >= 4:
            events.append(ReviewEvent("Detection count change", current, format_timestamp(current, fps), f"Count changed from {counts[previous]} to {counts[current]}"))

    low_frames = sorted(
        ((statistics.fmean(values), frame) for frame, values in confidences.items()),
        key=lambda value: value[0],
    )[:10]
    for mean_confidence, frame in low_frames:
        if mean_confidence < 0.45:
            events.append(ReviewEvent("Confidence drop", frame, format_timestamp(frame, fps), f"Mean confidence {mean_confidence:.2f}"))

    events.sort(key=lambda event: (event.frame, event.kind))
    return events


def run_ocr(
    image_paths: dict[str, list[Path]],
    progress: Callable[[str], None] | None = None,
) -> dict[str, str]:
    try:
        import easyocr
    except ImportError as exc:
        raise RuntimeError("EasyOCR is not installed. Jumper numbers can still be entered manually.") from exc

    reader = easyocr.Reader(["en"], gpu=False)
    answers: dict[str, str] = {}
    for track_id, paths in image_paths.items():
        votes: Counter[str] = Counter()
        for path in paths:
            if progress:
                progress(f"Reading jumper numbers for track {track_id}")
            results = reader.readtext(str(path), allowlist="0123456789", detail=1)
            for _, text, confidence in results:
                cleaned = "".join(char for char in text if char.isdigit())
                if cleaned and len(cleaned) <= 2 and confidence >= 0.25:
                    votes[cleaned] += 1
        if votes:
            answers[track_id] = votes.most_common(1)[0][0]
    return answers
