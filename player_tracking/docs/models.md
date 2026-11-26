# Player Tracking Model Register

**Owner:** Hassan
**Project:** Orion Player Tracking
**Purpose:** Record the available detection models, their training datasets, validation results, usage and storage locations.

## 1. Model Overview

The project has three officially released detection models and one older experimental model.

The official model weights are attached to the GitHub `models-v1` release rather than stored directly in the repository. They can be downloaded using `training/download_models.py`.

| Model | Classes | Main purpose |
|---|---|---|
| `player_ref_best.pt` | PLAYER, REF | Default model for detecting players and referees |
| `all_teams_best.pt` | CAR, GCS, HAW, CAT, REF, SS, WB | Detecting specific AFL teams and referees |
| `all_classes_best.pt` | Seven teams, REF, BALL, POST | Experimental detection of teams, ball and goal posts |
| `yolo_merged_best.pt` | Not documented | Older experimental model used by the legacy tracker |

## 2. Training Information

The three official models were trained using the following settings:

- Base model: YOLO11s pretrained
- Training duration: Up to 50 epochs
- Image size: 640
- Batch size: 16
- Early stopping patience: 10
- Random seed: 42
- Training hardware: NVIDIA RTX 3080
- Training script: `training/train.py`

The datasets were created using `training/build_datasets.py`. They use an 80/20 training and validation split, shuffled with seed 42.

| Dataset | Training images | Validation images | Total boxes | Classes |
|---|---:|---:|---:|---:|
| `player_ref` | 456 | 114 | 5,254 | 2 |
| `all_teams` | 456 | 114 | 5,254 | 7 |
| `all_classes` | 456 | 114 | 5,397 | 9 |

## 3. Official Model Details

### 3.1 player_ref_best.pt

**Purpose:** Default model for detecting players and referees across different AFL matches.

- Classes: PLAYER, REF
- Dataset: `player_ref`
- Training: 39 epochs (best epoch: 29)
- Validation images: 114
- Validation boxes: 1,068
- Storage: Attached to the GitHub `models-v1` release. Downloaded weights are stored locally in the git-ignored `models/` directory.

| Metric | Overall |
|---|---:|
| Precision | 0.828 |
| Recall | 0.801 |
| mAP@50 | 0.829 |
| mAP@50-95 | 0.354 |

This is the strongest and simplest official model when team identity is not required. It detects players and referees, while team identification can be handled later using jumper colours.

### 3.2 all_teams_best.pt

**Purpose:** Detecting specific AFL teams and referees.

- Classes: CAR, GCS, HAW, CAT, REF, SS, WB
- Dataset: `all_teams`
- Training: 44 epochs (best epoch: 34)
- Validation images: 114
- Validation boxes: 1,068
- Storage: Attached to the GitHub `models-v1` release. Downloaded weights are stored locally in the git-ignored `models/` directory.

| Metric | Precision | Recall | mAP@50 | mAP@50-95 |
|---|---:|---:|---:|---:|
| Overall | 0.807 | 0.807 | 0.817 | 0.346 |
| CAR | 0.919 | 0.923 | 0.942 | 0.462 |
| GCS | 0.899 | 0.939 | 0.954 | 0.465 |
| HAW | 0.826 | 0.879 | 0.898 | 0.376 |
| CAT | 0.856 | 0.870 | 0.913 | 0.409 |
| REF | 0.790 | 0.835 | 0.823 | 0.340 |
| SS | 0.730 | 0.592 | 0.606 | 0.181 |
| WB | 0.630 | 0.611 | 0.581 | 0.193 |

SS and WB are the weakest classes. Their similar red, white and blue jersey colours may cause confusion. More footage of these teams would help improve detection.

### 3.3 all_classes_best.pt

**Purpose:** Experimental model that detects AFL teams, referees, the ball and goal posts.

