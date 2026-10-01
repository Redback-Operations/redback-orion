import json
import time
from pathlib import Path

from config import RESULTS_DIR

def load_ground_truth(path):
    """Load per-video truth from JSON.
 
    Expected shape: {video_stem: {frame_index: true_count}}. Keys are
    stringified in the file; normalised here. Outer keys stay str (filename
    stems), inner keys become int frame indices. Returns None if no path given.
    """
    if path is None:
        return None
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Ground-truth file not found: {path}")
    with open(path) as f:
        raw = json.load(f)
    return {
        str(stem): {int(k): int(v) for k, v in frames.items()}
        for stem, frames in raw.items()
    }

def truth_for_video(truth, video_path):
    """Pull the {frame_idx: count} sub-map for one clip, or None if unlabelled."""
    if not truth:
        return None
    return truth.get(Path(video_path).stem)

def score_against_truth(counts, truth):
    """counts: per-frame count list. truth: {frame_idx: true_count}.
    Returns MAE and RMSE over the labelled frames only, or None if no overlap.
    These are the standard crowd-counting accuracy metrics."""
    if not truth:
        return None
    errs = [counts[i] - t for i, t in truth.items() if i < len(counts)]
    if not errs:
        return None
    mae = sum(abs(e) for e in errs) / len(errs)
    rmse = (sum(e * e for e in errs) / len(errs)) ** 0.5
    return {"mae": round(mae, 2), "rmse": round(rmse, 2), "n_labelled": len(errs)}

def write_results(results, skipped, settings):
    """Write one run's rows plus the settings that produced them."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = RESULTS_DIR / f"benchmark-{stamp}.json"

    payload = {
        "timestamp": stamp,
        "settings": settings,
        "results": results,
        "skipped": [
            {"label": l, "tiled": m, "video": v} for l, m, v in skipped
        ],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"\nwritten: {path}")
    return path