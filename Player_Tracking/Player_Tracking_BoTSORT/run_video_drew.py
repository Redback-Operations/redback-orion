import cv2
import numpy as np
import math
import csv
from collections import defaultdict, deque
from ultralytics import YOLO
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

VIDEO_PATH = "SF vs C.mov"
MODEL_PATH = "yolov8n.pt"
CONF_THRESHOLD = 0.30
TRACKER_CONFIG = "botsort.yaml"

RESIZE_WIDTH = 640
PROCESS_EVERY_N_FRAMES = 2
FRAME_DELAY_MULTIPLIER = 0.75

MIN_BOX_WIDTH = 25
MIN_BOX_HEIGHT = 50

PIXEL_TO_METER = 0.02
MAX_SPEED_KMH = 38

TEAM_HISTORY_LENGTH = 20
POSITION_HISTORY_LENGTH = 5

CLUSTER_SAMPLE_FRAMES = 250
MIN_CLUSTER_SAMPLES = 80

# 3 clusters = Team 1, Team 2, Umpire/Other
N_TEAM_CLUSTERS = 3

player_positions = {}
player_total_distance = {}
player_prev_speed = {}

team_history = defaultdict(lambda: deque(maxlen=TEAM_HISTORY_LENGTH))
position_history = defaultdict(lambda: deque(maxlen=POSITION_HISTORY_LENGTH))

colour_feature_samples = []
kmeans_model = None
scaler = None
clustering_ready = False


def get_torso_roi(frame, x1, y1, x2, y2):
    h, w = frame.shape[:2]

    x1, y1 = max(0, int(x1)), max(0, int(y1))
    x2, y2 = min(w, int(x2)), min(h, int(y2))

    if x2 <= x1 or y2 <= y1:
        return None

    box_w = x2 - x1
    box_h = y2 - y1

    # Only use torso area to avoid shorts, socks, grass and background
    rx1 = x1 + int(box_w * 0.25)
    rx2 = x1 + int(box_w * 0.75)
    ry1 = y1 + int(box_h * 0.20)
    ry2 = y1 + int(box_h * 0.55)

    roi = frame[ry1:ry2, rx1:rx2]

    if roi.size == 0:
        return None

    return roi


