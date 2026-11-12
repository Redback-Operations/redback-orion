#!/usr/bin/env python3
"""Smart OpenCV labeller for broadcast AFL videos.

Quickly build a player/referee detection dataset from broadcast footage by
using a generic COCO YOLO person detector and colour-based player/referee
classification, then reviewing and correcting the results in an OpenCV GUI.

Batch mode can filter out bad frames automatically (transitions, close-ups,
static shots) so you only keep useful gameplay frames.

Usage examples:
    # Interactive labelling of one broadcast video (uses COCO yolov8s by default)
    python scripts/smart_labeller.py data/videos/broadcast_stkilda_northmelbourne.mp4

    # Batch auto-label every 30th frame into data/raw/<video_name>/
    python scripts/smart_labeller.py data/videos/broadcast_*.mp4 \
        --auto --stride 30

    # Keep only good gameplay frames (skip close-ups, transitions, static shots)
    python scripts/smart_labeller.py data/videos/broadcast_*.mp4 \
        --auto --stride 30 \
        --min-detections 8 --max-detections 28 --max-box-area-ratio 0.35

    # Use a stronger person detector (e.g. yolov8m / yolov8x)
    python scripts/smart_labeller.py data/videos/broadcast_*.mp4 \
        --auto --model yolov8m.pt

    # Override output location for all videos
    python scripts/smart_labeller.py data/videos/broadcast_*.mp4 \
        --auto --stride 30 --output-dir datasets/player_ref/train

    # Resume / extend an existing dataset
    python scripts/smart_labeller.py data/videos/broadcast_brisbane_portadelaide.mp4 \
        --start-frame 5000

    # Review saved labels for a video (skips unlabelled frames)
    python scripts/smart_labeller.py data/videos/broadcast_stkilda_northmelbourne.mp4 \
        --review

    # Continue a review session you already started (first 84 frames done)
    python scripts/smart_labeller.py data/videos/broadcast_stkilda_northmelbourne.mp4 \
        --review --reviewed-up-to 84

    # Split labelled frames into reviewed/ and unreviewed/ subfolders
    python scripts/smart_labeller.py data/videos/broadcast_stkilda_northmelbourne.mp4 \
        --split

Keyboard controls (interactive mode):
    a           Auto-detect people on the current frame
    n / ->      Next frame (marks frame as reviewed in review mode)
    p / <-      Previous frame
    . / ,       Select next / previous box (useful if mouse clicks fail)
    d           Delete selected box
    D           Delete ALL boxes in current frame
    x           Delete current frame files from disk (label + image)
    m           Mark current frame as reviewed
    u           Mark current frame as unreviewed
    0/1         Set selected box class: 0=player, 1=ref
    r           Run auto-labelling on the whole video with the current stride
    s           Save labels for the current frame (also marks reviewed)
    S           Save all cached labels to disk now
    + / -       Increase / decrease frame stride
    space       Play / pause
    q / esc     Quit

Mouse controls:
    Left drag     Draw a new bounding box
    Left click    Select the box under the cursor
    Right click   Delete the box under the cursor
"""

from __future__ import annotations

import argparse
import glob
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    tqdm = None  # type: ignore

import cv2
import numpy as np

try:
    from ultralytics import YOLO
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "ultralytics is required. Install it with: pip install ultralytics"
    ) from exc


ROOT = Path(__file__).resolve().parent.parent

# Class indices used for the player_ref dataset (only 2 classes).
CLASS_PLAYER = 0
CLASS_REFEREE = 1

CLASS_NAMES = {
    CLASS_PLAYER: "player",
    CLASS_REFEREE: "ref",
}

CLASS_COLOURS = {
    CLASS_PLAYER: (0, 165, 255),    # orange
    CLASS_REFEREE: (0, 255, 255),   # yellow
}

SELECTED_COLOUR = (0, 255, 0)

DEFAULT_MODEL = Path("yolov8s.pt")  # COCO person detector; ultralytics auto-downloads it
DEFAULT_CONF = 0.35
DEFAULT_STRIDE = 30
DEFAULT_IMGSZ = 640

MIN_BOX_WIDTH = 10
MIN_BOX_HEIGHT = 25

# Quality-filter defaults for batch auto-labelling.
DEFAULT_MIN_DETECTIONS = 8
DEFAULT_MAX_DETECTIONS = 28
DEFAULT_MAX_BOX_AREA_RATIO = 0.35
DEFAULT_SCENE_THRESHOLD = 8.0

# HSV ranges tuned for AFL umpire tops.
YELLOW_LOWER = np.array([18, 80, 80])
YELLOW_UPPER = np.array([48, 255, 255])


def _is_person_class(name: str) -> bool:
    """Return True for classes that represent a person/player/ref/umpire."""
    low = name.lower()
    return any(k in low for k in ("person", "people", "human", "player", "ref", "umpire"))


def _is_explicit_referee_class(name: str) -> bool:
    """Return True only when the model itself labels the box as referee/umpire."""
    low = name.lower()
    return "ref" in low or "umpire" in low


