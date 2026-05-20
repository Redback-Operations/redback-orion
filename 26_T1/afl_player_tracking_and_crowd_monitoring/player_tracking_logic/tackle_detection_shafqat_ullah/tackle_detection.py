import pandas as pd
import numpy as np
import json

# =========================
# CONFIG (FINAL TUNED)
# =========================
INPUT_FILE = "afl_tracking_results(in).csv"
OUTPUT_CSV = "tackle_frames.csv"
OUTPUT_JSON = "tackle_events.json"

DIST_THRESHOLD = 100
MIN_INTERACTIONS = 8
MIN_PLAYERS = 4
DENSITY_THRESHOLD = 1.2
MIN_EVENT_LENGTH = 5
MAX_FRAME_GAP = 10   # NEW: allows merging small gaps


# =========================
# LOAD DATA
# =========================
df = pd.read_csv(INPUT_FILE)


# =========================
# FUNCTION: cluster score
# =========================
def cluster_score(group):
    players = group[["cx", "cy"]].values
    score = 0

    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            dist = np.linalg.norm(players[i] - players[j])
            if dist < DIST_THRESHOLD:
                score += 1

    return score


# =========================
# FUNCTION: group frames with GAP tolerance
# =========================
def group_frames(frames, max_gap=3):
    if not frames:
        return []

    frames = sorted(frames)
    grouped = []
    current = [frames[0]]

    for f in frames[1:]:
        if f <= current[-1] + max_gap:
            current.append(f)
        else:
            grouped.append(current)
            current = [f]

    grouped.append(current)
    return grouped


# =========================
# STEP 1: FRAME DETECTION
# =========================
results = []

for frame_id, group in df.groupby("frame_id"):

    num_players = group["player_id"].nunique()

    if num_players < MIN_PLAYERS:
        continue

    score = cluster_score(group)
    density_ratio = score / (num_players + 1)

    if score >= MIN_INTERACTIONS and density_ratio > DENSITY_THRESHOLD:

        x_min = group["x1"].min()
        y_min = group["y1"].min()
        x_max = group["x2"].max()
        y_max = group["y2"].max()

        timestamp = group["timestamps_s"].mean()

        results.append({
            "frame_id": int(frame_id),
            "timestamp_s": float(timestamp),
            "cluster_score": int(score),
            "density_ratio": float(density_ratio),
            "players": int(num_players),
            "x_min": float(x_min),
            "y_min": float(y_min),
            "x_max": float(x_max),
            "y_max": float(y_max)
        })


frame_df = pd.DataFrame(results)
frame_df.to_csv(OUTPUT_CSV, index=False)

print(f"\nDetected {len(frame_df)} filtered frames")
print(frame_df.head())


# =========================
# STEP 2: GROUP INTO EVENTS (with gap tolerance)
# =========================
tackle_frames = frame_df["frame_id"].tolist()
tackle_events = group_frames(tackle_frames, MAX_FRAME_GAP)


# =========================
# STEP 3: TEMPORAL FILTER
# =========================
filtered_events = []

for event in tackle_events:
    if len(event) >= MIN_EVENT_LENGTH:
        filtered_events.append(event)

print(f"\nEvents before filtering: {len(tackle_events)}")
print(f"Events after filtering: {len(filtered_events)}")


# =========================
# STEP 4: JSON OUTPUT
# =========================
events_output = []

for idx, event_frames in enumerate(filtered_events, start=1):

    event_group = df[df["frame_id"].isin(event_frames)]

    x_min = event_group["x1"].min()
    y_min = event_group["y1"].min()
    x_max = event_group["x2"].max()
    y_max = event_group["y2"].max()

    start_frame = event_frames[0]
    end_frame = event_frames[-1]

    start_time = event_group["timestamps_s"].min()
    end_time = event_group["timestamps_s"].max()

    avg_score = frame_df[frame_df["frame_id"].isin(event_frames)]["cluster_score"].mean()

    players_involved = event_group["player_id"].nunique()

    event_data = {
        "event_id": idx,
        "event_type": "multi_player_tackle",
        "start_frame": int(start_frame),
        "end_frame": int(end_frame),
        "start_time_s": float(start_time),
        "end_time_s": float(end_time),
        "duration_frames": int(end_frame - start_frame + 1),
        "players_involved": int(players_involved),
        "cluster_score": float(avg_score),
        "bounding_box": {
            "x_min": float(x_min),
            "y_min": float(y_min),
            "x_max": float(x_max),
            "y_max": float(y_max)
        },
        "confidence": round(min(avg_score / 15, 1.0), 2)
    }

    events_output.append(event_data)


final_output = {
    "video_id": "afl_tracking_sample",
    "events": events_output
}

with open(OUTPUT_JSON, "w") as f:
    json.dump(final_output, f, indent=4)


print("\nFinal Events:")
for e in events_output:
    print(f"Event {e['event_id']}: Frames {e['start_frame']} → {e['end_frame']}")