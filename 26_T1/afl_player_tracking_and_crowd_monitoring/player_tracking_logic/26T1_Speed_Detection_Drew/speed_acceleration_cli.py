"""
speed_acceleration_cli.py
=========================

SIT374 speed + acceleration pipeline.

Uses an existing tracking JSON, 
then adds:
- per-player speed
- acceleration
- distance
- total distance
- output video
- output CSV
- output JSON

Run:
python3 speed_acceleration_cli.py --input_video afl_video.mp4 --tracking_json clustered_tracking.json --output_folder outputs
"""

import argparse
import csv
import json
import math
import os
from collections import defaultdict, deque

import cv2
import numpy as np


def parse_bbox(bbox):
    if isinstance(bbox, dict):
        return (
            float(bbox["x1"]),
            float(bbox["y1"]),
            float(bbox["x2"]),
            float(bbox["y2"]),
        )

    return (
        float(bbox[0]),
        float(bbox[1]),
        float(bbox[2]),
        float(bbox[3]),
    )


def bbox_to_dict(x1, y1, x2, y2):
    return {
        "x1": int(round(x1)),
        "y1": int(round(y1)),
        "x2": int(round(x2)),
        "y2": int(round(y2)),
    }


class CentroidSmoother:
    def __init__(self, window):
        self.window = max(1, int(window))
        self.buffers = defaultdict(lambda: deque(maxlen=self.window))

    def push(self, player_id, x, y):
        self.buffers[player_id].append((x, y))
        xs, ys = zip(*self.buffers[player_id])
        return sum(xs) / len(xs), sum(ys) / len(ys)


def get_display_team(det):
    return det.get(
        "cluster_team",
        det.get(
            "team_name",
            det.get("team", "Unknown")
        )
    )


def get_box_colour(display_team):
    if display_team == "Team_1":
        return (255, 255, 255)

    if display_team == "Team_2":
        return (0, 0, 0)

    if display_team == "Umpire":
        return (0, 255, 255)

    if display_team in ("GCS", "GC"):
        return (0, 0, 255)

    if display_team in ("CAR", "Carlton"):
        return (255, 255, 255)

    return (180, 180, 180)


