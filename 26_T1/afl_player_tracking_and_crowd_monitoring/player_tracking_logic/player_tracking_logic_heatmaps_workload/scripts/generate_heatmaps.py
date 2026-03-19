#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path
import yaml

# Wrapper: call heatmappipeline_xuan.py directly so we don't depend on a non-existent
# `heatmaps` package. Pulls defaults from config.yaml when present.

def _get(cfg, path, default=None):
    cur = cfg
    for k in path.split('.'):
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur


def main():
    ap = argparse.ArgumentParser(description="Generate heatmaps from tracking data (wrapper)")
    ap.add_argument(
        "--tracking",
        default="examples/tracking2.0.csv",
        help="Path to tracking CSV (default: examples/tracking2.0.csv)"
    )
    ap.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    ap.add_argument("--out-dir", required=True, help="Directory for saving heatmaps")
    ap.add_argument("--group-by", default="player_id", help="Column to group by (e.g. player_id)")

    # Optional overrides; if omitted we'll pull from config or fall back to sensible defaults
    ap.add_argument("--nx", type=int, default=None, help="Grid bins in X (override)")
    ap.add_argument("--ny", type=int, default=None, help="Grid bins in Y (override)")
    ap.add_argument("--sigma", type=float, default=None, help="Gaussian blur sigma in bins (override)")
    ap.add_argument("--weight-mode", default=None, help="Weighting: none|conf|visibility|conf*visibility (override)")

    args = ap.parse_args()

    # Load config (best-effort)
    try:
        with open(args.config, "r") as f:
            cfg = yaml.safe_load(f) or {}
    except FileNotFoundError:
        cfg = {}

    # Field dimensions with defaults
    L = float(_get(cfg, "field.length_m", 165.0))
    W = float(_get(cfg, "field.width_m", 135.0))

    # Heatmap tunables from config if present
    nx = args.nx if args.nx is not None else int(_get(cfg, "heatmap.nx", 200))
    ny = args.ny if args.ny is not None else int(_get(cfg, "heatmap.ny", 150))
    sigma = args.sigma if args.sigma is not None else float(_get(cfg, "heatmap.sigma", 2.0))

    weight_mode = args.weight_mode if args.weight_mode is not None else _get(cfg, "heatmap.weight_mode", "conf")

    # Build command to call the canonical pipeline
    repo_root = Path(__file__).resolve().parents[1]
    pipeline_py = repo_root / "heatmappipeline_xuan.py"

    cmd = [
        sys.executable, str(pipeline_py),
        "--inputs", f"{args.tracking}:Xuan",
        "--out-dir", args.out_dir,
        "--field-length", str(L),
        "--field-width", str(W),
        "--nx", str(nx),
        "--ny", str(ny),
        "--sigma", str(sigma),
        "--weight-mode", str(weight_mode),
    ]

    if args.group_by:
        cmd += ["--group-by", args.group_by]

    # Run and stream output
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"Done. Outputs in {args.out_dir}")


if __name__ == "__main__":
    main()