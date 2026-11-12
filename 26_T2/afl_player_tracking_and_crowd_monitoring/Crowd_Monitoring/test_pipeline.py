"""
Chains crowd detection -> density zoning -> behaviour analytics on a short
sequence of frames, and reports how many detected people the tracker follows.

Run from the Crowd_Monitoring folder with the venv active:
    source .venv/Scripts/activate
    python test_pipeline.py

extract_frames() is importable so benchmark_models.py can share it rather than
keeping its own copy of the decode loop. Decode settings (fps fallback, JPEG
quality) are explicit arguments for the same reason: if the two scripts write
frames differently the timings stop being comparable.
"""

import json
import time
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path

import cv2

from crowd_detection.main import detect_crowd
from density_zoning.main import analyze_density
from crowd_behaviour_analytics.main import analyze_behaviour

VIDEO = "benchmarking/videos/side.mp4"
START_FRAME = 100
NUM_FRAMES = 20
FRAME_DIR = Path("test_frames")
FPS_FALLBACK = 25.0
JPEG_QUALITY = 95

# Over a short contiguous clip most people persist across all frames, so unique
# tracks should sit close to the peak per-frame count. Well above that means the
# tracker is breaking one person into several IDs.
FRAGMENTATION_THRESHOLD = 1.3

_stage_times = {}


@contextmanager
def stage(name):
    """Record wall time for a pipeline stage into _stage_times."""
    start = time.perf_counter()
    try:
        yield
    finally:
        _stage_times[name] = time.perf_counter() - start


def extract_frames(video=VIDEO, start_frame=START_FRAME, num_frames=NUM_FRAMES,
                   out_dir=FRAME_DIR, jpeg_quality=JPEG_QUALITY,
                   fps_fallback=FPS_FALLBACK):
    """Write consecutive frames to disk and return (frames, width, height)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)

    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        raise SystemExit(f"could not open video: {video}")

    fps = cap.get(cv2.CAP_PROP_FPS) or fps_fallback
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    frames = []
    height = width = 0

    for i in range(num_frames):
        ok, frame = cap.read()
        if not ok:
            print(f"[WARN] video ended after {i} frames")
            break

        if not height:
            height, width = frame.shape[:2]

        frame_id = start_frame + i
        path = out_dir / f"frame_{frame_id:04d}.jpg"
        cv2.imwrite(str(path), frame,
                    [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])

        frames.append({
            "frame_id": frame_id,
            "timestamp": round(frame_id / fps, 3),
            "frame_path": str(path).replace("\\", "/"),
        })

    cap.release()
    print(f"extracted {len(frames)} frames at {width}x{height}, {fps:.1f} fps")
    return frames, width, height


def per_frame_track_counts(tracking):
    """
    Map frame_id -> number of tracks present in that frame.

    Returns None if the tracker only reports summary data. A real tracked
    proportion needs per-frame membership; without it there is no honest way to
    divide track_count by anything.
    """
    counts = defaultdict(int)
    found = False

    for track in tracking.get("tracks", []):
        history = (track.get("frame_ids")
                   or track.get("frames")
                   or track.get("history")
                   or [])
        for entry in history:
            frame_id = entry.get("frame_id") if isinstance(entry, dict) else entry
            if frame_id is None:
                continue
            counts[frame_id] += 1
            found = True

    return dict(counts) if found else None


def report_tracking(tracking, detection_frames):
    """Print tracking quality using the strongest metric the data supports."""
    track_count = tracking.get("track_count", 0)
    detections = {f["frame_id"]: f["person_count"] for f in detection_frames}
    peak = max(detections.values()) if detections else 0

    print(f"unique tracks          : {track_count}")

    if peak:
        ratio = track_count / peak
        note = " (suggests ID fragmentation)" if ratio > FRAGMENTATION_THRESHOLD else ""
        print(f"tracks / peak frame    : {ratio:.2f}{note}")

    matched = per_frame_track_counts(tracking)
    if matched is None:
        print("tracked proportion     : unavailable, tracker reports no "
              "per-frame track membership")
        return

    total_tracked = sum(matched.get(fid, 0) for fid in detections)
    total_detected = sum(detections.values())
    if total_detected:
        print(f"tracked proportion     : {total_tracked / total_detected:.1%} "
              f"of detections matched to a track")

    worst = min(
        ((fid, matched.get(fid, 0), n) for fid, n in detections.items() if n),
        key=lambda row: row[1] / row[2],
        default=None,
    )
    if worst:
        fid, tracked, detected = worst
        print(f"worst frame            : {fid} ({tracked}/{detected} tracked)")


def main():
    frames, width, height = extract_frames()
    if not frames:
        raise SystemExit("no frames extracted, check the video path")

    # ---- Stage 1: detection -------------------------------------------------
    with stage("detection"):
        detection = detect_crowd({
            "video_id": "test_01",
            "frame_width": width,
            "frame_height": height,
            "frames": frames,
        })

    # ---- Stage 2: density zoning -------------------------------------------
    # grid_rows/grid_cols are not in SCHEMA.md but appear in the module's own
    # sample payload. Remove them if analyze_density rejects them.
    with stage("density"):
        density = analyze_density({
            "video_id": detection["video_id"],
            "frame_width": detection["frame_width"],
            "frame_height": detection["frame_height"],
            "grid_rows": 3,
            "grid_cols": 3,
            "frames": detection["frames"],
        })

    zones = density.get("zones", [])

    # ---- Stage 3: behaviour analytics --------------------------------------
    # heatmap is passed empty: analyze_behaviour only reads image_path from it.
    with stage("behaviour"):
        behaviour = analyze_behaviour({
            "video_id": detection["video_id"],
            "zones": zones,
            "heatmap": {},
            "frames": detection["frames"],
        })

    # ---- Timing -------------------------------------------------------------
    print("\n--- timing ---")
    total = sum(_stage_times.values())
    for name, elapsed in _stage_times.items():
        share = elapsed / total if total else 0
        print(f"{name:<10}: {elapsed:6.2f}s  "
              f"{elapsed / len(frames):5.3f}s/frame  {share:5.1%}")
    print(f"{'total':<10}: {total:6.2f}s")

    # ---- Results ------------------------------------------------------------
    counts = [f["person_count"] for f in detection["frames"]]

    print("\n--- results ---")
    print(f"zones returned         : {len(zones)}")
    print(f"person_count per frame : min {min(counts)}, max {max(counts)}, "
          f"avg {sum(counts) / len(counts):.1f}")

    report_tracking(
        behaviour.get("vision_metrics", {}).get("tracking", {}),
        detection["frames"],
    )

    print(f"crowd_state            : {behaviour.get('crowd_state')}")
    print(f"event_flags            : {behaviour.get('event_flags')}")

    Path("pipeline_output.json").write_text(
        json.dumps({"density": density, "behaviour": behaviour}, indent=2),
        encoding="utf-8",
    )
    print("\nfull output written to pipeline_output.json")


if __name__ == "__main__":
    main()