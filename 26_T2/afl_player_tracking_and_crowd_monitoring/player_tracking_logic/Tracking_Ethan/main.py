import argparse
from pathlib import Path

from player_tracking.config import TrackingConfig
from player_tracking.video_processor import process_video


def parse_args():
    parser = argparse.ArgumentParser(
        description="YOLO player tracking with robust matching and JerseyColorDetection-style team clustering."
    )
    parser.add_argument("--video", type=Path, default=Path("data/videos/video.mp4"))
    parser.add_argument("--model", type=Path, default=Path("models/best(SSvsWB).pt"))
    parser.add_argument("--output-video", type=Path, default=Path("outputs/video_track_clustered.mp4"))
    parser.add_argument("--output-json", type=Path, default=Path("outputs/video_track_clustered.json"))
    parser.add_argument("--output-csv", type=Path, default=Path("outputs/player_metrics.csv"))
    parser.add_argument("--seconds", type=int, default=40)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--clusters", type=int, default=3)
    parser.add_argument("--min-samples-per-track", type=int, default=5)
    parser.add_argument("--pixel-to-meter", type=float, default=0.05)
    return parser.parse_args()


def main():
    args = parse_args()

    config = TrackingConfig(
        video_path=args.video,
        model_path=args.model,
        output_video_path=args.output_video,
        output_json_path=args.output_json,
        output_csv_path=args.output_csv,
        process_seconds=args.seconds,
        conf_threshold=args.conf,
        imgsz=args.imgsz,
        jersey_clusters=args.clusters,
        min_samples_per_track=args.min_samples_per_track,
        pixel_to_meter=args.pixel_to_meter,
    )

    process_video(config)


if __name__ == "__main__":
    main()
