import json
from pathlib import Path

from shared.services.crowd_detection_service import process_detection


def main():
    project_root = Path(__file__).resolve().parent

    video_name = "crowd4.mp4"
    video_path = project_root / video_name

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    data = {
        "video_id": "crowd",
        "video_path": str(video_path)
    }

    print("[INFO] Running crowd detection service...")
    result = process_detection(data)

    output_dir = project_root / "detection_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    json_output_path = output_dir / "crowd4_detection_result.json"

    with open(json_output_path, "w") as f:
        json.dump(result, f, indent=4)

    print("[INFO] Detection completed successfully")
    print(f"[INFO] JSON result saved to: {json_output_path}")
    print("[INFO] Annotated frames saved in:")
    print(" - crowd_detection_output/face_detection_results")
    print(" - crowd_detection_output/people_detection_results")


if __name__ == "__main__":
    main()
    