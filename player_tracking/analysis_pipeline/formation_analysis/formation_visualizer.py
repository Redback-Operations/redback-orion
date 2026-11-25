import cv2
import json
import math
import numpy as np


# ============================================================
# CONFIG
# ============================================================

VIDEO_PATH = "../afl_video.mp4"

TRACKING_JSON = "../JerseyColorDetection/clustered_tracking.json"

OUTPUT_VIDEO = "formation_analysis_output.mp4"


# ------------------------------------------------------------
# FORMATION CONFIG
# ------------------------------------------------------------

MAX_CONNECTION_DISTANCE = 220

K_NEAREST_TEAMMATES = 3

BLOCK_DISTANCE_THRESHOLD = 35

CROWD_RADIUS = 80

MAX_LOCAL_PLAYERS = 6


# ------------------------------------------------------------
# VISUAL CONFIG
# ------------------------------------------------------------

TEAM_1_OPEN = (255, 255, 255)
TEAM_1_BLOCKED = (180, 180, 180)

TEAM_2_OPEN = (0, 255, 0)
TEAM_2_BLOCKED = (0, 120, 0)

OPEN_LINE_THICKNESS = 5

BLOCKED_LINE_THICKNESS = 2

PLAYER_BOX_THICKNESS = 2


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def euclidean_distance(p1, p2):

    return math.sqrt(
        (p1[0] - p2[0]) ** 2
        +
        (p1[1] - p2[1]) ** 2
    )


# ============================================================
# POINT TO LINE DISTANCE
# ============================================================

def point_line_distance(point, line_start, line_end):

    px, py = point

    x1, y1 = line_start

    x2, y2 = line_end

    line_mag = euclidean_distance(
        line_start,
        line_end
    )

    if line_mag < 1:
        return 9999

    u = (
        (
            (px - x1) * (x2 - x1)
        )
        +
        (
            (py - y1) * (y2 - y1)
        )
    ) / (line_mag ** 2)

    # --------------------------------------------------------
    # projection outside line segment
    # --------------------------------------------------------

    if u < 0 or u > 1:
        return 9999

    ix = x1 + u * (x2 - x1)

    iy = y1 + u * (y2 - y1)

    return euclidean_distance(
        point,
        (ix, iy)
    )


# ============================================================
# CROWD DETECTION
# ============================================================

def is_crowded(player_pos, all_positions):

    nearby_count = 0

    for other_pos in all_positions:

        dist = euclidean_distance(
            player_pos,
            other_pos
        )

        if dist < CROWD_RADIUS:
            nearby_count += 1

    return nearby_count >= MAX_LOCAL_PLAYERS


# ============================================================
# BLOCK CHECK
# ============================================================

def is_line_blocked(
    start_pos,
    end_pos,
    opponent_positions
):

    for opp_pos in opponent_positions:

        dist = point_line_distance(
            opp_pos,
            start_pos,
            end_pos
        )

        if dist < BLOCK_DISTANCE_THRESHOLD:
            return True

    return False


# ============================================================
# LOAD JSON
# ============================================================

print("Loading tracking JSON...")

with open(TRACKING_JSON, "r") as f:

    tracking_data = json.load(f)

frame_map = {}

for frame_data in tracking_data["tracking_results"]:

    frame_number = frame_data["frame_number"]

    frame_map[frame_number] = frame_data["players"]


# ============================================================
# VIDEO SETUP
# ============================================================

cap = cv2.VideoCapture(VIDEO_PATH)

fps = cap.get(cv2.CAP_PROP_FPS)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

out = cv2.VideoWriter(
    OUTPUT_VIDEO,
    fourcc,
    fps,
    (width, height)
)

current_frame = 0

