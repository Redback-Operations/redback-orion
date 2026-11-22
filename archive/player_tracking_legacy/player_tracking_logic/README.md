# Archived T1 player tracking code

Parts of `player_tracking/player_tracking_logic/` that nothing runs and that newer code replaces. Moved here in T3 2026 after the audit in `player_tracking/docs/inventory.md`.

| Item | Why it was archived |
|---|---|
| `matthew_player_tracking/`, `yolo_player_tracker.py` | Two identical copies of one tracker. The newer version is `player_tracking/experiments/player_tracker.py`. |
| `player_tracking_Matthew/` | README only |
| `Yolov11_retain/` | Older copy of the labelling flow in `26T1_Labelling_Ethan/`; `player_tracking/training/smart_labeller.py` replaces both |
| `colour_speed_detection_drew/` | Near-copy of `early_afl_work/Player_Tracking_BoTSORT/run_video_drew.py` |
| `Re-Identification/ReID/`, `Re-Identification/PlayerTracking/` | Experimental re-ID and tracker test harness, not connected to anything. `ReID` needs `torchreid`, which no requirements file installs. |
| `26T1-Modelling-Sri/temp*.py` | One-line scratch files |
| `CSV Converter.py`, `BoundingBoxes`, `sprint_detection.py` | Google Colab exports that only run inside Colab |
