"""Stampede Detection pipeline entry point."""

from pathlib import Path
from typing import Optional, Union

import cv2

from stampede_detection.stampede_detection import (
    analyse_video,
    resolve_camera_and_zone,
)


def extract_consecutive_frames(
    video_path: str,
    output_dir: Path,
):
    """Extract every video frame consecutively for Stampede Detection."""

    video_path = Path(video_path).resolve()

    if not video_path.exists():
        raise FileNotFoundError(
            f"Video not found: {video_path}"
        )

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open video: {video_path}"
        )

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 30.0

    frames_dir = output_dir / "consecutive_frames"
    frames_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    frames = []
    frame_id = 0

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                break

            frame_path = frames_dir / (
                f"frame_{frame_id:06d}.jpg"
            )

            if not cv2.imwrite(
                str(frame_path),
                frame,
            ):
                raise RuntimeError(
                    f"Could not save frame {frame_id}."
                )

            frames.append(
                {
                    "frame_id": frame_id,
                    "timestamp": frame_id / fps,
                    "frame_path": str(frame_path),
                }
            )

            frame_id += 1

    finally:
        cap.release()

    if not frames:
        raise ValueError(
            f"No frames could be extracted from: {video_path}"
        )

    return frames


def analyze_stampede(
    input_source: Union[str, Path, dict],
    video_id: Optional[str] = None,
    camera_id: Optional[str] = "CAM_02",
    zone_id: Optional[str] = "ZONE_B",
):
    """Run Stampede Detection from a raw video or Video Processing result.

    Video Processing integration:
        vp_result = process_input_video(video_path, video_id)
        analyze_stampede(vp_result)

    Important:
        When a Video Processing result dictionary is supplied, only its
        original ``video_path`` and ``video_id`` are used. The extracted
        ``frames`` from Video Processing are intentionally ignored.
        Stampede Detection performs its own frame extraction and analysis.
    """

    # --------------------------------------------------------
    # VIDEO PROCESSING RESULT
    # --------------------------------------------------------
    if isinstance(input_source, dict):
        video_path = input_source.get("video_path")

        if not video_path:
            raise ValueError(
                "Video Processing result must contain 'video_path'."
            )

        video_id = (
            video_id
            or input_source.get("video_id")
        )

        if not video_id:
            raise ValueError(
                "Video Processing result must contain 'video_id'."
            )

        # Deliberately use only the original video path.
        input_source = video_path

    # --------------------------------------------------------
    # RAW VIDEO PATH
    # --------------------------------------------------------
    if isinstance(input_source, (str, Path)):
        video_path = Path(input_source).resolve()

        if not video_path.exists():
            raise FileNotFoundError(
                f"Video not found: {video_path}"
            )

        if video_id is None:
            video_id = video_path.stem

        output_dir = (
            Path(__file__).resolve().parent
            / "data"
            / "output"
            / "stampede_runs"
            / str(video_id)
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        print()
        print("=" * 70)
        print("STAMPEDE DETECTION - VIDEO INPUT")
        print("=" * 70)
        print(f"Video : {video_path}")
        print(f"ID    : {video_id}")
        print()

        print("Extracting consecutive frames...")

        frames = extract_consecutive_frames(
            video_path=str(video_path),
            output_dir=output_dir,
        )

        print(
            f"Extracted {len(frames)} consecutive frames."
        )

        input_data = {
            "video_id": video_id,
            "frames": frames,
        }

        temporary_frames_dir = (
            output_dir / "consecutive_frames"
        )

    else:
        raise TypeError(
            "input_source must be a Video Processing result dictionary "
            "or a raw video path."
        )

    # --------------------------------------------------------
    # RUN STAMPEDE ANALYSIS
    # --------------------------------------------------------
    resolved_camera_id, resolved_zone_id = (
        resolve_camera_and_zone(
            input_data,
            camera_id_override=camera_id,
            zone_id_override=zone_id,
        )
    )

    try:
        _features, events = analyse_video(
            input_data=input_data,
            output_dir=output_dir,
            video_id=video_id,
            camera_id=resolved_camera_id,
            zone_id=resolved_zone_id,
        )
    finally:
        # The original-video path creates these frames specifically for
        # Stampede Detection, so they can be cleaned up afterwards.
        if (
            temporary_frames_dir is not None
            and temporary_frames_dir.exists()
        ):
            import shutil
            shutil.rmtree(temporary_frames_dir)

    return {
        "video_id": video_id,
        "events": events,
    }


if __name__ == "__main__":
    pass