print("Starting formation analysis rendering...")


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    ret, frame = cap.read()

    if not ret:
        break

    current_frame += 1

    annotated_frame = frame.copy()

    # --------------------------------------------------------
    # STATUS TEXT
    # --------------------------------------------------------

    cv2.putText(
        annotated_frame,
        "FORMATION ANALYSIS",
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
        0.7,
        (255, 255, 255),
        2
    )

    if current_frame not in frame_map:

        out.write(annotated_frame)

        cv2.imshow("Formation Analysis", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        continue

    detections = frame_map[current_frame]

    # ========================================================
    # TEAM PLAYER COLLECTION
    # ========================================================

    team_players = {
        "Team_1": [],
        "Team_2": []
    }

    all_positions = []

    for det in detections:

        # ----------------------------------------------------
        # USE CLUSTER TEAM ONLY
        # ----------------------------------------------------

        if "cluster_team" not in det:
            continue

        team_name = det["cluster_team"]

        if team_name == "Umpire":
            continue

        if team_name not in team_players:
            continue

        player_id = det["player_id"]

        bbox = det["bbox"]

        x1 = int(bbox["x1"])
        y1 = int(bbox["y1"])
        x2 = int(bbox["x2"])
        y2 = int(bbox["y2"])

        cx = int((x1 + x2) / 2)

        cy = int(y2)

        player_data = {
            "player_id": player_id,
            "pos": (cx, cy),
            "bbox": (x1, y1, x2, y2)
        }

        team_players[team_name].append(player_data)

        all_positions.append((cx, cy))

    # ========================================================
    # DRAW PLAYER BOXES
    # ========================================================

    for team_name, players in team_players.items():

        for player in players:

            x1, y1, x2, y2 = player["bbox"]

            player_id = player["player_id"]

            if team_name == "Team_1":

                box_colour = TEAM_1_OPEN

                text_colour = (0, 0, 0)

            else:

                box_colour = TEAM_2_OPEN

                text_colour = (255, 255, 255)

            cv2.rectangle(
                annotated_frame,
                (x1, y1),
                (x2, y2),
                box_colour,
                PLAYER_BOX_THICKNESS
            )

            cv2.putText(
                annotated_frame,
                f"{team_name} ID:{player_id}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                text_colour,
                2
            )

    # ========================================================
    # FORMATION GRAPH DRAWING
    # ========================================================

    for team_name in ["Team_1", "Team_2"]:

        teammates = team_players[team_name]

        opponents = (
            team_players["Team_2"]
            if team_name == "Team_1"
            else team_players["Team_1"]
        )

        opponent_positions = [
            p["pos"]
            for p in opponents
        ]

        # ----------------------------------------------------
        # TEAM COLOUR CONFIG
        # ----------------------------------------------------

        if team_name == "Team_1":

            open_colour = TEAM_1_OPEN

            blocked_colour = TEAM_1_BLOCKED

        else:

            open_colour = TEAM_2_OPEN

            blocked_colour = TEAM_2_BLOCKED

        # ----------------------------------------------------
        # BUILD CONNECTIONS
        # ----------------------------------------------------

        for player in teammates:

            p1 = player["pos"]

            # ------------------------------------------------
            # CROWD SUPPRESSION
            # ------------------------------------------------

            if is_crowded(p1, all_positions):
                continue

            candidate_connections = []

            for other in teammates:

                if (
                    other["player_id"]
                    ==
                    player["player_id"]
                ):
                    continue

                p2 = other["pos"]

                dist = euclidean_distance(
                    p1,
                    p2
                )

                if dist < MAX_CONNECTION_DISTANCE:

                    candidate_connections.append(
                        (dist, other)
                    )

            # ------------------------------------------------
            # SORT NEAREST TEAMMATES
            # ------------------------------------------------

            candidate_connections.sort(
                key=lambda x: x[0]
            )

            nearest_teammates = candidate_connections[
                :K_NEAREST_TEAMMATES
            ]

            # ------------------------------------------------
            # DRAW CONNECTIONS
            # ------------------------------------------------

            for _, teammate in nearest_teammates:

                p2 = teammate["pos"]

                if is_crowded(p2, all_positions):
                    continue

                # --------------------------------------------
                # BLOCK CHECK
                # --------------------------------------------

                blocked = is_line_blocked(
                    p1,
                    p2,
                    opponent_positions
                )

                # --------------------------------------------
                # BLOCKED LINE
                # --------------------------------------------

                if blocked:

                    cv2.line(
                        annotated_frame,
                        p1,
                        p2,
                        blocked_colour,
                        BLOCKED_LINE_THICKNESS,
                        cv2.LINE_AA
                    )

                # --------------------------------------------
                # OPEN LINE
                # --------------------------------------------

                else:

                    cv2.line(
                        annotated_frame,
                        p1,
                        p2,
                        open_colour,
                        OPEN_LINE_THICKNESS,
                        cv2.LINE_AA
                    )

    # ========================================================
    # WRITE FRAME
    # ========================================================

    out.write(annotated_frame)

    cv2.imshow(
        "Formation Analysis",
        annotated_frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

out.release()

cv2.destroyAllWindows()

print("===================================================")

print("FORMATION ANALYSIS COMPLETE")

print("===================================================")

print(f"Output Video: {OUTPUT_VIDEO}")