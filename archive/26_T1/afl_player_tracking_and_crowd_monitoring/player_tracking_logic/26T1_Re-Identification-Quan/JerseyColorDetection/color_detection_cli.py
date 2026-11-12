import os
import cv2
import json
import csv
import math
import argparse
import numpy as np

from collections import defaultdict
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# ============================================================
# ROI EXTRACTION
# ============================================================

def get_torso_roi(frame, x1, y1, x2, y2):

    h, w = frame.shape[:2]

    x1 = max(0, int(x1))
    y1 = max(0, int(y1))
    x2 = min(w, int(x2))
    y2 = min(h, int(y2))

    if x2 <= x1 or y2 <= y1:
        return None

    box_w = x2 - x1
    box_h = y2 - y1

    rx1 = x1 + int(box_w * 0.25)
    rx2 = x1 + int(box_w * 0.75)

    ry1 = y1 + int(box_h * 0.20)
    ry2 = y1 + int(box_h * 0.55)

    roi = frame[ry1:ry2, rx1:rx2]

    if roi.size == 0:
        return None

    return roi


# ============================================================
# COLOUR HELPERS
# ============================================================

def colour_ratio(hsv, lower, upper):

    mask = cv2.inRange(hsv, lower, upper)

    area = hsv.shape[0] * hsv.shape[1]

    if area == 0:
        return 0

    return cv2.countNonZero(mask) / area


# ============================================================
# FEATURE EXTRACTION
# ============================================================

