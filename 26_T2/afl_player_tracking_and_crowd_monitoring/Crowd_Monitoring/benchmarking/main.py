import argparse

import torch

from config import (
    DEFAULT_CONF,
    DEFAULT_IOU,
    DEFAULT_N_FRAMES,
    DEFAULT_SHOW_SCALE,
    GROUND_TRUTH_PATH,
    MODELS,
    TILE_OVERLAP,
    TILE_SIZE,
    VIDEO_PATHS,
)
from inspection import diagnose, visualise
from measure import run_benchmark, sweep
from scoring import load_ground_truth, write_results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--diagnose",
        metavar="LABEL",
        choices=MODELS,
        help="Inspect one model's classes and raw detections. Use a key from MODELS.",
    )
    parser.add_argument(
        "--sweep",
        action="store_true",
        help="Compare all models' count across a range of confidence thresholds.",
    )
    parser.add_argument(
        "--truth",
        metavar="PATH",
        default=GROUND_TRUTH_PATH,
        help="JSON of {video_stem: {frame_index: true_count}} for MAE/RMSE scoring.",
    )
    parser.add_argument(
        "--show",
        metavar="LABEL",
        choices=MODELS,
        help="Play the videos with one model's detections drawn. Use a MODELS key.",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=DEFAULT_CONF,
        help="Confidence threshold for --show (drop to ~0.10 to see stock models).",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="With --show, also write annotated_<model>_<clip>.mp4 instead of only live view.",
    )
    parser.add_argument(
        "--show-scale",
        type=float,
        default=DEFAULT_SHOW_SCALE,
        help="Display scale for --show (0.25 = quarter size). Does NOT affect inference.",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=DEFAULT_N_FRAMES,
        help="Frames per clip. Drop this well below the default when tiling.",
    )
    parser.add_argument(
        "--tiled",
        action="store_true",
        help="Run full-resolution tiled inference instead of one downscaled pass.",
    )
    parser.add_argument(
        "--compare-tiling",
        action="store_true",
        help="Benchmark each model BOTH tiled and untiled. This is the only valid "
             "tiling comparison. Needs --truth to be conclusive.",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Print results without writing a JSON file to results/.",
    )
    args = parser.parse_args()

    if args.diagnose:
        diagnose(args.diagnose, MODELS[args.diagnose], VIDEO_PATHS)

    elif args.sweep:
        sweep(VIDEO_PATHS, n_frames=args.frames, tiled=args.tiled)

    elif args.show:
        visualise(args.show, MODELS[args.show], VIDEO_PATHS, conf=args.conf,
                  save=args.save, show_scale=args.show_scale, tiled=args.tiled)

    else:
        truth = load_ground_truth(args.truth)
        if truth is None:
            print(
                "NOTE: no --truth supplied. 'avg_count' is box count, NOT accuracy.\n"
                "      Supply hand-labelled frames for MAE/RMSE.\n"
            )
        results, skipped = run_benchmark(
            VIDEO_PATHS, truth=truth, n_frames=args.frames,
            conf=args.conf, tiled=args.tiled,
            compare_tiling=args.compare_tiling,
        )

        if not args.no_save:
            write_results(results, skipped, {
                "conf": args.conf,
                "iou": DEFAULT_IOU,
                "n_frames": args.frames,
                "tiled": args.tiled,
                "compare_tiling": args.compare_tiling,
                "truth_supplied": truth is not None,
                "tile_size": TILE_SIZE,
                "tile_overlap": TILE_OVERLAP,
                "torch": torch.__version__,
                "cuda_available": torch.cuda.is_available(),
            })


if __name__ == "__main__":
    main()