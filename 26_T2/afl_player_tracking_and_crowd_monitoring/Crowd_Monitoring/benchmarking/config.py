from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
MODEL_CROWDHUMAN = SCRIPT_DIR.parent / "crowd_detection" / "yolov8n_crowdhuman.pt"
RESULTS_DIR = SCRIPT_DIR / "results"

MODELS = {
    "26T1 (v8 crowdhuman)": MODEL_CROWDHUMAN,
    "yolo26n (stock coco)": "yolo26n.pt",
    "yolo11n (stock coco)": "yolo11n.pt",
}

# Countable class names in priority order. Resolved by name so body, head and
# face models all work without a hardcoded index.
COUNT_CLASS_PREFERENCE = ("person", "head", "face")

# Some weights ship without real class names. Ultralytics falls back to
# stringified indices ({0: '0', 1: '1'}) when the training YAML had no names
# list, so name lookup fails and the mapping has to be declared here.
# Check any new entry with --diagnose first: a wrong index counts the wrong
# thing silently rather than raising.
MODEL_CLASS_OVERRIDES = {
    # label: (class_id, class_name)
    # class 1 confirmed as head via --diagnose: median box height ratio to
    # class 0 was 1:6.6 (new_test.mp4) and 1:5.1 (side.mp4). Head:body is
    # ~1:7.5, face:body ~1:15.
    "yolo26m (crowdpeoplefaces)": (1, "head"),
}

# side.mp4 is a committed sample clip. Add further clips under
# benchmarking/videos/ and list them here. Videos are processed sequentially
# and benchmarked separately, so per-clip metrics stay comparable and
# ground-truth frame indices never collide across clips.
VIDEO_PATHS = [
    SCRIPT_DIR / "videos" / "side.mp4",
]

# Ground truth is keyed by the clip's filename stem, so frame 5 in one clip
# does not overwrite frame 5 in another:
#   { "side": { "0": 42, "1": 43, ... }, "clip2": { ... } }
GROUND_TRUTH_PATH = None

DEFAULT_CONF = 0.35
DEFAULT_IOU = 0.30
DEFAULT_N_FRAMES = 50

# Ultralytics defaults to max_det=300, which truncates dense crowd frames
# without warning: a 300-box result is a cap rather than a count. Raised well
# above any plausible per-frame crowd so the counts are real measurements.
DEFAULT_MAX_DET = 5000

# Tiles are fed at native imgsz; resizing 4K to 640 shrinks heads below the
# detector's size floor. Overlap exceeds the largest counted object so
# seam-straddling boxes survive cross-tile NMS.
TILE_SIZE = 640
TILE_OVERLAP = 192  # > largest counted object; heads ~108px median on side.mp4
TILE_BATCH = 8

# Display-only downscale for --show. A 4K frame does not fit on screen. Does
# not affect inference or saved output.
DEFAULT_SHOW_SCALE = 0.5

SWEEP_THRESHOLDS = (0.05, 0.10, 0.20, 0.35, 0.50)