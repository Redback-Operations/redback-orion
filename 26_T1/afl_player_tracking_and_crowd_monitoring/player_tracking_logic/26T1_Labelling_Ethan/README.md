# 26T1_Labelling_Ethan: AFL / YOLO Labelling Pipeline

This project integrates the original three scripts into a complete Python project for the AFL video data labelling workflow:

1. **Extract frames**: Use OpenCV to split videos into image frames.
2. **Prelabel**: Use Ultralytics YOLO to automatically detect people and roughly classify them into `CAR / GCS / REF` based on jersey colour.
3. **Extract and prelabel**: Extract frames first, then automatically generate initial YOLO labels.
4. **Manual annotate**: Use an OpenCV GUI to manually modify, add, and delete bounding boxes and class labels.

After this, you mainly only need to modify the `config.py` file, then run:

```bash
python main.py
```

---

## 1. Project structure

```text
26T1_Labelling_Ethan/
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   ├── videos/
│   │   └── .gitkeep
│   ├── frames/
│   │   └── .gitkeep
│   └── labels/
│       └── .gitkeep
├── models/
│   └── .gitkeep
└── labelling_pipeline/
    ├── __init__.py
    ├── frame_extractor.py
    ├── prelabeler.py
    ├── manual_annotator.py
    └── utils.py
```

### Purpose of each file

| File | Purpose |
|---|---|
| `main.py` | Main entry point. Run this file to execute the currently selected pipeline operation. |
| `config.py` | The most important file. All paths, operation modes, FPS settings, YOLO parameters, and the manual annotation start frame are configured here. |
| `labelling_pipeline/frame_extractor.py` | OpenCV frame extraction logic. |
| `labelling_pipeline/prelabeler.py` | Ultralytics YOLO automatic pre-labelling logic. |
| `labelling_pipeline/manual_annotator.py` | OpenCV manual annotation and correction tool. |
| `labelling_pipeline/utils.py` | Shared utility functions, such as creating folders, listing images, and printing configuration details. |
| `data/videos/` | Stores original videos, for example `video.mp4`. |
| `data/frames/` | Extracted image frames are saved here. |
| `data/labels/` | YOLO `.txt` labels are saved here. |
| `models/` | Optional: stores your own YOLO model, for example `best.pt`. |

---

## 2. Installation

It is recommended to enter the project folder first:

```bash
cd 26T1_Labelling_Ethan
```

### Option A: using pip

```bash
pip install -r requirements.txt
```

### Option B: using conda environment

```bash
conda create -n labelling_26t1 python=3.11 -y
conda activate labelling_26t1
pip install -r requirements.txt
```

### Required packages

```text
ultralytics
opencv-python
numpy
```

When Ultralytics uses `yolo11x.pt` for the first time, it will usually download the model weights automatically. If the school network or local network blocks the download, you can manually download the model, place it in the `models/` folder, and then modify `YOLO_MODEL_PATH` in `config.py`.

---

## 3. Basic usage

### Step 1: Put video into the project

Put your video here:

```text
data/videos/video.mp4
```

The default configuration already points to this file:

```python
VIDEO_PATH = VIDEO_DIR / "video.mp4"
```

If your video name is not `video.mp4`, for example:

```text
data/videos/GoldCoast_Carlton_VFL.mp4
```

change `config.py` to:

```python
VIDEO_PATH = VIDEO_DIR / "GoldCoast_Carlton_VFL.mp4"
```

### Step 2: Select operation mode

Open `config.py` and modify:

```python
OPERATION_MODE = "extract_and_prelabel"
```

There are four available modes:

```python
OPERATION_MODE = "extract_frames"
OPERATION_MODE = "prelabel"
OPERATION_MODE = "extract_and_prelabel"
OPERATION_MODE = "manual_annotate"
```

### Step 3: Run project

```bash
python main.py
```

---

## 4. Operation modes

## 4.1 Extract video into frames only

Use this when you only want to split the video into image frames.

```python
OPERATION_MODE = "extract_frames"
```

Then run:

```bash
python main.py
```

Output:

