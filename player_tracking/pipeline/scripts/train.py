#!/usr/bin/env python3
"""Train a YOLO model on one of the built datasets or a custom data.yaml.

Fresh runs use the T1 recipe; --fine-tune adapts the existing player/ref model.

Usage:
    python scripts/train.py all_teams
    python scripts/train.py player_ref --epochs 60 --batch 8
    python scripts/train.py --data datasets/player_ref_broadcast_clean/data.yaml --fine-tune --name broadcast_repaired

Outputs land in runs/detect/<name>/ (weights under .../weights/best.pt).
"""

import argparse
import json
from pathlib import Path

from dataset_integrity import audit_yaml

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("dataset", nargs="?", choices=["all_teams", "all_classes", "player_ref"],
                   default=None, help="named dataset under datasets/ (ignored if --data is given)")
    p.add_argument("--data", type=Path, default=None,
                   help="path to a built data.yaml with separate train and val image directories")
    p.add_argument("--name", default=None,
                   help="run name (default: dataset name, or the data.yaml's parent dir)")
    p.add_argument("--weights", default=None,
                   help="initial checkpoint (default: player_ref_best.pt with --fine-tune, otherwise yolo11s.pt)")
    p.add_argument("--fine-tune", action="store_true",
                   help="adapt the existing player/ref model with AdamW, low LR and gentler augmentation")
    p.add_argument("--lr0", type=float, default=None)
    p.add_argument("--patience", type=int, default=None,
                   help="early-stop patience (default 20 for fine-tuning, otherwise 10)")
    p.add_argument("--device", default=None, help="cpu, mps, or CUDA device index")
    p.add_argument("--preflight-only", action="store_true", help="check all images/labels and split isolation, then exit")
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--batch", type=int, default=16)
    args = p.parse_args()
    if args.lr0 is not None and args.lr0 <= 0:
        p.error("--lr0 must be positive")

    if args.data is not None:
        data_yaml = args.data.resolve()
        if not data_yaml.exists():
            raise SystemExit(f"{data_yaml} not found")
        run_name = args.name or data_yaml.parent.name  # e.g. "reviewed"
    elif args.dataset is not None:
        data_yaml = ROOT / "datasets" / args.dataset / "data.yaml"
        if not data_yaml.exists():
            raise SystemExit(f"{data_yaml} not found — run scripts/build_datasets.py first")
        run_name = args.name or args.dataset
    else:
        raise SystemExit("Provide a dataset name or --data path")

    try:
        snapshot = audit_yaml(data_yaml)
    except (ValueError, KeyError) as exc:
        raise SystemExit(f"Dataset preflight FAILED: {exc}") from exc
    for split, entries in snapshot["splits"].items():
        print(f"{split}: {len(entries)} verified pairs, "
              f"{sum(e['boxes'] for e in entries)} boxes, "
              f"{sum(e['boxes'] == 0 for e in entries)} explicit backgrounds")
    if args.preflight_only:
        return

    from ultralytics import YOLO

    weights = args.weights or (str(ROOT / "models" / "player_ref_best.pt")
                               if args.fine_tune else "yolo11s.pt")
    model = YOLO(weights)
    if args.fine_tune:
        names = snapshot["names"]
        names = dict(enumerate(names)) if isinstance(names, list) else names
        if model.names != names:
            raise SystemExit(f"Fine-tuning requires matching classes: checkpoint={model.names}, data={names}")

    def save_snapshot(trainer):
        (Path(trainer.save_dir) / "dataset_snapshot.json").write_text(json.dumps(snapshot, indent=2))

    model.add_callback("on_pretrain_routine_start", save_snapshot)
    options = {}
    if args.fine_tune:
        options.update(optimizer="AdamW", lr0=0.0001 if args.lr0 is None else args.lr0,
                       mosaic=0.0, scale=0.2, warmup_bias_lr=0.0)
    elif args.lr0 is not None:
        # optimizer=auto ignores manually supplied learning rates.
        options.update(optimizer="AdamW", lr0=args.lr0)
    if args.device is not None:
        options["device"] = args.device
    model.train(
        data=str(data_yaml),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        patience=args.patience if args.patience is not None else (20 if args.fine_tune else 10),
        seed=42,
        project=str(ROOT / "runs" / "detect"),
        name=run_name,
        **options,
    )


if __name__ == "__main__":
    main()