def extract_colour_features(frame, x1, y1, x2, y2):

    roi = get_torso_roi(frame, x1, y1, x2, y2)

    if roi is None:
        return None

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    h_channel, s_channel, v_channel = cv2.split(hsv)

    valid_mask = (s_channel > 35) & (v_channel > 35)

    valid_pixels = hsv[valid_mask]

    if len(valid_pixels) < 15:
        return None

    median_h = np.median(valid_pixels[:, 0])
    median_s = np.median(valid_pixels[:, 1])
    median_v = np.median(valid_pixels[:, 2])

    red_ratio = (
        colour_ratio(
            hsv,
            np.array([0, 70, 50]),
            np.array([10, 255, 255])
        )
        +
        colour_ratio(
            hsv,
            np.array([170, 70, 50]),
            np.array([180, 255, 255])
        )
    )

    yellow_ratio = colour_ratio(
        hsv,
        np.array([18, 80, 80]),
        np.array([48, 255, 255])
    )

    blue_ratio = colour_ratio(
        hsv,
        np.array([90, 40, 30]),
        np.array([140, 255, 180])
    )

    white_ratio = colour_ratio(
        hsv,
        np.array([0, 0, 160]),
        np.array([180, 65, 255])
    )

    dark_ratio = colour_ratio(
        hsv,
        np.array([0, 0, 0]),
        np.array([180, 255, 80])
    )

    return np.array([
        median_h,
        median_s,
        median_v,
        red_ratio,
        yellow_ratio,
        blue_ratio,
        white_ratio,
        dark_ratio
    ])


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline(args):

    # ========================================================
    # OUTPUT PATHS
    # ========================================================

    os.makedirs(args.output_folder, exist_ok=True)

    base_name = os.path.splitext(
        os.path.basename(args.input_video)
    )[0]

    output_video = os.path.join(
        args.output_folder,
        f"{base_name}_clustered.mp4"
    )

    output_json = os.path.join(
        args.output_folder,
        f"{base_name}_clustered.json"
    )

    output_csv = os.path.join(
        args.output_folder,
        f"{base_name}_metrics.csv"
    )

    # ========================================================
    # LOAD TRACKING JSON
    # ========================================================

    print("Loading tracking JSON...")

    with open(args.tracking_json, "r") as f:
        tracking_data = json.load(f)

    frame_map = {}

    for frame_data in tracking_data["tracking_results"]:

        frame_number = frame_data["frame_number"]

        frame_map[frame_number] = frame_data["players"]

    # ========================================================
    # PASS 1 - FEATURE EXTRACTION
    # ========================================================

    print("PASS 1 - Extracting features...")

    player_feature_bank = defaultdict(list)

    cap = cv2.VideoCapture(args.input_video)

    fps = cap.get(cv2.CAP_PROP_FPS)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    current_frame = 0

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        current_frame += 1

        if current_frame % args.process_every != 0:
            continue

        if current_frame not in frame_map:
            continue

        detections = frame_map[current_frame]

        for det in detections:

            player_id = det["player_id"]

            bbox = det["bbox"]

            x1 = bbox["x1"]
            y1 = bbox["y1"]
            x2 = bbox["x2"]
            y2 = bbox["y2"]

            box_w = x2 - x1
            box_h = y2 - y1

            if box_w < args.min_box_width:
                continue

            if box_h < args.min_box_height:
                continue

            features = extract_colour_features(
                frame,
                x1,
                y1,
                x2,
                y2
            )

            if features is not None:
                player_feature_bank[player_id].append(features)

        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        if not args.no_display:

            display = frame.copy()

            cv2.putText(
                display,
                f"PASS 1 - Feature Extraction",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2
            )

            cv2.putText(
                display,
                f"Frame: {current_frame}/{total_frames}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            cv2.putText(
                display,
                f"Tracks: {len(player_feature_bank)}",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            cv2.imshow("Processing", display)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()

    # ========================================================
    # REPRESENTATIVE FEATURES
    # ========================================================

    print("Building representative vectors...")

    player_ids = []
    representative_vectors = []

    for player_id, features_list in player_feature_bank.items():

        if len(features_list) < args.min_samples_per_track:
            continue

        median_vector = np.median(
            np.array(features_list),
            axis=0
        )

        player_ids.append(player_id)

        representative_vectors.append(median_vector)

    representative_vectors = np.array(representative_vectors)

    print(f"Valid tracks: {len(player_ids)}")

    # ========================================================
    # CLUSTERING
    # ========================================================

    print("Running KMeans clustering...")

    scaler = StandardScaler()

    scaled_vectors = scaler.fit_transform(
        representative_vectors
    )

    kmeans = KMeans(
        n_clusters=args.clusters,
        random_state=42,
        n_init=10
    )

    cluster_labels = kmeans.fit_predict(
        scaled_vectors
    )

    player_cluster_map = {}

    for idx, player_id in enumerate(player_ids):

        cluster_id = int(cluster_labels[idx])

        player_cluster_map[player_id] = {
            "cluster_id": cluster_id,
            "cluster_label": f"Cluster_{cluster_id}"
        }

    print("Clustering complete.")

    # ========================================================
    # PASS 2 - OUTPUT RENDERING
    # ========================================================

    print("PASS 2 - Rendering outputs...")

    cap = cv2.VideoCapture(args.input_video)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    out = cv2.VideoWriter(
        output_video,
        fourcc,
        fps,
        (width, height)
    )

    csv_file = open(output_csv, "w", newline="")

    writer = csv.writer(csv_file)

    writer.writerow([
        "frame",
        "player_id",
        "cluster_id",
        "cluster_label",
        "x",
        "y",
        "speed_kmh",
        "distance_m",
        "total_distance_m"
    ])

    player_positions = {}
    player_total_distance = {}

    final_tracking_results = []

    current_frame = 0

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        current_frame += 1

        annotated_frame = frame.copy()

        frame_output = {
            "frame_number": current_frame,
            "players": []
        }

        if current_frame in frame_map:

            detections = frame_map[current_frame]

            for det in detections:

                player_id = det["player_id"]

                if player_id not in player_cluster_map:
                    continue

                bbox = det["bbox"]

                x1 = bbox["x1"]
                y1 = bbox["y1"]
                x2 = bbox["x2"]
                y2 = bbox["y2"]

                cx = int((x1 + x2) / 2)
                cy = int(y2)

                cluster_id = player_cluster_map[player_id]["cluster_id"]

                cluster_label = player_cluster_map[player_id]["cluster_label"]

                # ------------------------------------------------
                # SPEED
                # ------------------------------------------------

                if player_id in player_positions:

                    prev_x, prev_y = player_positions[player_id]

                    dist_pixels = math.sqrt(
                        (cx - prev_x) ** 2
                        +
                        (cy - prev_y) ** 2
                    )

                    dist_m = dist_pixels * args.pixel_to_meter

                    speed_kmh = (
                        dist_m * fps * 3.6
                    )

                    if speed_kmh > args.max_speed_kmh:
                        speed_kmh = 0
                        dist_m = 0

                    player_total_distance[player_id] += dist_m

                else:

                    speed_kmh = 0
                    dist_m = 0

                    player_total_distance[player_id] = 0

                player_positions[player_id] = (cx, cy)

                # ------------------------------------------------
                # COLOURS
                # ------------------------------------------------

                colours = [
                    (255, 255, 255),
                    (0, 0, 0),
                    (0, 255, 255),
                    (255, 0, 0),
                    (0, 255, 0),
                    (0, 0, 255)
                ]

                box_colour = colours[
                    cluster_id % len(colours)
                ]

                text_colour = (
                    0,
                    0,
                    0
                ) if np.mean(box_colour) > 127 else (
                    255,
                    255,
                    255
                )

                # ------------------------------------------------
                # DRAW
                # ------------------------------------------------

                cv2.rectangle(
                    annotated_frame,
                    (x1, y1),
                    (x2, y2),
                    box_colour,
                    2
                )

                label = (
                    f"{cluster_label} "
                    f"ID:{player_id}"
                )

                cv2.putText(
                    annotated_frame,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    text_colour,
                    2
                )

                # ------------------------------------------------
                # CSV
                # ------------------------------------------------

                writer.writerow([
                    current_frame,
                    player_id,
                    cluster_id,
                    cluster_label,
                    cx,
                    cy,
                    round(speed_kmh, 2),
                    round(dist_m, 2),
                    round(player_total_distance[player_id], 2)
                ])

                # ------------------------------------------------
                # JSON
                # ------------------------------------------------

                clean_player = {
                    "player_id": player_id,

                    "cluster_id": cluster_id,

                    "cluster_label": cluster_label,

                    "bbox": bbox,

                    "center": {
                        "x": cx,
                        "y": cy
                    }
                }

                frame_output["players"].append(
                    clean_player
                )

        final_tracking_results.append(frame_output)

        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        if not args.no_display:

            cv2.putText(
                annotated_frame,
                "PASS 2 - Rendering Output",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2
            )

            cv2.putText(
                annotated_frame,
                f"Frame: {current_frame}/{total_frames}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "Processing",
                annotated_frame
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        out.write(annotated_frame)

    cap.release()
    out.release()

    csv_file.close()

    cv2.destroyAllWindows()

    # ========================================================
    # SAVE JSON
    # ========================================================

    final_output = {
        "video_info": tracking_data["video_info"],
        "tracking_results": final_tracking_results
    }

    with open(output_json, "w") as f:
        json.dump(final_output, f, indent=2)

    print("\n================================================")
    print("DONE")
    print("================================================")

    print(f"Video : {output_video}")
    print(f"JSON  : {output_json}")
    print(f"CSV   : {output_csv}")


# ============================================================
# CLI
# ============================================================

def parse_args():

    parser = argparse.ArgumentParser(
        description="Offline Jersey Colour Clustering"
    )

    parser.add_argument(
        "--input_video",
        required=True,
        help="Input video path"
    )

    parser.add_argument(
        "--tracking_json",
        required=True,
        help="Tracking JSON path"
    )

    parser.add_argument(
        "--output_folder",
        default="outputs",
        help="Output folder"
    )

    parser.add_argument(
        "--clusters",
        type=int,
        default=3,
        help="Number of KMeans clusters"
    )

    parser.add_argument(
        "--process_every",
        type=int,
        default=2,
        help="Process every N frames"
    )

    parser.add_argument(
        "--min_box_width",
        type=int,
        default=20
    )

    parser.add_argument(
        "--min_box_height",
        type=int,
        default=35
    )

    parser.add_argument(
        "--min_samples_per_track",
        type=int,
        default=5
    )

    parser.add_argument(
        "--pixel_to_meter",
        type=float,
        default=0.02
    )

    parser.add_argument(
        "--max_speed_kmh",
        type=float,
        default=40
    )

    parser.add_argument(
        "--no_display",
        action="store_true",
        help="Disable live display"
    )

    return parser.parse_args()


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":

    args = parse_args()

    run_pipeline(args)