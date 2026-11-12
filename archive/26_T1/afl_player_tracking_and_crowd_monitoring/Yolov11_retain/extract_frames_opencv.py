import os
import cv2

# =========================
# Config
# =========================
VIDEO_PATH = "data/video/GoldCoast_Carlton_VFL.mp4"
OUTPUT_DIR = "data/frames"

TARGET_FPS = 5  # Save 5 frames per second


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"Failed to open video: {VIDEO_PATH}")
        return

    original_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_sec = total_frames / original_fps if original_fps > 0 else 0

    print(f"Video: {VIDEO_PATH}")
    print(f"Original FPS: {original_fps}")
    print(f"Total frames: {total_frames}")
    print(f"Duration (sec): {duration_sec:.2f}")

    if original_fps <= 0:
        print("Invalid video FPS.")
        cap.release()
        return

    # How many original frames to skip between each saved frame
    frame_interval = max(int(round(original_fps / TARGET_FPS)), 1)

    frame_idx = 0
    saved_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_interval == 0:
            out_path = os.path.join(OUTPUT_DIR, f"frame_{saved_idx:06d}.jpg")
            cv2.imwrite(out_path, frame)
            saved_idx += 1

        frame_idx += 1

    cap.release()
    print(f"Done. Saved {saved_idx} frames to:")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()