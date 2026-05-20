import argparse
from pathlib import Path

from player_tracking.config import TrackingConfig
from player_tracking.video_processor import process_video


def parse_args():
    parser = argparse.ArgumentParser(
        description="YOLO player tracking with fixed initial class and robust matching."
    )
    parser.add_argument("--video", type=Path, default=Path("data/videos/video.mp4"))
    parser.add_argument("--model", type=Path, default=Path("models/model.pt"))
    parser.add_argument("--output-video", type=Path, default=Path("video_track.mp4"))
    parser.add_argument("--output-json", type=Path, default=Path("video_track.json"))
    parser.add_argument("--seconds", type=int, default=40)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=640)
    return parser.parse_args()


def main():
    args = parse_args()

    config = TrackingConfig(
        video_path=args.video,
        model_path=args.model,
        output_video_path=args.output_video,
        output_json_path=args.output_json,
        process_seconds=args.seconds,
        conf_threshold=args.conf,
        imgsz=args.imgsz,
    )

    process_video(config)


if __name__ == "__main__":
    main()
