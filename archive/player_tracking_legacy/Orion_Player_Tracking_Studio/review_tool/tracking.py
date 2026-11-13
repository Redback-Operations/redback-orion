from __future__ import annotations

import csv
import json
import subprocess
import tempfile
from pathlib import Path
from threading import Event
from typing import Callable


def inspect_model(path: str | Path) -> list[str]:
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise RuntimeError("Ultralytics is not installed") from exc
    names = YOLO(str(path)).names
    return [str(names[key]) for key in sorted(names)] if isinstance(names, dict) else list(names)


def track_video(
    video_path: str | Path,
    model_path: str | Path,
    output_folder: str | Path,
    tracker: str = "bytetrack.yaml",
    confidence: float = 0.4,
    max_frames: int | None = None,
    progress: Callable[[int, int, str], None] | None = None,
    cancel: Event | None = None,
) -> tuple[Path, Path, float]:
    try:
        import cv2
        import imageio_ffmpeg
        from ultralytics import YOLO
    except ImportError as exc:
        raise RuntimeError(f"Tracking setup problem: {exc}") from exc

    video_path = Path(video_path)
    model_path = Path(model_path)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    if max_frames is not None and max_frames <= 0:
        raise ValueError("Frame limit must be greater than zero")
    if not video_path.exists() or not model_path.exists():
        raise FileNotFoundError("Choose an existing video and model")

    model = YOLO(str(model_path))
    names = model.names
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if not cap.isOpened() or width <= 0 or height <= 0 or total <= 0:
        cap.release()
        raise ValueError("This video could not be opened. Choose a readable video file.")
    limit = min(total, max_frames) if max_frames else total
    stem = f"{video_path.stem}_{model_path.stem}"
    output_folder = Path(tempfile.mkdtemp(prefix="run_", dir=str(output_folder)))
    out_video = output_folder / f"{stem}.mp4"
    out_csv = output_folder / f"{stem}.csv"

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    writer = subprocess.Popen([
        ffmpeg, "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{width}x{height}",
        "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-pix_fmt", "yuv420p", "-movflags", "frag_keyframe+empty_moov", "-loglevel", "error", str(out_video),
    ], stdin=subprocess.PIPE)

    processed = 0
    try:
        with out_csv.open("w", newline="", encoding="utf-8") as handle:
            csv_writer = csv.writer(handle)
            csv_writer.writerow(["frame", "track_id", "class", "confidence", "x1", "y1", "x2", "y2"])
            while processed < limit:
                if cancel and cancel.is_set():
                    break
                ok, frame = cap.read()
                if not ok:
                    break
                result = model.track(frame, persist=True, conf=confidence, tracker=tracker, verbose=False)[0]
                if result.boxes is not None and result.boxes.id is not None:
                    for box, track_id, class_id, score in zip(
                        result.boxes.xyxy.tolist(), result.boxes.id.tolist(),
                        result.boxes.cls.tolist(), result.boxes.conf.tolist(),
                    ):
                        class_name = names[int(class_id)] if isinstance(names, dict) else names[int(class_id)]
                        csv_writer.writerow([processed, int(track_id), class_name, round(score, 4), *(round(value, 1) for value in box)])
                if writer.stdin:
                    writer.stdin.write(result.plot().tobytes())
                processed += 1
                if progress and (processed == 1 or processed % 10 == 0 or processed == limit):
                    progress(processed, limit, "Tracking players")
    finally:
        cap.release()
        if writer.stdin:
            writer.stdin.close()
        code = writer.wait()
    if code:
        raise RuntimeError("Video export failed. The tracking CSV remains in the run folder.")
    if processed == 0:
        raise RuntimeError("No frames were processed")
    out_csv.with_suffix(".json").write_text(json.dumps({
        "processed_frames": processed, "source_frames": total, "fps": fps,
        "source_video": str(video_path.resolve()),
        "width": width, "height": height,
        "stopped": processed < limit,
    }, indent=2), encoding="utf-8")

    if progress:
        progress(processed, limit, "Preparing review")
    return out_video, out_csv, fps