```text
data/frames/frame_000000.jpg
data/frames/frame_000001.jpg
data/frames/frame_000002.jpg
...
```

---

## 4.2 Prelabel existing frames only

Use this when `data/frames/` already contains extracted images and you only want to generate YOLO `.txt` labels.

```python
OPERATION_MODE = "prelabel"
```

Then run:

```bash
python main.py
```

Output:

```text
data/labels/frame_000000.txt
data/labels/frame_000001.txt
data/labels/frame_000002.txt
...
```

Each label line uses standard YOLO format:

```text
class_id x_center y_center width height
```

All coordinates are normalised between 0 and 1.

Example:

```text
0 0.421532 0.512894 0.038214 0.112435
1 0.602123 0.485812 0.041252 0.118392
2 0.733819 0.491723 0.035182 0.105773
```

---

## 4.3 Extract video and prelabel automatically

This is the most common first run.

```python
OPERATION_MODE = "extract_and_prelabel"
```

It will run these two steps in order:

1. Extract frames from `VIDEO_PATH` into `FRAME_DIR`.
2. Run YOLO pre-labelling on those frames and save labels into `LABEL_DIR`.

Run:

```bash
python main.py
```

---

## 4.4 Manually correct labels

Use this after pre-labelling.

```python
OPERATION_MODE = "manual_annotate"
```

Then run:

```bash
python main.py
```

An OpenCV window will open. It loads images from `data/frames/` and labels from `data/labels/`.

The manual annotation window keeps the same visual style and interaction logic as the original `yolo_manual_annotator.py`: the window title is `YOLO Manual Annotator`, the top-left HUD shows the frame and current class, the top-right shortcut panel stays visible, the grey crosshair follows the cursor, the selected box is highlighted in green, and the default box colours are class `0` = black, class `1` = red, class `2` = yellow.

### Manual annotation controls

| Key / Mouse | Action |
|---|---|
| Left mouse drag | Draw a new bounding box. |
| Right click | Select an existing box. |
| `1` | Set current class to class 0, or relabel selected box to class 0. |
| `2` | Set current class to class 1, or relabel selected box to class 1. |
| `3` | Set current class to class 2, or relabel selected box to class 2. |
| `x` | Delete selected box. |
| `u` | Undo the most recently added box. |
| `s` | Save current image labels. |
| `d` | Save current labels and move to next image. |
| `a` | Save current labels and move to previous image. |
| `q` | Save current labels and quit. |

---

## 5. Important parameters in `config.py`

## 5.1 Path parameters

```python
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
VIDEO_DIR = DATA_DIR / "videos"
FRAME_DIR = DATA_DIR / "frames"
LABEL_DIR = DATA_DIR / "labels"
MODEL_DIR = PROJECT_ROOT / "models"
VIDEO_PATH = VIDEO_DIR / "video.mp4"
```

These paths are relative to the project folder, so the project can be moved to a different computer without changing absolute paths.

Normally, only change this line:

```python
VIDEO_PATH = VIDEO_DIR / "video.mp4"
```

---

## 5.2 Operation mode

```python
OPERATION_MODE = "extract_and_prelabel"
```

| Value | Meaning |
|---|---|
| `"extract_frames"` | Only split video into image frames. |
| `"prelabel"` | Only run YOLO pre-labelling on existing frames. |
| `"extract_and_prelabel"` | Split video into frames, then generate labels. |
| `"manual_annotate"` | Open manual annotation tool. |

---

## 5.3 Frame extraction parameters

```python
TARGET_FPS = 5
EXTRACT_START_FRAME = 0
EXTRACT_END_FRAME = None
FRAME_NAME_PREFIX = "frame"
FRAME_IMAGE_EXT = ".jpg"
OVERWRITE_EXISTING_FRAMES = True
```

| Parameter | Meaning | Example |
|---|---|---|
| `TARGET_FPS` | Number of frames saved per second. | `5` means save 5 frames per second. |
| `EXTRACT_START_FRAME` | Start extracting from this original video frame index. | `0` means start from the beginning. |
| `EXTRACT_END_FRAME` | Stop before this original video frame index. | `None` means extract until the end. |
| `FRAME_NAME_PREFIX` | Prefix of saved image names. | `"frame"` gives `frame_000000.jpg`. |
| `FRAME_IMAGE_EXT` | Saved image format. | `".jpg"` or `".png"`. |
| `OVERWRITE_EXISTING_FRAMES` | Whether to overwrite existing frames. | `True` overwrites; `False` skips existing files. |

