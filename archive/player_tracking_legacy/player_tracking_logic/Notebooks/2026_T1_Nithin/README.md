# AFL Player Detection & Tracking — YOLOv11 + DeepSORT

**Author:** Nithin JS
**Branch:** `player-tracking-sp3/nithin-model-improvements`

---

## Overview

This notebook covers the full AFL player detection and tracking pipeline, built using a unified YOLOv11 model trained across multiple AFL matches. It identifies players, referees, the ball, and goalposts, and tracks them across video frames using DeepSORT to produce per-player movement data.

The pipeline covers:

1. Model training on a combined multi-match dataset
2. Inference testing on unseen images
3. DeepSORT-based tracking on match video
4. CSV export of tracking data for downstream analysis

---

## Classes

| ID | Label | Description |
|----|-------|-------------|
| 0  | CAR   | Carlton Football Club players |
| 1  | GCS   | Gold Coast Suns players |
| 2  | HAW   | Hawthorn Football Club players |
| 3  | CAT   | Geelong Cats players |
| 4  | REF   | Match referees |
| 5  | BALL  | AFL football |
| 6  | POST  | Goalposts |

---

## Files

- `Player_Detection_Nithin.ipynb` — end-to-end notebook covering training, inference, and tracking

---

## Datasets

Training data is **not included in this repository** due to size and licensing. All datasets are stored in Google Drive at:

`Colab Notebooks/Project_Orion/Labelled_Data/`

| Folder | Contents |
|--------|----------|
| `yolo_train_data/` | Original ~200 annotated frames (Carlton vs Gold Coast) |
| `dataset2_hawcat/` | Hawthorn vs Geelong Cats annotated frames |
| `combined_dataset/` | Merged dataset used for unified model training |

- **Annotation tool:** Label Studio
- **Format:** YOLO format (one `.txt` label file per image)
- **Total classes:** 7

---

## How to Run

1. Open `Player_Detection_Nithin.ipynb` in Google Colab with GPU runtime enabled.
2. Mount Google Drive when prompted.
3. Run cells in order.
4. Trained weights are saved to `Colab Notebooks/Project_Orion/AFL_Model/best_unified.pt`.

---

## Training Configuration

| Parameter  | Value |
|------------|-------|
| Base model | YOLOv11 (Ultralytics, COCO-pretrained) |
| Epochs     | 50 |
| Image size | 640 |
| Batch size | 16 |
| Hardware   | Colab T4 GPU |

---

## Results

### Sprint 2 Baseline — Carlton vs Gold Coast (3 classes)

> **Note:** Sprint 2 metrics were produced with train and validation sets pointing to the same folder. Numbers are inflated and included here for reference only.

| Metric    | Value |
|-----------|-------|
| Precision | 0.949 |
| Recall    | 0.932 |
| mAP@50    | 0.976 |
| mAP@50-95 | 0.574 |

### Sprint 3 — Unified Model (Combined Dataset, 7 classes)

| Metric    | Value |
|-----------|-------|
| Precision | 0.930 |
| Recall    | 0.880 |
| mAP@50    | 0.949 |
| mAP@50-95 | 0.510 |

### Inference — Carlton vs Gold Coast (6 images)

| Class | Avg Conf | Max  | Min  | Detections |
|-------|----------|------|------|------------|
| CAR   | 0.73     | 0.90 | 0.43 | 33         |
| GCS   | 0.73     | 0.94 | 0.34 | 31         |
| REF   | 0.74     | 0.93 | 0.31 | 14         |

### Inference — Hawthorn vs Geelong Cats (4 images)

Model correctly identified HAW, CAT, REF, BALL, and POST detections. Performance drops on long-distance and wide-angle shots as expected — smaller player size reduces the pixel information available to the model.

---

## Tracking Pipeline

DeepSORT is integrated for persistent player ID assignment across frames. The tracking pipeline:

1. Runs YOLO inference on each video frame (confidence threshold: 0.4)
2. Passes detections to DeepSORT for ID assignment
3. Writes per-frame tracking data to a CSV file
4. Renders bounding boxes and player IDs onto the output video

### Tracking CSV Format

| Column     | Description |
|------------|-------------|
| frame      | Frame number in the video |
| player_id  | Unique DeepSORT-assigned ID |
| class      | Detected class label |
| x_center   | Horizontal centre of bounding box (pixels) |
| y_center   | Vertical centre of bounding box (pixels) |
| width      | Bounding box width (pixels) |
| height     | Bounding box height (pixels) |
| confidence | YOLO detection confidence score |

> **Note:** Coordinates are in pixel space, not real-world metres. Field calibration using goalposts is required for accurate distance calculations.

---

## Known Limitations

- Pixel-space coordinates only — real-world distance requires field calibration
- Performance degrades on wide/long-distance shots
- Dataset size is still relatively small; more annotated frames would improve robustness

---

## Dependencies

- `ultralytics` (YOLOv11)
- `deep_sort_realtime`
- `torch`, `torchvision`
- `opencv-python`, `numpy`, `matplotlib`

Install via:

    pip install ultralytics deep_sort_realtime opencv-python