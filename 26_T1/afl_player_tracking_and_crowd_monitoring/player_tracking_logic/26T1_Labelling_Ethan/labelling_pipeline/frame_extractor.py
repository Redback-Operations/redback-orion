"""Video-to-frame extraction using OpenCV."""

from pathlib import Path
import cv2


def extract_frames(config) -> None:
    """
    Extract image frames from a video according to the settings in config.py.

    The extraction keeps the original logic: read the video with OpenCV and save
    one frame every frame_interval frames, where frame_interval is calculated
    from the original FPS and TARGET_FPS.
    """
    video_path = Path(config.VIDEO_PATH)
    output_dir = Path(config.FRAME_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not video_path.exists():
        print(f"Video not found: {video_path}")
        print("Please put your video in data/videos/ or update VIDEO_PATH in config.py.")
        return

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Failed to open video: {video_path}")
        return

    original_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_sec = total_frames / original_fps if original_fps > 0 else 0

    print(f"Video: {video_path}")
    print(f"Original FPS: {original_fps}")
    print(f"Total frames: {total_frames}")
    print(f"Duration (sec): {duration_sec:.2f}")

    if original_fps <= 0:
        print("Invalid video FPS. Frame extraction stopped.")
        cap.release()
        return

    target_fps = max(float(config.TARGET_FPS), 0.0001)
    frame_interval = max(int(round(original_fps / target_fps)), 1)

    start_frame = max(int(config.EXTRACT_START_FRAME), 0)
    end_frame = config.EXTRACT_END_FRAME
    if end_frame is not None:
        end_frame = min(int(end_frame), total_frames)
        if end_frame <= start_frame:
            print("EXTRACT_END_FRAME must be larger than EXTRACT_START_FRAME.")
            cap.release()
            return

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    frame_idx = start_frame
    saved_idx = 0
    saved_count = 0

    print(f"Extraction start frame: {start_frame}")
    print(f"Extraction end frame: {end_frame if end_frame is not None else 'video end'}")
    print(f"Frame interval: every {frame_interval} original frame(s)")
    print("Frame extraction started...")

    while True:
        if end_frame is not None and frame_idx >= end_frame:
            break

        ret, frame = cap.read()
        if not ret:
            break

        if (frame_idx - start_frame) % frame_interval == 0:
            out_path = output_dir / f"{config.FRAME_NAME_PREFIX}_{saved_idx:06d}{config.FRAME_IMAGE_EXT}"

            if out_path.exists() and not config.OVERWRITE_EXISTING_FRAMES:
                print(f"Skipped existing frame: {out_path.name}")
            else:
                cv2.imwrite(str(out_path), frame)
                saved_count += 1

            saved_idx += 1

        frame_idx += 1

    cap.release()
    print(f"Done. Saved {saved_count} frame(s) to:")
    print(output_dir)
