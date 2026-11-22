# Player tracking code inventory

What the T1 and T2 player tracking code does, whether it runs, and where it's going. Written in T3 2026 as the input to `target_pipeline.md`.

**Checks run on all 101 Python files (November 2026):** every file parses, and all 41 existing tests pass (Tracking_Ethan 5, 26T1_Labelling_Ethan 5, T2 pipeline 17, player_service 1, Studio 13). Only `CSV Converter.py` and `tackle_detection_shafqat_ullah/validation/apaar_validator.py` contain Colab or machine-specific paths.

## T1: `player_tracking_logic/`

### Still in use or still to be moved

| Folder | What it does | In → Out | Model | Status | Goes to |
|---|---|---|---|---|---|
| `Tracking_Ethan/` | Modular tracker with appearance features, jersey clustering, homography calibration and movement metrics | video → JSON, metrics CSV, video | `player_ref_best.pt` (via player_service) | Live in `/path_trajectory`. Best-structured T1 code, with tests. | `field_calibration.py`, `movement_metrics.py` |
| `Re-Identification/JerseyColorDetection/` | HSV + KMeans team clustering | video + tracking JSON → team-labelled JSON | none | Live in `/jersey_color` | `identify_players.py`, if it wins the team test |
| `Re-Identification/Formation_Visualization/` | Team shape and connectivity overlay | video + clustered JSON → video | none | Live in `/formation` | `formation_analysis.py` |
| `Re-Identification/JerseyOCR/` | EasyOCR jumper numbers with voting across frames | crops → numbers | none | Not connected. Close to the Studio's OCR. | Compare with the Studio, keep one |
| `tackle_detection_shafqat_ullah/` | Tackle events from player clustering, plus a validator | tracking CSV → events JSON | none | Logic is copied inline into `/tackle`; the folder isn't imported | `tackle_detection.py` (imported, not copied) |
| `26T1_Speed_Detection_Drew/` | Speed, acceleration and distance, added to the backend's JSON shape | tracking JSON + video → JSON, CSV, video | none | Not connected | Output fields go into `movement_metrics.py` |
| `player_tracking_logic_heatmaps_workload/` | Heatmaps and workload (sprints, high-intensity segments) | tracking CSV → PNG, JSON | none | Not connected | `workload_heatmaps.py` |
| `Yolov11_ByteTrack_Player_Tracking/` | YOLO + ByteTrack tracker, plus older DeepSORT and OCR variants | video → tracking JSON | T1 CAR/GCS/REF `best.pt` | No longer used: `/tracking` runs `analysis_pipeline/` | Archive |
| `26T1-Modelling-Sri/` | Training notebooks for the three per-match T1 models | dataset → `.pt` | produces CAR_vs_GCS, SS_vs_WB, CAT_vs_HAW | Reference | Archive |
| `26T1_Labelling_Ethan/` | Frame extraction, YOLO pre-labelling, OpenCV annotator | video → YOLO labels | COCO YOLO | Works (5 tests pass) | Archive once `training/smart_labeller.py` covers its use |
| `Notebooks/` | Unified-model training (Nithin), heatmap and distance notebook | n/a | n/a | Reference | Archive |
| Event tools: `annotation_converter.py`, `annotation_sync.py`, `merge_synced.py`, `prediction_vs_truth.py`, `event_timing_analysis.py` | Sync hand-labelled kick, mark and tackle events with tracking data | CSV → CSV, report | none | Not connected | `evaluation/` if event labelling continues, otherwise archive |

### Archived in T3 2026

Moved to `archive/player_tracking_legacy/player_tracking_logic/` (its README says why): `matthew_player_tracking/`, `yolo_player_tracker.py` (identical copies), `player_tracking_Matthew/` (README only), `Yolov11_retain/`, `colour_speed_detection_drew/`, `Re-Identification/ReID/`, `Re-Identification/PlayerTracking/`, `26T1-Modelling-Sri/temp*.py`, `CSV Converter.py`, `BoundingBoxes`, `sprint_detection.py`.

## T2: what was `pipeline/`, and the Studio

