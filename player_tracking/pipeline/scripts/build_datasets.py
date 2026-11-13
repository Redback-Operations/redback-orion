#!/usr/bin/env python3
"""Build train/val datasets from the raw T1 match datasets.

Reads from data/raw/{gcs_vs_car,ss_vs_wb,cat_vs_haw} and writes:

  datasets/all_teams/     combined, 7 classes
                          (CAR GCS HAW CAT REF SS WB)
                          BALL/POST boxes are dropped (too thin: 29/114 boxes).
                          T1's unified model had BALL/POST instead of SS/WB —
                          they never merged the SS_vs_WB dataset.
  datasets/all_classes/   combined, 9 classes — everything
                          (CAR GCS HAW CAT REF SS WB BALL POST)
  datasets/player_ref/    combined, 2 classes (PLAYER REF);
                          BALL/POST boxes are dropped.

All splits are 80/20 train/val, shuffled with seed 42 (same as T1).
In combined datasets, files are prefixed with the source dataset name
(e.g. ss_vs_wb__012f0df2-01.jpg) to avoid filename collisions.

Usage:
    python scripts/build_datasets.py
"""

import random
import shutil
import argparse
import json
from pathlib import Path

import yaml
from dataset_integrity import read_pairs

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "datasets"
SEED = 42
VAL_FRACTION = 0.2
EXPECTED_RAW_COUNTS = {"gcs_vs_car": 200, "ss_vs_wb": 194, "cat_vs_haw": 176}

# Original class indices per raw dataset, from each dataset's classes.txt.
RAW_CLASSES = {
    "gcs_vs_car": ["CAR", "GCS", "REF"],
    "ss_vs_wb": ["REF", "SS", "WB"],
    "cat_vs_haw": ["BALL", "CAT", "HAW", "POST", "REF"],
}

# Combined all-teams layout. BALL/POST dropped (too thin to train).
ALL_TEAMS_CLASSES = ["CAR", "GCS", "HAW", "CAT", "REF", "SS", "WB"]

# Combined all-classes layout — everything, including BALL and POST.
ALL_CLASSES_CLASSES = ["CAR", "GCS", "HAW", "CAT", "REF", "SS", "WB", "BALL", "POST"]

PLAYER_REF_CLASSES = ["PLAYER", "REF"]

# Per-dataset remap into the all-teams index space; None = drop the box.
ALL_TEAMS_MAP = {
    ds: {i: (None if name in ("BALL", "POST") else ALL_TEAMS_CLASSES.index(name))
         for i, name in enumerate(classes)}
    for ds, classes in RAW_CLASSES.items()
}

# Per-dataset remap into the all-classes index space (nothing dropped).
ALL_CLASSES_MAP = {
    ds: {i: ALL_CLASSES_CLASSES.index(name) for i, name in enumerate(classes)}
    for ds, classes in RAW_CLASSES.items()
}

# Per-dataset remap into PLAYER(0)/REF(1); None = drop the box (BALL, POST).
PLAYER_REF_MAP = {
    ds: {i: (None if name in ("BALL", "POST") else PLAYER_REF_CLASSES.index("REF" if name == "REF" else "PLAYER"))
         for i, name in enumerate(classes)}
    for ds, classes in RAW_CLASSES.items()
}


def load_pairs(ds: str) -> list[tuple[Path, list[str]]]:
    """Return [(image_path, label_lines)] for one raw dataset."""
    pairs = read_pairs(RAW / ds, len(RAW_CLASSES[ds]))
    if len(pairs) < EXPECTED_RAW_COUNTS[ds]:
        raise ValueError(f"Incomplete original dataset {ds}: {len(pairs)} pairs; "
                         f"expected at least {EXPECTED_RAW_COUNTS[ds]}. Restore the backup first.")
    return pairs


def remap(lines: list[str], mapping: dict[int, int | None]) -> list[str]:
    out = []
    for line in lines:
        parts = line.split()
        new = mapping[int(parts[0])]
        if new is not None:
            out.append(f"{new} " + " ".join(parts[1:]))
    return out


