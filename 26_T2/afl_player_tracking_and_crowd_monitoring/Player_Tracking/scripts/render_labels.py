#!/usr/bin/env python3
"""Render saved YOLO labels onto a video.

Draws the label boxes (e.g. produced by smart_labeller.py) over every frame
that has a label file and writes a new H.264 video. Frames without labels are
copied through unchanged, so the output keeps the source timing.

Usage:
    python scripts/render_labels.py data/videos/broadcast_stkilda_northmelbourne.mp4
    python scripts/render_labels.py data/videos/broadcast_stkilda_northmelbourne.mp4 \
        --labels-dir data/raw/broadcast_stkilda_northmelbourne/reviewed/labels \
        --output outputs/broadcast_stkilda_northmelbourne_reviewed.mp4
"""

import argparse
import subprocess
from pathlib import Path

import cv2
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent.parent

CLASS_COLOURS = {
    0: (0, 165, 255),   # player - orange
    1: (0, 255, 255),   # ref    - yellow
}
CLASS_NAMES = {0: "player", 1: "ref"}


def load_labels(labels_dir: Path, video_name: str, w: int, h: int) -> dict:
    """Return {frame_idx: [(cls, x1, y1, x2, y2), ...]} from YOLO label files."""
    labels = {}
    prefix = f"{video_name}_frame_"
    for txt in sorted(labels_dir.glob(f"{prefix}*.txt")):
        try:
            frame_idx = int(txt.stem[len(prefix):])
        except ValueError:
            continue
        boxes = []
        for line in txt.read_text().splitlines():
            parts = line.split()
            if len(parts) != 5:
                continue
            cls, xc, yc, bw, bh = map(float, parts)
            cls = 1 if int(cls) == 2 else int(cls)  # fold old umpire class into ref
            xc = min(1.0, max(0.0, xc))
            yc = min(1.0, max(0.0, yc))
            bw = min(1.0, max(0.0, bw))
            bh = min(1.0, max(0.0, bh))
            x1 = int((xc - bw / 2) * w)
            y1 = int((yc - bh / 2) * h)
            x2 = int((xc + bw / 2) * w)
            y2 = int((yc + bh / 2) * h)
            boxes.append((cls, x1, y1, x2, y2))
        labels[frame_idx] = boxes
    return labels


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video", type=Path)
    p.add_argument("--labels-dir", type=Path, default=None,
                   help="directory with YOLO .txt files (default: data/raw/<video_stem>/labels)")
    p.add_argument("--output", type=Path, default=None,
                   help="output video path (default: outputs/<stem>_labelled.mp4)")
    p.add_argument("--max-frames", type=int, default=None, help="stop after N frames")
    args = p.parse_args()

    if not args.video.exists():
        raise SystemExit(f"Video not found: {args.video}")
    labels_dir = args.labels_dir or (ROOT / "data" / "raw" / args.video.stem / "labels")
    if not labels_dir.exists():
        raise SystemExit(f"Labels not found: {labels_dir}")
    output = args.output or (ROOT / "outputs" / f"{args.video.stem}_labelled.mp4")
    output.parent.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise SystemExit(f"Could not open video: {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    labels = load_labels(labels_dir, args.video.stem, w, h)
    print(f"{len(labels)} labelled frames loaded from {labels_dir}")

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    writer = subprocess.Popen(
        [ffmpeg, "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
         "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-movflags", "frag_keyframe+empty_moov",
         "-loglevel", "error", str(output)],
        stdin=subprocess.PIPE)

    frame_idx = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok or (args.max_frames and frame_idx >= args.max_frames):
                break
            for cls, x1, y1, x2, y2 in labels.get(frame_idx, []):
                colour = CLASS_COLOURS.get(cls, (255, 255, 255))
                cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)
                name = CLASS_NAMES.get(cls, "?")
                (tw, th), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 6, y1), colour, -1)
                cv2.putText(frame, name, (x1 + 3, y1 - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            writer.stdin.write(frame.tobytes())
            frame_idx += 1
            if frame_idx % 1000 == 0:
                print(f"  {frame_idx}/{total} frames...", flush=True)
    finally:
        cap.release()
        writer.stdin.close()
        writer.wait()

    # Remux to a regular (non-fragmented) MP4.
    remux = output.with_suffix(".remux.mp4")
    subprocess.run(
        [ffmpeg, "-y", "-v", "error", "-i", str(output),
         "-c", "copy", "-movflags", "+faststart", str(remux)],
        check=True)
    remux.replace(output)
    print(f"Done: {frame_idx} frames -> {output}")


if __name__ == "__main__":
    main()
