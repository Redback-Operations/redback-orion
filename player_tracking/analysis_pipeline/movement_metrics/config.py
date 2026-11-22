from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple


Point = Tuple[float, float]


@dataclass
class TrackingConfig:
    # =========================
    # Paths
    # =========================
    # Your current project input paths.
    video_path: Path = Path("data/videos/video.mp4")
    model_path: Path = Path("models/best(SSvsWB).pt")

    # All generated files are saved in outputs/ by default.
    output_video_path: Path = Path("outputs/video_track_clustered.mp4")
    output_json_path: Path = Path("outputs/video_track_clustered.json")
    output_csv_path: Path = Path("outputs/player_metrics.csv")

    # =========================
    # Detection parameters
    # =========================
    player_classes: List[int] = field(default_factory=lambda: [0])
    conf_threshold: float = 0.25
    imgsz: int = 640
    process_seconds: int = 40

    # =========================
    # Tracking parameters
    # =========================
    # Pixel distance is only one part of the matching logic.
    # IoU, direction and appearance are also used.
    max_distance: float = 120.0
    trail_length: int = 30
    max_missing: int = 15
    duplicate_center_distance: float = 35.0

    # If a new detection is close to an existing track but not confidently
    # matched, do not immediately create a new ID.
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

    # If the best and second-best matches are too close,
    # skip the uncertain match rather than forcing an ID assignment.
    ambiguity_margin: float = 0.08
    confident_cost_threshold: float = 0.45

    # =========================
    # Appearance / jersey colour
    # =========================
    appearance_momentum: float = 0.8

    # Jersey clustering is performed offline after tracking.
    jersey_clusters: int = 3
    min_samples_per_track: int = 5
    kmeans_random_state: int = 42

    # =========================
    # Metrics
    # =========================
    # Fallback conversion used when field calibration is unavailable.
    # This remains an approximate image-space conversion.
    pixel_to_meter: float = 0.05
    max_speed_kmh: float = 40.0

    # Optional image-to-field calibration.
    #
    # image_calibration_points:
    #     Landmark coordinates in the video frame, in pixels.
    #
    # field_calibration_points:
    #     Matching landmark coordinates on the field, in metres.
    #
    # At least four matching point pairs are required.
    # Leave both as None to keep the existing image-space metric behaviour.
    image_calibration_points: Optional[List[Point]] = None
    field_calibration_points: Optional[List[Point]] = None

    # =========================
    # Display/output
    # =========================
    draw_confidence: bool = True
    draw_cluster: bool = False
    print_every_n_frames: int = 50