"""Tracking results for an uploaded video, reused by file hash.

/tracking stores its result here. Any endpoint that needs tracks calls
get_tracks() with the same video: if tracking already ran on that file the
saved result is reused, otherwise tracking runs first. Calling an endpoint
on its own is slower but never fails for lack of tracks.
"""

import hashlib
import json
from pathlib import Path
from typing import Callable


def file_hash(path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tracks_csv_path(tracks_dir: Path, key: str) -> Path:
    return Path(tracks_dir) / f"{key}.csv"


def get_tracks(video_path, tracks_dir: Path, run_tracking: Callable[[Path, Path, str], dict],
               key: str = None) -> dict:
    """Return the tracking result for this video, running tracking if needed.

    run_tracking(video_path, tracks_dir, key) must write <key>.csv into
    tracks_dir and return a JSON-serialisable result. A result counts as
    saved only when both <key>.json and <key>.csv exist. Pass key if the
    caller already hashed the file.
    """
    key = key or file_hash(video_path)
    saved = Path(tracks_dir) / f"{key}.json"
    if saved.exists() and tracks_csv_path(tracks_dir, key).exists():
        return json.loads(saved.read_text())

    # ponytail: two requests for the same new video at the same moment both run
    # tracking. The result is identical, just wasted work. Add a lock per key
    # if that becomes common.
    result = run_tracking(Path(video_path), Path(tracks_dir), key)
    part = saved.with_name(saved.name + ".part")
    part.write_text(json.dumps(result))
    part.replace(saved)  # never leave a half-written result for the next request
    return result
