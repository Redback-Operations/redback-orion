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
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "datasets"
SEED = 42
VAL_FRACTION = 0.2

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
    pairs = []
    for lbl in sorted((RAW / ds / "labels").glob("*.txt")):
        matches = [p for p in (RAW / ds / "images").glob(lbl.stem + ".*")
                   if p.suffix.lower() in (".jpg", ".jpeg", ".png")]
        if not matches:
            print(f"  WARNING: no image for {lbl}, skipped")
            continue
        pairs.append((matches[0], lbl.read_text().splitlines()))
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
    variants = {
        "all_teams": (ALL_TEAMS_CLASSES, ALL_TEAMS_MAP),
        "all_classes": (ALL_CLASSES_CLASSES, ALL_CLASSES_MAP),
        "player_ref": (PLAYER_REF_CLASSES, PLAYER_REF_MAP),
    }
    for name, (class_names, mapping) in variants.items():
        pairs = []
        for ds in RAW_CLASSES:
            for img, lines in load_pairs(ds):
                pairs.append((img, remap(lines, mapping[ds]),
                              f"{ds}__{img.stem}"))
        write_split(name, class_names, pairs)


if __name__ == "__main__":
    main()
