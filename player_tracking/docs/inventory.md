# Player tracking code inventory

What the T1 and T2 player tracking code did, whether it ran, and where it went. Written in T3 2026 as the input to `target_pipeline.md`; updated after PR #161 merged both into `analysis_pipeline/`.

**Checks run on all 101 Python files at the audit (November 2026):** every file parses, and all 41 existing tests pass (Tracking_Ethan 5, 26T1_Labelling_Ethan 5, T2 pipeline 17, player_service 1, Studio 13). Only `CSV Converter.py` and `tackle_detection_shafqat_ullah/validation/apaar_validator.py` contain Colab or machine-specific paths.

## T1: what was `player_tracking_logic/`

The folder no longer exists. The code still in use moved into `analysis_pipeline/` with history, and everything else is in `archive/player_tracking_legacy/player_tracking_logic/`, whose README says why each item was archived.

| T1 folder | What it does | Status at audit | Now |
|---|---|---|---|
| `Tracking_Ethan/` | Modular tracker with appearance features, jersey clustering, homography calibration and movement metrics | Live in `/path_trajectory`, ran its own YOLO pass. Tests pass. | `analysis_pipeline/movement_metrics/`, reading the saved tracks. Its own matcher and YOLO parsing were removed (ByteTrack gave 28 tracks where it gave 55 on the same clip). |
| `Re-Identification/JerseyColorDetection/` | HSV + KMeans team clustering | Live in `/jersey_color` | `analysis_pipeline/identify_players/` |
| `Re-Identification/Formation_Visualization/` | Team shape and connectivity overlay | Live in `/formation` | `analysis_pipeline/formation_analysis/` |
| `tackle_detection_shafqat_ullah/` | Tackle events from player clustering, plus a validator | Logic copied inline into `/tackle`; folder not imported | The inline logic is `analysis_pipeline/tackle_detection.py` (tested). The original module and validator are archived. |
| `player_tracking_logic_heatmaps_workload/` | Heatmaps and workload (sprints, high-intensity segments) | Not connected | `analysis_pipeline/workload_heatmaps/`, run by `run_pipeline.py` |
| `26T1_Speed_Detection_Drew/` | Speed, acceleration and distance | Not connected | Archived. Acceleration not yet carried over. |
| `Re-Identification/JerseyOCR/` | EasyOCR jumper numbers with voting across frames | Not connected | Archived; the Studio has the newer OCR |
| `Yolov11_ByteTrack_Player_Tracking/` | YOLO + ByteTrack tracker with the T1 CAR/GCS/REF model | Live in `/tracking` | Archived; `analysis_pipeline/detect_and_track.py` replaced it |
| `26T1-Modelling-Sri/`, `Notebooks/` | Training notebooks for the T1 models | Reference | Archived |
| `26T1_Labelling_Ethan/` | Frame extraction, pre-labelling, annotator | Works (5 tests pass) | Archived; `training/smart_labeller.py` covers it |
| Event tools (`annotation_*.py`, `merge_synced.py`, `prediction_vs_truth.py`, `event_timing_analysis.py`) | Sync hand-labelled events with tracking data | Not connected | Archived |
| Duplicates, scratch files, Colab exports, re-ID experiments | see the duplicates section below | Not used | Archived |

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
| Studio | `orion_player_tracking_studio/` | Tracking, review events, team suggestion, multi-frame EasyOCR, identity merging of fragmented tracks, export | Newest feature set. Logic is separable from the tkinter GUI. |

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
