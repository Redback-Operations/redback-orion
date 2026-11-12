"""
Crowd detection configuration.

Import this module before `ultralytics`. It sets YOLO_VERBOSE and, on the
DirectML path, YOLO_AUTOINSTALL, both of which Ultralytics reads at import
time (main.py handles this ordering).

Environment variables
---------------------
CROWD_DEVICE (default "auto")
    Selects the inference backend.

    auto    Use the fastest backend this machine supports, in order:
            cuda:0 if CUDA torch detects an NVIDIA GPU, then dml if
            onnxruntime-directml is installed and the .onnx export exists,
            then cpu (OpenVINO if installed and exported, otherwise the
            plain .pt weights).
    cuda:0  NVIDIA GPU. Uses the TensorRT .engine if built, otherwise the
            .pt weights on CUDA.
    dml     DirectML. Runs the .onnx export on any DX12 GPU (AMD or Intel).
    cpu     Uses the OpenVINO export if installed and exported, otherwise
            the plain .pt weights. OpenVINO is roughly 2 to 4x faster than
            plain CPU torch.

    An explicit "cuda" or "dml" that is unavailable raises an error. Only
    "auto" falls back.

CROWD_DETECT_STRIDE (default 30)
    Run the detector on every Nth extracted frame. 1 = every frame.

CROWD_DETECT_MAX_WIDTH (default 1920)
    Downscale frames wider than this before inference. 0 = off.

CROWD_SKIP_EMPTY_TILES (default true)
    Skip tiles that the crowd region mask has left almost entirely black.

To restore the original unoptimised behaviour, set:
    CROWD_DETECT_STRIDE=1 CROWD_DETECT_MAX_WIDTH=0 CROWD_SKIP_EMPTY_TILES=false

Backend setup
-------------
CUDA:
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
    Use cu128, not cu124, which has no wheels for Python 3.14. If the
    installed driver rejects cu128 at runtime, try cu126.
    Optional TensorRT engine (machine-specific; rebuild per box, do not commit):
    yolo export model=yolo26mcrowdpeoplefaces.pt format=engine imgsz=640 quantize=16 dynamic=True device=0

DirectML:
    pip install onnxruntime-directml
    Uninstall any other onnxruntime* package first; they share an install
    folder and shadow the DirectML build.
    yolo export model=yolo26mcrowdpeoplefaces.pt format=onnx imgsz=640 dynamic=True opset=17

OpenVINO (CPU):
    YOLO("yolo26mcrowdpeoplefaces.pt").export(format="openvino", imgsz=640, dynamic=True)
"""
import importlib.util
import os
from pathlib import Path

# Silences Ultralytics' load-time messages so the benchmark report is the only
# output. Ultralytics reads this at import time (see module docstring).
os.environ.setdefault("YOLO_VERBOSE", "False")

# --- Paths --------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_NAME = os.path.join(CURRENT_DIR, "face_model.pt")   # Model downloaded from https://huggingface.co/arnabdhar/YOLOv8-Face-Detection

# Model paths. Export commands for each format are in the module docstring.
_PEOPLE_PT       = os.path.join(CURRENT_DIR, "yolo26mcrowdpeoplefaces.pt")
_PEOPLE_ENGINE   = os.path.join(CURRENT_DIR, "yolo26mcrowdpeoplefaces.engine")
_PEOPLE_ONNX     = os.path.join(CURRENT_DIR, "yolo26mcrowdpeoplefaces.onnx")
_PEOPLE_OPENVINO = os.path.join(CURRENT_DIR, "yolo26mcrowdpeoplefaces_openvino_model")

ANNOTATED_DIR = Path("crowd_detection_output") / "face_detection_results"
PEOPLE_ANNOTATED_DIR = Path("crowd_detection_output") / "people_detection_results"
TILE_DEBUG_DIR = Path("crowd_detection_output") / "tile_debug"

# --- Detection settings -------------------------------------------------------
PEOPLE_CLASS_ID = 1
DEFAULT_CONF = 0.20
DEFAULT_IOU = 0.30
USE_TILING = True
USE_FACE_DETECTION = False
SAVE_TILE_DEBUG = False
TILE_IMGSZ = 640