def _colour_ratio(hsv: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> float:
    if hsv.size == 0:
        return 0.0
    mask = cv2.inRange(hsv, lower, upper)
    return float(cv2.countNonZero(mask)) / (hsv.shape[0] * hsv.shape[1])


def _torso_roi(frame: np.ndarray, x1: float, y1: float, x2: float, y2: float) -> Optional[np.ndarray]:
    h, w = frame.shape[:2]
    x1, y1 = max(0, int(x1)), max(0, int(y1))
    x2, y2 = min(w, int(x2)), min(h, int(y2))
    if x2 <= x1 or y2 <= y1:
        return None
    box_w = x2 - x1
    box_h = y2 - y1
    rx1 = x1 + int(box_w * 0.25)
    rx2 = x1 + int(box_w * 0.75)
    ry1 = y1 + int(box_h * 0.20)
    ry2 = y1 + int(box_h * 0.55)
    roi = frame[ry1:ry2, rx1:rx2]
    return roi if roi.size > 0 else None


def _infer_referee_by_colour(frame: np.ndarray, x1: float, y1: float, x2: float, y2: float) -> bool:
    """Return True if the torso is predominantly yellow (AFL umpire kit)."""
    roi = _torso_roi(frame, x1, y1, x2, y2)
    if roi is None:
        return False
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    h_channel, s_channel, v_channel = cv2.split(hsv)
    valid_mask = (s_channel > 35) & (v_channel > 35)
    valid_pixels = hsv[valid_mask]
    if len(valid_pixels) < 15:
        return False
    yellow_ratio = _colour_ratio(hsv, YELLOW_LOWER, YELLOW_UPPER)
    median_s = float(np.median(valid_pixels[:, 1]))
    median_v = float(np.median(valid_pixels[:, 2]))
    return yellow_ratio > 0.25 and median_s > 40 and median_v > 60


def _box_iou(a: Tuple[float, float, float, float], b: Tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    union = area_a + area_b - inter_area
    return inter_area / union if union > 0 else 0.0


def _xyxy_to_yolo(x1: float, y1: float, x2: float, y2: float, w: int, h: int) -> Tuple[float, float, float, float]:
    x_center = ((x1 + x2) / 2.0) / w
    y_center = ((y1 + y2) / 2.0) / h
    bw = (x2 - x1) / w
    bh = (y2 - y1) / h
    return (
        max(0.0, min(1.0, x_center)),
        max(0.0, min(1.0, y_center)),
        max(0.0, min(1.0, bw)),
        max(0.0, min(1.0, bh)),
    )


def _yolo_to_xyxy(cls: int, xc: float, yc: float, bw: float, bh: float, w: int, h: int) -> Tuple[int, int, int, int, int]:
    bw = min(1.0, max(0.0, bw))
    bh = min(1.0, max(0.0, bh))
    xc = min(1.0, max(0.0, xc))
    yc = min(1.0, max(0.0, yc))
    x1 = int((xc - bw / 2) * w)
    y1 = int((yc - bh / 2) * h)
    x2 = int((xc + bw / 2) * w)
    y2 = int((yc + bh / 2) * h)
    return cls, x1, y1, x2, y2


class Box:
    def __init__(self, cls: int, x1: float, y1: float, x2: float, y2: float, conf: float = 1.0):
        self.cls = cls
        self.x1 = float(x1)
        self.y1 = float(y1)
        self.x2 = float(x2)
        self.y2 = float(y2)
        self.conf = float(conf)

    @property
    def centre(self) -> Tuple[float, float]:
        return ((self.x1 + self.x2) / 2.0, (self.y1 + self.y2) / 2.0)

    def contains(self, x: float, y: float) -> bool:
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2


class SmartLabeller:
    def __init__(
        self,
        video_paths: List[Path],
        model_path: Path,
        output_dir: Optional[Path],
        conf: float = DEFAULT_CONF,
        stride: int = DEFAULT_STRIDE,
        start_frame: int = 0,
        max_frames: Optional[int] = None,
        min_detections: int = DEFAULT_MIN_DETECTIONS,
        max_detections: int = DEFAULT_MAX_DETECTIONS,
        max_box_area_ratio: float = DEFAULT_MAX_BOX_AREA_RATIO,
        scene_threshold: float = DEFAULT_SCENE_THRESHOLD,
        imgsz: int = DEFAULT_IMGSZ,
        device: Optional[str] = None,
        save_images: bool = True,
        auto_mode: bool = False,
        review_mode: bool = False,
        review_all: bool = False,
        split_mode: bool = False,
        reviewed_up_to: int = 0,
    ):
        self.video_paths = [p.resolve() for p in video_paths]
        self.model_path = model_path
        # If no output dir is given, each video gets its own folder under data/raw.
        self._fixed_output_dir: Optional[Path] = output_dir.resolve() if output_dir else None
        self.conf = conf
        self.stride = max(1, stride)
        self.start_frame = start_frame
        self.max_frames = max_frames
        self.min_detections = min_detections
        self.max_detections = max_detections
        self.max_box_area_ratio = max_box_area_ratio
        self.scene_threshold = scene_threshold
        self.imgsz = imgsz
        self.device = device
        self.save_images = save_images
        self.auto_mode = auto_mode
        self.review_mode = review_mode
        self.review_all = review_all
        self.split_mode = split_mode
        self.reviewed_up_to = reviewed_up_to

        # Reviewed-frame tracking (persisted to reviewed.txt next to labels/).
        self._reviewed: Set[int] = set()

        self.model = YOLO(str(model_path))
        self.model_names: Dict[int, str] = self.model.names

        self.images_dir = Path(".")
        self.labels_dir = Path(".")

        self.cap: Optional[cv2.VideoCapture] = None
        self.current_video_idx = 0
        self.current_video_path: Path = self.video_paths[0]
        self.frame_idx = start_frame
        self.total_frames = 0
        self.fps = 25.0
        self.width = 0
        self.height = 0
        self.frame: Optional[np.ndarray] = None

        # Per-frame annotations: {video_name: {frame_idx: [Box]}}
        self.annotations: Dict[str, Dict[int, List[Box]]] = defaultdict(lambda: defaultdict(list))
        self.video_name = ""

        # Quality filtering state for batch mode.
        self._last_saved_frame: Optional[np.ndarray] = None
        self._small_size = (64, 36)

        # Review mode state
        self._review_frames: List[int] = []
        self._review_index: int = 0

        # GUI state
        self.selected_box: Optional[Box] = None
        self.drawing = False
        self.draw_start: Optional[Tuple[int, int]] = None
        self.draw_end: Optional[Tuple[int, int]] = None
        self.playing = False
        self.closed = False
        self.window_name = "Smart Labeller"
        self._display_scale = 1.0

        self._load_video(0)
        self._seek(start_frame)
        self.load_existing_labels()

    # ------------------------------------------------------------------
    # Video IO
    # ------------------------------------------------------------------
    def _set_output_dirs(self, video_name: str) -> None:
        """Set images_dir/labels_dir based on the current video."""
        if self._fixed_output_dir is not None:
            base = self._fixed_output_dir
        else:
            base = ROOT / "data" / "raw" / video_name
        self.images_dir = base / "images"
        self.labels_dir = base / "labels"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.labels_dir.mkdir(parents=True, exist_ok=True)

    def _load_video(self, idx: int) -> bool:
        if self.cap is not None:
            self.cap.release()
        if idx >= len(self.video_paths):
            return False
        self.current_video_idx = idx
        self.current_video_path = self.video_paths[idx]
        path = self.current_video_path
        self.video_name = path.stem
        self._set_output_dirs(self.video_name)
        self.cap = cv2.VideoCapture(str(path))
        if not self.cap.isOpened():
            raise SystemExit(f"Could not open video: {path}")
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_idx = 0

        # Fit the display inside a reasonable screen area while keeping aspect ratio.
        max_w, max_h = 1600, 900
        self._display_scale = min(1.0, max_w / self.width, max_h / self.height)

        print(f"Loaded {path} ({self.total_frames} frames @ {self.fps:.2f} fps)")
        print(f"  output -> {self.images_dir.parent}")
        print(f"  display scale: {self._display_scale:.2f}")
        self._load_reviewed()
        return True

    # ------------------------------------------------------------------
    # Reviewed-frame manifest
    # ------------------------------------------------------------------
    def _reviewed_path(self) -> Path:
        return self.labels_dir.parent / "reviewed.txt"

    def _load_reviewed(self) -> None:
        self._reviewed = set()
        path = self._reviewed_path()
        if path.exists():
            for line in path.read_text().splitlines():
                line = line.strip()
                if line:
                    self._reviewed.add(int(line))

    def _save_reviewed(self) -> None:
        path = self._reviewed_path()
        path.write_text("".join(f"{idx}\n" for idx in sorted(self._reviewed)))

    def _mark_reviewed(self, frame_idx: int) -> None:
        # Persist corrections before approval; advancing used to mark the old
        # on-disk labels reviewed while leaving edits only in memory.
        if frame_idx == self.frame_idx and self.frame is not None:
            boxes = self.annotations[self.video_name].get(frame_idx, [])
            self.save_frame(self.video_name, frame_idx, boxes, self.frame)
        if frame_idx not in self._reviewed:
            self._reviewed.add(frame_idx)
            self._save_reviewed()

    def _mark_unreviewed(self, frame_idx: int) -> None:
        if frame_idx in self._reviewed:
            self._reviewed.discard(frame_idx)
            self._save_reviewed()

    def _seek(self, frame_idx: int) -> bool:
        if self.cap is None:
            return False
        frame_idx = max(0, min(frame_idx, self.total_frames - 1))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, self.frame = self.cap.read()
        if ok:
            self.frame_idx = frame_idx
        return ok

    def _next_frame(self) -> bool:
        return self._seek(self.frame_idx + self.stride)

    def _prev_frame(self) -> bool:
        return self._seek(self.frame_idx - self.stride)

    # ------------------------------------------------------------------
    # Detection / classification
    # ------------------------------------------------------------------
    def detect_frame(self, frame: np.ndarray) -> List[Box]:
        results = self.model(
            frame,
            conf=self.conf,
            imgsz=self.imgsz,
            device=self.device,
            verbose=False,
        )
        boxes: List[Box] = []
        for r in results:
            if r.boxes is None:
                continue
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().tolist()
                bw = x2 - x1
                bh = y2 - y1
                if bw < MIN_BOX_WIDTH or bh < MIN_BOX_HEIGHT:
                    continue

                model_cls = int(box.cls[0].item())
                model_name = self.model_names.get(model_cls, "")
                conf = float(box.conf[0].item())

                # Skip non-person classes when using a generic COCO detector.
                if not _is_person_class(model_name):
                    continue

                # Decide the label: trust an explicit referee/umpire class,
                # otherwise fall back to the yellow-torso heuristic.
                if _is_explicit_referee_class(model_name):
                    cls = CLASS_REFEREE
                elif _infer_referee_by_colour(frame, x1, y1, x2, y2):
                    cls = CLASS_REFEREE
                else:
                    cls = CLASS_PLAYER

                # Merge overlapping duplicates from generic detectors.
                candidate = (x1, y1, x2, y2)
                duplicate = False
                for existing in boxes:
                    if _box_iou(candidate, (existing.x1, existing.y1, existing.x2, existing.y2)) > 0.5:
                        duplicate = True
                        break
                if not duplicate:
                    boxes.append(Box(cls, x1, y1, x2, y2, conf))
        return boxes

    def _is_quality_frame(self, boxes: List[Box]) -> Tuple[bool, str]:
        """Return (keep, reason) after applying batch quality filters."""
        if len(boxes) < self.min_detections:
            return False, f"too few detections ({len(boxes)} < {self.min_detections})"
        if len(boxes) > self.max_detections:
            return False, f"too many detections ({len(boxes)} > {self.max_detections})"

        frame_area = self.width * self.height
        if frame_area > 0:
            for box in boxes:
                box_area = (box.x2 - box.x1) * (box.y2 - box.y1)
                if (box_area / frame_area) > self.max_box_area_ratio:
                    return False, f"close-up box ({box_area / frame_area:.1%} of frame)"
        return True, ""

    def _scene_change_score(self, frame: np.ndarray) -> float:
        """Low score means the frame is nearly identical to the last saved one."""
        if self._last_saved_frame is None:
            return float("inf")
        small_a = cv2.resize(self._last_saved_frame, self._small_size)
        small_b = cv2.resize(frame, self._small_size)
        gray_a = cv2.cvtColor(small_a, cv2.COLOR_BGR2GRAY).astype(np.float32)
        gray_b = cv2.cvtColor(small_b, cv2.COLOR_BGR2GRAY).astype(np.float32)
        return float(np.mean(np.abs(gray_a - gray_b)))

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def _label_path(self, video_name: str, frame_idx: int) -> Path:
        return self.labels_dir / f"{video_name}_frame_{frame_idx:06d}.txt"

    def _image_path(self, video_name: str, frame_idx: int) -> Path:
        return self.images_dir / f"{video_name}_frame_{frame_idx:06d}.jpg"

    def save_frame(self, video_name: str, frame_idx: int, boxes: List[Box], frame: np.ndarray) -> None:
        # An explicitly reviewed empty frame is a valid negative. Write an empty
        # label to replace any old false-positive boxes rather than retaining them.
        label_path = self._label_path(video_name, frame_idx)
        with open(label_path, "w") as f:
            for box in boxes:
                xc, yc, bw, bh = _xyxy_to_yolo(box.x1, box.y1, box.x2, box.y2, self.width, self.height)
                f.write(f"{box.cls} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")
        if self.save_images:
            image_path = self._image_path(video_name, frame_idx)
            cv2.imwrite(str(image_path), frame)
        print(f"Saved {len(boxes)} labels for {video_name} frame {frame_idx}")

    def _read_frame_from_path(self, video_path: Path, frame_idx: int) -> Optional[np.ndarray]:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return None
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, frame = cap.read()
        cap.release()
        return frame if ok else None

    def save_all(self) -> None:
        total = 0
        for video_name, frames in self.annotations.items():
            # Locate the source video for this annotation set.
            video_path = next((p for p in self.video_paths if p.stem == video_name), None)
            if video_path is None:
                print(f"Warning: could not find source video for {video_name}, skipping save.")
                continue

            for frame_idx, boxes in frames.items():
                if video_name == self.video_name and frame_idx == self.frame_idx and self.frame is not None:
                    self.save_frame(video_name, frame_idx, boxes, self.frame)
                else:
                    frame = self._read_frame_from_path(video_path, frame_idx)
                    if frame is not None:
                        self.save_frame(video_name, frame_idx, boxes, frame)
                total += 1
        print(f"Saved {total} labelled frames.")

    def load_existing_labels(self) -> None:
        """Load any labels already present in the output directory."""
        for txt in self.labels_dir.glob("*.txt"):
            stem = txt.stem
            # Expected stems: {video_name}_frame_{frame_idx:06d}
            if "_frame_" not in stem:
                continue
            video_name, frame_part = stem.rsplit("_frame_", 1)
            try:
                frame_idx = int(frame_part)
            except ValueError:
                continue
            boxes: List[Box] = []
            with open(txt) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) != 5:
                        continue
                    cls, xc, yc, bw, bh = map(float, parts)
                    cls = int(cls)
                    # Old labels may contain class 2 (umpire) — fold into ref (1).
                    if cls == 2:
                        cls = CLASS_REFEREE
                    _, x1, y1, x2, y2 = _yolo_to_xyxy(int(cls), xc, yc, bw, bh, self.width, self.height)
                    boxes.append(Box(cls, x1, y1, x2, y2))
            self.annotations[video_name][frame_idx] = boxes

    def _saved_frame_indices(self) -> List[int]:
        """Return sorted frame indices that already have label files for the current video."""
        indices: List[int] = []
        prefix = f"{self.video_name}_frame_"
        for txt in self.labels_dir.glob(f"{prefix}*.txt"):
            try:
                frame_idx = int(txt.stem[len(prefix):])
                indices.append(frame_idx)
            except ValueError:
                continue
        return sorted(indices)

    def _run_split(self) -> None:
        """Split labelled frames into reviewed/ and unreviewed/ subfolders."""
        base = self.labels_dir.parent
        reviewed_dir = base / "reviewed"
        unreviewed_dir = base / "unreviewed"
        for section in (reviewed_dir, unreviewed_dir):
            (section / "images").mkdir(parents=True, exist_ok=True)
            (section / "labels").mkdir(parents=True, exist_ok=True)

        n_reviewed = 0
        n_unreviewed = 0
        prefix = f"{self.video_name}_frame_"
        source_labels = sorted(self.labels_dir.glob(f"{prefix}*.txt"))
        for label_path in source_labels:
            if not (self.images_dir / f"{label_path.stem}.jpg").is_file():
                raise ValueError(f"Cannot export label without image: {label_path}")
        # Exports are derived copies. Clear the previous export for this video
        # so revoked/deleted frames cannot remain eligible for training.
        for section in (reviewed_dir, unreviewed_dir):
            for subdir, suffix in (("images", ".jpg"), ("labels", ".txt")):
                for old in (section / subdir).glob(f"{prefix}*{suffix}"):
                    old.unlink()
            (section / "labels.cache").unlink(missing_ok=True)
        for label_path in source_labels:
            try:
                frame_idx = int(label_path.stem[len(prefix):])
            except ValueError:
                continue
            target = reviewed_dir if frame_idx in self._reviewed else unreviewed_dir
            shutil.copy2(label_path, target / "labels" / label_path.name)

            # Remap class 2 -> 1 in the copied label file.
            lines = []
            for line in (target / "labels" / label_path.name).read_text().splitlines():
                parts = line.split()
                if parts and parts[0] == "2":
                    parts[0] = "1"
                lines.append(" ".join(parts))
            (target / "labels" / label_path.name).write_text("\n".join(lines) + "\n")

            image_path = self.images_dir / f"{label_path.stem}.jpg"
            if image_path.exists():
                shutil.copy2(image_path, target / "images" / image_path.name)

            if frame_idx in self._reviewed:
                n_reviewed += 1
            else:
                n_unreviewed += 1

        # This is a reviewed source export, not a train/val dataset. Build an
        # isolated holdout with build_datasets.py --broadcast-reviewed.
        data_yaml = reviewed_dir / "data.yaml"
        data_yaml.write_text(
            "names:\n"
            "  0: PLAYER\n"
            "  1: REF\n"
            f"path: {reviewed_dir.resolve()}\n"
            "train: images\n"
        )
        print(
            f"Split complete for {self.video_name}: "
            f"{n_reviewed} reviewed -> {reviewed_dir}, "
            f"{n_unreviewed} unreviewed -> {unreviewed_dir}"
        )

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def _draw_frame(self) -> np.ndarray:
        canvas = self.frame.copy()
        boxes = self.annotations[self.video_name].get(self.frame_idx, [])
        for box in boxes:
            colour = CLASS_COLOURS.get(box.cls, (200, 200, 200))
            if box is self.selected_box:
                colour = SELECTED_COLOUR
            cv2.rectangle(canvas, (int(box.x1), int(box.y1)), (int(box.x2), int(box.y2)), colour, 2)
            label = f"{CLASS_NAMES.get(box.cls, '?')} {box.conf:.2f}"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(canvas, (int(box.x1), int(box.y1) - th - 8), (int(box.x1) + tw + 6, int(box.y1)), colour, -1)
            cv2.putText(canvas, label, (int(box.x1) + 3, int(box.y1) - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        if self.drawing and self.draw_start and self.draw_end:
            cv2.rectangle(canvas, self.draw_start, self.draw_end, (255, 255, 255), 1)

        # Info overlay
        mode_label = "AUTO" if self.auto_mode else ("REVIEW" if self.review_mode else "manual")
        info_lines = [
            f"Video: {self.video_name}  Frame: {self.frame_idx}/{self.total_frames}",
            f"Boxes: {len(boxes)}  Stride: {self.stride}  Mode: {mode_label}",
        ]
        if self.review_mode and self._review_frames:
            status = "R" if self.frame_idx in self._reviewed else "-"
            info_lines.append(
                f"Review: {self._review_index + 1}/{len(self._review_frames)}"
                f"  reviewed: {len(self._reviewed)}  [{status}]"
            )
        info_lines.append("a=auto  n=next  p=prev  s=save  .=sel  d=del  0/1=class  m=ok  u=unmark  q=quit")
        y = 25
        for line in info_lines:
            cv2.putText(canvas, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y += 25
        return canvas

    # ------------------------------------------------------------------
    # Mouse / keyboard callbacks
    # ------------------------------------------------------------------
    def _map_mouse_to_frame(self, x: int, y: int) -> Tuple[int, int]:
        """Map window mouse coordinates back to original frame coordinates."""
        if self._display_scale <= 0:
            return x, y
        return int(x / self._display_scale), int(y / self._display_scale)

    def _on_mouse(self, event: int, x: int, y: int, flags: int, param: None) -> None:
        x, y = self._map_mouse_to_frame(x, y)

        if event == cv2.EVENT_LBUTTONDOWN:
            boxes = self.annotations[self.video_name].get(self.frame_idx, [])
            clicked = [b for b in boxes if b.contains(x, y)]
            if clicked:
                self.selected_box = clicked[-1]
            else:
                self.drawing = True
                self.draw_start = (x, y)
                self.draw_end = (x, y)
                self.selected_box = None

        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            self.draw_end = (x, y)

        elif event == cv2.EVENT_LBUTTONUP and self.drawing:
            self.drawing = False
            x1 = min(self.draw_start[0], self.draw_end[0])
            y1 = min(self.draw_start[1], self.draw_end[1])
            x2 = max(self.draw_start[0], self.draw_end[0])
            y2 = max(self.draw_start[1], self.draw_end[1])
            if x2 - x1 >= MIN_BOX_WIDTH and y2 - y1 >= MIN_BOX_HEIGHT:
                new_box = Box(CLASS_PLAYER, x1, y1, x2, y2)
                self.annotations[self.video_name][self.frame_idx].append(new_box)
                self.selected_box = new_box
            self.draw_start = None
            self.draw_end = None

        elif event == cv2.EVENT_RBUTTONDOWN:
            boxes = self.annotations[self.video_name].get(self.frame_idx, [])
            clicked = [b for b in boxes if b.contains(x, y)]
            if clicked:
                boxes.remove(clicked[-1])
                if self.selected_box is clicked[-1]:
                    self.selected_box = None

    def _set_selected_class(self, cls: int) -> None:
        if self.selected_box is not None:
            self.selected_box.cls = cls

    def _select_next_box(self) -> None:
        boxes = self.annotations[self.video_name].get(self.frame_idx, [])
        if not boxes:
            self.selected_box = None
            return
        if self.selected_box is None or self.selected_box not in boxes:
            self.selected_box = boxes[0]
        else:
            idx = boxes.index(self.selected_box)
            self.selected_box = boxes[(idx + 1) % len(boxes)]

    def _select_prev_box(self) -> None:
        boxes = self.annotations[self.video_name].get(self.frame_idx, [])
        if not boxes:
            self.selected_box = None
            return
        if self.selected_box is None or self.selected_box not in boxes:
            self.selected_box = boxes[-1]
        else:
            idx = boxes.index(self.selected_box)
            self.selected_box = boxes[(idx - 1) % len(boxes)]

    def _delete_selected(self) -> None:
        if self.selected_box is not None:
            boxes = self.annotations[self.video_name].get(self.frame_idx, [])
            if self.selected_box in boxes:
                boxes.remove(self.selected_box)
            self.selected_box = None

    def _delete_all_boxes_in_frame(self) -> None:
        if self.frame_idx in self.annotations[self.video_name]:
            del self.annotations[self.video_name][self.frame_idx]
        self.selected_box = None
        print(f"Deleted all boxes for frame {self.frame_idx}")

    def _delete_current_frame_files(self) -> bool:
        """Permanently delete the current frame's label file and image from disk."""
        label_path = self._label_path(self.video_name, self.frame_idx)
        image_path = self._image_path(self.video_name, self.frame_idx)
        deleted = False
        if label_path.exists():
            label_path.unlink()
            deleted = True
        if image_path.exists():
            image_path.unlink()
            deleted = True
        if deleted:
            self._delete_all_boxes_in_frame()
            print(f"Deleted frame {self.frame_idx} from disk")
        else:
            print(f"No saved files for frame {self.frame_idx}")
        return deleted

    def _auto_detect_current(self) -> None:
        if self.frame is None:
            return
        boxes = self.detect_frame(self.frame)
        self.annotations[self.video_name][self.frame_idx] = boxes
        self.selected_box = boxes[0] if boxes else None
        print(f"Auto-detected {len(boxes)} objects")

    def _run_auto_labelling(self) -> None:
        """Batch auto-label every stride frame and save immediately."""
        print("Starting batch auto-labelling...")
        print(
            f"Quality filters: detections {self.min_detections}-{self.max_detections}, "
            f"max box area {self.max_box_area_ratio:.0%}, scene threshold {self.scene_threshold}"
        )

        # Compute total iterations for the progress bar.
        if self.max_frames is not None:
            total_iterations = self.max_frames
        else:
            total_iterations = max(0, (self.total_frames - self.frame_idx + self.stride - 1) // self.stride)

        frame_idx = self.frame_idx
        processed = 0
        saved = 0
        skipped = 0
        pbar = tqdm(total=total_iterations, desc="Labelling", unit="frame") if tqdm else None

        try:
            while True:
                if self.max_frames is not None and processed >= self.max_frames:
                    print(f"Reached --max-frames limit ({self.max_frames}).")
                    break
                if not self._seek(frame_idx):
                    break
                boxes = self.detect_frame(self.frame)

                keep, reason = self._is_quality_frame(boxes)
                if keep:
                    scene_score = self._scene_change_score(self.frame)
                    if scene_score < self.scene_threshold:
                        keep = False
                        reason = f"too similar to last saved frame (score {scene_score:.1f})"

                if keep:
                    self.annotations[self.video_name][frame_idx] = boxes
                    self.save_frame(self.video_name, frame_idx, boxes, self.frame)
                    self._last_saved_frame = self.frame.copy()
                    saved += 1
                else:
                    skipped += 1

                frame_idx += self.stride
                processed += 1
                if frame_idx >= self.total_frames:
                    break
                if pbar is not None:
                    pbar.update(1)
                    pbar.set_postfix(saved=saved, skipped=skipped)
        finally:
            if pbar is not None:
                pbar.close()
        print(f"Batch auto-labelling complete: {saved} saved, {skipped} skipped ({processed} processed).")

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def _next_review_frame(self) -> bool:
        if not self._review_frames:
            return False
        self._review_index = min(self._review_index + 1, len(self._review_frames) - 1)
        return self._seek(self._review_frames[self._review_index])

    def _prev_review_frame(self) -> bool:
        if not self._review_frames:
            return False
        self._review_index = max(self._review_index - 1, 0)
        return self._seek(self._review_frames[self._review_index])

    def run(self) -> None:
        if self.auto_mode:
            self._run_auto_labelling()
            # Continue to next video if any
            while self.current_video_idx + 1 < len(self.video_paths):
                if not self._load_video(self.current_video_idx + 1):
                    break
                self._run_auto_labelling()
            return

        if self.split_mode:
            for path in self.video_paths:
                self.video_name = path.stem
                self._set_output_dirs(self.video_name)
                self._load_reviewed()
                if self.reviewed_up_to > 0:
                    seed = self._saved_frame_indices()[: self.reviewed_up_to]
                    self._reviewed.update(seed)
                    self._save_reviewed()
                    print(f"Marked {len(seed)} frames as reviewed (seed)")
                self._run_split()
            return

        # WINDOW_AUTOSIZE is more reliable on macOS Cocoa than WINDOW_NORMAL.
        cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(self.window_name, self._on_mouse)

        # In review mode, jump straight to the first unreviewed saved frame.
        if self.review_mode:
            self._review_frames = self._saved_frame_indices()
            # Seed reviewed state (e.g. --reviewed-up-to 84) and continue from there.
            if self.reviewed_up_to > 0:
                seed = self._review_frames[: self.reviewed_up_to]
                self._reviewed.update(seed)
                self._save_reviewed()
                print(f"Marked {len(seed)} frames as reviewed (seed)")
            if not self.review_all:
                self._review_frames = [f for f in self._review_frames if f not in self._reviewed]
            self._review_index = 0
            if self._review_frames:
                self._seek(self._review_frames[self._review_index])
                print(
                    f"Review mode: {len(self._review_frames)} frames to review, "
                    f"{len(self._reviewed)} already reviewed"
                )
            else:
                print(f"Review mode: nothing left to review in {self.labels_dir}")

        try:
            while not self.closed:
                if self.frame is None:
                    if self.current_video_idx + 1 < len(self.video_paths):
                        if not self._load_video(self.current_video_idx + 1):
                            break
                        if self.review_mode:
                            self._review_frames = self._saved_frame_indices()
                            if not self.review_all:
                                self._review_frames = [f for f in self._review_frames if f not in self._reviewed]
                            self._review_index = 0
                            if self._review_frames:
                                self._seek(self._review_frames[0])
                            else:
                                print(f"Review mode: nothing left to review for {self.video_name}")
                        continue
                    break

                canvas = self._draw_frame()
                display_canvas = cv2.resize(
                    canvas,
                    (int(self.width * self._display_scale), int(self.height * self._display_scale)),
                )
                cv2.imshow(self.window_name, display_canvas)
                # Use a short delay when paused so Ctrl+C and the closed flag are checked.
                delay = max(1, int(1000 / self.fps)) if self.playing else 50
                key = cv2.waitKey(delay) & 0xFF

                if key == ord("q") or key == 27:
                    self.closed = True
                    continue

                if self.playing:
                    if key == ord(" "):
                        self.playing = False
                    elif self.review_mode:
                        self._mark_reviewed(self.frame_idx)
                        if not self._next_review_frame():
                            self.playing = False
                    elif not self._next_frame():
                        self.playing = False
                    continue

                if key == ord("n") or key == 83:  # right arrow
                    if self.review_mode:
                        self._mark_reviewed(self.frame_idx)
                        self._next_review_frame()
                    else:
                        self._next_frame()
                elif key == ord("p") or key == 81:  # left arrow
                    if self.review_mode:
                        self._prev_review_frame()
                    else:
                        self._prev_frame()
                elif key == ord("a"):
                    self._auto_detect_current()
                elif key == ord("d"):
                    self._delete_selected()
                elif key == ord("D"):
                    self._delete_all_boxes_in_frame()
                elif key == ord("."):
                    self._select_next_box()
                elif key == ord(","):
                    self._select_prev_box()
                elif key == ord("m"):
                    self._mark_reviewed(self.frame_idx)
                elif key == ord("u"):
                    self._mark_unreviewed(self.frame_idx)
                elif key == ord("x"):
                    if self._delete_current_frame_files() and self.review_mode:
                        # Remove current frame from review list and advance.
                        self._mark_unreviewed(self.frame_idx)
                        if self.frame_idx in self._review_frames:
                            self._review_frames.pop(self._review_index)
                        if self._review_index >= len(self._review_frames):
                            self._review_index = max(0, len(self._review_frames) - 1)
                        if self._review_frames:
                            self._seek(self._review_frames[self._review_index])
                        else:
                            self.frame = None
                elif key == ord("0"):
                    self._set_selected_class(CLASS_PLAYER)
                elif key == ord("1"):
                    self._set_selected_class(CLASS_REFEREE)
                elif key == ord("s"):
                    boxes = self.annotations[self.video_name].get(self.frame_idx, [])
                    self.save_frame(self.video_name, self.frame_idx, boxes, self.frame)
                    if self.review_mode:
                        self._mark_reviewed(self.frame_idx)
                elif key == ord("S"):
                    self.save_all()
                elif key == ord("r"):
                    self._run_auto_labelling()
                elif key == ord("+") or key == ord("="):
                    self.stride += 1
                elif key == ord("-"):
                    self.stride = max(1, self.stride - 1)
                elif key == ord(" "):
                    self.playing = True
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
        finally:
            self.closed = True
            cv2.destroyAllWindows()
            if self.cap is not None:
                self.cap.release()


def _is_auto_downloadable_model(name: str) -> bool:
    """Ultralytics can auto-download official YOLO weights by name."""
    low = name.lower()
    return (
        low.startswith(("yolov8", "yolov9", "yolo11", "yolov5", "yolov10"))
        and low.endswith(".pt")
    )


def _expand_paths(inputs: List[str]) -> List[Path]:
    paths: List[Path] = []
    for raw in inputs:
        expanded = sorted(glob.glob(raw))
        if expanded:
            paths.extend(Path(p) for p in expanded)
        else:
            paths.append(Path(raw))
    return paths


def main() -> None:
    p = argparse.ArgumentParser(
        description="Smart OpenCV labeller for broadcast AFL videos.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("videos", nargs="+", help="Video file(s) to label. Glob patterns accepted.")
    p.add_argument("--model", type=Path, default=DEFAULT_MODEL,
                   help="YOLO model path (default: yolov8s.pt COCO person detector)")
    p.add_argument("--output-dir", type=Path, default=None,
                   help="Directory for images/ and labels/ (default: data/raw/<video_name>)")
    p.add_argument("--conf", type=float, default=DEFAULT_CONF, help="Detection confidence threshold")
    p.add_argument("--stride", type=int, default=DEFAULT_STRIDE,
                   help="Frame stride for next/prev and batch auto-labelling")
    p.add_argument("--start-frame", type=int, default=0, help="Start at this frame")
    p.add_argument("--max-frames", type=int, default=None,
                   help="Stop after labelling N frames (useful for quick tests)")
    p.add_argument("--min-detections", type=int, default=DEFAULT_MIN_DETECTIONS,
                   help="Minimum person detections to keep a frame in batch mode")
    p.add_argument("--max-detections", type=int, default=DEFAULT_MAX_DETECTIONS,
                   help="Maximum person detections to keep a frame in batch mode")
    p.add_argument("--max-box-area-ratio", type=float, default=DEFAULT_MAX_BOX_AREA_RATIO,
                   help="Reject frames where any box exceeds this ratio of the frame area")
    p.add_argument("--scene-threshold", type=float, default=DEFAULT_SCENE_THRESHOLD,
                   help="Skip frames whose downscaled pixel change is below this (0-255)")
    p.add_argument("--imgsz", type=int, default=DEFAULT_IMGSZ,
                   help="YOLO inference size (lower = faster, e.g. 320 or 416)")
    p.add_argument("--device", default=None,
                   help="torch device: cpu, mps, cuda, etc. (auto-detected if omitted)")
    p.add_argument("--no-images", action="store_true", help="Only write label files, do not copy frames")
    p.add_argument("--auto", action="store_true",
                   help="Batch auto-label every --stride frame and exit (no GUI)")
    p.add_argument("--review", action="store_true",
                   help="Interactive review of saved labels (unreviewed frames only by default)")
    p.add_argument("--all", dest="review_all", action="store_true",
                   help="Review all saved frames, including already-reviewed ones")
    p.add_argument("--reviewed-up-to", type=int, default=0,
                   help="Seed review state: mark the first N saved frames as already reviewed")
    p.add_argument("--split", action="store_true",
                   help="Split labelled frames into reviewed/ and unreviewed/ subfolders, then exit")
    args = p.parse_args()

    video_paths = _expand_paths(args.videos)
    for path in video_paths:
        if not path.exists():
            raise SystemExit(f"Video not found: {path}")
    if not args.model.exists() and not _is_auto_downloadable_model(str(args.model)):
        raise SystemExit(f"Model not found and not a known auto-downloadable name: {args.model}")

    labeller = SmartLabeller(
        video_paths=video_paths,
        model_path=args.model,
        output_dir=args.output_dir,
        conf=args.conf,
        stride=args.stride,
        start_frame=args.start_frame,
        max_frames=args.max_frames,
        min_detections=args.min_detections,
        max_detections=args.max_detections,
        max_box_area_ratio=args.max_box_area_ratio,
        scene_threshold=args.scene_threshold,
        imgsz=args.imgsz,
        device=args.device,
        save_images=not args.no_images,
        auto_mode=args.auto,
        review_mode=args.review,
        review_all=args.review_all,
        split_mode=args.split,
        reviewed_up_to=args.reviewed_up_to,
    )
    labeller.run()


if __name__ == "__main__":
    main()