def run_pipeline(args):
    os.makedirs(args.output_folder, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(args.input_video))[0]

    output_video = os.path.join(args.output_folder, f"{base_name}_metrics.mp4")
    output_json = os.path.join(args.output_folder, f"{base_name}_metrics.json")
    output_csv = os.path.join(args.output_folder, f"{base_name}_metrics.csv")

    print("Loading tracking JSON...")

    with open(args.tracking_json, "r") as f:
        tracking_data = json.load(f)

    frame_map = {}
    frame_meta = {}

    for frame_data in tracking_data["tracking_results"]:
        frame_number = int(frame_data["frame_number"])
        frame_map[frame_number] = frame_data.get("players", [])

        meta = {
            k: v
            for k, v in frame_data.items()
            if k not in ("frame_number", "players")
        }

        if meta:
            frame_meta[frame_number] = meta

    print(f"Frames with tracking records: {len(frame_map)}")

    cap = cv2.VideoCapture(args.input_video)

    if not cap.isOpened():
        raise SystemExit(f"ERROR: cannot open video: {args.input_video}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dt = 1.0 / fps

    print(f"Video: {width}x{height} @ {fps:.2f} fps, {total_frames} frames")

    json_res = tracking_data.get("video_info", {}).get("resolution")

    if isinstance(json_res, (list, tuple)) and len(json_res) == 2:
        json_w = int(json_res[0])
        json_h = int(json_res[1])
        scale_x = width / json_w
        scale_y = height / json_h
    else:
        scale_x = 1.0
        scale_y = 1.0

    if abs(scale_x - 1.0) > 0.01 or abs(scale_y - 1.0) > 0.01:
        print(
            f"BBox scaling applied: tracking={json_w}x{json_h}, "
            f"video={width}x{height}, scale=({scale_x:.3f}, {scale_y:.3f})"
        )

    last_tracking_frame = max(frame_map.keys()) if frame_map else total_frames

    if args.max_frames:
        end_frame = min(args.max_frames, last_tracking_frame, total_frames)
    else:
        end_frame = min(last_tracking_frame, total_frames)

    print(f"Processing until frame: {end_frame}")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    csv_file = open(output_csv, "w", newline="")
    writer = csv.writer(csv_file)

    writer.writerow([
        "frame",
        "player_id",
        "display_team",
        "team_id",
        "team_name",
        "x",
        "y",
        "speed_mps",
        "speed_kmh",
        "accel_mps2",
        "distance_m",
        "total_distance_m",
    ])

    smoother = CentroidSmoother(args.smoothing_window)

    prev_position = {}
    prev_speed_mps = {}
    last_seen = {}

    player_total_distance = defaultdict(float)
    player_max_speed_kmh = defaultdict(float)
    player_max_accel = defaultdict(float)
    player_team_label = {}

    final_tracking_results = []

    current_frame = 0
    drawn = 0

    print("Rendering outputs...")

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        current_frame += 1

        if current_frame > end_frame:
            print(f"Reached end of available tracking data at frame {end_frame}.")
            break

        annotated = frame.copy()

        frame_output = {
            "frame_number": current_frame
        }

        frame_output.update(frame_meta.get(current_frame, {}))

        if "timestamp" not in frame_output:
            frame_output["timestamp"] = round(current_frame / fps, 4)

        frame_output["players"] = []

        detections = frame_map.get(current_frame, [])

        for det in detections:
            try:
                player_id = det["player_id"]
                rx1, ry1, rx2, ry2 = parse_bbox(det["bbox"])
            except (KeyError, ValueError, TypeError):
                continue

            x1 = rx1 * scale_x
            x2 = rx2 * scale_x
            y1 = ry1 * scale_y
            y2 = ry2 * scale_y

            cx_raw = (x1 + x2) / 2.0
            cy_raw = y2

            cx, cy = smoother.push(player_id, cx_raw, cy_raw)

            speed_clamped = False

            if player_id in prev_position:
                frames_since = current_frame - last_seen.get(
                    player_id,
                    current_frame - 1
                )

                if frames_since > 1:
                    speed_mps = 0.0
                    speed_kmh = 0.0
                    dist_m = 0.0
                    speed_clamped = True

                else:
                    px, py = prev_position[player_id]

                    dist_px = math.hypot(cx - px, cy - py)
                    dist_m = dist_px * args.pixel_to_meter

                    speed_mps = dist_m / dt
                    speed_kmh = speed_mps * 3.6

                    if speed_kmh > args.max_speed_kmh:
                        speed_mps = 0.0
                        speed_kmh = 0.0
                        dist_m = 0.0
                        speed_clamped = True

            else:
                speed_mps = 0.0
                speed_kmh = 0.0
                dist_m = 0.0
                speed_clamped = True

            if speed_clamped or player_id not in prev_speed_mps:
                accel_mps2 = 0.0
            else:
                accel_mps2 = (speed_mps - prev_speed_mps[player_id]) / dt

                if abs(accel_mps2) > args.max_accel_mps2:
                    accel_mps2 = 0.0

            prev_position[player_id] = (cx, cy)

            if not speed_clamped:
                prev_speed_mps[player_id] = speed_mps

            last_seen[player_id] = current_frame
            player_total_distance[player_id] += dist_m

            if speed_kmh > player_max_speed_kmh[player_id]:
                player_max_speed_kmh[player_id] = speed_kmh

            if abs(accel_mps2) > player_max_accel[player_id]:
                player_max_accel[player_id] = abs(accel_mps2)

            display_team = get_display_team(det)
            player_team_label[player_id] = display_team

            box_colour = get_box_colour(display_team)

            text_colour = (
                (0, 0, 0)
                if np.mean(box_colour) > 127
                else (255, 255, 255)
            )

            ix1, iy1, ix2, iy2 = int(x1), int(y1), int(x2), int(y2)

            cv2.rectangle(
                annotated,
                (ix1, iy1),
                (ix2, iy2),
                box_colour,
                2
            )

            label = f"{display_team} ID:{player_id} {speed_kmh:4.1f} km/h"

            cv2.putText(
                annotated,
                label,
                (ix1, max(0, iy1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                text_colour,
                2,
                cv2.LINE_AA,
            )

            drawn += 1

            writer.writerow([
                current_frame,
                player_id,
                display_team,
                det.get("team_id", ""),
                det.get("team_name", det.get("team", "")),
                round(cx, 2),
                round(cy, 2),
                round(speed_mps, 3),
                round(speed_kmh, 2),
                round(accel_mps2, 3),
                round(dist_m, 3),
                round(player_total_distance[player_id], 2),
            ])

            out_player = dict(det)

            out_player["bbox"] = bbox_to_dict(x1, y1, x2, y2)

            out_player["center"] = {
                "x": int(round(cx)),
                "y": int(round(cy))
            }

            out_player["display_team"] = display_team
            out_player["speed_mps"] = round(speed_mps, 3)
            out_player["speed_kmh"] = round(speed_kmh, 2)
            out_player["accel_mps2"] = round(accel_mps2, 3)
            out_player["distance_m"] = round(dist_m, 3)
            out_player["total_distance_m"] = round(
                player_total_distance[player_id],
                2
            )

            frame_output["players"].append(out_player)

        final_tracking_results.append(frame_output)

        cv2.putText(
            annotated,
            f"Frame {current_frame}/{end_frame}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        out.write(annotated)

        if not args.no_display:
            cv2.imshow("Speed + Acceleration", annotated)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("Interrupted by user.")
                break

        if current_frame % 500 == 0:
            print(f"Frame {current_frame}/{end_frame}, drawn so far: {drawn}")

    cap.release()
    out.release()
    csv_file.close()

    if not args.no_display:
        cv2.destroyAllWindows()

    video_info = dict(tracking_data.get("video_info", {}))

    video_info["fps"] = fps
    video_info["total_frames"] = total_frames
    video_info["resolution"] = [width, height]
    video_info["duration"] = round(total_frames / fps, 4) if fps else None
    video_info["frames_processed_by_speed_pipeline"] = len(final_tracking_results)
    video_info["processing_stopped_at_frame"] = current_frame

    final_output = {
        "video_info": video_info,
        "parameters": {
            "pixel_to_meter": args.pixel_to_meter,
            "smoothing_window": args.smoothing_window,
            "max_speed_kmh": args.max_speed_kmh,
            "max_accel_mps2": args.max_accel_mps2,
        },
        "player_summary": [
            {
                "player_id": pid,
                "display_team": player_team_label.get(pid, "Unknown"),
                "total_distance_m": round(player_total_distance[pid], 2),
                "max_speed_kmh": round(player_max_speed_kmh[pid], 2),
                "peak_accel_mps2": round(player_max_accel[pid], 2),
            }
            for pid in sorted(player_total_distance.keys(), key=lambda x: str(x))
        ],
        "tracking_results": final_tracking_results,
    }

    with open(output_json, "w") as f:
        json.dump(final_output, f, indent=2)

    print("\n================================================")
    print("DONE")
    print("================================================")
    print(f"Video : {output_video}")
    print(f"JSON  : {output_json}")
    print(f"CSV   : {output_csv}")
    print(f"Detections drawn : {drawn}")
    print(f"Players tracked  : {len(player_total_distance)}")


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "AFL per-player speed, acceleration and distance metrics. "
            "Consumes a tracking JSON and outputs video, CSV and JSON."
        )
    )

    parser.add_argument(
        "--input_video",
        required=True,
        help="Input video path."
    )

    parser.add_argument(
        "--tracking_json",
        required=True,
        help="Tracking JSON, preferably clustered_tracking.json."
    )

    parser.add_argument(
        "--output_folder",
        default="outputs",
        help="Output folder."
    )

    parser.add_argument(
        "--pixel_to_meter",
        type=float,
        default=0.02,
        help="Flat metres-per-pixel estimate."
    )

    parser.add_argument(
        "--smoothing_window",
        type=int,
        default=5,
        help="Moving average smoothing window."
    )

    parser.add_argument(
        "--max_speed_kmh",
        type=float,
        default=40.0,
        help="Clamp unrealistic speeds above this value."
    )

    parser.add_argument(
        "--max_accel_mps2",
        type=float,
        default=15.0,
        help="Clamp unrealistic acceleration above this value."
    )

    parser.add_argument(
        "--max_frames",
        type=int,
        default=0,
        help="Optional frame limit for testing."
    )

    parser.add_argument(
        "--no_display",
        action="store_true",
        help="Disable live OpenCV preview."
    )

    return parser.parse_args()


if __name__ == "__main__":
    run_pipeline(parse_args())