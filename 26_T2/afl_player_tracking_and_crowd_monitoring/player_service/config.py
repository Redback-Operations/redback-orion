from pathlib import Path

SERVICE_DIR = Path(__file__).parent
PROJECT_ROOT = SERVICE_DIR.parent
SCRIPTS_BASE = PROJECT_ROOT / "player_tracking_logic"

TRACKING_SCRIPT_DIR   = SCRIPTS_BASE / "Yolov11_ByteTrack_Player_Tracking" / "final_code"
PATH_TRAJ_SCRIPT_DIR  = SCRIPTS_BASE / "Tracking_Ethan"
JERSEY_COLOR_SCRIPT_DIR = SCRIPTS_BASE / "Re-Identification" / "JerseyColorDetection"
TACKLE_SCRIPT_DIR     = SCRIPTS_BASE / "tackle_detection_shafqat_ullah"
FORMATION_SCRIPT_DIR  = SCRIPTS_BASE / "Re-Identification" / "Formation_Visualization"

MODEL_PATH = TRACKING_SCRIPT_DIR / "best.pt"

UPLOADS_DIR = SERVICE_DIR / "uploads"
OUTPUTS_DIR = SERVICE_DIR / "outputs"

UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)