def colour_ratio(hsv, lower, upper):
    mask = cv2.inRange(hsv, lower, upper)
    area = hsv.shape[0] * hsv.shape[1]

    if area == 0:
        return 0

    return cv2.countNonZero(mask) / area


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

    red_ratio = colour_ratio(
        hsv,
        np.array([0, 70, 50]),
        np.array([10, 255, 255])
    ) + colour_ratio(
        hsv,
        np.array([170, 70, 50]),
        np.array([180, 255, 255])
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

    features = np.array([
        median_h,
        median_s,
        median_v,
        red_ratio,
        yellow_ratio,
        blue_ratio,
        white_ratio,
        dark_ratio
    ])

    return features


def classify_team(features):
    global kmeans_model, scaler, clustering_ready

    if features is None:
        return "Unknown"

    if not clustering_ready or kmeans_model is None or scaler is None:
        return "Unknown"

    scaled_features = scaler.transform([features])
    cluster_id = int(kmeans_model.predict(scaled_features)[0])

    if cluster_id == 0:
        return "Team_1"
    elif cluster_id == 1:
        return "Team_2"
    else:
        return "Umpire"


model = YOLO(MODEL_PATH)
cap = cv2.VideoCapture(VIDEO_PATH)

# Start video at 5 minutes
cap.set(cv2.CAP_PROP_POS_MSEC, 300 * 1000)

if not cap.isOpened():
    print(f"Could not open video: {VIDEO_PATH}")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
if fps <= 0:
    fps = 25

FRAME_DELAY = int((1000 / fps) * PROCESS_EVERY_N_FRAMES * FRAME_DELAY_MULTIPLIER)
FRAME_DELAY = max(1, FRAME_DELAY)

orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

scale = RESIZE_WIDTH / orig_width
width = RESIZE_WIDTH
height = int(orig_height * scale)

frame_number = 0
processed_count = 0

csv_file = open("player_metrics.csv", "w", newline="")
writer = csv.writer(csv_file)

writer.writerow([
    "frame",
    "player_id",
    "team",
    "x",
    "y",
    "speed_kmh",
    "acceleration_mps2",
    "distance_m",
    "total_distance_m",
    "stamina"
])

cv2.namedWindow("Live Tracking", cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    frame_number += 1

    if frame_number % PROCESS_EVERY_N_FRAMES != 0:
        continue

    frame = cv2.resize(frame, (width, height))

    results = model.track(
        frame,
        persist=True,
        tracker=TRACKER_CONFIG,
        conf=CONF_THRESHOLD,
        classes=[0],
        verbose=False
    )

    annotated_frame = frame.copy()
    boxes = results[0].boxes

    if boxes is not None and len(boxes) > 0:
        xyxy = boxes.xyxy.cpu().numpy()
        conf = boxes.conf.cpu().numpy()

        ids = (
            boxes.id.cpu().numpy().astype(int)
            if boxes.id is not None
            else np.arange(len(boxes)) + 1
        )

        # Collect colour samples for KMeans learning
        if not clustering_ready and processed_count < CLUSTER_SAMPLE_FRAMES:
            for i in range(len(boxes)):
                if conf[i] < CONF_THRESHOLD:
                    continue

                x1, y1, x2, y2 = xyxy[i]

                box_w = int(x2 - x1)
                box_h = int(y2 - y1)

                if box_w < MIN_BOX_WIDTH or box_h < MIN_BOX_HEIGHT:
                    continue

                features = extract_colour_features(frame, x1, y1, x2, y2)

                if features is not None:
                    colour_feature_samples.append(features)

        # Train KMeans after enough samples
        if (
            not clustering_ready
            and len(colour_feature_samples) >= MIN_CLUSTER_SAMPLES
            and processed_count >= CLUSTER_SAMPLE_FRAMES
        ):
            scaler = StandardScaler()
            scaled_samples = scaler.fit_transform(np.array(colour_feature_samples))

            kmeans_model = KMeans(
                n_clusters=N_TEAM_CLUSTERS,
                random_state=42,
                n_init=10
            )

            kmeans_model.fit(scaled_samples)
            clustering_ready = True
            print("Generic team and umpire clustering ready.")

        for i in range(len(boxes)):
            if conf[i] < CONF_THRESHOLD:
                continue

            x1, y1, x2, y2 = xyxy[i]
            track_id = int(ids[i])

            box_w = int(x2 - x1)
            box_h = int(y2 - y1)

            if box_w < MIN_BOX_WIDTH or box_h < MIN_BOX_HEIGHT:
                continue

            features = extract_colour_features(frame, x1, y1, x2, y2)

            raw_team_label = classify_team(features)

            if raw_team_label != "Unknown":
                team_history[track_id].append(raw_team_label)

            if len(team_history[track_id]) > 0:
                counts = {}

                for label in team_history[track_id]:
                    counts[label] = counts.get(label, 0) + 1

                team_label = max(counts, key=counts.get)
            else:
                team_label = "Unknown"

            if team_label == "Unknown":
                continue

            cx = int((x1 + x2) / 2)
            cy = int(y2)

            position_history[track_id].append((cx, cy))

            cx = int(sum(p[0] for p in position_history[track_id]) / len(position_history[track_id]))
            cy = int(sum(p[1] for p in position_history[track_id]) / len(position_history[track_id]))

            if track_id in player_positions:
                prev_x, prev_y = player_positions[track_id]

                dist_pixels = math.sqrt((cx - prev_x) ** 2 + (cy - prev_y) ** 2)
                dist_m = dist_pixels * PIXEL_TO_METER

                time_between_frames = PROCESS_EVERY_N_FRAMES / fps

                speed_mps = dist_m / time_between_frames
                speed_kmh = speed_mps * 3.6

                if speed_kmh > MAX_SPEED_KMH:
                    speed_mps = player_prev_speed.get(track_id, 0)
                    speed_kmh = speed_mps * 3.6
                    dist_m = 0

                player_total_distance[track_id] = (
                    player_total_distance.get(track_id, 0) + dist_m
                )

            else:
                dist_m = 0
                speed_mps = 0
                speed_kmh = 0
                player_total_distance[track_id] = 0

            player_positions[track_id] = (cx, cy)

            if track_id in player_prev_speed:
                acceleration = (
                    speed_mps - player_prev_speed[track_id]
                ) / (PROCESS_EVERY_N_FRAMES / fps)
            else:
                acceleration = 0

            player_prev_speed[track_id] = speed_mps

            stamina = max(0, 100 - (player_total_distance[track_id] * 0.5))

            writer.writerow([
                frame_number,
                track_id,
                team_label,
                cx,
                cy,
                round(speed_kmh, 2),
                round(acceleration, 2),
                round(dist_m, 2),
                round(player_total_distance[track_id], 2),
                round(stamina, 2)
            ])

            if team_label == "Umpire":
                box_colour = (0, 255, 255)
                text_colour = (0, 0, 0)
                label_bg_colour = (0, 255, 255)

            elif team_label == "Team_1":
                box_colour = (255, 255, 255)
                text_colour = (0, 0, 0)
                label_bg_colour = (255, 255, 255)

            else:
                box_colour = (0, 0, 0)
                text_colour = (255, 255, 255)
                label_bg_colour = (0, 0, 0)

            cv2.rectangle(
                annotated_frame,
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                box_colour,
                2
            )

            label = f"{team_label} ID:{track_id} | {speed_kmh:.1f} km/h"

            label_x = int(x1)
            label_y = max(25, int(y1) - 10)

            cv2.rectangle(
                annotated_frame,
                (label_x, label_y - 18),
                (label_x + 250, label_y + 5),
                label_bg_colour,
                -1
            )

            cv2.putText(
                annotated_frame,
                label,
                (label_x + 3, label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                text_colour,
                2
            )

    processed_count += 1

    if not clustering_ready:
        cv2.putText(
            annotated_frame,
            "Learning team and umpire colour profiles...",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

    cv2.imshow("Live Tracking", annotated_frame)

    if cv2.waitKey(FRAME_DELAY) & 0xFF == ord("q"):
        break

cap.release()
csv_file.close()
cv2.destroyAllWindows()

print("CSV saved as player_metrics.csv")