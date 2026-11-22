import sys
from pathlib import Path

SERVICE_DIR = Path(__file__).parent
PROJECT_ROOT = SERVICE_DIR.parent
SCRIPTS_BASE = PROJECT_ROOT / "player_tracking_logic"

PATH_TRAJ_SCRIPT_DIR  = SCRIPTS_BASE / "Tracking_Ethan"
JERSEY_COLOR_SCRIPT_DIR = SCRIPTS_BASE / "Re-Identification" / "JerseyColorDetection"
TACKLE_SCRIPT_DIR     = SCRIPTS_BASE / "tackle_detection_shafqat_ullah"
FORMATION_SCRIPT_DIR  = SCRIPTS_BASE / "Re-Identification" / "Formation_Visualization"

MODEL_NAME = "player_ref_best.pt"
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / MODEL_NAME
TRACKER_CONFIG = PROJECT_ROOT / "analysis_pipeline" / "configs" / "afl_broadcast_bytetrack.yaml"
TRACKING_CONFIDENCE = 0.3

UPLOADS_DIR = SERVICE_DIR / "uploads"
OUTPUTS_DIR = SERVICE_DIR / "outputs"
TRACKS_DIR = OUTPUTS_DIR / "tracks"

UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)
TRACKS_DIR.mkdir(exist_ok=True)

# analysis_pipeline/ and training/ sit next to player_service/.
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "training"))

from download_models import DownloadError, download  # noqa: E402


def ensure_model() -> Path:
    """Download the tracking model the first time it's needed.

    Raises DownloadError with a plain explanation if it can't be fetched.
    """
    if not MODEL_PATH.exists():
        download(MODEL_NAME, MODELS_DIR)
    return MODEL_PATH
