from pathlib import Path


MODEL_NAME   = "model.pt" # Model downloaded from https://huggingface.co/arnabdhar/YOLOv8-Face-Detection
PERSON_CLASS = None


DEFAULT_CONF = 0.45
DEFAULT_IOU  = 0.40

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


OUTPUT_DIR = Path("detection_output")