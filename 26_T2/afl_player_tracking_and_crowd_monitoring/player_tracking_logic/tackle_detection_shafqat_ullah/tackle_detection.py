import argparse
import json
import logging
from pathlib import Path

import cv2
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

CONFIG = {
    "MIN_PLAYERS": 2,
    "MIN_INTERACTIONS": 20,
    "DENSITY_THRESHOLD": 1.20,
    "MAX_FRAME_GAP": 15,
    "MIN_EVENT_LENGTH": 5,

    # Focused tackle bbox settings
    "MAX_PLAYERS_IN_TACKLE_BOX": 4,
    "TACKLE_BOX_PADDING": 20,
    "DEFAULT_CLIP_DURATION": 40
}


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


# ============================================================
# LOAD TRACKING DATA
# ============================================================

def load_tracking_data(csv_path):
    df = pd.read_csv(csv_path)

    required_columns = [
        "frame_id",
        "player_id",
        "timestamps_s",
        "x1",
        "y1",
        "x2",
        "y2",
        "cx",
        "cy",
        "w",
        "h",
        "confidence"
    ]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if df.empty:
        raise ValueError("Tracking CSV is empty.")

    return df


# ============================================================
# DETECT CANDIDATE FRAMES
# ============================================================

def detect_candidate_frames(df):
    detected_frames = []

    for frame_id, group in df.groupby("frame_id"):
        players = len(group)

        if players < CONFIG["MIN_PLAYERS"]:
            continue

        x_min = group["x1"].min()
        y_min = group["y1"].min()
        x_max = group["x2"].max()
        y_max = group["y2"].max()

        width = max(x_max - x_min, 1)
        height = max(y_max - y_min, 1)
        area = width * height

        density_ratio = players / max(area / 100000, 1)
        cluster_score = players + int(density_ratio * 5)

        if (
            cluster_score >= CONFIG["MIN_INTERACTIONS"]
            and density_ratio >= CONFIG["DENSITY_THRESHOLD"]
        ):
            detected_frames.append({
                "frame_id": int(frame_id),
                "timestamps_s": float(group["timestamps_s"].iloc[0]),
                "cluster_score": int(cluster_score),
                "density_ratio": float(density_ratio),
                "players": int(players),
                "x_min": int(x_min),
                "y_min": int(y_min),
                "x_max": int(x_max),
                "y_max": int(y_max)
            })

    return pd.DataFrame(detected_frames)


# ============================================================
# GROUP EVENTS
# ============================================================

def group_events(filtered_df, fps):
    events = []

    if filtered_df.empty:
        return events

    frames = filtered_df["frame_id"].tolist()

    current_start = frames[0]
    previous_frame = frames[0]

    for frame in frames[1:]:
        if frame - previous_frame <= CONFIG["MAX_FRAME_GAP"]:
            previous_frame = frame
        else:
            duration = previous_frame - current_start + 1

            if duration >= CONFIG["MIN_EVENT_LENGTH"]:
                events.append({
                    "start_frame": current_start,
                    "end_frame": previous_frame
                })

            current_start = frame
            previous_frame = frame

    duration = previous_frame - current_start + 1

    if duration >= CONFIG["MIN_EVENT_LENGTH"]:
        events.append({
            "start_frame": current_start,
            "end_frame": previous_frame
        })

    final_events = []

    for idx, event in enumerate(events, start=1):
        start_frame = event["start_frame"]
        end_frame = event["end_frame"]
        duration_frames = end_frame - start_frame + 1

        final_events.append({
            "event_id": idx,
            "label": "tackle",
            "start_frame": int(start_frame),
            "end_frame": int(end_frame),
            "start_time_s": round(start_frame / fps, 3),
            "end_time_s": round(end_frame / fps, 3),
            "duration_frames": int(duration_frames),
            "duration_s": round(duration_frames / fps, 3)
        })

    return final_events


# ============================================================
# FOCUSED TACKLE BBOX + STRICT PLAYER ID LOGIC
# ============================================================

def get_peak_tackle_frame(frame_rows):
    peak_row = frame_rows.sort_values(
        by=["cluster_score", "density_ratio"],
        ascending=False
    ).iloc[0]

    return int(peak_row["frame_id"])


def get_players_inside_bbox(frame_df, bbox):
    inside_players = frame_df[
        (frame_df["cx"] >= bbox["x_min"])
        & (frame_df["cx"] <= bbox["x_max"])
        & (frame_df["cy"] >= bbox["y_min"])
        & (frame_df["cy"] <= bbox["y_max"])
    ]

    return inside_players.copy()


