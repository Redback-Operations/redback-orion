#!/usr/bin/env python3
"""Download the shared dataset backup from Google Drive.

Pulls folders from the team Drive folder "afl_player_tracking"
(https://drive.google.com/drive/u/0/folders/1Pioq0m2zHVQiwKFOBVWZUQ6PtYcP01Ui)
into the Player_Tracking directory, mirroring the local layout.

Usage:
    pip install gdown
    python scripts/download_data.py              # downloads everything
    python scripts/download_data.py data         # only the data/ folder
    python scripts/download_data.py data models  # multiple folders

Requires the Drive folder to be shared as "anyone with the link can view".
"""

import sys
from pathlib import Path

import gdown

SUBFOLDERS = {
    "data": "1SQOLSeu1PAxjxPXu6CzjRK-CCLCEoM2R",
    "datasets": "1rZcBWUohFglw3szlbwu_HHUH0uajYlA-",
    "models": "17ey3VrJ9arxfzVZ1a2G62p7dHFKUlpCE",
}

OUTPUT_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    targets = sys.argv[1:] or list(SUBFOLDERS)
    unknown = [t for t in targets if t not in SUBFOLDERS]
    if unknown:
        sys.exit(f"Unknown folder(s): {unknown}. Choose from {list(SUBFOLDERS)}")

    for name in targets:
        url = f"https://drive.google.com/drive/folders/{SUBFOLDERS[name]}"
        out = OUTPUT_ROOT / name
        print(f"Downloading '{name}' -> {out}")
        gdown.download_folder(url=url, output=str(out), quiet=False)

    print("Done.")


if __name__ == "__main__":
    main()
