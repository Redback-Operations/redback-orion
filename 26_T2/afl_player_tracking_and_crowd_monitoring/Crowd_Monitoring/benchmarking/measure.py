import time
from pathlib import Path

from config import (
    DEFAULT_CONF,
    DEFAULT_IOU,
    DEFAULT_N_FRAMES,
    MODELS,
    SWEEP_THRESHOLDS,
)
from core import count_frame, load_model, model_device, read_frames, target_class
from scoring import score_against_truth, truth_for_video
from tiling import tile_grid

def benchmark_model(label, model_path, video_path, truth=None,
                    n_frames=DEFAULT_N_FRAMES, conf=DEFAULT_CONF,
                    iou=DEFAULT_IOU, tiled=False):
    """Benchmark one model against ONE video. truth is that video's
    {frame_idx: true_count} sub-map (already resolved by the caller).

    tiled=True runs the full-resolution tiled path instead of a single
    downscaled forward pass. Rows are tagged so tiled and untiled results are
    never mistaken for each other.
    """
    model = load_model(model_path)
    cid, cname = target_class(model, label)

    # Real weight file Ultralytics loaded, so the size metric works for both a
    # local path and a freshly-downloaded bare name.
    resolved = Path(getattr(model, "ckpt_path", None) or str(model_path))
    size_mb = round(resolved.stat().st_size / 1e6, 1) if resolved.is_file() else None

    frames = read_frames(video_path, n_frames)

    # warm-up (first call includes setup overhead, don't count it). Warmed on
    # the same path being timed, since tiled/untiled differ in postprocessing.
    count_frame(model, frames[0], cid, conf, iou, tiled=tiled)

    start = time.perf_counter()
    counts = [count_frame(model, f, cid, conf, iou, tiled=tiled) for f in frames]
    elapsed = time.perf_counter() - start

    result = {
        "label": label,
        "video": Path(video_path).name,
        "model": resolved.name,
        "counted_class": cname,  # report WHAT was counted, not always 'person'
        "tiled": tiled,  # tiled and untiled counts are NOT comparable
        "device": model_device(model),
        "model_size_mb": size_mb,
        "frames_tested": len(frames),
        "avg_latency_ms": round((elapsed / len(frames)) * 1000, 2),
        "fps": round(len(frames) / elapsed, 2),
        "avg_count": round(sum(counts) / len(counts), 1),
    }
    if tiled:
        h, w = frames[0].shape[:2]
        result["n_tiles"] = len(tile_grid(w, h))

    accuracy = score_against_truth(counts, truth)
    if accuracy is not None:
        result.update(accuracy)  # mae, rmse, n_labelled

    return result

def run_benchmark(video_paths, truth=None, n_frames=DEFAULT_N_FRAMES,
                  conf=DEFAULT_CONF, iou=DEFAULT_IOU, tiled=False,
                  compare_tiling=False):
    """Benchmark every model against every video, sequentially. Each clip gets
    its own result rows tagged with the source filename, so per-clip metrics
    stay comparable and one bad video/model doesn't sink the batch.

    compare_tiling=True runs each model BOTH ways, which is the only valid
    tiling comparison: same model, same clip, one variable changed.

    NOTE: rows are only cross-comparable where 'counted_class' AND 'tiled'
    match. A head count and a body count are different quantities, and so are
    a tiled and an untiled count.
    """
    if not video_paths:
        raise RuntimeError("VIDEO_PATHS is empty. Nothing to benchmark.")

    modes = [False, True] if compare_tiling else [tiled]
    results = []
    skipped = []
    for video_path in video_paths:
        print(f"\n=== video: {Path(video_path).name} ===")
        v_truth = truth_for_video(truth, video_path)
        if truth is not None and v_truth is None:
            print(f"  (no ground truth for '{Path(video_path).stem}': counts only)")
        if v_truth is None and any(modes):
            print("  (no truth for this clip: a HIGHER tiled count is not "
                  "evidence tiling is better. It may be counting seam duplicates)")

        for label, model_path in MODELS.items():
            for mode in modes:
                try:
                    row = benchmark_model(
                        label, model_path, video_path, truth=v_truth,
                        n_frames=n_frames, conf=conf, iou=iou, tiled=mode,
                    )
                    print(row)
                    results.append(row)
                except (FileNotFoundError, ValueError) as e:
                    # Missing weight/video, failed download, or a model with no
                    # countable class. Skip it, keep benchmarking the rest.
                    print(f"SKIPPED [{label}] tiled={mode} on "
                          f"{Path(video_path).name}: {e}")
                    skipped.append((label, mode, Path(video_path).name))
                except Exception as e:
                    print(f"SKIPPED [{label}] tiled={mode} on {Path(video_path).name}: "
                          f"unexpected {type(e).__name__}: {e}")
                    skipped.append((label, mode, Path(video_path).name))

    if skipped:
        print(f"\n{len(skipped)} run(s) skipped: {skipped}")

    return results, skipped

