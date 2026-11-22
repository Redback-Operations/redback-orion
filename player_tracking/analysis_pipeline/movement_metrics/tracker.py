"""Per-player track records built from the tracks CSV.

Each Track collects one player's boxes, appearance and jersey-colour samples
across frames. The IDs come from ByteTrack in detect_and_track.py.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from .appearance import update_appearance
from .config import TrackingConfig


@dataclass
class Track:
    track_id: int
    initial_class_id: int
    initial_class_name: str
    bbox: List[float]
    center: Tuple[float, float]
    appearance: Optional[np.ndarray]
    trail_length: int
    current_conf: float = 0.0
    current_detected_class_id: Optional[int] = None
    current_detected_class_name: Optional[str] = None
    previous_center: Optional[Tuple[float, float]] = None
    missing: int = 0
    age: int = 1
    hits: int = 1
    trail: List[Tuple[float, float]] = field(default_factory=list)
    frames: List[Dict] = field(default_factory=list)
    jersey_features: List[np.ndarray] = field(default_factory=list)
    cluster_id: Optional[int] = None
    cluster_team: str = "Unknown"

    def __post_init__(self):
        if not self.trail:
            self.trail = [self.center]

    def update(self, detection: Dict, frame_index: int, time_sec: float, appearance_momentum: float):
        self.previous_center = self.center
        self.bbox = [float(v) for v in detection["bbox"]]
        self.center = tuple(float(v) for v in detection["center"])
        self.current_conf = float(detection["conf"])
        self.current_detected_class_id = int(detection["class_id"])
        self.current_detected_class_name = str(detection["class_name"])
        self.appearance = update_appearance(self.appearance, detection.get("appearance"), appearance_momentum)

        jersey_feature = detection.get("jersey_feature")
        if jersey_feature is not None:
            self.jersey_features.append(np.asarray(jersey_feature, dtype=np.float32))

        self.missing = 0
        self.age += 1
        self.hits += 1

        self.trail.append(self.center)
        if len(self.trail) > self.trail_length:
            self.trail = self.trail[-self.trail_length :]

        self.frames.append(
            {
                "frame_index": int(frame_index),
                "time_sec": float(time_sec),
                "bbox": [float(v) for v in self.bbox],
                "center": [float(self.center[0]), float(self.center[1])],
                "ground_point": (
                    [float(v) for v in detection["ground_point"]]
                    if detection.get("ground_point") is not None
                    else None
                ),
                "confidence": float(self.current_conf),
                "detected_class_id": int(self.current_detected_class_id),
                "detected_class_name": str(self.current_detected_class_name),
                "fixed_initial_class_id": int(self.initial_class_id),
                "fixed_initial_class_name": str(self.initial_class_name),
                "cluster_id": None,
                "cluster_team": "Unknown",
            }
        )

    def mark_missing(self):
        self.missing += 1
        self.age += 1

    def representative_jersey_feature(self) -> Optional[np.ndarray]:
        if not self.jersey_features:
            return None
        return np.median(np.stack(self.jersey_features, axis=0), axis=0).astype(np.float32)

    def apply_cluster_to_frames(self):
        for frame_record in self.frames:
            frame_record["cluster_id"] = None if self.cluster_id is None else int(self.cluster_id)
            frame_record["cluster_team"] = str(self.cluster_team)


def track_from_detection(track_id: int, detection: Dict, frame_index: int, time_sec: float,
                         config: TrackingConfig) -> Track:
    """Start a new track from its first detection."""
    track = Track(
        track_id=int(track_id),
        initial_class_id=int(detection["class_id"]),
        initial_class_name=str(detection["class_name"]),
        bbox=[float(v) for v in detection["bbox"]],
        center=tuple(float(v) for v in detection["center"]),
        appearance=detection.get("appearance"),
        trail_length=config.trail_length,
        current_conf=float(detection["conf"]),
        current_detected_class_id=int(detection["class_id"]),
        current_detected_class_name=str(detection["class_name"]),
    )
    track.update(detection, frame_index, time_sec, config.appearance_momentum)
    return track


def tracks_to_json_records(tracks: Dict[int, Track]) -> Dict:
    records = {}
    for track_id, track in sorted(tracks.items(), key=lambda item: item[0]):
        representative = track.representative_jersey_feature()
        records[str(track_id)] = {
            "track_id": int(track.track_id),
            "initial_class_id": int(track.initial_class_id),
            "initial_class_name": str(track.initial_class_name),
            "cluster_id": None if track.cluster_id is None else int(track.cluster_id),
            "cluster_team": str(track.cluster_team),
            "jersey_sample_count": int(len(track.jersey_features)),
            "representative_jersey_feature": None
            if representative is None
            else [float(v) for v in representative.tolist()],
            "frames": track.frames,
            "num_observed_frames": int(len(track.frames)),
        }
    return records
