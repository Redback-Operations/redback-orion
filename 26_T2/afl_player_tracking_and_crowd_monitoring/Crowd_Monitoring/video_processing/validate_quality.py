import cv2
import csv
import os
import statistics

from image_quality import (
    ImageQualityAnalyzer,
    recommend_enhancement,
    BRIGHTNESS_THRESHOLD,
    CONTRAST_THRESHOLD,
    BLUR_THRESHOLD,
    SHARPNESS_THRESHOLD,
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VIDEO_DIR = os.path.join(BASE_DIR, "data", "test_videos")
TEMP_DIR = os.path.join(BASE_DIR, "data", "validation_frames")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "validation_results")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


FRAME_SAMPLE_INTERVAL = 30
MAX_FRAMES_PER_VIDEO = 20


analyzer = ImageQualityAnalyzer()

video_files = [
    filename
    for filename in os.listdir(VIDEO_DIR)
    if filename.lower().endswith((".mp4", ".avi", ".mov", ".mkv"))
]

video_files.sort()

if not video_files:
    raise FileNotFoundError(f"No video files found in: {VIDEO_DIR}")


all_results = []
video_summaries = []


for video_name in video_files:
    video_path = os.path.join(VIDEO_DIR, video_name)

    print(f"\nProcessing: {video_name}")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Could not open {video_name}")
        continue

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"Total frames: {total_frames}")
    print(f"FPS: {fps:.2f}")

    frame_number = 0
    analyzed_count = 0

    brightness_values = []
    contrast_values = []
    blur_values = []
    sharpness_values = []

    brightness_flags = 0
    contrast_flags = 0
    blur_flags = 0
    sharpness_flags = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        if frame_number % FRAME_SAMPLE_INTERVAL == 0:
            temp_filename = (
                f"{os.path.splitext(video_name)[0]}"
                f"_frame_{frame_number:06d}.jpg"
            )

            temp_path = os.path.join(TEMP_DIR, temp_filename)

            cv2.imwrite(temp_path, frame)

            metrics = analyzer.analyze(temp_path)
            recommendations = recommend_enhancement(metrics)

            brightness = metrics["brightness"]
            contrast = metrics["contrast"]
            blur = metrics["blur"]
            sharpness = metrics["sharpness"]

            brightness_values.append(brightness)
            contrast_values.append(contrast)
            blur_values.append(blur)
            sharpness_values.append(sharpness)

            if brightness < BRIGHTNESS_THRESHOLD:
                brightness_flags += 1

            if contrast < CONTRAST_THRESHOLD:
                contrast_flags += 1

            if blur < BLUR_THRESHOLD:
                blur_flags += 1

            if sharpness < SHARPNESS_THRESHOLD:
                sharpness_flags += 1

            all_results.append({
                "video": video_name,
                "frame": frame_number,
                "brightness": brightness,
                "contrast": contrast,
                "blur": blur,
                "sharpness": sharpness,
                "recommendations": "; ".join(
                    recommendations["recommendations"]
                ),
            })

            analyzed_count += 1

            if analyzed_count >= MAX_FRAMES_PER_VIDEO:
                break

        frame_number += 1

    cap.release()

    if analyzed_count > 0:
        video_summaries.append({
            "video": video_name,
            "frames_analyzed": analyzed_count,
            "brightness_mean": round(
                statistics.mean(brightness_values), 2
            ),
            "contrast_mean": round(
                statistics.mean(contrast_values), 2
            ),
            "blur_mean": round(
                statistics.mean(blur_values), 2
            ),
            "sharpness_mean": round(
                statistics.mean(sharpness_values), 2
            ),
            "brightness_flags": brightness_flags,
            "contrast_flags": contrast_flags,
            "blur_flags": blur_flags,
            "sharpness_flags": sharpness_flags,
        })


results_path = os.path.join(
    OUTPUT_DIR,
    "image_quality_validation.csv"
)

with open(
    results_path,
    "w",
    newline="",
    encoding="utf-8"
) as csv_file:

    fieldnames = [
        "video",
        "frame",
        "brightness",
        "contrast",
        "blur",
        "sharpness",
        "recommendations",
    ]

    writer = csv.DictWriter(
        csv_file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(all_results)


summary_path = os.path.join(
    OUTPUT_DIR,
    "image_quality_video_summary.csv"
)

with open(
    summary_path,
    "w",
    newline="",
    encoding="utf-8"
) as csv_file:

    fieldnames = [
        "video",
        "frames_analyzed",
        "brightness_mean",
        "contrast_mean",
        "blur_mean",
        "sharpness_mean",
        "brightness_flags",
        "contrast_flags",
        "blur_flags",
        "sharpness_flags",
    ]

    writer = csv.DictWriter(
        csv_file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(video_summaries)


print("\nValidation summary")

for summary in video_summaries:
    print(f"\n{summary['video']}")
    print(f"Frames analyzed: {summary['frames_analyzed']}")
    print(f"Brightness flags: {summary['brightness_flags']}")
    print(f"Contrast flags: {summary['contrast_flags']}")
    print(f"Blur flags: {summary['blur_flags']}")
    print(f"Sharpness flags: {summary['sharpness_flags']}")


print("\nValidation complete.")
print(f"Detailed results: {results_path}")
print(f"Video summary: {summary_path}")