### Example: extract only part of a video

If you want to start from original video frame 1000 and stop before frame 3000:

```python
EXTRACT_START_FRAME = 1000
EXTRACT_END_FRAME = 3000
```

### Example: save fewer frames

If the video has too many near-duplicate frames, reduce FPS:

```python
TARGET_FPS = 2
```

### Example: save more frames

If the action is fast or you need denser annotation:

```python
TARGET_FPS = 10
```

---

## 5.4 YOLO pre-labelling parameters

```python
YOLO_MODEL_NAME = "yolo11x.pt"
YOLO_MODEL_PATH = None
YOLO_IMAGE_SIZE = 1280
YOLO_CONF_THRES = 0.20
YOLO_IOU_THRES = 0.50
YOLO_PERSON_CLASS_ID = 0
MIN_BOX_WIDTH = 8
MIN_BOX_HEIGHT = 15
OVERWRITE_EXISTING_LABELS = True
```

| Parameter | Meaning | Recommendation |
|---|---|---|
| `YOLO_MODEL_NAME` | YOLO model name used when no local model path is given. | `"yolo11x.pt"` is strong but slower. |
| `YOLO_MODEL_PATH` | Optional local model path. | Use `MODEL_DIR / "best.pt"` if you trained your own model. |
| `YOLO_IMAGE_SIZE` | Inference image size. | Larger value may detect small players better but is slower. |
| `YOLO_CONF_THRES` | Detection confidence threshold. | Lower value detects more players but may add false positives. |
| `YOLO_IOU_THRES` | IoU threshold for NMS. | Adjust if boxes overlap too much or duplicate detections appear. |
| `YOLO_PERSON_CLASS_ID` | COCO person class id. | Keep as `0` for person detection. |
| `MIN_BOX_WIDTH` | Remove boxes narrower than this many pixels. | Useful for filtering noise. |
| `MIN_BOX_HEIGHT` | Remove boxes shorter than this many pixels. | Useful for filtering noise. |
| `OVERWRITE_EXISTING_LABELS` | Whether prelabel replaces existing labels. | Use `False` if you already manually corrected labels. |

### Important warning about overwriting labels

After manual correction, set this to `False` before running prelabel again:

```python
OVERWRITE_EXISTING_LABELS = False
```

Otherwise, pre-labelling will overwrite your manually corrected `.txt` files.

---

## 5.5 Class names

```python
CLASS_NAMES = {
    0: "CAR",
    1: "GCS",
    2: "REF",
}
```

Default classes:

| Class id | Class name | Meaning |
|---|---|---|
| `0` | `CAR` | Carlton player / Team A. |
| `1` | `GCS` | Gold Coast player / Team B. |
| `2` | `REF` | Referee. |

These names are shown in the manual annotation window. The YOLO `.txt` files store only class ids, not class names.

---

## 5.6 Jersey colour classification parameters

The pre-labelling process works in two stages:

1. YOLO detects people.
2. The code checks the upper-body colour inside each person box and assigns the class to `CAR`, `GCS`, or `REF`.

Relevant parameters:

```python
UPPER_BODY_Y1_RATIO = 0.10
UPPER_BODY_Y2_RATIO = 0.55

RED_HSV_RANGE_1 = ((0, 70, 50), (10, 255, 255))
RED_HSV_RANGE_2 = ((170, 70, 50), (180, 255, 255))
REFEREE_YELLOW_HSV_RANGE = ((20, 120, 140), (40, 255, 255))
BLACK_HSV_RANGE = ((0, 0, 0), (180, 120, 70))

RED_RATIO_THRES = 0.06
REFEREE_YELLOW_RATIO_THRES = 0.08
BLACK_RATIO_THRES = 0.12
```

### Why only upper body?

