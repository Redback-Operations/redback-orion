#!/usr/bin/env python3
"""Run a trained model on a video with ByteTrack player tracking.

Writes an annotated video and a tracking CSV to outputs/.

Usage:
    python scripts/track_video.py data/videos/video_1.mp4
    python scripts/track_video.py data/videos/video_1.mp4 --model models/all_teams_best.pt
    python scripts/track_video.py data/videos/video_1.mp4 --max-frames 300   # quick test
    python scripts/track_video.py data/videos/video_1.mp4 --start-frame 50000 \
        --track-id-offset 1200 --output-suffix _part2

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
    p.add_argument("--start-frame", type=int, default=0,
                   help="seek to this zero-based source frame before tracking")
    p.add_argument("--track-id-offset", type=int, default=0,
                   help="add this value to IDs in resumed video/CSV output")
    p.add_argument("--output-suffix", default="",
                   help="append text such as _part2 to output filenames")
    args = p.parse_args()

    if not args.video.exists():
        raise SystemExit(f"Video not found: {args.video}")
    if not args.model.exists():
        raise SystemExit(f"Model not found: {args.model}")
    if args.start_frame < 0 or args.track_id_offset < 0:
        raise SystemExit("start-frame and track-id-offset must be non-negative")
    if args.max_frames is not None and args.max_frames <= 0:
        raise SystemExit("max-frames must be positive")

    out_dir = ROOT / "outputs"
    out_dir.mkdir(exist_ok=True)
    stem = f"{args.video.stem}_{args.model.stem}{args.output_suffix}"
    out_video = out_dir / f"{stem}.mp4"
    out_csv = out_dir / f"{stem}.csv"

    model = YOLO(str(args.model))
    names = model.names

    cap = cv2.VideoCapture(str(args.video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if args.start_frame >= total_frames:
        raise SystemExit(
            f"start-frame {args.start_frame} is outside video ({total_frames} frames)"
        )
    if args.start_frame:
        cap.set(cv2.CAP_PROP_POS_FRAMES, args.start_frame)

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
    source_frame = args.start_frame
    with open(out_csv, "w", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["frame", "track_id", "class", "confidence",
                             "x1", "y1", "x2", "y2"])
        while True:
            ok, frame = cap.read()
            if not ok or (args.max_frames and processed >= args.max_frames):
                break
            result = model.track(frame, persist=True, conf=args.conf,
                                 tracker=args.tracker, verbose=False)[0]
            if result.boxes is not None and result.boxes.id is not None:
                if args.track_id_offset:
                    # Keep the annotated video IDs consistent with the CSV IDs.
                    result.boxes.data = result.boxes.data.clone()
                    result.boxes.data[:, -3] += args.track_id_offset
                for box, tid, cls, conf in zip(result.boxes.xyxy.tolist(),
                                               result.boxes.id.tolist(),
                                               result.boxes.cls.tolist(),
                                               result.boxes.conf.tolist()):
                    csv_writer.writerow([source_frame, int(tid), names[int(cls)],
                                         round(conf, 3),
                                         *(round(v, 1) for v in box)])
            writer.stdin.write(result.plot().tobytes())
            processed += 1
            source_frame += 1
            if processed % 100 == 0:
                print(
                    f"{source_frame}/{total_frames} source frames "
                    f"({processed} this run)...",
                    flush=True,
                )

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
    print(f"Done: {processed} frames")
    print(f"  video: {out_video}")
    print(f"  csv:   {out_csv}")


if __name__ == "__main__":
    main()
