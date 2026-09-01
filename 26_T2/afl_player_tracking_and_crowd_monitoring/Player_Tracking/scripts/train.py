#!/usr/bin/env python3
"""Train a YOLO model on one of the built datasets.

Follows the T1 recipe: yolo11s pretrained base, imgsz 640, batch 16, seed 42.

Usage:
    python scripts/train.py all_teams
    python scripts/train.py player_ref --epochs 60 --batch 8

Outputs land in runs/detect/<dataset>/ (weights under .../weights/best.pt).
"""

import argparse
from pathlib import Path

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("dataset", choices=["all_teams", "all_classes", "player_ref"])
    p.add_argument("--weights", default="yolo11s.pt",
                   help="pretrained weights to start from (default yolo11s.pt)")
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--batch", type=int, default=16)
    args = p.parse_args()

    data_yaml = ROOT / "datasets" / args.dataset / "data.yaml"
    if not data_yaml.exists():
        raise SystemExit(f"{data_yaml} not found — run scripts/build_datasets.py first")

    model = YOLO(args.weights)
    model.train(
        data=str(data_yaml),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        patience=10,
        seed=42,
        project=str(ROOT / "runs" / "detect"),
        name=args.dataset,
    )


if __name__ == "__main__":
    main()