Players often have shorts, socks, shadows, grass background, and motion blur. Using the upper-body region makes the jersey colour signal more reliable.

### When to adjust these values

Adjust these values when:

- Team A is not red.
- Team B is not black/dark.
- The referee colour is not fluorescent yellow.
- The lighting or camera colour balance is different.
- Too many players are assigned to the wrong team.

This colour classifier is only for fast initial labelling. It is not expected to be perfect. The manual annotator is still needed for final correction.

---

## 5.7 Manual annotation start index

```python
ANNOTATION_START_FRAME_INDEX = 0
```

This controls where manual annotation starts in the sorted image list.

Examples:

```python
ANNOTATION_START_FRAME_INDEX = 0      # start from frame_000000.jpg
ANNOTATION_START_FRAME_INDEX = 140    # start from frame_000140.jpg
ANNOTATION_START_FRAME_INDEX = 240    # start from frame_000240.jpg
```

This is useful for team-based annotation splitting:

```text
0-139    -> Sri
140-239  -> Ethan
240-339  -> Nikhil
340-439  -> Nithin
440-539  -> Vinuk
```

---

## 6. Recommended workflow

### First time for a new video

1. Put the video into `data/videos/`.
2. Edit `VIDEO_PATH` in `config.py` if needed.
3. Set:

```python
OPERATION_MODE = "extract_and_prelabel"
TARGET_FPS = 5
OVERWRITE_EXISTING_FRAMES = True
OVERWRITE_EXISTING_LABELS = True
```

4. Run:

```bash
python main.py
```

5. Inspect labels in `data/labels/`.
6. Set:

```python
OPERATION_MODE = "manual_annotate"
ANNOTATION_START_FRAME_INDEX = 0
```

7. Run:

```bash
python main.py
```

8. Manually correct bounding boxes and classes.

---

## 7. Method details

## 7.1 Frame extraction method

The frame extraction module uses OpenCV:

```python
cv2.VideoCapture(VIDEO_PATH)
```

It reads the original video FPS and computes:

```text
frame_interval = round(original_fps / TARGET_FPS)
```

For example, if the original video is 25 FPS and `TARGET_FPS = 5`, then:

```text
frame_interval = round(25 / 5) = 5
```

So the script saves one frame every 5 original frames.

## 7.2 Pre-labelling method

The pre-labelling module uses Ultralytics YOLO:

```python
YOLO("yolo11x.pt")
```

It only detects the COCO person class:

```python
classes=[0]
```

Then it converts each detected box from absolute coordinates:

```text
x1, y1, x2, y2
```

to YOLO normalised format:

```text
class_id x_center y_center width height
```

## 7.3 Team/referee class estimation

After YOLO detects a person, the script crops the upper-body part of the bounding box and converts it to HSV colour space.

It then estimates whether the box belongs to:

- `CAR`: red jersey rule
- `GCS`: dark / black jersey rule
- `REF`: fluorescent yellow jersey rule

This keeps the original logic of using jersey colour as a rough automatic labelling strategy.

## 7.4 Manual annotation method

The manual annotator loads:

```text
data/frames/frame_xxxxxx.jpg
data/labels/frame_xxxxxx.txt
```

It converts YOLO labels back into pixel boxes, displays them in an OpenCV window, and lets you:

- draw new boxes,
- select existing boxes,
- relabel boxes,
- delete boxes,
- save labels back into YOLO format.

---

## 8. Output format

The labels are saved as YOLO `.txt` files.

For each image:

```text
data/frames/frame_000000.jpg
```

there should be a matching label file:

```text
data/labels/frame_000000.txt
```

Each row is:

```text
class_id x_center y_center width height
```

Example:

```text
0 0.421532 0.512894 0.038214 0.112435
1 0.602123 0.485812 0.041252 0.118392
2 0.733819 0.491723 0.035182 0.105773
```

---

## 9. Common tasks

### Task A: I only want to extract frames

```python
OPERATION_MODE = "extract_frames"
```

Run:

```bash
python main.py
```

### Task B: I already have frames and only want labels

```python
OPERATION_MODE = "prelabel"
```

Run:

```bash
python main.py
```

