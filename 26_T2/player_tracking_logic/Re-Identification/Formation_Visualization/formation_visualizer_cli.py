import cv2
import json
import math
import argparse


# ============================================================
# ARGUMENT PARSER
# ============================================================

parser = argparse.ArgumentParser(
    description="AFL Formation Visualizer"
)

parser.add_argument(
    "--input_video",
    type=str,
    required=True,
    help="Input AFL video path"
)

parser.add_argument(
    "--input_tracking",
    type=str,
    required=True,
    help="Clustered tracking JSON path"
)

parser.add_argument(
    "--output_video",
    type=str,
    default="formation_output.mp4",
    help="Output annotated video"
)

parser.add_argument(
    "--max_connection_distance",
    type=int,
    default=220,
    help="Maximum teammate connection distance"
)

parser.add_argument(
    "--k_nearest",
    type=int,
    default=3,
    help="Number of nearest teammates"
)

parser.add_argument(
    "--block_distance",
    type=int,
    default=35,
    help="Opponent blocking threshold"
)

parser.add_argument(
    "--crowd_radius",
    type=int,
    default=80,
    help="Crowd detection radius"
)

parser.add_argument(
    "--max_local_players",
    type=int,
    default=6,
    help="Maximum nearby players before suppression"
)

parser.add_argument(
    "--no_display",
    action="store_true",
    help="Disable live display window"
)

args = parser.parse_args()


# ============================================================
# CONFIG
# ============================================================

VIDEO_PATH = args.input_video

TRACKING_JSON = args.input_tracking

OUTPUT_VIDEO = args.output_video

MAX_CONNECTION_DISTANCE = args.max_connection_distance

K_NEAREST_TEAMMATES = args.k_nearest

BLOCK_DISTANCE_THRESHOLD = args.block_distance

CROWD_RADIUS = args.crowd_radius

MAX_LOCAL_PLAYERS = args.max_local_players


# ============================================================
# VISUAL CONFIG
# ============================================================

TEAM_1_OPEN = (255, 255, 255)

TEAM_1_BLOCKED = (180, 180, 180)

TEAM_2_OPEN = (0, 255, 0)

TEAM_2_BLOCKED = (0, 120, 0)

OPEN_LINE_THICKNESS = 5

BLOCKED_LINE_THICKNESS = 2

PLAYER_BOX_THICKNESS = 2


# ============================================================
# DISTANCE
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

print("===================================================")
print("FORMATION ANALYSIS STARTED")
print("===================================================")


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    ret, frame = cap.read()

    if not ret:
        break

    current_frame += 1

    annotated_frame = frame.copy()

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

        if not args.no_display:

            cv2.imshow(
                "Formation Analysis",
                annotated_frame
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        continue

    detections = frame_map[current_frame]

    # ========================================================
    # TEAM COLLECTION
    # ========================================================

    team_players = {
        "Team_1": [],
        "Team_2": []
    }

    all_positions = []

    for det in detections:

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
    # FORMATION DRAWING
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

        if team_name == "Team_1":

            open_colour = TEAM_1_OPEN

            blocked_colour = TEAM_1_BLOCKED

        else:

            open_colour = TEAM_2_OPEN

            blocked_colour = TEAM_2_BLOCKED

        for player in teammates:

            p1 = player["pos"]

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

            candidate_connections.sort(
                key=lambda x: x[0]
            )

            nearest_teammates = candidate_connections[
                :K_NEAREST_TEAMMATES
            ]

            for _, teammate in nearest_teammates:

                p2 = teammate["pos"]

                if is_crowded(p2, all_positions):
                    continue

                blocked = is_line_blocked(
                    p1,
                    p2,
                    opponent_positions
                )

                if blocked:

                    cv2.line(
                        annotated_frame,
                        p1,
                        p2,
                        blocked_colour,
                        BLOCKED_LINE_THICKNESS,
                        cv2.LINE_AA
                    )

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
    # OUTPUT
    # ========================================================

    out.write(annotated_frame)

    if not args.no_display:

        cv2.imshow(
            "Formation Analysis",
            annotated_frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # --------------------------------------------------------
    # PROGRESS
    # --------------------------------------------------------

    if current_frame % 100 == 0:

        print(
            f"Processed "
            f"{current_frame}/{total_frames} frames"
        )


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