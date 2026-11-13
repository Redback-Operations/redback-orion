"""
Central configuration for the 26T1 labelling pipeline.

Change values in this file, then run:

    python main.py
"""

from pathlib import Path


# =========================================================
# Project paths
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
VIDEO_DIR = DATA_DIR / "videos"
FRAME_DIR = DATA_DIR / "frames"
LABEL_DIR = DATA_DIR / "labels"
MODEL_DIR = PROJECT_ROOT / "models"

# Default input video. Put your video at data/videos/video.mp4 or change this path.
VIDEO_PATH = VIDEO_DIR / "video.mp4"


# =========================================================
# Operation mode
# =========================================================
# Available modes:
#   "extract_frames"       -> split video into image frames only
#   "prelabel"             -> generate YOLO labels from existing frames only
#   "extract_and_prelabel" -> extract frames first, then prelabel them
#   "manual_annotate"      -> open the OpenCV annotation GUI
OPERATION_MODE = "extract_and_prelabel"


# =========================================================
# Frame extraction settings
# =========================================================
TARGET_FPS = 5
EXTRACT_START_FRAME = 0
EXTRACT_END_FRAME = None  # Use None to extract until the end of the video.

FRAME_NAME_PREFIX = "frame"
FRAME_IMAGE_EXT = ".jpg"
OVERWRITE_EXISTING_FRAMES = True


# =========================================================
# YOLO pre-labelling settings
# =========================================================
# If YOLO_MODEL_PATH is None, Ultralytics will use YOLO_MODEL_NAME.
# To use your own model, set for example:
# YOLO_MODEL_PATH = MODEL_DIR / "best.pt"
YOLO_MODEL_NAME = "yolo11x.pt"
YOLO_MODEL_PATH = None

YOLO_IMAGE_SIZE = 1280
YOLO_CONF_THRES = 0.20
YOLO_IOU_THRES = 0.50
YOLO_PERSON_CLASS_ID = 0  # COCO person class.

MIN_BOX_WIDTH = 8
MIN_BOX_HEIGHT = 15
OVERWRITE_EXISTING_LABELS = True


# =========================================================
# Class definitions
# =========================================================
TEAM_A_ID = 0
TEAM_B_ID = 1
REFEREE_ID = 2

CLASS_NAMES = {
    0: "CAR",
    1: "GCS",
    2: "REF",
}

# BGR colours used by the manual annotator.
# These values match the original yolo_manual_annotator.py UI style.
CLASS_BOX_COLOURS = {
    0: (0, 0, 0),      # black
    1: (0, 0, 255),    # red
    2: (0, 255, 255),  # yellow
}

VALID_IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".bmp")


# =========================================================
# Jersey colour classification settings
# =========================================================
# The classifier analyses the upper-body area inside each detected person box.
UPPER_BODY_Y1_RATIO = 0.10
UPPER_BODY_Y2_RATIO = 0.55

# HSV ranges used for initial class estimation.
RED_HSV_RANGE_1 = ((0, 70, 50), (10, 255, 255))
RED_HSV_RANGE_2 = ((170, 70, 50), (180, 255, 255))
REFEREE_YELLOW_HSV_RANGE = ((20, 120, 140), (40, 255, 255))
BLACK_HSV_RANGE = ((0, 0, 0), (180, 120, 70))

RED_RATIO_THRES = 0.06
REFEREE_YELLOW_RATIO_THRES = 0.08
BLACK_RATIO_THRES = 0.12


# =========================================================
# Manual annotation settings
# =========================================================
# 0 = start from the first sorted image.
# Example team split:
#   Sri    -> 0
#   Ethan  -> 140
#   Nikhil -> 240
#   Nithin -> 340
#   Vinuk  -> 440
ANNOTATION_START_FRAME_INDEX = 0

# Keep this title to match the original yolo_manual_annotator.py window style.
ANNOTATION_WINDOW_NAME = "YOLO Manual Annotator"

# Original annotator accepted boxes larger than 5 pixels in both width and height.
MANUAL_MIN_BOX_SIZE = 5
