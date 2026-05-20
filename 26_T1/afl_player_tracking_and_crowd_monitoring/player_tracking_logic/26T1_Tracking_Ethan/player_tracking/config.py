from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class TrackingConfig:
    # =========================
    # Paths
    # =========================
    video_path: Path = Path("data/videos/video.mp4")
    model_path: Path = Path("models/model.pt")
    output_video_path: Path = Path("video_track.mp4")
    output_json_path: Path = Path("video_track.json")

    # =========================
    # Detection parameters
    # =========================
    player_classes: List[int] = field(default_factory=lambda: [0, 1])
    conf_threshold: float = 0.25
    imgsz: int = 640
    process_seconds: int = 40

    # =========================
    # Tracking parameters
    # =========================
    # Pixel distance is only one part of the matching logic.
    # IoU, direction and appearance are also used, so this can be larger than a pure distance tracker.
    max_distance: float = 120.0
    trail_length: int = 30
    max_missing: int = 15
    duplicate_center_distance: float = 35.0

    # If a new detection is close to an existing track but not confidently matched,
    # do not immediately create a new ID. This helps reduce duplicate IDs during overlap.
    new_track_suppression_distance: float = 60.0

    # =========================
    # Matching cost weights
    # =========================
    # Total cost = weighted sum of these four costs.
    # Smaller cost means better match.
    distance_weight: float = 0.45
    iou_weight: float = 0.25
    direction_weight: float = 0.15
    appearance_weight: float = 0.15

    match_cost_threshold: float = 0.85

    # If best match and second-best match are too close, the match is uncertain.
    # In that case, we skip updating instead of forcing a wrong ID assignment.
    ambiguity_margin: float = 0.08
    confident_cost_threshold: float = 0.45

    # =========================
    # Appearance update
    # =========================
    appearance_momentum: float = 0.8

    # =========================
    # Display/output
    # =========================
    draw_confidence: bool = True
    print_every_n_frames: int = 50
