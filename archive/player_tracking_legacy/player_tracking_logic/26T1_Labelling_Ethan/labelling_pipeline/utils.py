"""Shared helper functions for the labelling pipeline."""

from pathlib import Path
from typing import Iterable, List


def ensure_project_dirs(config) -> None:
    """Create all required project folders if they do not already exist."""
    for path in [
        config.DATA_DIR,
        config.VIDEO_DIR,
        config.FRAME_DIR,
        config.LABEL_DIR,
        config.MODEL_DIR,
    ]:
        Path(path).mkdir(parents=True, exist_ok=True)


def list_image_files(image_dir: Path, valid_exts: Iterable[str]) -> List[Path]:
    """Return sorted image files from a folder."""
    valid_exts = tuple(ext.lower() for ext in valid_exts)
    image_dir = Path(image_dir)
    if not image_dir.exists():
        return []
    return sorted([p for p in image_dir.iterdir() if p.suffix.lower() in valid_exts])


def print_project_summary(config) -> None:
    """Print the active configuration summary before running the selected operation."""
    print("=" * 70)
    print("26T1 Labelling Ethan Pipeline")
    print("=" * 70)
    print(f"Operation mode: {config.OPERATION_MODE}")
    print(f"Project root:   {config.PROJECT_ROOT}")
    print(f"Video path:     {config.VIDEO_PATH}")
    print(f"Frame dir:      {config.FRAME_DIR}")
    print(f"Label dir:      {config.LABEL_DIR}")
    print(f"Target FPS:     {config.TARGET_FPS}")
    print("=" * 70)
