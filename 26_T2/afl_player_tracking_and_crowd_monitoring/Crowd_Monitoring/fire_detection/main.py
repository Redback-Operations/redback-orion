"""
fire_detector_color.py

Fire detection service using classic HSV color thresholding.
Handles fire detection only - crowd detection and stampede detection
are separate services.

Input: frame metadata JSON from Video Processing (video_id, video_path,
frame_width, frame_height, frames[]).

Output: detections JSON for Data Aggregation (video_id, detections[]),
each with frame_id, timestamp, camera_id, zone_id, fire_detected,
smoke_detected, confidence, severity, and bounding_box when fire is
detected.

camera_id/zone_id aren't in the frame metadata we get from Video
Processing, so they're passed in per-video by the caller (one video =
one fixed camera in one zone). If that changes we'll need to pull
them from a lookup table instead.

Uses HSV color thresholding to find red/orange/yellow blobs - no
model to load, runs fast, but prone to false positives (stage
lighting, orange signage, skin tones). Smoke detection is a rough
gray/low-saturation heuristic and isn't reliable; a trained model
would do much better here.
"""

import os
import json
import sys

import cv2
import numpy as np


# HSV range for fire-colored pixels (red/orange/yellow)
FIRE_LOWER_HSV = (0, 100, 150)
FIRE_UPPER_HSV = (35, 255, 255)
FIRE_MIN_AREA_PX = 800          # ignore blobs smaller than this

# smoke tends to be low-saturation gray/white; much less reliable
# than the fire color check
SMOKE_LOWER_HSV = (0, 0, 120)
SMOKE_UPPER_HSV = (180, 40, 220)
SMOKE_MIN_AREA_PX = 1500

# severity buckets - cutoffs picked by hand, retune once we have
# real footage to test against
SEVERITY_MEDIUM_CONF = 0.5
SEVERITY_HIGH_CONF = 0.8

# confidence reported when nothing is detected
NO_DETECTION_CONFIDENCE = 0.03


def _detect_fire_blobs(frame_bgr):
    """
    Returns a list of (x, y, w, h, area) boxes for fire-colored
    regions in the frame, sorted largest-first.
    """
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(FIRE_LOWER_HSV), np.array(FIRE_UPPER_HSV))

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for c in contours:
        area = cv2.contourArea(c)
        if area > FIRE_MIN_AREA_PX:
            x, y, w, h = cv2.boundingRect(c)
            boxes.append((x, y, w, h, area))

    boxes.sort(key=lambda b: b[4], reverse=True)
    return boxes


def _detect_smoke(frame_bgr):
    """
    Rough smoke check - looks for large low-saturation gray/white
    blobs. Not a reliable smoke detector; a real version would need
    optical flow or a trained model.
    """
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(SMOKE_LOWER_HSV), np.array(SMOKE_UPPER_HSV))

    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        if cv2.contourArea(c) > SMOKE_MIN_AREA_PX:
            return True
    return False


def _confidence_from_area(area, frame_area):
    """
    Converts a fire blob's pixel area into a confidence score -
    bigger blob relative to frame size = higher confidence. Not a
    calibrated probability, just a usable signal for Data
    Aggregation. Scaling factor picked by trial and error against
    sample footage.
    """
    ratio = area / frame_area
    confidence = min(0.3 + ratio * 20, 0.97)
    return round(confidence, 2)


def _severity_from_confidence(confidence):
    if confidence >= SEVERITY_HIGH_CONF:
        return "HIGH"
    elif confidence >= SEVERITY_MEDIUM_CONF:
        return "MEDIUM"
    else:
        return "LOW"


