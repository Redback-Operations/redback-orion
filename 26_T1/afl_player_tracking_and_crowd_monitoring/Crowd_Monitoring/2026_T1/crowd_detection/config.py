import os
from pathlib import Path

CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
MODEL_NAME = os.path.join(CURRENT_DIR, "model.pt") # Model downloaded from https://huggingface.co/arnabdhar/YOLOv8-Face-Detection
 
ANNOTATED_DIR = Path("crowd_detection_output") / "face_detection_results"
PERSON_CLASS = None


DEFAULT_CONF = 0.45
DEFAULT_IOU  = 0.40

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


OUTPUT_DIR = Path("detection_output")