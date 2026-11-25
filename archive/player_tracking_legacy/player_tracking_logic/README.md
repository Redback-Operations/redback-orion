# Archived T1 player tracking code

Everything from `player_tracking/player_tracking_logic/` that isn't part of the pipeline. The code that is still used moved to `player_tracking/analysis_pipeline/` (Tracking_Ethan → `movement_metrics/`, JerseyColorDetection → `identify_players/`, Formation_Visualization → `formation_analysis/`, heatmaps and workload → `workload_heatmaps/`, the tackle logic → `tackle_detection.py`). Archived in T3 2026 after the audit in `player_tracking/docs/inventory.md`. `README_t1_pipeline.md` is the T1 team's own overview.

| Item | Why it was archived |
|---|---|
| `matthew_player_tracking/`, `yolo_player_tracker.py` | Two identical copies of one tracker. The newer version is `player_tracking/experiments/player_tracker.py`. |
| `player_tracking_Matthew/` | README only |
| `Yolov11_retain/` | Older copy of the labelling flow in `26T1_Labelling_Ethan/`; `player_tracking/training/smart_labeller.py` replaces both |
| `colour_speed_detection_drew/` | Near-copy of `early_afl_work/Player_Tracking_BoTSORT/run_video_drew.py` |
| `Re-Identification/ReID/`, `Re-Identification/PlayerTracking/` | Experimental re-ID and tracker test harness, not connected to anything. `ReID` needs `torchreid`, which no requirements file installs. |
| `26T1-Modelling-Sri/temp*.py` | One-line scratch files |
| `CSV Converter.py`, `BoundingBoxes`, `sprint_detection.py` | Google Colab exports that only run inside Colab |
| `Yolov11_ByteTrack_Player_Tracking/` | The T1 tracker `/tracking` ran before `analysis_pipeline/detect_and_track.py` replaced it, with the CAR/GCS/REF model |
| `26T1-Modelling-Sri/`, `Notebooks/` | Training notebooks for the T1 per-match models; `player_tracking/training/` replaces them |
| `26T1_Labelling_Ethan/` | Frame extraction and labelling; `player_tracking/training/smart_labeller.py` covers the same work |
| `26T1_Speed_Detection_Drew/` | Speed and acceleration CLI. `analysis_pipeline/movement_metrics/` and `workload_heatmaps/` produce speed and distance; per-player acceleration from this script hasn't been carried over yet. |
| `tackle_detection_shafqat_ullah/` | The original tackle module, documentation and Apaar's validator. The logic the service runs is `analysis_pipeline/tackle_detection.py`. |
| `Re-Identification/JerseyOCR/`, `Re-Identification/best.pt` | Jumper OCR (the Studio has a newer version) and a copy of the T1 model |
| Event tools: `annotation_converter.py`, `annotation_sync.py`, `merge_synced.py`, `prediction_vs_truth.py`, `event_timing_analysis.py` | Sync hand-labelled kick, mark and tackle events with tracking data. Not connected to anything. |
| `Tracking_Ethan/main.py`, `Tracking_Ethan/outputs/`, sample outputs in `Re-Identification/` | Old entry point and outputs from T1 runs |
| `Dockerfile`, `README_old.md`, `notebook_v1.ipynb`, `pred_V1.jpg` | Leftovers from the T1 folder |
