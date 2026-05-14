from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

try:
    from scipy.optimize import linear_sum_assignment

    SCIPY_AVAILABLE = True
except Exception:
    linear_sum_assignment = None
    SCIPY_AVAILABLE = False

from .appearance import update_appearance
from .config import TrackingConfig
from .geometry import (
    bbox_center,
    cosine_similarity,
    direction_cost,
    euclidean_distance,
    iou_xyxy,
)


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
                "confidence": float(self.current_conf),
                "detected_class_id": int(self.current_detected_class_id),
                "detected_class_name": str(self.current_detected_class_name),
                "fixed_initial_class_id": int(self.initial_class_id),
                "fixed_initial_class_name": str(self.initial_class_name),
            }
        )

    def mark_missing(self):
        self.missing += 1
        self.age += 1


class RobustPlayerTracker:
    def __init__(self, config: TrackingConfig):
        self.config = config
        self.next_track_id = 0
        self.tracks: Dict[int, Track] = {}
        self.finished_tracks: Dict[int, Track] = {}

    def update(self, detections: List[Dict], frame_index: int, time_sec: float) -> Dict[int, Track]:
        active_ids = list(self.tracks.keys())

        if not active_ids:
            for det in detections:
                self._create_track(det, frame_index, time_sec)
            return self.tracks

        cost_matrix = self._build_cost_matrix(active_ids, detections)
        matches, unmatched_track_ids, unmatched_det_indices = self._assign_matches(
            active_ids, detections, cost_matrix
        )

        for track_id, det_idx in matches:
            self.tracks[track_id].update(
                detections[det_idx],
                frame_index=frame_index,
                time_sec=time_sec,
                appearance_momentum=self.config.appearance_momentum,
            )

        for track_id in unmatched_track_ids:
            if track_id in self.tracks:
                self.tracks[track_id].mark_missing()

        for det_idx in unmatched_det_indices:
            det = detections[det_idx]
            if not self._is_close_to_existing_track(det):
                self._create_track(det, frame_index, time_sec)

        self._remove_stale_tracks()
        return self.tracks

    def _create_track(self, detection: Dict, frame_index: int, time_sec: float) -> int:
        track_id = self.next_track_id
        self.next_track_id += 1

        track = Track(
            track_id=track_id,
            initial_class_id=int(detection["class_id"]),
            initial_class_name=str(detection["class_name"]),
            bbox=[float(v) for v in detection["bbox"]],
            center=tuple(float(v) for v in detection["center"]),
            appearance=detection.get("appearance"),
            trail_length=self.config.trail_length,
            current_conf=float(detection["conf"]),
            current_detected_class_id=int(detection["class_id"]),
            current_detected_class_name=str(detection["class_name"]),
        )
        track.update(detection, frame_index, time_sec, self.config.appearance_momentum)
        self.tracks[track_id] = track
        return track_id

    def _build_cost_matrix(self, active_ids: List[int], detections: List[Dict]) -> np.ndarray:
        if not active_ids or not detections:
            return np.zeros((len(active_ids), len(detections)), dtype=np.float32)

        cost_matrix = np.zeros((len(active_ids), len(detections)), dtype=np.float32)

        for row, track_id in enumerate(active_ids):
            track = self.tracks[track_id]
            for col, det in enumerate(detections):
                distance = euclidean_distance(track.center, det["center"])
                distance_cost = min(distance / max(self.config.max_distance, 1e-6), 1.0)

                iou_score = iou_xyxy(track.bbox, det["bbox"])
                iou_cost = 1.0 - iou_score

                dir_cost = direction_cost(track.previous_center, track.center, det["center"])

                app_sim = cosine_similarity(track.appearance, det.get("appearance"))
                app_cost = 1.0 - max(0.0, min(1.0, app_sim))

                total_cost = (
                    self.config.distance_weight * distance_cost
                    + self.config.iou_weight * iou_cost
                    + self.config.direction_weight * dir_cost
                    + self.config.appearance_weight * app_cost
                )

                # Soft gating. If the detection is far and has almost no overlap, discourage assignment.
                if distance > self.config.max_distance and iou_score < 0.05:
                    total_cost += 1.0

                cost_matrix[row, col] = float(total_cost)

        return cost_matrix

    def _assign_matches(
        self,
        active_ids: List[int],
        detections: List[Dict],
        cost_matrix: np.ndarray,
    ) -> Tuple[List[Tuple[int, int]], Set[int], Set[int]]:
        unmatched_track_ids: Set[int] = set(active_ids)
        unmatched_det_indices: Set[int] = set(range(len(detections)))
        matches: List[Tuple[int, int]] = []

        if not active_ids or not detections:
            return matches, unmatched_track_ids, unmatched_det_indices

        if SCIPY_AVAILABLE:
            row_indices, col_indices = linear_sum_assignment(cost_matrix)
        else:
            row_indices, col_indices = self._greedy_assignment(cost_matrix)

        for row, col in zip(row_indices, col_indices):
            track_id = active_ids[int(row)]
            cost = float(cost_matrix[int(row), int(col)])

            if cost > self.config.match_cost_threshold:
                continue

            if self._is_ambiguous(cost_matrix, int(row), int(col)):
                continue

            matches.append((track_id, int(col)))
            unmatched_track_ids.discard(track_id)
            unmatched_det_indices.discard(int(col))

        return matches, unmatched_track_ids, unmatched_det_indices

    def _is_ambiguous(self, cost_matrix: np.ndarray, row: int, col: int) -> bool:
        best = float(cost_matrix[row, col])
        if best <= self.config.confident_cost_threshold:
            return False

        row_costs = np.asarray(cost_matrix[row], dtype=np.float32)
        if row_costs.size <= 1:
            return False

        sorted_costs = np.sort(row_costs)
        second_best = float(sorted_costs[1]) if sorted_costs.size > 1 else float("inf")
        return (second_best - best) < self.config.ambiguity_margin

    @staticmethod
    def _greedy_assignment(cost_matrix: np.ndarray):
        pairs = []
        used_rows = set()
        used_cols = set()

        flat = []
        rows, cols = cost_matrix.shape
        for r in range(rows):
            for c in range(cols):
                flat.append((float(cost_matrix[r, c]), r, c))
        flat.sort(key=lambda item: item[0])

        for _, r, c in flat:
            if r in used_rows or c in used_cols:
                continue
            used_rows.add(r)
            used_cols.add(c)
            pairs.append((r, c))

        if not pairs:
            return [], []

        row_indices = [p[0] for p in pairs]
        col_indices = [p[1] for p in pairs]
        return row_indices, col_indices

    def _is_close_to_existing_track(self, detection: Dict) -> bool:
        for track in self.tracks.values():
            if track.missing > 0:
                continue
            if euclidean_distance(track.center, detection["center"]) < self.config.new_track_suppression_distance:
                return True
        return False

    def _remove_stale_tracks(self):
        stale_ids = [track_id for track_id, track in self.tracks.items() if track.missing > self.config.max_missing]
        for track_id in stale_ids:
            self.finished_tracks[track_id] = self.tracks.pop(track_id)

    def all_tracks(self) -> Dict[int, Track]:
        merged = dict(self.finished_tracks)
        merged.update(self.tracks)
        return merged

    def to_json_records(self) -> Dict:
        records = {}
        for track_id, track in sorted(self.all_tracks().items(), key=lambda item: item[0]):
            records[str(track_id)] = {
                "track_id": int(track.track_id),
                "initial_class_id": int(track.initial_class_id),
                "initial_class_name": str(track.initial_class_name),
                "frames": track.frames,
                "num_observed_frames": int(len(track.frames)),
            }
        return records
