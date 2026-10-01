import cv2
import json
import csv
import math
import numpy as np

from collections import defaultdict, deque
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# ============================================================
# CONFIG
# ============================================================

VIDEO_PATH = "../afl_video.mp4"
TRACKING_JSON = "../afl_video_tracking.json"

OUTPUT_VIDEO = "clustered_output.mp4"
OUTPUT_JSON = "clustered_tracking.json"
OUTPUT_CSV = "player_metrics.csv"

PROCESS_EVERY_N_FRAMES = 2

MIN_BOX_WIDTH = 20
MIN_BOX_HEIGHT = 35

N_CLUSTERS = 3

TEAM_HISTORY_LENGTH = 15

DISPLAY_SCALE = 1.0

PIXEL_TO_METER = 0.02
MAX_SPEED_KMH = 40


# ============================================================
# GLOBALS
# ============================================================

player_feature_bank = defaultdict(list)

player_positions = {}
player_total_distance = {}
player_prev_speed = {}

team_history = defaultdict(lambda: deque(maxlen=TEAM_HISTORY_LENGTH))


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
# COLOUR RATIO
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
# LOAD TRACKING JSON
# ============================================================

print("Loading tracking JSON...")

with open(TRACKING_JSON, "r") as f:
    tracking_data = json.load(f)

frame_map = {}

for frame_data in tracking_data["tracking_results"]:

    frame_number = frame_data["frame_number"]

    frame_map[frame_number] = frame_data["players"]


# ============================================================
# PASS 1 - FEATURE EXTRACTION
# ============================================================

print("PASS 1 - Extracting colour features...")

cap = cv2.VideoCapture(VIDEO_PATH)

fps = cap.get(cv2.CAP_PROP_FPS)

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

current_frame = 0

while True:

    ret, frame = cap.read()

    if not ret:
        break

    current_frame += 1

    if current_frame % PROCESS_EVERY_N_FRAMES != 0:
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

        if box_w < MIN_BOX_WIDTH:
            continue

        if box_h < MIN_BOX_HEIGHT:
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

    # --------------------------------------------------------
    # LIVE STATUS
    # --------------------------------------------------------

    display = frame.copy()

    cv2.putText(
        display,
        f"PASS 1: Extracting Features",
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

print("Feature extraction complete.")


# ============================================================
# BUILD REPRESENTATIVE PLAYER FEATURES
# ============================================================

print("Building representative vectors...")

player_ids = []
representative_vectors = []

for player_id, features_list in player_feature_bank.items():

    if len(features_list) < 5:
        continue

    features_array = np.array(features_list)

    median_vector = np.median(features_array, axis=0)

    player_ids.append(player_id)

    representative_vectors.append(median_vector)

representative_vectors = np.array(representative_vectors)

print(f"Valid player tracks: {len(player_ids)}")


# ============================================================
# GLOBAL CLUSTERING
# ============================================================

print("Running global clustering...")

scaler = StandardScaler()

scaled_vectors = scaler.fit_transform(representative_vectors)

kmeans = KMeans(
    n_clusters=N_CLUSTERS,
    random_state=42,
    n_init=10
)

cluster_labels = kmeans.fit_predict(scaled_vectors)

print("Clustering complete.")


# ============================================================
# PLAYER -> TEAM MAPPING
# ============================================================

cluster_to_team = {
    0: "Team_1",
    1: "Team_2",
    2: "Umpire"
}

player_team_map = {}

for idx, player_id in enumerate(player_ids):

    cluster_id = int(cluster_labels[idx])

    team_name = cluster_to_team[cluster_id]

    player_team_map[player_id] = {
        "cluster_id": cluster_id,
        "team_name": team_name
    }


# ============================================================
# PASS 2 - FINAL VIDEO + JSON + CSV
# ============================================================

print("PASS 2 - Rendering final outputs...")

cap = cv2.VideoCapture(VIDEO_PATH)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

out = cv2.VideoWriter(
    OUTPUT_VIDEO,
    fourcc,
    fps,
    (width, height)
)

csv_file = open(OUTPUT_CSV, "w", newline="")

writer = csv.writer(csv_file)

writer.writerow([
    "frame",
    "player_id",
    "team",
    "x",
    "y",
    "speed_kmh",
    "distance_m",
    "total_distance_m"
])

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

            bbox = det["bbox"]

            x1 = bbox["x1"]
            y1 = bbox["y1"]
            x2 = bbox["x2"]
            y2 = bbox["y2"]

            cx = int((x1 + x2) / 2)
            cy = int(y2)

            if player_id not in player_team_map:
                continue

            team_name = player_team_map[player_id]["team_name"]

            # ------------------------------------------------
            # SPEED ESTIMATION
            # ------------------------------------------------

            if player_id in player_positions:

                prev_x, prev_y = player_positions[player_id]

                dist_pixels = math.sqrt(
                    (cx - prev_x) ** 2
                    +
                    (cy - prev_y) ** 2
                )

                dist_m = dist_pixels * PIXEL_TO_METER

                time_delta = 1 / fps

                speed_mps = dist_m / time_delta

                speed_kmh = speed_mps * 3.6

                if speed_kmh > MAX_SPEED_KMH:
                    speed_kmh = 0
                    dist_m = 0

                player_total_distance[player_id] = (
                    player_total_distance.get(player_id, 0)
                    +
                    dist_m
                )

            else:

                speed_kmh = 0
                dist_m = 0

                player_total_distance[player_id] = 0

            player_positions[player_id] = (cx, cy)

            # ------------------------------------------------
            # TEAM COLOURS
            # ------------------------------------------------

            if team_name == "Team_1":

                box_colour = (255, 255, 255)
                text_colour = (0, 0, 0)

            elif team_name == "Team_2":

                box_colour = (0, 0, 0)
                text_colour = (255, 255, 255)

            else:

                box_colour = (0, 255, 255)
                text_colour = (0, 0, 0)

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

            label = f"{team_name} ID:{player_id}"

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
                team_name,
                cx,
                cy,
                round(speed_kmh, 2),
                round(dist_m, 2),
                round(player_total_distance[player_id], 2)
            ])

            # ------------------------------------------------
            # JSON
            # ------------------------------------------------

            det["cluster_team"] = team_name

            frame_output["players"].append(det)

    final_tracking_results.append(frame_output)

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    cv2.putText(
        annotated_frame,
        f"PASS 2: Rendering Output",
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

    out.write(annotated_frame)

    cv2.imshow("Processing", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
out.release()

csv_file.close()

cv2.destroyAllWindows()


# ============================================================
# SAVE FINAL JSON
# ============================================================

final_output = {
    "video_info": tracking_data["video_info"],
    "tracking_results": final_tracking_results
}

with open(OUTPUT_JSON, "w") as f:

    json.dump(final_output, f, indent=2)

print("===================================================")
print("DONE")
print("===================================================")

print(f"Video: {OUTPUT_VIDEO}")
print(f"JSON: {OUTPUT_JSON}")
print(f"CSV: {OUTPUT_CSV}")