def build_focused_tackle_bbox(df, frame_rows):
    peak_frame = get_peak_tackle_frame(frame_rows)

    peak_players = df[df["frame_id"] == peak_frame].copy()

    if peak_players.empty:
        return {}, [], peak_frame

    cluster_row = frame_rows[frame_rows["frame_id"] == peak_frame].iloc[0]

    cluster_center_x = (
        int(cluster_row["x_min"]) + int(cluster_row["x_max"])
    ) / 2

    cluster_center_y = (
        int(cluster_row["y_min"]) + int(cluster_row["y_max"])
    ) / 2

    peak_players["distance_to_cluster"] = (
        (peak_players["cx"] - cluster_center_x) ** 2
        + (peak_players["cy"] - cluster_center_y) ** 2
    ) ** 0.5

    candidate_players = peak_players.sort_values(
        "distance_to_cluster"
    ).head(CONFIG["MAX_PLAYERS_IN_TACKLE_BOX"])

    padding = CONFIG["TACKLE_BOX_PADDING"]

    bbox = {
        "x_min": max(int(candidate_players["x1"].min()) - padding, 0),
        "y_min": max(int(candidate_players["y1"].min()) - padding, 0),
        "x_max": int(candidate_players["x2"].max()) + padding,
        "y_max": int(candidate_players["y2"].max()) + padding
    }

    # IMPORTANT FIX:
    # Player IDs are now taken ONLY from players whose centers are actually inside
    # the final displayed red bbox.
    players_inside_box = get_players_inside_bbox(peak_players, bbox)

    player_ids = players_inside_box["player_id"].astype(int).tolist()

    # Rebuild bbox using only verified players inside the box.
    # This prevents bbox and player IDs from disagreeing visually.
    if not players_inside_box.empty:
        bbox = {
            "x_min": max(int(players_inside_box["x1"].min()) - padding, 0),
            "y_min": max(int(players_inside_box["y1"].min()) - padding, 0),
            "x_max": int(players_inside_box["x2"].max()) + padding,
            "y_max": int(players_inside_box["y2"].max()) + padding
        }

        player_ids = players_inside_box["player_id"].astype(int).tolist()

    return bbox, player_ids, peak_frame


# ============================================================
# EXTRACT PLAYER INFORMATION
# ============================================================

def extract_players_for_event(df, start_frame, end_frame, selected_player_ids):
    event_df = df[
        (df["frame_id"] >= start_frame)
        & (df["frame_id"] <= end_frame)
        & (df["player_id"].isin(selected_player_ids))
    ]

    players_output = []

    for player_id in selected_player_ids:
        player_df = event_df[event_df["player_id"] == player_id]

        if player_df.empty:
            continue

        avg_bbox = {
            "x1": int(player_df["x1"].mean()),
            "y1": int(player_df["y1"].mean()),
            "x2": int(player_df["x2"].mean()),
            "y2": int(player_df["y2"].mean())
        }

        players_output.append({
            "player_id": int(player_id),
            "avg_bbox": avg_bbox,
            "frames_present": player_df["frame_id"].astype(int).tolist()
        })

    return players_output


# ============================================================
# BUILD FINAL JSON
# ============================================================

def build_json(events, df, filtered_df, video_name, fps):
    final_events = []

    for event in events:
        start_frame = event["start_frame"]
        end_frame = event["end_frame"]

        frame_rows = filtered_df[
            (filtered_df["frame_id"] >= start_frame)
            & (filtered_df["frame_id"] <= end_frame)
        ]

        if frame_rows.empty:
            continue

        tackle_bbox, player_ids, peak_frame = build_focused_tackle_bbox(
            df,
            frame_rows
        )

        players_involved = extract_players_for_event(
            df,
            start_frame,
            end_frame,
            player_ids
        )

        event_output = {
            **event,
            "peak_frame": int(peak_frame),
            "peak_time_s": round(peak_frame / fps, 3),
            "cluster_score": int(frame_rows["cluster_score"].max()),
            "density_ratio": round(float(frame_rows["density_ratio"].max()), 3),
            "players_detected": int(len(players_involved)),
            "player_ids": player_ids,
            "tackle_bbox": tackle_bbox,
            "players_involved": players_involved
        }

        final_events.append(event_output)

    return {
        "video_name": video_name,
        "fps": fps,
        "total_detected_events": len(final_events),
        "events": final_events
    }


# ============================================================
# SAVE JSON
# ============================================================

def save_json(data, output_path):
    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)

    logging.info(f"JSON saved: {output_path}")


# ============================================================
# SAVE CSV
# ============================================================

