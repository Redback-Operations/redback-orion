"""
Main entry point for the 26T1 labelling pipeline.

Change OPERATION_MODE in config.py, then run:

    python main.py
"""

from labelling_pipeline.frame_extractor import extract_frames
from labelling_pipeline.manual_annotator import run_manual_annotator
from labelling_pipeline.prelabeler import run_prelabeler
from labelling_pipeline.utils import ensure_project_dirs, print_project_summary
import config


def main() -> None:
    ensure_project_dirs(config)
    print_project_summary(config)

    mode = str(config.OPERATION_MODE).strip().lower()

    if mode == "extract_frames":
        extract_frames(config)
    elif mode == "prelabel":
        run_prelabeler(config)
    elif mode == "extract_and_prelabel":
        extract_frames(config)
        run_prelabeler(config)
    elif mode == "manual_annotate":
        run_manual_annotator(config)
    else:
        valid_modes = [
            "extract_frames",
            "prelabel",
            "extract_and_prelabel",
            "manual_annotate",
        ]
        raise ValueError(
            f"Unknown OPERATION_MODE: {config.OPERATION_MODE}. "
            f"Please choose one of: {valid_modes}"
        )


if __name__ == "__main__":
    main()
