import os
from pathlib import Path

CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
MODEL_NAME = os.path.join(CURRENT_DIR, "face_model.pt")   # Model downloaded from https://huggingface.co/arnabdhar/YOLOv8-Face-Detection
PEOPLE_MODEL_NAME = os.path.join(CURRENT_DIR, "yolov8s")
 
ANNOTATED_DIR = Path("crowd_detection_output") / "face_detection_results"
PERSON_CLASS = None
PEOPLE_ANNOTATED_DIR = Path("crowd_detection_output") / "people_detection_results"

DEFAULT_CONF = 0.35
DEFAULT_IOU  = 0.30

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


OUTPUT_DIR = Path("detection_output")