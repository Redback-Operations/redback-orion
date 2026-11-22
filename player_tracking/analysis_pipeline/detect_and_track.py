#!/usr/bin/env python3
"""Stage 1 of the analysis pipeline: find players in each frame and follow them.

Runs a YOLO model with ByteTrack on a video and writes an annotated H.264
video plus a tracks CSV. Later stages read the CSV instead of running the
model again.

Command line (run from player_tracking/):
    python analysis_pipeline/detect_and_track.py data/videos/video_1.mp4
    python analysis_pipeline/detect_and_track.py data/videos/video_1.mp4 --model models/all_teams_best.pt
    python analysis_pipeline/detect_and_track.py data/videos/video_1.mp4 --max-frames 300   # quick test
    python analysis_pipeline/detect_and_track.py data/videos/video_1.mp4 --start-frame 50000 \
        --track-id-offset 1200 --output-suffix _part2
    python analysis_pipeline/detect_and_track.py data/videos/broadcast.mp4 \
        --tracker analysis_pipeline/configs/afl_broadcast_bytetrack.yaml --grass-filter

From Python, call run(); it returns the output paths and video details.

CSV columns: frame, track_id, class, confidence, x1, y1, x2, y2 (pixels).
"""

import argparse
import csv
import subprocess
from pathlib import Path

import cv2
import imageio_ffmpeg
import torch
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = ROOT / "models" / "player_ref_best.pt"
BROADCAST_TRACKER = Path(__file__).resolve().parent / "configs" / "afl_broadcast_bytetrack.yaml"
CSV_COLUMNS = ["frame", "track_id", "class", "confidence", "x1", "y1", "x2", "y2"]


def grass_keep_mask(frame, boxes_xyxy, min_frac: float = 0.3):
    """Keep detections standing on green grass.

    Optional visual heuristic: require green pixels below the box. This does
    not repair a failed detector and may also remove valid players when their
    feet are occluded or over a field marking. Evaluate recall before using it.
    """
    H, W = frame.shape[:2]
    keep = []
    for x1, y1, x2, y2 in boxes_xyxy:
        bh = max(1.0, float(y2 - y1))
        ys = int(y2) + 1
        ye = min(H, int(y2 + max(4.0, 0.05 * bh)))
        xs = max(0, int(x1))
        xe = min(W, int(x2) + 1)
        if ye <= ys or xe <= xs:
            keep.append(True)  # box at frame edge — don't filter
            continue
        strip = frame[ys:ye, xs:xe].astype(int)
        b, g, r = strip[..., 0], strip[..., 1], strip[..., 2]
        green = (g > r + 15) & (g > b + 10)
        keep.append(bool(green.mean() >= min_frac))
    return keep


