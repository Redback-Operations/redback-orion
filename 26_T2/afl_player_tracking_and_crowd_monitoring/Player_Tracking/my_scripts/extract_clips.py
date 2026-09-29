"""
Extracts stable, single-camera-angle clips from broadcast footage
for tracking instability testing.
"""

import subprocess

VIDEO = "data/videos/broadcast_essendon_hawthorn.mp4"

CLIPS = [
    ("00:20:37", "00:21:21", "clip1.mp4"),
    ("00:46:36", "00:47:28", "clip2.mp4"),
    ("01:28:20", "01:29:24", "clip3.mp4"),
    ("01:56:57", "01:57:34", "clip4.mp4"),
]

for start, end, name in CLIPS:
    subprocess.run([
        "ffmpeg", "-i", VIDEO,
        "-ss", start, "-to", end,
        "-c", "copy", name
    ])
    print(f"Created {name}")
