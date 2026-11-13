# YOLOv8 + ByteTrack — AFL Baseline Tracker

This folder contains a reproducible **baseline tracker** for AFL Vision Insight using YOLOv8 with ByteTrack.

## Features
- MOT-format CSV export (TrackEval compatible)
- Per-frame JSON output
- Deterministic ID colors for overlay visualization
- ROI crop support (ignore overlays)
- Runtime/FPS logging + summary statistics

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