- Classes: CAR, GCS, HAW, CAT, REF, SS, WB, BALL, POST
- Dataset: `all_classes`
- Training: 43 epochs (best epoch: 33)
- Validation images: 114
- Validation boxes: 1,110
- Storage: Attached to the GitHub `models-v1` release. Downloaded weights are stored locally in the git-ignored `models/` directory.

| Metric | Precision | Recall | mAP@50 | mAP@50-95 |
|---|---:|---:|---:|---:|
| Overall | 0.786 | 0.778 | 0.789 | 0.338 |
| CAR | 0.893 | 0.923 | 0.953 | 0.462 |
| GCS | 0.916 | 0.934 | 0.928 | 0.443 |
| HAW | 0.797 | 0.861 | 0.854 | 0.357 |
| CAT | 0.866 | 0.902 | 0.938 | 0.406 |
| REF | 0.858 | 0.820 | 0.829 | 0.328 |
| SS | 0.662 | 0.585 | 0.565 | 0.176 |
| WB | 0.734 | 0.676 | 0.640 | 0.208 |
| BALL | 0.607 | 0.667 | 0.611 | 0.288 |
| POST | 0.738 | 0.639 | 0.785 | 0.373 |

BALL has limited validation data, with only six validation boxes. More labelled examples would help improve its reliability. SS and WB also remain weaker classes.

## 4. Experimental Model

### 4.1 yolo_merged_best.pt

**Purpose:** Older experimental model used by the original tracking scripts.

- Referenced by `experiments/track_videos.py`.
- Associated with the older starter tracker.
- The tracker is documented in `docs/inventory.md` as superseded by `analysis_pipeline/`.
- Training dataset, class details and validation metrics are not documented in the current training results.
- It is not listed among the three models downloaded by `training/download_models.py`.

Its original training details should be confirmed before using it as a benchmark or treating it as an officially released model.

## 5. Model Usage

Run commands from the `player_tracking/` directory.

Download all three official models:

```bash
python training/download_models.py
```

Download only the default model:

```bash
python training/download_models.py player_ref_best.pt
```

The current analysis pipeline uses YOLO and ByteTrack. The default model is `player_ref_best.pt`.

Run the detection and tracking script:

```bash
python analysis_pipeline/detect_and_track.py data/videos/test_clip_20s.mp4
```

A different model can be specified using the `--model` argument.

Example:

```bash
python analysis_pipeline/detect_and_track.py data/videos/test_clip_20s.mp4 --model models/all_teams_best.pt
```

The model weights are stored locally in the git-ignored `models/` directory after downloading.

## 6. Model Storage and Versioning

Official model weights are attached to GitHub releases rather than committed to the repository.

- Current release: `models-v1`
- Download script: `training/download_models.py`
- Local model directory: `player_tracking/models/`
- Dataset and training information: `docs/datasets.md` and `docs/training.md`

The download script verifies each model using its SHA-256 checksum to help ensure the downloaded file is correct.

### Publishing a New Model Version

When a new model is trained and approved:

1. Upload the new model weights to the appropriate model storage location.
2. Create a new GitHub release, for example `models-v2`.
3. Attach the model weight files to the release.
4. Calculate the SHA-256 checksum of each new model.
5. Add the new model filename and checksum to `training/download_models.py`.
6. Update this register with the new model's classes, dataset, training settings and validation metrics.
7. Update the relevant setup documentation so team members know how to download the new model.

This keeps model versions organised and allows team members to download and verify the correct weights.

## 7. References

- `docs/training.md` — training settings and validation results.
- `docs/datasets.md` — dataset sizes, splits and class information.
- `docs/setup.md` — model downloads, storage and setup instructions.
- `docs/inventory.md` — project code inventory and older tracking tools.
- `training/train.py` — model training script.
- `training/download_models.py` — model download and checksum verification.
- `analysis_pipeline/detect_and_track.py` — current detection and tracking script.
- [GitHub models-v1 release](https://github.com/Redback-Operations/redback-orion/releases/tag/models-v1).