def save_csv(events_json, output_path):
    rows = []

    for event in events_json["events"]:
        rows.append({
            "event_id": event["event_id"],
            "label": event["label"],
            "start_frame": event["start_frame"],
            "end_frame": event["end_frame"],
            "peak_frame": event["peak_frame"],
            "start_time_s": event["start_time_s"],
            "end_time_s": event["end_time_s"],
            "peak_time_s": event["peak_time_s"],
            "players_detected": event["players_detected"],
            "player_ids": ",".join(map(str, event["player_ids"])),
            "cluster_score": event["cluster_score"],
            "density_ratio": event["density_ratio"]
        })

    pd.DataFrame(rows).to_csv(output_path, index=False)

    logging.info(f"CSV saved: {output_path}")


# ============================================================
# VIDEO HELPERS
# ============================================================

def get_video_properties(video_path):
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise ValueError("Could not open video.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    cap.release()

    return fps, width, height, total_frames


def calculate_clip_range(events_json, video_fps, total_frames, clip_duration):
    clip_frames = int(clip_duration * video_fps)

    if not events_json["events"]:
        start_frame = 0
    else:
        first_event_start = int(events_json["events"][0]["start_frame"])
        start_frame = max(first_event_start - int(5 * video_fps), 0)

    end_frame = min(start_frame + clip_frames, total_frames)

    return start_frame, end_frame


# ============================================================
# GENERATE OUTPUT VIDEO
# ============================================================

def generate_output_video(video_path, events_json, output_video, clip_duration):
    video_fps, width, height, total_frames = get_video_properties(video_path)

    start_clip_frame, end_clip_frame = calculate_clip_range(
        events_json,
        video_fps,
        total_frames,
        clip_duration
    )

    logging.info(
        f"Generating {clip_duration}-second output video "
        f"from frame {start_clip_frame} to {end_clip_frame}"
    )

    cap = cv2.VideoCapture(str(video_path))

    writer = cv2.VideoWriter(
        str(output_video),
        cv2.VideoWriter_fourcc(*"mp4v"),
        video_fps,
        (width, height)
    )

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_clip_frame)

    frame_id = start_clip_frame

    while frame_id < end_clip_frame:
        ret, frame = cap.read()

        if not ret:
            break

        for event in events_json["events"]:
            if event["start_frame"] <= frame_id <= event["end_frame"]:
                bbox = event["tackle_bbox"]

                if not bbox:
                    continue

                cv2.rectangle(
                    frame,
                    (bbox["x_min"], bbox["y_min"]),
                    (bbox["x_max"], bbox["y_max"]),
                    (0, 0, 255),
                    3
                )

                player_ids_text = ", ".join(
                    map(str, event.get("player_ids", []))
                )

                if not player_ids_text:
                    player_ids_text = "N/A"

                cv2.putText(
                    frame,
                    f"TACKLE #{event['event_id']}",
                    (40, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"Player IDs: {player_ids_text}",
                    (40, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"Peak Frame: {event['peak_frame']}",
                    (40, 125),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )

        writer.write(frame)
        frame_id += 1

    cap.release()
    writer.release()

    logging.info(f"Output video saved: {output_video}")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="AFL tackle detection pipeline"
    )

    parser.add_argument(
        "--tracking",
        required=True,
        help="Path to tracking CSV"
    )

    parser.add_argument(
        "--video",
        required=True,
        help="Path to input video"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output directory"
    )

    parser.add_argument(
        "--fps",
        type=float,
        default=29.97,
        help="Video FPS"
    )

    parser.add_argument(
        "--clip-duration",
        type=int,
        default=CONFIG["DEFAULT_CLIP_DURATION"],
        help="Output video duration in seconds"
    )

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    logging.info("Loading tracking data...")
    df = load_tracking_data(args.tracking)

    logging.info("Detecting candidate tackle frames...")
    filtered_df = detect_candidate_frames(df)

    logging.info(f"Detected {len(filtered_df)} filtered frames")

    logging.info("Grouping tackle events...")
    events = group_events(filtered_df, args.fps)

    logging.info(f"Final tackle events: {len(events)}")

    logging.info("Building JSON output...")
    final_json = build_json(
        events,
        df,
        filtered_df,
        Path(args.video).name,
        args.fps
    )

    json_path = output_dir / "tackle_events.json"
    save_json(final_json, json_path)

    csv_path = output_dir / "tackle_events.csv"
    save_csv(final_json, csv_path)

    video_output = output_dir / "tackle_detection_output_40s.mp4"

    logging.info("Generating focused 40-second output video...")
    generate_output_video(
        args.video,
        final_json,
        video_output,
        args.clip_duration
    )

    logging.info("Pipeline completed successfully.")


if __name__ == "__main__":
    main()