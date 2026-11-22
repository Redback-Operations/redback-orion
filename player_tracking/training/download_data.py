#!/usr/bin/env python3
"""Download the shared datasets and match videos from Google Drive.

Pulls folders from the team Drive folder "afl_player_tracking"
(https://drive.google.com/drive/u/0/folders/1Pioq0m2zHVQiwKFOBVWZUQ6PtYcP01Ui)
into player_tracking/, mirroring the local layout. Model weights come from
the GitHub release instead: python training/download_models.py

Usage (from player_tracking/):
    python training/download_data.py              # data and datasets
    python training/download_data.py data         # only data/ (raw datasets + videos)
    python training/download_data.py datasets     # only the built train/val splits

Files already downloaded are skipped, so a failed run can simply be repeated.
Requires the Drive folder to be shared as "anyone with the link can view".
"""

import sys
from pathlib import Path

import gdown

DRIVE_FOLDER = "https://drive.google.com/drive/u/0/folders/1Pioq0m2zHVQiwKFOBVWZUQ6PtYcP01Ui"
SUBFOLDERS = {
    "data": "1SQOLSeu1PAxjxPXu6CzjRK-CCLCEoM2R",
    "datasets": "1rZcBWUohFglw3szlbwu_HHUH0uajYlA-",
}

OUTPUT_ROOT = Path(__file__).resolve().parent.parent


def explain(name: str, error: Exception) -> str:
    """Turn a gdown failure into a message that says what to do next."""
    text = str(error)
    lower = text.lower()
    first_line = text.strip().splitlines()[0] if text.strip() else type(error).__name__
    if "too many users" in lower or "quota" in lower:
        cause = ("Google Drive has temporarily blocked this file because it was "
                 "downloaded too many times recently. The block usually clears "
                 "within 24 hours.\n"
                 "Run this again tomorrow (finished files are kept), or download "
                 f"the file in a browser from {DRIVE_FOLDER}")
    elif "permission" in lower or "access" in lower or "cannot retrieve the folder" in lower:
        cause = ("The Drive folder is not shared with 'anyone with the link'. Ask the "
                 "Player Tracking lead to check the folder's sharing settings.")
    else:
        cause = ("Check your internet connection and run this again (finished files "
                 f"are kept). If it keeps failing, download from {DRIVE_FOLDER}")
    return f"Downloading '{name}' from Google Drive failed: {first_line}\n{cause}"


def main() -> None:
    targets = sys.argv[1:] or list(SUBFOLDERS)
    if "models" in targets:
        sys.exit("Model weights are on GitHub now. Run: python training/download_models.py")
    unknown = [t for t in targets if t not in SUBFOLDERS]
    if unknown:
        sys.exit(f"Unknown folder(s): {unknown}. Choose from {list(SUBFOLDERS)}")
    if int(gdown.__version__.split(".")[0]) < 5:
        sys.exit(f"gdown {gdown.__version__} can't download from Google Drive any more. "
                 "Upgrade it: pip install -U 'gdown>=5'")

    for name in targets:
        url = f"https://drive.google.com/drive/folders/{SUBFOLDERS[name]}"
        out = OUTPUT_ROOT / name
        print(f"Downloading '{name}' -> {out}")
        try:
            files = gdown.download_folder(url=url, output=str(out), quiet=False, resume=True)
        except Exception as e:  # gdown raises several error types; all mean the same to the user
            sys.exit("\n" + explain(name, e) + "\n")
        if files is None:
            sys.exit("\n" + explain(name, RuntimeError("gdown returned no files")) + "\n")

    print("Done.")


if __name__ == "__main__":
    main()