# --- Latency knobs (see module docstring) -------------------------------------
DETECT_STRIDE = int(os.environ.get("CROWD_DETECT_STRIDE", "30"))
DETECT_MAX_WIDTH = int(os.environ.get("CROWD_DETECT_MAX_WIDTH", "1920"))
SKIP_EMPTY_TILES = os.environ.get("CROWD_SKIP_EMPTY_TILES", "true").strip().lower() in {"1", "true", "yes", "on"}
MIN_TILE_FILL = 0.02   # minimum fraction of non-black pixels a tile needs to be processed

# --- Inference device ---------------------------------------------------------
# See the module docstring for CROWD_DEVICE options and backend setup.
DEVICE = os.environ.get("CROWD_DEVICE", "auto")


def _cuda_available():
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


def _dml_available():
    """Return True if the DirectML build of onnxruntime is installed and the ONNX export exists."""
    if not os.path.isfile(_PEOPLE_ONNX):
        return False
    try:
        import onnxruntime as ort
        return "DmlExecutionProvider" in ort.get_available_providers()
    except Exception:
        return False


def _openvino_available():
    return os.path.isdir(_PEOPLE_OPENVINO) and importlib.util.find_spec("openvino") is not None


def _resolve_device(pref):
    """Resolve CROWD_DEVICE to a concrete device string.

    "auto" picks the fastest available backend. An explicit "cuda" or "dml"
    that isn't available raises RuntimeError instead of falling back.
    """
    pref = (pref or "auto").strip().lower()
    explicit = pref not in ("", "auto")
    if not explicit:
        if _cuda_available():
            return "cuda:0"
        pref = "dml" if _dml_available() else "cpu"
    if pref == "dml":
        if explicit and not _dml_available():
            raise RuntimeError(
                "CROWD_DEVICE='dml' requested but DirectML is unavailable. Install "
                "onnxruntime-directml (with no other onnxruntime* package) and build "
                "the .onnx export. See the module docstring for the commands."
            )
        # Stops Ultralytics' check_requirements from pip-installing plain
        # onnxruntime over the DirectML build (see module docstring).
        os.environ.setdefault("YOLO_AUTOINSTALL", "false")
        return "dml"
    if pref.startswith("cuda") or pref.isdigit():
        if not _cuda_available():
            raise RuntimeError(
                f"CROWD_DEVICE={pref!r} requested but torch.cuda.is_available() is False. "
                "Install a CUDA build of torch, e.g.\n"
                "  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128"
            )
        return f"cuda:{pref}" if pref.isdigit() else pref
    return pref  # "cpu", "mps", or any other torch device string


# --- Device-dependent settings ------------------------------------------------
RESOLVED_DEVICE = _resolve_device(DEVICE)
USE_CUDA = RESOLVED_DEVICE.startswith("cuda")
USE_DML = RESOLVED_DEVICE == "dml"

if USE_CUDA:
    PEOPLE_MODEL_NAME = _PEOPLE_ENGINE if os.path.isfile(_PEOPLE_ENGINE) else _PEOPLE_PT
elif USE_DML:
    PEOPLE_MODEL_NAME = _PEOPLE_ONNX
elif RESOLVED_DEVICE == "cpu" and _openvino_available():
    PEOPLE_MODEL_NAME = _PEOPLE_OPENVINO
else:
    PEOPLE_MODEL_NAME = _PEOPLE_PT   # no OpenVINO (or "mps" etc.): plain weights

# Passed to every model(...) predict call.
PREDICT_KWARGS = {"device": RESOLVED_DEVICE}
if USE_CUDA:
    PREDICT_KWARGS["quantize"] = 16   # FP16
elif USE_DML:
    # Ultralytics can't parse "dml" as a torch device, so it gets "cpu" for its
    # pre- and post-processing tensors. Inference itself still runs on DirectML,
    # because dml_backend.enable_dml pins the ONNX session to that provider.
    PREDICT_KWARGS["device"] = "cpu"

TILE_BATCH = 16 if (USE_CUDA or USE_DML) else 8