| Area | Now in | What it does | Status |
|---|---|---|---|
| Tracking | `analysis_pipeline/detect_and_track.py`, `analysis_pipeline/configs/` | YOLO + ByteTrack → H.264 video + tracks CSV (`frame, track_id, class, confidence, x1..y2`). Supports resume and an ID offset. | Live in `/tracking` |
| Models | `training/train.py`, `build_datasets.py`, `dataset_integrity.py` | Builds datasets from the T1 labelled data and trains models | Produced the three models on the `models-v1` release |
| Data | `training/download_models.py`, `training/download_data.py` | Weights from the GitHub release; datasets and videos from Drive | Works |
| Labelling | `training/smart_labeller.py`, `audit_labels.py`, `render_labels.py`, `extract_player_crops.py` | Broadcast labeller with review state and holdout split | Most mature labelling tool |
| Tracking QA | `evaluation/analyze_tracking.py`, `analyze_camera_motion.py`, `create_tracker_evidence_sheet.py`, `analyse_player_metrics.py`, `extract_clips.py` | Review queue (short tracks, count jumps), camera-motion check, evidence sheets | Works, with tests |
| Ball | `experiments/ball_tracking/` | Ball-only detector and temporal tracker | Experimental |
| Forward-50 | `experiments/forward50_analysis/` | Zone calibration and positions in the forward-50 area. Has its own tracker. | Works, with tests |
| Jumper numbers | `experiments/jumper_numbers/` | CNN trained on a Kaggle **NFL** jersey dataset, plus OCR tests | Experimental, not connected |
| Starter tracker | `experiments/player_tracker.py`, `track_videos.py`, `yolo_merged_best.pt` | Newer copy of Matthew's T1 tracker (with an ID-stability fix), batch runner | Superseded by `analysis_pipeline/` |
| Studio | `Orion_Player_Tracking_Studio/` | Tracking, review events, team suggestion, multi-frame EasyOCR, identity merging of fragmented tracks, export | Newest feature set. Logic is separable from the tkinter GUI. |

## Where T1 and T2 overlap

| Capability | T1 | T2 | Keep |
|---|---|---|---|
| Detection model | `best.pt`: CAR/GCS/REF, one match | `player_ref_best.pt`: PLAYER/REF, all matches | **T2** (done) |
| Tracking | 4 trackers: `track.py`, Tracking_Ethan, Matthew's, Drew's | `detect_and_track.py`, Studio, Forward-50 | **T2** (done). Compare Tracking_Ethan's tracker before archiving it. |
| Output format | JSON (`frame_number`, `players[]`) | CSV (`frame, track_id, …`) | **T2 CSV**. The service still converts it to the old JSON for the backend. |
| Team classification | JerseyColorDetection, Matthew's and Drew's KMeans, Ethan's jersey clustering | Studio `suggest_teams` | Decide by testing on the same clips |
| Jumper numbers | `JerseyOCR` | Studio OCR, NFL CNN | Studio |
| Identity across gaps | `ReID` (archived) | Studio identity merging | Studio |
| Speed, distance, acceleration | Tracking_Ethan (homography, tested), Drew (backend fields) | `experiments/player_tracker.py` (pixel ratio) | **T1** Tracking_Ethan, with Drew's output fields |
| Heatmaps and workload | `heatmaps_workload` | none | T1 |
| Tackles | `tackle_detection` | none | T1 |
| Formation | `Formation_Visualization` | none | T1 |
| Forward-50 | none | `forward50_analysis` | T2 |
| Labelling | two overlapping labellers | `smart_labeller.py` | T2 |
| Tracking QA | none | `analyze_tracking.py` and the Studio review page | T2 |

## Duplicates found

- Identical: `yolo_player_tracker.py` ×2 (archived), `best.pt` ×3 (`Yolov11_ByteTrack…/final_code/`, `Re-Identification/`, `26T1-Modelling-Sri/1/best(CAR_vs_GCS).pt`), `temp*.py` ×4 (archived)
- Near-identical: `base_pipeline.py` (in `Yolov11_ByteTrack_Player_Tracking/` and the archived `colour_speed_detection_drew/` and `early_afl_work/`), Drew's colour scripts (8 lines differ), `experiments/player_tracker.py` vs the archived `yolo_player_tracker.py` (18 lines differ; the experiments copy is newer)
