# Player Tracking — YOLOv11 Pre-labelling Pipeline

This folder contains a three-stage pipeline for producing YOLO-format annotations from a raw VFL match video.  
The stages are: **frame extraction → automatic pre-labelling → manual correction**.

---

## Directory Structure

```
Yolov11_retain/
├── extract_frames_opencv.py       # Stage 1 – extract frames from video
├── prelabel_with_ultralytics.py   # Stage 2 – auto-detect and classify players
├── yolo_manual_annotator.py       # Stage 3 – manual review and correction
└── data/
    ├── video/                     # Source video here
    ├── frames/                    # Output frames (created by Stage 1)
    └── labels/                    # YOLO .txt label files (created by Stages 2 & 3)
```

---

## Classes

| ID | Label | Player / Role       | Jersey colour       |
|----|-------|---------------------|---------------------|
| 0  | CAR   | Carlton             | Red                 |
| 1  | GCS   | Gold Coast Suns     | Black               |
| 2  | REF   | Referee             | Fluorescent yellow  |

---

## Stage 1 — Frame Extraction (`extract_frames_opencv.py`)

### What it does

Uses **OpenCV** (`cv2.VideoCapture`) to read a video file and save individual frames as JPEG images.  
Rather than saving every frame, the script samples at a fixed rate of **5 fps**, which reduces the dataset size while keeping enough temporal coverage for training.

### Key config

```python
VIDEO_PATH  = "data/video/GoldCoast_Carlton_VFL.mp4"
OUTPUT_DIR  = "data/frames"
TARGET_FPS  = 5   # frames saved per second of video
```

### How it works

1. Open the video and read its native frame rate (`CAP_PROP_FPS`) and total frame count.
2. Compute `frame_interval = round(native_fps / TARGET_FPS)` — e.g. for a 25 fps video this is 5, meaning every 5th frame is saved.
3. Loop through all frames; when `frame_idx % frame_interval == 0`, write the frame to `data/frames/frame_XXXXXX.jpg`.
4. Print a summary of how many frames were saved.

### Run

```bash
python extract_frames_opencv.py
```

---

## Stage 2 — Automatic Pre-labelling (`prelabel_with_ultralytics.py`)

### What it does

Runs every extracted frame through **YOLOv11x** (`yolo11x.pt`) to detect all people, then uses HSV colour analysis on each detected bounding box to assign a class label (CAR / GCS / REF) based on jersey colour.  
The output is one YOLO-format `.txt` file per frame, saved to `data/labels/`.

### Key config

```python
MODEL_NAME  = "yolo11x.pt"    # downloaded automatically on first run
IMG_SIZE    = 1280
CONF_THRES  = 0.20            # detection confidence threshold
IOU_THRES   = 0.50            # NMS IoU threshold
```

### How it works

**Detection**

`model.predict()` is called with `classes=[0]` (COCO person class only), so the model ignores the ball, goalposts, and other objects.  
Bounding boxes smaller than 8 × 15 pixels are discarded as noise.

**Jersey colour classification (`classify_by_jersey_color`)**

For each detected person box, only the **upper-body region** (roughly 10 %–55 % of the box height) is analysed to avoid interference from green grass, shorts, and shoes.  
The crop is converted to **HSV** and three colour masks are applied:

| Colour        | HSV range (approx.)                        | Assigned class |
|---------------|--------------------------------------------|----------------|
| Red           | H 0–10 or 170–180, S > 70, V > 50         | CAR (0)        |
| Fluorescent yellow | H 20–40, S > 120, V > 140            | REF (2)        |
| Black         | H any, S < 120, V < 70                     | GCS (1)        |

The decision order is: **referee first** (yellow is the most distinctive), then **red**, then **black**.  
If no threshold is met, the mean HSV values are used as a fallback, and the box defaults to CAR if still ambiguous.

**Label format**

Each line in the output `.txt` file follows the YOLO format:
```
<class_id> <x_center> <y_center> <width> <height>
```
All coordinates are normalised to [0, 1] relative to the image dimensions.

### Run

```bash
python prelabel_with_ultralytics.py
```

> `yolo11x.pt` will be downloaded automatically by Ultralytics on the first run if it is not already present.

---

## Stage 3 — Manual Annotation Tool (`yolo_manual_annotator.py`)

### What it does

Opens an **OpenCV** window that lets you review and correct the pre-labels frame by frame.  
Existing `.txt` labels are loaded automatically for each frame.  
Changes are written back to the same label files when you save or navigate.

### Key config

```python
IMAGE_DIR        = "data/frames"
LABEL_DIR        = "data/labels"
START_FRAME_INDEX = 140   # which frame to start from (0-based)
```

The `START_FRAME_INDEX` variable lets multiple team members split the workload across different frame ranges without overwriting each other's work.

### Keyboard shortcuts

| Key | Action |
|-----|--------|
| Left-drag | Draw a new bounding box (assigned to the current class) |
| Right-click | Select the box under the cursor |
| `1` / `2` / `3` | Set current class to CAR / GCS / REF — or re-label the selected box |
| `x` | Delete the selected box |
| `u` | Undo the last added box |
| `s` | Save labels for the current frame |
| `d` | Save and go to the **next** frame |
| `a` | Save and go to the **previous** frame |
| `q` | Save and quit |

### Visual aids

- **Crosshair** — grey guide lines follow the cursor and display pixel coordinates, making it easy to align boxes precisely.
- **Box colours** — CAR = black outline, GCS = red outline, REF = yellow outline.
- **Selected box** — highlighted with a bright green border.
- **HUD** — current frame index, current class, and selected box index are displayed in the top-left corner.
- **Shortcut legend** — always visible in the top-right corner.

### How the drawing logic works

```
Mouse down  →  start_point recorded, drawing = True
Mouse move  →  end_point updated, preview rectangle shown
Mouse up    →  box appended to the list if width > 5px and height > 5px
Right click →  iterates boxes back-to-front to find which box contains the cursor
Save        →  converts pixel coords back to normalised YOLO format and writes the .txt file
Load        →  converts normalised YOLO coords back to pixel coords for display
```

### Run

```bash
python yolo_manual_annotator.py
```

---

## Full Pipeline — Quick Start

```bash
# 1. Extract frames
python extract_frames_opencv.py

# 2. Pre-label with YOLOv11x
python prelabel_with_ultralytics.py

# 3. Manually correct labels
python yolo_manual_annotator.py
```

### Dependencies

```bash
pip install opencv-python ultralytics numpy
```