def run(
    video,
    model_path=DEFAULT_MODEL,
    tracker="bytetrack.yaml",
    conf: float = 0.4,
    out_dir=ROOT / "outputs",
    stem: str = None,
    max_frames: int = None,
    start_frame: int = 0,
    track_id_offset: int = 0,
    grass_filter: bool = False,
    grass_min: float = 0.3,
    log=print,
) -> dict:
    """Track players in a video. Returns the output paths and video details.

    The model is loaded on every call so tracker state never carries over
    from one video to the next.
    """
    video, model_path, out_dir = Path(video), Path(model_path), Path(out_dir)
    if not video.exists():
        raise FileNotFoundError(f"Video not found: {video}")
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}. Run: python training/download_models.py"
        )
    if start_frame < 0 or track_id_offset < 0:
        raise ValueError("start_frame and track_id_offset must be non-negative")
    if max_frames is not None and max_frames <= 0:
        raise ValueError("max_frames must be positive")

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = stem or f"{video.stem}_{model_path.stem}"
    out_video = out_dir / f"{stem}.mp4"
    out_csv = out_dir / f"{stem}.csv"

    model = YOLO(str(model_path))
    names = model.names

    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if start_frame >= total_frames:
        cap.release()
        raise ValueError(f"start_frame {start_frame} is outside video ({total_frames} frames)")
    if start_frame:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    # Pipe frames to ffmpeg for H.264 output (mp4v from cv2.VideoWriter is
    # unplayable in most players). frag_keyframe+empty_moov keeps the file
    # playable even if the run is interrupted mid-way.
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    writer = subprocess.Popen(
        [ffmpeg, "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
         "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-movflags", "frag_keyframe+empty_moov",
         "-loglevel", "error", str(out_video)],
        stdin=subprocess.PIPE)

    processed = 0
    source_frame = start_frame
    try:
        with open(out_csv, "w", newline="") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(CSV_COLUMNS)
            while True:
                ok, frame = cap.read()
                if not ok or (max_frames and processed >= max_frames):
                    break
                result = model.track(frame, persist=True, conf=conf,
                                     tracker=str(tracker), verbose=False)[0]
                if (grass_filter and result.boxes is not None
                        and len(result.boxes) > 0):
                    keep = grass_keep_mask(frame, result.boxes.xyxy.cpu().numpy(), grass_min)
                    idx = [i for i, k in enumerate(keep) if k]
                    if idx:
                        device = result.boxes.data.device
                        result.boxes = result.boxes[
                            torch.tensor(idx, dtype=torch.long, device=device)]
                    else:
                        result.boxes = None
                if result.boxes is not None and result.boxes.id is not None:
                    if track_id_offset:
                        # Keep the annotated video IDs consistent with the CSV IDs.
                        result.boxes.data = result.boxes.data.clone()
                        result.boxes.data[:, -3] += track_id_offset
                    for box, tid, cls, score in zip(result.boxes.xyxy.tolist(),
                                                    result.boxes.id.tolist(),
                                                    result.boxes.cls.tolist(),
                                                    result.boxes.conf.tolist()):
                        csv_writer.writerow([source_frame, int(tid), names[int(cls)],
                                             round(score, 3),
                                             *(round(v, 1) for v in box)])
                writer.stdin.write(result.plot().tobytes())
                processed += 1
                source_frame += 1
                if processed % 100 == 0:
                    log(f"{source_frame}/{total_frames} source frames ({processed} this run)...")
    finally:
        cap.release()
        writer.stdin.close()
        writer.wait()

    # Remux to a regular (non-fragmented) MP4 — fragmented files can show
    # blocky playback artifacts in some players.
    remux = out_video.with_suffix(".remux.mp4")
    subprocess.run(
        [ffmpeg, "-y", "-v", "error", "-i", str(out_video),
         "-c", "copy", "-movflags", "+faststart", str(remux)],
        check=True)
    remux.replace(out_video)

    return {
        "csv": out_csv,
        "video": out_video,
        "fps": fps,
        "width": w,
        "height": h,
        "total_frames": total_frames,
        "start_frame": start_frame,
        "processed_frames": processed,
        "class_names": dict(names),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("video", type=Path)
    p.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    p.add_argument("--conf", type=float, default=0.4)
    p.add_argument("--tracker", default="bytetrack.yaml",
                   help="bytetrack.yaml, botsort.yaml or a config file such as "
                        "analysis_pipeline/configs/afl_broadcast_bytetrack.yaml")
    p.add_argument("--max-frames", type=int, default=None,
                   help="stop after N frames (for quick tests)")
    p.add_argument("--start-frame", type=int, default=0,
                   help="seek to this zero-based source frame before tracking")
    p.add_argument("--track-id-offset", type=int, default=0,
                   help="add this value to IDs in resumed video/CSV output")
    p.add_argument("--output-suffix", default="",
                   help="append text such as _part2 to output filenames")
    p.add_argument("--grass-filter", action="store_true",
                   help="optional green-pixel heuristic below boxes; may also remove valid detections")
    p.add_argument("--grass-min", type=float, default=0.3,
                   help="min green fraction below a box to keep it (default 0.3)")
    args = p.parse_args()

    try:
        result = run(
            args.video,
            model_path=args.model,
            tracker=args.tracker,
            conf=args.conf,
            stem=f"{args.video.stem}_{args.model.stem}{args.output_suffix}",
            max_frames=args.max_frames,
            start_frame=args.start_frame,
            track_id_offset=args.track_id_offset,
            grass_filter=args.grass_filter,
            grass_min=args.grass_min,
        )
    except (FileNotFoundError, ValueError) as e:
        raise SystemExit(str(e))

    print(f"Done: {result['processed_frames']} frames")
    print(f"  video: {result['video']}")
    print(f"  csv:   {result['csv']}")


if __name__ == "__main__":
    main()
