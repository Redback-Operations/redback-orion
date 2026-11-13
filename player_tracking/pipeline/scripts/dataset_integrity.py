"""Strict YOLO dataset checks: missing annotations are not negative examples."""

import hashlib
import math
from pathlib import Path

import yaml

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def read_pairs(directory: Path, nc: int) -> list[tuple[Path, list[str]]]:
    images_dir, labels_dir = directory / "images", directory / "labels"
    images = sorted(p for p in images_dir.glob("*") if p.suffix.lower() in IMAGE_SUFFIXES)
    if not images:
        raise ValueError(f"No images in {images_dir}; restore the dataset first")
    stems = [p.stem for p in images]
    stem_set = set(stems)
    if len(stems) != len(stem_set):
        raise ValueError(f"Duplicate image stems in {images_dir}")
    missing = [p for p in images if not (labels_dir / f"{p.stem}.txt").is_file()]
    orphans = [p for p in labels_dir.glob("*.txt") if p.stem not in stem_set]
    if missing or orphans:
        raise ValueError(
            f"{directory}: {len(images)} images, {len(missing)} missing label files, "
            f"{len(orphans)} labels without images. Restore missing files; never "
            "replace missing annotations with empty labels. Intentional backgrounds "
            "must have an explicit empty .txt file."
        )
    pairs = []
    for image in images:
        label = labels_dir / f"{image.stem}.txt"
        lines = [line.strip() for line in label.read_text().splitlines() if line.strip()]
        for n, line in enumerate(lines, 1):
            try:
                cls, x, y, w, h = map(float, line.split())
                valid = (all(math.isfinite(v) for v in (cls, x, y, w, h))
                         and cls.is_integer() and 0 <= cls < nc
                         and 0 <= x <= 1 and 0 <= y <= 1
                         and 0 < w <= 1 and 0 < h <= 1)
            except ValueError:
                valid = False
            if not valid:
                raise ValueError(f"Invalid YOLO annotation at {label}:{n}: {line}")
        pairs.append((image, lines))
    return pairs


def audit_yaml(path: Path) -> dict:
    """Validate directory-based train/val splits and snapshot their content hashes."""
    path = path.resolve()
    data = yaml.safe_load(path.read_text())
    root = Path(data.get("path", path.parent))
    if not root.is_absolute():
        root = path.parent / root
    names = data["names"]
    if isinstance(names, dict) and set(names) != set(range(len(names))):
        raise ValueError("Class IDs must be consecutive integers starting at 0")
    snapshot = {"data_yaml": str(path), "names": names, "splits": {}}
    hashes = {}
    for split in ("train", "val"):
        values = data[split] if isinstance(data[split], list) else [data[split]]
        entries = []
        seen_paths = set()
        for value in values:
            directory = Path(value)
            if not directory.is_absolute():
                directory = root / directory
            directory = directory.resolve()
            if directory.name != "images" or not directory.is_dir():
                raise ValueError(f"{split}: expected an existing images/ directory: {directory}")
            for image, lines in read_pairs(directory.parent, len(names)):
                if str(image) in seen_paths:
                    raise ValueError(f"Duplicate {split} image: {image}")
                seen_paths.add(str(image))
                label = directory.parent / "labels" / f"{image.stem}.txt"
                entries.append({"image": str(image), "label": str(label), "boxes": len(lines),
                                "image_sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                                "label_sha256": hashlib.sha256(label.read_bytes()).hexdigest()})
        if not entries:
            raise ValueError(f"Empty {split} split")
        snapshot["splits"][split] = entries
        hashes[split] = {e["image_sha256"] for e in entries}
    overlap = hashes["train"] & hashes["val"]
    if overlap:
        raise ValueError(f"Train/validation leakage: {len(overlap)} identical images in both splits")
    return snapshot