def write_split(name: str, class_names: list[str],
                pairs: list[tuple[Path, list[str], str]]) -> None:
    """pairs: [(image_path, remapped_label_lines, output_stem)]."""
    random.seed(SEED)
    random.shuffle(pairs)
    n_val = int(VAL_FRACTION * len(pairs))
    splits = {"val": pairs[:n_val], "train": pairs[n_val:]}

    out_dir = OUT / name
    if out_dir.exists():
        shutil.rmtree(out_dir)
    for split, group in splits.items():
        (out_dir / split / "images").mkdir(parents=True)
        (out_dir / split / "labels").mkdir(parents=True)
        for img, lines, stem in group:
            shutil.copy(img, out_dir / split / "images" / f"{stem}{img.suffix}")
            (out_dir / split / "labels" / f"{stem}.txt").write_text(
                "\n".join(lines) + "\n" if lines else "")

    with open(out_dir / "data.yaml", "w") as f:
        yaml.safe_dump(
            {"path": str(out_dir.resolve()),
             "train": "train/images", "val": "val/images",
             "names": dict(enumerate(class_names))}, f)

    n_boxes = sum(len(lines) for _, lines, _ in pairs)
    print(f"{name}: {len(splits['train'])} train / {len(splits['val'])} val, "
          f"{n_boxes} boxes, classes={class_names}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--broadcast-reviewed", nargs="+", type=Path,
                        help="reviewed/ folders to add to the original raw player/ref data")
    parser.add_argument("--name", default="player_ref_broadcast_clean")
    parser.add_argument("--val-gap-frames", type=int, default=300,
                        help="exclude training frames this close to the broadcast validation tail")
    args = parser.parse_args()
    # Check every source before write_split can replace any existing dataset.
    try:
        raw_pairs = {ds: load_pairs(ds) for ds in RAW_CLASSES}
        if args.broadcast_reviewed:
            build_broadcast(raw_pairs, args.broadcast_reviewed, args.name, args.val_gap_frames)
            return
    except (ValueError, OSError) as exc:
        raise SystemExit(f"Dataset build FAILED: {exc}") from exc
    variants = {
        "all_teams": (ALL_TEAMS_CLASSES, ALL_TEAMS_MAP),
        "all_classes": (ALL_CLASSES_CLASSES, ALL_CLASSES_MAP),
        "player_ref": (PLAYER_REF_CLASSES, PLAYER_REF_MAP),
    }
    for name, (class_names, mapping) in variants.items():
        pairs = []
        for ds in RAW_CLASSES:
            for img, lines in raw_pairs[ds]:
                pairs.append((img, remap(lines, mapping[ds]),
                              f"{ds}__{img.stem}"))
        write_split(name, class_names, pairs)


def build_broadcast(raw_pairs, reviewed_dirs, name, gap):
    """Build a fresh, traceable dataset; never read unreviewed detector proposals."""
    if Path(name).name != name or name in (".", "..") or gap < 0:
        raise ValueError("Use a simple output name and a nonnegative frame gap")
    destination = OUT / name
    if destination.exists():
        raise ValueError(f"{destination} already exists; choose a fresh --name")
    old = [(img, remap(lines, PLAYER_REF_MAP[ds]), f"{ds}__{img.stem}")
           for ds in RAW_CLASSES for img, lines in raw_pairs[ds]]
    random.Random(SEED).shuffle(old)
    n_val = int(VAL_FRACTION * len(old))
    splits = {"train": old[n_val:], "val": old[:n_val]}
    excluded = []
    seen = set()
    for folder in reviewed_dirs:
        folder = folder.resolve()
        if folder.name != "reviewed" or folder in seen:
            raise ValueError(f"Expected a unique reviewed/ directory: {folder}")
        seen.add(folder)
        approved = {int(s) for s in (folder.parent / "reviewed.txt").read_text().splitlines() if s.strip()}
        pairs = read_pairs(folder, 2)
        video = folder.parent.name
        frame_pairs = []
        for img, lines in pairs:
            prefix = f"{video}_frame_"
            if not img.stem.startswith(prefix):
                raise ValueError(f"Unexpected reviewed image name: {img}")
            frame = int(img.stem[len(prefix):])
            if frame not in approved:
                raise ValueError(f"Unreviewed/stale frame in reviewed export: {img}")
            frame_pairs.append((frame, img, lines))
        if {f for f, _, _ in frame_pairs} != approved:
            raise ValueError(f"{folder}: reviewed manifest and exported files differ; run --split again")
        frame_pairs.sort()
        if len(frame_pairs) < 10:
            raise ValueError(f"{folder}: review at least 10 frames before making a holdout")
        count = max(1, int(VAL_FRACTION * len(frame_pairs)))
        boundary = frame_pairs[-count][0]
        train_count = 0
        for frame, img, lines in frame_pairs:
            if boundary - gap <= frame < boundary:
                excluded.append(str(img))
                continue
            split = "val" if frame >= boundary else "train"
            splits[split].append((img, lines, img.stem))
            train_count += split == "train"
        if not train_count:
            raise ValueError(f"{folder}: no training frames remain outside the validation gap")
    # All source validation has succeeded; now write an independent dataset.
    provenance = {"seed": SEED, "val_gap_frames": gap, "excluded_for_gap": excluded, "splits": {}}
    for split, pairs in splits.items():
        stems = [stem for _, _, stem in pairs]
        if len(stems) != len(set(stems)):
            raise ValueError(f"Duplicate output names in {split}")
        (destination / split / "images").mkdir(parents=True)
        (destination / split / "labels").mkdir()
        provenance["splits"][split] = []
        for img, lines, stem in pairs:
            shutil.copy2(img, destination / split / "images" / f"{stem}{img.suffix}")
            (destination / split / "labels" / f"{stem}.txt").write_text("\n".join(lines) + ("\n" if lines else ""))
            provenance["splits"][split].append({"source_image": str(img.resolve()), "stem": stem})
    data = {"path": str(destination.resolve()), "train": "train/images", "val": "val/images",
            "names": dict(enumerate(PLAYER_REF_CLASSES))}
    (destination / "data.yaml").write_text(yaml.safe_dump(data))
    (destination / "provenance.json").write_text(json.dumps(provenance, indent=2))
    print(f"{destination}: {len(splits['train'])} train / {len(splits['val'])} val; "
          f"{len(excluded)} frames excluded for temporal separation")


if __name__ == "__main__":
    main()
