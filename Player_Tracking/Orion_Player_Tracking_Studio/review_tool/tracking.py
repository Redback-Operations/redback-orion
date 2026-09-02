from __future__ import annotations

import csv
import subprocess
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
        raise RuntimeError("Install the tracking requirements before starting a new run") from exc

    video_path = Path(video_path)
    model_path = Path(model_path)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    if not video_path.exists() or not model_path.exists():
        raise FileNotFoundError("Choose an existing video and model")

    model = YOLO(str(model_path))
    names = model.names
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    limit = min(total, max_frames) if max_frames else total
    stem = f"{video_path.stem}_{model_path.stem}"
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
        writer.wait()

    if progress:
        progress(processed, limit, "Preparing review")
    return out_video, out_csv, fps
