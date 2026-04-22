# AFL Player Detection — YOLOv11

**Author:** Nithin JS
**Sprint:** Sprint 2 (4 – 17 April)
**Branch:** `player-tracking-sp2/nithin-yolo-training`

## Overview

This notebook trains a custom YOLOv11 object detection model to identify Australian Football League (AFL) match participants across three classes:

- `CAR` — Carlton Football Club players
- `GCS` — Gold Coast Suns players
- `REF` — Match referees

The trained model is the detection stage of the broader AFL Player Tracking pipeline, which uses DeepSORT for tracking identified detections across frames.

## Files

- `Player_Detection_Nithin.ipynb` — end-to-end training and inference notebook

## Dataset

The training dataset is **not included in this repository** due to size and licensing considerations. It is stored at:

```
Google Drive: Colab Notebooks/Project_Orion/Labelled_Data/yolo_train_data/
```

- **Source:** AFL broadcast frames extracted by the team, annotated in Label Studio
- **Size:** ~200 frames
- **Classes:** 3 (CAR, GCS, REF)
- **Format:** YOLO format (one `.txt` label file per image)

To run the notebook, you must have Drive access to the Project Orion folder.

## How to Run

1. Open `Player_Detection_Nithin.ipynb` in Google Colab with GPU runtime enabled.
2. Mount Google Drive when prompted.
3. Run cells in order. Training takes roughly 30–40 minutes on a Colab T4 GPU.
4. Trained weights are saved to `Colab Notebooks/Project_Orion/AFL_Model/best.pt`.

## Training Configuration

| Parameter    | Value |
|--------------|-------|
| Base model   | YOLOv11 (Ultralytics, COCO-pretrained) |
| Epochs       | 50    |
| Image size   | 640   |
| Batch size   | 16    |
| Hardware     | Colab T4 GPU |

## Results (Sprint 2 — Initial Baseline)

> **Caveat:** These metrics were produced with train and validation sets pointing to the same folder. Numbers are inflated. A proper train/val split is planned for Sprint 3.

| Metric        | Value |
|---------------|-------|
| Precision     | 0.949 |
| Recall        | 0.932 |
| mAP@50        | 0.976 |
| mAP@50-95     | 0.574 |

**Inference confidence across 6 test images:**

| Class | Avg Conf | Max  | Min  | Detections |
|-------|----------|------|------|------------|
| CAR   | 0.73     | 0.90 | 0.43 | 33         |
| GCS   | 0.73     | 0.94 | 0.34 | 31         |
| REF   | 0.74     | 0.93 | 0.31 | 14         |

## Known Limitations


- Classes are tied to specific teams (Carlton, Gold Coast). Model does not generalise to other matches.
- Dataset size (200 frames) is small; more data needed for robust performance.

## Sprint 3 Plan

- Evaluate merging teammate-annotated data (pending class schema alignment).
- Explore generalisation of class labels to support different matches.

## Dependencies

- `ultralytics` (YOLOv11)
- `torch`, `torchvision`
- Standard scientific Python stack (numpy, matplotlib, opencv-python)

Installed via `!pip install ultralytics` in the notebook.

