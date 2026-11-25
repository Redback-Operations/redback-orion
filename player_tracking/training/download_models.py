#!/usr/bin/env python3
"""Download the player tracking model weights into player_tracking/models/.

Weights are attached to a GitHub release of the repo, not stored in git:
https://github.com/Redback-Operations/redback-orion/releases/tag/models-v1

Each file is checked against a SHA-256 checksum before it is kept, because
.pt files are loaded with pickle and could run code if tampered with.

Usage (from player_tracking/):
    python training/download_models.py                     # all models
    python training/download_models.py player_ref_best.pt  # just one

Set ORION_MODELS_URL to download from a mirror instead of GitHub.
Only the Python standard library is needed.
"""

import hashlib
import os
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

RELEASES_PAGE = "https://github.com/Redback-Operations/redback-orion/releases"
RELEASE_URL = os.environ.get("ORION_MODELS_URL", f"{RELEASES_PAGE}/download/models-v1")

# File name -> SHA-256. Update both together when a new release is made.
MODELS = {
    "player_ref_best.pt": "627afeadbac707f11efb359b4bdb0da090f96a5dc2b355fca0c49e94b1b12a9f",
    "all_teams_best.pt": "34e87d6c645d30df872515e603a3cafa946504f6adb9c18e3536c8f1f79eac1f",
    "all_classes_best.pt": "b31cc495240865cc0fdf23cc4c2e6c40ea08ab31be33fdb16893ac1c7eafa956",
}

MODELS_DIR = Path(__file__).resolve().parents[1] / "models"


class DownloadError(Exception):
    """A model could not be downloaded or failed its checksum."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(name: str, models_dir: Path = MODELS_DIR) -> Path:
    """Download one model if it isn't already present. Returns its path."""
    if name not in MODELS:
        raise DownloadError(f"Unknown model {name!r}. Choose from: {list(MODELS)}")
    models_dir.mkdir(parents=True, exist_ok=True)
    dest = models_dir / name
    if dest.exists() and sha256(dest) == MODELS[name]:
        print(f"{name}: already downloaded")
        return dest

    url = f"{RELEASE_URL}/{name}"
    part = dest.with_name(dest.name + ".part")
    print(f"{name}: downloading from {url}")
    try:
        with urllib.request.urlopen(url, timeout=60) as response, open(part, "wb") as f:
            shutil.copyfileobj(response, f)
    except urllib.error.HTTPError as e:
        part.unlink(missing_ok=True)
        if e.code == 404:
            raise DownloadError(
                f"{url} was not found (HTTP 404).\n"
                f"The release tag or file name may have changed. "
                f"Check the current release at {RELEASES_PAGE}") from e
        raise DownloadError(
            f"GitHub returned HTTP {e.code} for {url}. Try again in a few minutes.") from e
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        part.unlink(missing_ok=True)
        reason = getattr(e, "reason", e)
        raise DownloadError(
            f"Could not reach {RELEASE_URL} ({reason}).\n"
            "Check your internet connection, VPN or proxy, then try again.") from e

    actual = sha256(part)
    if actual != MODELS[name]:
        part.unlink()
        raise DownloadError(
            f"{name} downloaded, but its checksum doesn't match.\n"
            f"  expected {MODELS[name]}\n  got      {actual}\n"
            "The file may be corrupted or replaced. It has been deleted; "
            "tell the Player Tracking lead.")
    part.replace(dest)
    print(f"{name}: OK")
    return dest


def main() -> None:
    names = sys.argv[1:] or list(MODELS)
    try:
        for name in names:
            download(name)
    except DownloadError as e:
        sys.exit(f"\nModel download failed.\n{e}\n")
    print(f"Models are in {MODELS_DIR}")


if __name__ == "__main__":
    main()
