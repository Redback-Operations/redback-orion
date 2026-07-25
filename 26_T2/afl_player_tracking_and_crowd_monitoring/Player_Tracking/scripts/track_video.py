#!/usr/bin/env python3
"""Run a trained model on a video with ByteTrack player tracking.

Writes an annotated video and a tracking CSV to outputs/.

Usage:
    python scripts/track_video.py data/videos/video_1.mp4
    python scripts/track_video.py data/videos/video_1.mp4 --model models/all_teams_best.pt
    python scripts/track_video.py data/videos/video_1.mp4 --max-frames 300   # quick test

CSV columns: frame, track_id, class, confidence, x1, y1, x2, y2 (pixels).
"""

import argparse
import csv
import subprocess
from pathlib import Path

import cv2
import imageio_ffmpeg
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("video", type=Path)
    p.add_argument("--model", type=Path, default=ROOT / "models" / "player_ref_best.pt")
    p.add_argument("--conf", type=float, default=0.4)
    p.add_argument("--tracker", default="bytetrack.yaml",
                   help="bytetrack.yaml or botsort.yaml")
    p.add_argument("--max-frames", type=int, default=None,
                   help="stop after N frames (for quick tests)")
    args = p.parse_args()

    if not args.video.exists():
        raise SystemExit(f"Video not found: {args.video}")
    if not args.model.exists():
        raise SystemExit(f"Model not found: {args.model}")

    out_dir = ROOT / "outputs"
    out_dir.mkdir(exist_ok=True)
    stem = f"{args.video.stem}_{args.model.stem}"
    out_video = out_dir / f"{stem}.mp4"
    out_csv = out_dir / f"{stem}.csv"

    model = YOLO(str(args.model))
    names = model.names

    cap = cv2.VideoCapture(str(args.video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

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

    n = 0
    with open(out_csv, "w", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["frame", "track_id", "class", "confidence",
                             "x1", "y1", "x2", "y2"])
        while True:
            ok, frame = cap.read()
            if not ok or (args.max_frames and n >= args.max_frames):
                break
            result = model.track(frame, persist=True, conf=args.conf,
                                 tracker=args.tracker, verbose=False)[0]
            if result.boxes is not None and result.boxes.id is not None:
                for box, tid, cls, conf in zip(result.boxes.xyxy.tolist(),
                                               result.boxes.id.tolist(),
                                               result.boxes.cls.tolist(),
                                               result.boxes.conf.tolist()):
                    csv_writer.writerow([n, int(tid), names[int(cls)],
                                         round(conf, 3),
                                         *(round(v, 1) for v in box)])
            writer.stdin.write(result.plot().tobytes())
            n += 1
            if n % 100 == 0:
                print(f"{n} frames...", flush=True)

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
    print(f"Done: {n} frames")
    print(f"  video: {out_video}")
    print(f"  csv:   {out_csv}")


if __name__ == "__main__":
    main()
