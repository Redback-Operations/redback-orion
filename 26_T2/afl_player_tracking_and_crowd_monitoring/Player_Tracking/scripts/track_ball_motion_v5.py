#!/usr/bin/env python3
"""Track one AFL match ball using detections plus short-term motion.

This is an experimental, standalone tracker. It does not modify Orion's player
tracker. Real detections and motion-only predictions are recorded separately so
that predicted positions are never mistaken for detector ground truth.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
from collections import deque
from dataclasses import dataclass
from ball_motion import Observation, forecast
from pathlib import Path

import cv2
import imageio_ffmpeg
from ultralytics import YOLO


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = ROOT / "training_runs" / "dataset_v4_30epochs" / "weights" / "best.pt"
DEFAULT_OUTPUT_DIR = ROOT / "temporal_tracker_runs" / "motion_v5"


@dataclass
class Candidate:
    box: tuple[float, float, float, float]
    confidence: float

    @property
    def center(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.box
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    @property
    def width(self) -> float:
        return self.box[2] - self.box[0]

    @property
    def height(self) -> float:
        return self.box[3] - self.box[1]

    @property
    def area(self) -> float:
        return self.width * self.height


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def shifted_box(
    box: tuple[float, float, float, float],
    center: tuple[float, float],
    frame_width: int,
    frame_height: int,
) -> tuple[float, float, float, float]:
    """Move the last box to a predicted centre while keeping it on screen."""
    width = box[2] - box[0]
    height = box[3] - box[1]
    x1 = max(0.0, min(center[0] - width / 2, frame_width - width))
    y1 = max(0.0, min(center[1] - height / 2, frame_height - height))
    return (x1, y1, x1 + width, y1 + height)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Experimental motion-based tracker for a single AFL ball."
    )
    parser.add_argument("video", type=Path)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--ball-class", type=int, default=0)
    parser.add_argument("--conf", type=float, default=0.05)
    parser.add_argument(
        "--new-track-conf",
        type=float,
        default=0.15,
        help="minimum confidence needed to begin a new track",
    )
    parser.add_argument(
        "--confirm-frames",
        type=int,
        default=3,
        help="nearby detections required before a new track is accepted",
    )
    parser.add_argument(
        "--confirmation-gate-ratio",
        type=float,
        default=0.04,
        help="new-track confirmation distance as a fraction of frame diagonal",
    )
    parser.add_argument(
        "--min-confirm-motion-ratio",
        type=float,
        default=0.003,
        help="movement required before accepting a new active-play track",
    )
    parser.add_argument("--imgsz", type=int, default=1280)
    parser.add_argument(
        "--max-gap",
        type=int,
        default=6,
        help="maximum missing frames bridged by motion prediction",
    )
    parser.add_argument(
        "--memory-gap",
        type=int,
        default=24,
        help="frames to remember a lost track without drawing predictions",
    )
    parser.add_argument(
        "--base-gate-ratio",
        type=float,
        default=0.025,
        help="base matching distance as a fraction of the frame diagonal",
    )
    parser.add_argument(
        "--max-gate-ratio",
        type=float,
        default=0.10,
        help="maximum association distance as a fraction of frame diagonal",
    )
    parser.add_argument(
        "--max-area-change-ratio",
        type=float,
        default=2.0,
        help="largest allowed box-area change between associated detections",
    )
    parser.add_argument(
        "--max-box-area-ratio",
        type=float,
        default=0.004,
        help="reject boxes larger than this fraction of the frame",
    )
    parser.add_argument("--max-aspect-ratio", type=float, default=4.0)
    parser.add_argument("--max-frames", type=int, default=None)
    parser.add_argument("--motion-window", type=int, default=5)
    parser.add_argument("--motion-max-span", type=int, default=12)
    parser.add_argument("--motion-residual-ratio", type=float, default=0.5)
    parser.add_argument("--motion-uncertainty-ratio", type=float, default=1.0)
    parser.add_argument(
        "--enable-controlled-reacquisition",
        action="store_true",
        help="allow a confirmed strong detection sequence to replace stale memory",
    )
    parser.add_argument("--reacquire-conf", type=float, default=0.35)
    parser.add_argument("--reacquire-frames", type=int, default=3)
    parser.add_argument("--reacquire-gate-ratio", type=float, default=0.035)
    args = parser.parse_args()
    if args.motion_window < 3 or args.motion_max_span < 2:
        parser.error("motion window must be >= 3 and span >= 2")
    if args.motion_residual_ratio <= 0 or args.motion_uncertainty_ratio <= 0:
        parser.error("motion ratios must be positive")
    if args.max_gap < 0 or args.memory_gap < args.max_gap:
        parser.error("require 0 <= max-gap <= memory-gap")
    if args.reacquire_frames < 2 or args.reacquire_conf < args.conf:
        parser.error("reacquisition requires >= 2 frames and confidence >= detector confidence")
    return args


def main() -> None:
    args = parse_args()
    if not args.video.exists():
        raise SystemExit(f"Video not found: {args.video}")
    if not args.model.exists():
        raise SystemExit(f"Model not found: {args.model}")

    capture = cv2.VideoCapture(str(args.video))
    if not capture.isOpened():
        raise SystemExit(f"Could not open video: {args.video}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_area = frame_width * frame_height
    frame_diagonal = math.hypot(frame_width, frame_height)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{args.video.stem}_temporal_ball"
    output_video = args.output_dir / f"{stem}.mp4"
    output_csv = args.output_dir / f"{stem}.csv"
    output_summary = args.output_dir / f"{stem}_summary.json"

    output_decisions = args.output_dir / f"{stem}_decisions.csv"
    if any(p.exists() for p in (output_video, output_csv, output_summary, output_decisions)):
        raise SystemExit("Output already exists; choose a new --output-dir")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    writer = subprocess.Popen(
        [
            ffmpeg,
            "-y",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "bgr24",
            "-s",
            f"{frame_width}x{frame_height}",
            "-r",
            str(fps),
            "-i",
            "-",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-loglevel",
            "error",
            str(output_video),
        ],
        stdin=subprocess.PIPE,
    )

    model = YOLO(str(args.model))
    active = False
    track_id = 0
    gap = 0
    last_box: tuple[float, float, float, float] | None = None
    last_center: tuple[float, float] | None = None
    velocity = (0.0, 0.0)
    trajectory: deque[tuple[int, int]] = deque(maxlen=30)
    pending_candidate: Candidate | None = None
    pending_start_center: tuple[float, float] | None = None
    pending_hits = 0
    reacquire_candidate: Candidate | None = None
    reacquire_hits = 0

    observations = deque(maxlen=args.motion_window)
    motion_rejections: dict[str, int] = {}
    suppressed_prediction_frames = 0
    frame_number = 0
    detected_frames = 0
    predicted_frames = 0
    missing_frames = 0
    rejected_large = 0
    rejected_shape = 0
    rejected_size_change = 0
    rejected_unconfirmed = 0
    reacquisition_attempts = 0
    reacquisitions = 0
    rejected_reacquisition_sequences = 0
    track_lengths: dict[int, int] = {}

    try:
        with output_csv.open("w", newline="") as csv_file, output_decisions.open("w", newline="") as decision_file:
            decision_writer = csv.writer(decision_file)
            decision_writer.writerow(["frame", "source", "track_id", "reason",
                                      "motion_observations", "fit_residual_px",
                                      "uncertainty_px"])
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(
                [
                    "frame",
                    "track_id",
                    "source",
                    "confidence",
                    "center_x",
                    "center_y",
                    "x1",
                    "y1",
                    "x2",
                    "y2",
                    "gap_length",
                    "motion_uncertainty_px",
                ]
            )

            while True:
                ok, frame = capture.read()
                if not ok or (
                    args.max_frames is not None and frame_number >= args.max_frames
                ):
                    break

                result = model.predict(
                    frame,
                    conf=args.conf,
                    imgsz=args.imgsz,
                    verbose=False,
                )[0]
                candidates: list[Candidate] = []

                if result.boxes is not None:
                    for box, confidence, class_id in zip(
                        result.boxes.xyxy.tolist(),
                        result.boxes.conf.tolist(),
                        result.boxes.cls.tolist(),
                    ):
                        if int(class_id) != args.ball_class:
                            continue
                        candidate = Candidate(tuple(box), float(confidence))
                        if candidate.area / frame_area > args.max_box_area_ratio:
                            rejected_large += 1
                            continue
                        aspect = max(
                            candidate.width / max(candidate.height, 1e-6),
                            candidate.height / max(candidate.width, 1e-6),
                        )
                        if aspect > args.max_aspect_ratio:
                            rejected_shape += 1
                            continue
                        candidates.append(candidate)

                motion = (forecast(
                    observations, frame_number, width=frame_width, height=frame_height,
                    max_gap=args.max_gap, max_span=args.motion_max_span,
                    residual_ratio=args.motion_residual_ratio,
                    uncertainty_ratio=args.motion_uncertainty_ratio,
                ) if observations else None)
                decision_reason = "no_active_track"
                chosen: Candidate | None = None
                reacquired_this_frame = False
                predicted_center: tuple[float, float] | None = None

                if active and last_center is not None and last_box is not None:
                    predicted_center = (
                        last_center[0] + velocity[0],
                        last_center[1] + velocity[1],
                    )
                    if motion is not None and motion.center is not None:
                        predicted_center = motion.center
                    speed = math.hypot(*(motion.velocity if motion and motion.center else velocity))
                    gate = (
                        args.base_gate_ratio * frame_diagonal
                        + speed * 1.5
                    )
                    gate = min(gate, args.max_gate_ratio * frame_diagonal)

                    position_matched = [
                        candidate
                        for candidate in candidates
                        if distance(candidate.center, predicted_center) <= gate
                    ]
                    previous_area = max(
                        (last_box[2] - last_box[0])
                        * (last_box[3] - last_box[1]),
                        1e-6,
                    )
                    matched: list[Candidate] = []
                    for candidate in position_matched:
                        area_change = max(
                            candidate.area / previous_area,
                            previous_area / max(candidate.area, 1e-6),
                        )
                        if area_change > args.max_area_change_ratio:
                            rejected_size_change += 1
                            continue
                        matched.append(candidate)

                    if matched:
                        def match_score(candidate: Candidate) -> float:
                            motion_cost = distance(candidate.center, predicted_center) / gate
                            size_cost = abs(math.log(max(candidate.area, 1e-6) / previous_area))
                            return motion_cost + 0.25 * size_cost - 0.35 * candidate.confidence

                        chosen = min(matched, key=match_score)

                if chosen is not None:
                    reacquire_candidate = None
                    reacquire_hits = 0
                elif (
                    args.enable_controlled_reacquisition
                    and active
                    and gap >= args.max_gap
                ):
                    eligible_reacquisitions = [
                        candidate
                        for candidate in candidates
                        if candidate.confidence >= args.reacquire_conf
                    ]
                    reacquire_gate = args.reacquire_gate_ratio * frame_diagonal
                    nearby_reacquisitions: list[Candidate] = []
                    if reacquire_candidate is not None:
                        nearby_reacquisitions = [
                            candidate
                            for candidate in eligible_reacquisitions
                            if distance(
                                candidate.center,
                                reacquire_candidate.center,
                            ) <= reacquire_gate
                        ]

                    if nearby_reacquisitions:
                        reacquire_candidate = min(
                            nearby_reacquisitions,
                            key=lambda candidate: (
                                distance(candidate.center, reacquire_candidate.center)
                                - 0.25 * reacquire_gate * candidate.confidence
                            ),
                        )
                        reacquire_hits += 1
                    elif eligible_reacquisitions:
                        if reacquire_candidate is not None:
                            rejected_reacquisition_sequences += 1
                        reacquire_candidate = max(
                            eligible_reacquisitions,
                            key=lambda candidate: candidate.confidence,
                        )
                        reacquire_hits = 1
                        reacquisition_attempts += 1
                    elif reacquire_candidate is not None:
                        rejected_reacquisition_sequences += 1
                        reacquire_candidate = None
                        reacquire_hits = 0

                    if reacquire_hits >= args.reacquire_frames:
                        chosen = reacquire_candidate
                        reacquire_candidate = None
                        reacquire_hits = 0
                        reacquired_this_frame = True
                        reacquisitions += 1
                        track_id += 1
                        track_lengths[track_id] = 0
                        gap = 0
                        last_center = None
                        last_box = None
                        velocity = (0.0, 0.0)
                        trajectory.clear()
                        observations.clear()
                        motion = None

                if not active:
                    eligible = [
                        candidate
                        for candidate in candidates
                        if candidate.confidence >= args.new_track_conf
                    ]
                    if eligible:
                        confirmation_gate = (
                            args.confirmation_gate_ratio * frame_diagonal
                        )
                        nearby: list[Candidate] = []
                        if pending_candidate is not None:
                            nearby = [
                                candidate
                                for candidate in eligible
                                if distance(
                                    candidate.center, pending_candidate.center
                                ) <= confirmation_gate
                            ]

                        if nearby:
                            pending_candidate = min(
                                nearby,
                                key=lambda candidate: (
                                    distance(
                                        candidate.center,
                                        pending_candidate.center,
                                    )
                                    - 0.25
                                    * confirmation_gate
                                    * candidate.confidence
                                ),
                            )
                            pending_hits += 1
                        else:
                            if pending_candidate is not None:
                                rejected_unconfirmed += pending_hits
                            pending_candidate = max(
                                eligible,
                                key=lambda candidate: candidate.confidence,
                            )
                            pending_start_center = pending_candidate.center
                            pending_hits = 1

                        if pending_hits >= args.confirm_frames:
                            confirmation_motion = distance(
                                pending_candidate.center,
                                pending_start_center,
                            )
                            minimum_motion = (
                                args.min_confirm_motion_ratio * frame_diagonal
                            )
                            if confirmation_motion >= minimum_motion:
                                chosen = pending_candidate
                                pending_candidate = None
                                pending_start_center = None
                                pending_hits = 0
                                track_id += 1
                                track_lengths[track_id] = 0
                                velocity = (0.0, 0.0)
                                trajectory.clear()
                                active = True
                                observations.clear()
                                motion = None
                            elif pending_hits >= args.confirm_frames * 2:
                                rejected_unconfirmed += pending_hits
                                pending_candidate = None
                                pending_start_center = None
                                pending_hits = 0
                    elif pending_candidate is not None:
                        rejected_unconfirmed += pending_hits
                        pending_candidate = None
                        pending_start_center = None
                        pending_hits = 0

                if chosen is not None:
                    center = chosen.center
                    if last_center is not None and gap == 0:
                        observed_velocity = (
                            center[0] - last_center[0],
                            center[1] - last_center[1],
                        )
                        velocity = (
                            0.65 * velocity[0] + 0.35 * observed_velocity[0],
                            0.65 * velocity[1] + 0.35 * observed_velocity[1],
                        )
                    last_center = center
                    last_box = chosen.box
                    if gap > args.max_gap:
                        observations.clear()
                    gap = 0
                    detected_frames += 1
                    track_lengths[track_id] += 1
                    trajectory.append((round(center[0]), round(center[1])))
                    source = "detected"
                    confidence = chosen.confidence
                    observations.append(Observation(
                        frame_number, center[0], center[1],
                        math.hypot(chosen.width, chosen.height),
                    ))
                    decision_reason = (
                        "controlled_reacquisition"
                        if reacquired_this_frame
                        else "accepted_detection"
                    )
                    colour = (0, 220, 0)
                elif active and last_center is not None and last_box is not None:
                    gap += 1
                    decision_reason = motion.reason if motion else "insufficient_history"
                    if gap <= args.memory_gap and predicted_center is not None:
                        center = (
                            max(0.0, min(predicted_center[0], frame_width - 1)),
                            max(0.0, min(predicted_center[1], frame_height - 1)),
                        )
                        last_center = center
                        last_box = shifted_box(
                            last_box, center, frame_width, frame_height
                        )
                        if gap <= args.max_gap and motion is not None and motion.allowed:
                            predicted_frames += 1
                            track_lengths[track_id] += 1
                            trajectory.append((round(center[0]), round(center[1])))
                            source = "predicted"
                            confidence = 0.0
                            colour = (0, 165, 255)
                        else:
                            if gap <= args.max_gap:
                                suppressed_prediction_frames += 1
                                motion_rejections[decision_reason] = motion_rejections.get(decision_reason, 0) + 1
                            trajectory.clear()
                            missing_frames += 1
                            source = "missing"
                            confidence = 0.0
                            colour = (0, 0, 0)
                    else:
                        active = False
                        observations.clear()
                        reacquire_candidate = None
                        reacquire_hits = 0
                        decision_reason = "memory_expired"
                        gap = 0
                        last_center = None
                        last_box = None
                        velocity = (0.0, 0.0)
                        trajectory.clear()
                        missing_frames += 1
                        source = "missing"
                        confidence = 0.0
                        colour = (0, 0, 0)
                else:
                    missing_frames += 1
                    source = "missing"
                    confidence = 0.0
                    colour = (0, 0, 0)

                if source != "missing" and last_box is not None and last_center is not None:
                    x1, y1, x2, y2 = last_box
                    csv_writer.writerow(
                        [
                            frame_number,
                            track_id,
                            source,
                            round(confidence, 4),
                            round(last_center[0], 1),
                            round(last_center[1], 1),
                            round(x1, 1),
                            round(y1, 1),
                            round(x2, 1),
                            round(y2, 1),
                            gap,
                            round(motion.uncertainty_px, 3) if source == "predicted" else 0.0,
                        ]
                    )
                    cv2.rectangle(
                        frame,
                        (round(x1), round(y1)),
                        (round(x2), round(y2)),
                        colour,
                        2,
                    )
                    label = f"BALL id:{track_id} {source}"
                    if source == "detected":
                        label += f" {confidence:.2f}"
                    else:
                        label += f" uncertainty:{motion.uncertainty_px:.1f}px"
                    cv2.putText(
                        frame,
                        label,
                        (round(x1), max(20, round(y1) - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        colour,
                        2,
                        cv2.LINE_AA,
                    )

                decision_writer.writerow([
                    frame_number, source, track_id if active else "",
                    decision_reason, len(observations),
                    round(motion.residual_px, 4) if motion else "",
                    round(motion.uncertainty_px, 4) if motion else "",
                ])
                points = list(trajectory)
                for start, end in zip(points, points[1:]):
                    cv2.line(frame, start, end, (255, 180, 0), 2)

                if writer.stdin is None:
                    raise RuntimeError("ffmpeg input pipe was not created")
                writer.stdin.write(frame.tobytes())
                frame_number += 1
                if frame_number % 100 == 0:
                    print(f"{frame_number} frames...", flush=True)
    finally:
        capture.release()
        if writer.stdin is not None:
            writer.stdin.close()
        writer.wait()

    summary = {
        "algorithm_version": 6 if args.enable_controlled_reacquisition else 5,
        "suppressed_prediction_frames": suppressed_prediction_frames,
        "motion_rejections": motion_rejections,
        "motion_method": "Linear fit over recent accepted detections; predictions never enter fit. Pixel uncertainty is heuristic, not calibrated.",
        "development_status": "Experimental; quality improvement not yet established",
        "controlled_reacquisition": {
            "enabled": args.enable_controlled_reacquisition,
            "attempts": reacquisition_attempts,
            "successful_reacquisitions": reacquisitions,
            "rejected_sequences": rejected_reacquisition_sequences + int(reacquire_hits > 0),
        },
        "video": str(args.video),
        "model": str(args.model),
        "frames_processed": frame_number,
        "detected_frames": detected_frames,
        "predicted_bridge_frames": predicted_frames,
        "missing_frames": missing_frames,
        "track_starts": track_id,
        "longest_track_frames": max(track_lengths.values(), default=0),
        "rejected_large_detections": rejected_large,
        "rejected_shape_detections": rejected_shape,
        "rejected_size_change_detections": rejected_size_change,
        "rejected_unconfirmed_detection_frames": (
            rejected_unconfirmed + pending_hits
        ),
        "settings": {
            "confidence": args.conf,
            "new_track_confidence": args.new_track_conf,
            "confirm_frames": args.confirm_frames,
            "confirmation_gate_ratio": args.confirmation_gate_ratio,
            "min_confirm_motion_ratio": args.min_confirm_motion_ratio,
            "image_size": args.imgsz,
            "max_gap": args.max_gap,
            "motion_window": args.motion_window,
            "motion_max_span": args.motion_max_span,
            "motion_residual_ratio": args.motion_residual_ratio,
            "motion_uncertainty_ratio": args.motion_uncertainty_ratio,
            "reacquire_confidence": args.reacquire_conf,
            "reacquire_frames": args.reacquire_frames,
            "reacquire_gate_ratio": args.reacquire_gate_ratio,
            "memory_gap": args.memory_gap,
            "base_gate_ratio": args.base_gate_ratio,
            "max_gate_ratio": args.max_gate_ratio,
            "max_area_change_ratio": args.max_area_change_ratio,
            "max_box_area_ratio": args.max_box_area_ratio,
            "max_aspect_ratio": args.max_aspect_ratio,
        },
        "outputs": {
            "video": str(output_video),
            "csv": str(output_csv),
            "decisions": str(output_decisions),
        },
    }
    output_summary.write_text(json.dumps(summary, indent=2) + "\n")

    print(json.dumps(summary, indent=2))
    print(f"Annotated video: {output_video}")
    print(f"Tracking CSV:    {output_csv}")
    print(f"Run summary:     {output_summary}")


if __name__ == "__main__":
    main()