def sweep_video(video_path, thresholds=SWEEP_THRESHOLDS,
                n_frames=DEFAULT_N_FRAMES, iou=DEFAULT_IOU, tiled=False):
    """Compare every model's average per-frame count across confidence
    thresholds, for ONE video. Exposes the confidence-calibration difference
    between a stock COCO model and a domain-tuned one: a stock model may detect
    crowd members only at low confidence, so its count collapses toward 0 at a
    normal threshold while the tuned model stays stable. A single-threshold
    benchmark hides this. The spread (max - min count across thresholds) is a
    label-free stability proxy: smaller = better calibrated for THIS footage.

    NOTE: counts at very low thresholds (e.g. 0.05) include duplicate boxes and
    false positives. they are NOT ground truth. Validate against hand-labelled
    frames (--truth) before treating any single number as the true crowd size.

    NOTE: columns are only comparable to each other where the counted class
    matches (printed above the table). Spread stays valid per model regardless,
    since it is internal to that model's own series.
    """
    frames = read_frames(video_path, n_frames)

    # Load what we can; skip missing weights, failed downloads, or models with
    # no countable class, so one bad entry doesn't sink the comparison.
    models, class_ids, class_names = {}, {}, {}
    for label, path in MODELS.items():
        try:
            m = load_model(path)
            cid, cname = target_class(m, label)
            class_ids[label] = cid
            class_names[label] = cname
            models[label] = m
        except Exception as e:  # noqa: BLE001
            print(f"SKIPPED [{label}]: {type(e).__name__}: {e}")
    if not models:
        raise RuntimeError("No models could be loaded. Nothing to sweep.")

    # warm-up on the same path being measured
    for label, m in models.items():
        count_frame(m, frames[0], class_ids[label], 0.25, iou, tiled=tiled)

    print("counting:", ", ".join(f"{lbl} -> '{class_names[lbl]}'" for lbl in models))
    if len(set(class_names.values())) > 1:
        print("WARNING: models are counting DIFFERENT classes. Absolute counts "
              "across columns are not comparable, only per-model spread is.")
    if tiled:
        h, w = frames[0].shape[:2]
        print(f"tiled: {len(tile_grid(w, h))} tiles/frame. This will be slow")

    header = "conf   | " + " | ".join(f"{label:>22}" for label in models)
    print(header)
    print("-" * len(header))

    per_model_counts = {label: [] for label in models}
    for c in thresholds:
        row = [f"{c:<5.2f}"]
        for label, m in models.items():
            counts = [count_frame(m, f, class_ids[label], c, iou, tiled=tiled)
                      for f in frames]
            avg = sum(counts) / len(counts)
            per_model_counts[label].append(avg)
            row.append(f"{avg:>22.1f}")
        print(" | ".join(row))

    # Stability summary: spread across thresholds (lower = more stable).
    print("\nstability (max-min avg count across thresholds; lower = better):")
    for label, series in per_model_counts.items():
        spread = max(series) - min(series)
        print(f"  {label:>22} [{class_names[label]}]: {spread:.1f}")

def sweep(video_paths, thresholds=SWEEP_THRESHOLDS,
          n_frames=DEFAULT_N_FRAMES, iou=DEFAULT_IOU, tiled=False):
    """Run the confidence sweep on each video in turn. Calibration is
    footage-specific, so results are reported per-clip rather than blended."""
    if not video_paths:
        raise RuntimeError("VIDEO_PATHS is empty. Nothing to sweep.")
    for video_path in video_paths:
        print(f"\n=== sweep: {Path(video_path).name} ===")
        try:
            sweep_video(video_path, thresholds=thresholds,
                        n_frames=n_frames, iou=iou, tiled=tiled)
        except (FileNotFoundError, RuntimeError) as e:
            print("  skipped:", e)