def process_frame(frame_bgr, frame_id, timestamp, camera_id, zone_id):
    """
    Runs the color-threshold fire detector on a single already-loaded
    frame (BGR numpy array) and returns one detection entry.
    """
    frame_area = frame_bgr.shape[0] * frame_bgr.shape[1]
    fire_boxes = _detect_fire_blobs(frame_bgr)

    if not fire_boxes:
        return {
            "frame_id": frame_id,
            "timestamp": timestamp,
            "camera_id": camera_id,
            "zone_id": zone_id,
            "fire_detected": False,
            "smoke_detected": False,
            "confidence": NO_DETECTION_CONFIDENCE,
            "severity": "NONE",
        }

    # only room for one bounding_box per detection, so take the
    # largest fire-colored blob
    x, y, w, h, area = fire_boxes[0]
    confidence = _confidence_from_area(area, frame_area)
    smoke = _detect_smoke(frame_bgr)

    return {
        "frame_id": frame_id,
        "timestamp": timestamp,
        "camera_id": camera_id,
        "zone_id": zone_id,
        "fire_detected": True,
        "smoke_detected": smoke,
        "confidence": confidence,
        "severity": _severity_from_confidence(confidence),
        "bounding_box": {
            "x": int(x),
            "y": int(y),
            "width": int(w),
            "height": int(h),
        },
    }


def process_video(frame_metadata, camera_id, zone_id):
    """
    Main entry point. Takes Video Processing output (already parsed
    into a dict) and returns the Fire Detection output dict, ready
    for Data Aggregation.
    """
    video_id = frame_metadata["video_id"]
    detections = []

    for frame_info in frame_metadata["frames"]:
        frame_path = frame_info["frame_path"]

        if not os.path.exists(frame_path):
            print(f"[fire_detector_color] WARNING: frame not found on disk: {frame_path}, skipping")
            continue

        frame_bgr = cv2.imread(frame_path)
        if frame_bgr is None:
            print(f"[fire_detector_color] WARNING: couldn't read frame: {frame_path}, skipping")
            continue

        detection = process_frame(
            frame_bgr,
            frame_id=frame_info["frame_id"],
            timestamp=frame_info["timestamp"],
            camera_id=camera_id,
            zone_id=zone_id,
        )
        detections.append(detection)

    return {
        "video_id": video_id,
        "detections": detections,
    }


def _build_sample_input(output_dir="output"):
    """
    Builds a small runnable demo: two synthetic frames (one plain,
    one with a bright orange patch) written to disk, plus the
    frame-metadata dict this service expects as input.
    """
    frames_dir = os.path.join(output_dir, "sample_frames")
    os.makedirs(frames_dir, exist_ok=True)

    frame1 = np.full((720, 1280, 3), 60, dtype=np.uint8)
    frame1_path = os.path.join(frames_dir, "frame_000001.jpg")
    cv2.imwrite(frame1_path, frame1)

    frame2 = frame1.copy()
    cv2.rectangle(frame2, (850, 320), (1030, 520), (0, 100, 255), -1)  # BGR orange
    frame2_path = os.path.join(frames_dir, "frame_000002.jpg")
    cv2.imwrite(frame2_path, frame2)

    return {
        "video_id": "DEMO_VID_001",
        "video_path": "demo_stadium_cam_02.mp4",
        "frame_width": 1280,
        "frame_height": 720,
        "frames": [
            {"frame_id": 1, "timestamp": 0.0, "frame_path": frame1_path},
            {"frame_id": 2, "timestamp": 1.0, "frame_path": frame2_path},
        ],
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No frame_metadata.json given - running built-in demo instead.")
        print("(Usage: python main.py <frame_metadata.json> [camera_id] [zone_id])")
        print()

        input_metadata = _build_sample_input()
        cam_id = "CAM_02"
        zone = "ZONE_B"
    else:
        with open(sys.argv[1]) as f:
            input_metadata = json.load(f)

        cam_id = sys.argv[2] if len(sys.argv) > 2 else "CAM_UNKNOWN"
        zone = sys.argv[3] if len(sys.argv) > 3 else "ZONE_UNKNOWN"

    output = process_video(input_metadata, camera_id=cam_id, zone_id=zone)
    print(json.dumps(output, indent=2))