### Task C: I want to do everything from video to labels

```python
OPERATION_MODE = "extract_and_prelabel"
```

Run:

```bash
python main.py
```

### Task D: I want to continue manual correction from frame 140

```python
OPERATION_MODE = "manual_annotate"
ANNOTATION_START_FRAME_INDEX = 140
```

Run:

```bash
python main.py
```

### Task E: I do not want to overwrite manually corrected labels

```python
OVERWRITE_EXISTING_LABELS = False
```

---

## 10. Troubleshooting

## 10.1 `Video not found`

Check this line in `config.py`:

```python
VIDEO_PATH = VIDEO_DIR / "video.mp4"
```

Make sure the video exists here:

```text
data/videos/video.mp4
```

## 10.2 `No images found in data/frames`

You probably selected:

```python
OPERATION_MODE = "prelabel"
```

before extracting frames. Use:

```python
OPERATION_MODE = "extract_frames"
```

or:

```python
OPERATION_MODE = "extract_and_prelabel"
```

## 10.3 YOLO model download is slow or fails

The default model is:

```python
YOLO_MODEL_NAME = "yolo11x.pt"
YOLO_MODEL_PATH = None
```

If auto-download fails, manually place a model file in:

```text
models/best.pt
```

Then set:

```python
YOLO_MODEL_PATH = MODEL_DIR / "best.pt"
```

## 10.4 Manual annotation window does not open

The manual annotator uses OpenCV GUI. It needs a local graphical environment.

It may not work directly on a headless remote server or HPC login node. In that case, run the manual annotation part on your local computer.

## 10.5 Existing labels disappeared after prelabel

This happens if:

```python
OVERWRITE_EXISTING_LABELS = True
```

Set it to:

```python
OVERWRITE_EXISTING_LABELS = False
```

before re-running prelabel if you want to keep corrected labels.

## 10.6 Team classification is inaccurate

The colour classifier is only a rough first pass. Try adjusting:

```python
RED_RATIO_THRES
REFEREE_YELLOW_RATIO_THRES
BLACK_RATIO_THRES
RED_HSV_RANGE_1
RED_HSV_RANGE_2
REFEREE_YELLOW_HSV_RANGE
BLACK_HSV_RANGE
```

However, the safest approach is still to use prelabel as a starting point and then manually correct labels.

---

## 11. Suggested annotation quality checklist

Before using labels for training, check:

- Each player has exactly one bounding box.
- Boxes are tight around visible body regions.
- Heavily occluded players are labelled consistently according to your team rule.
- Referees are labelled as `REF`.
- Carlton / Team A players are labelled as `CAR`.
- Gold Coast / Team B players are labelled as `GCS`.
- Very small, blurry, or crowd/background people are handled consistently according to your dataset policy.
- `.jpg` frame names and `.txt` label names match exactly.

---

## 12. Notes for GitHub submission

The `.gitignore` file ignores large generated files by default:

```text
*.pt
*.mp4
data/frames/*
data/labels/*
```

This keeps the repository lightweight. If you need to submit example frames or labels, remove or adjust the relevant `.gitignore` rules carefully.

---

## 13. Quick configuration examples

### Example 1: Full automatic first pass

```python
OPERATION_MODE = "extract_and_prelabel"
VIDEO_PATH = VIDEO_DIR / "video.mp4"
TARGET_FPS = 5
ANNOTATION_START_FRAME_INDEX = 0
OVERWRITE_EXISTING_FRAMES = True
OVERWRITE_EXISTING_LABELS = True
```

### Example 2: Manual correction only

```python
OPERATION_MODE = "manual_annotate"
ANNOTATION_START_FRAME_INDEX = 140
```

### Example 3: Re-run prelabel without overwriting corrected labels

```python
OPERATION_MODE = "prelabel"
OVERWRITE_EXISTING_LABELS = False
```

### Example 4: Use a custom trained YOLO model

```python
YOLO_MODEL_PATH = MODEL_DIR / "best.pt"
```

### Example 5: Use the default YOLO11 model

```python
YOLO_MODEL_PATH = None
YOLO_MODEL_NAME = "yolo11x.pt"
```
