import csv
from collections import defaultdict
from pathlib import Path


INPUT_FILE = Path("player_metrics.csv")


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def analyse_metrics(csv_path):
    players = defaultdict(lambda: {
        "team_counts": defaultdict(int),
        "frames": 0,
        "speed_sum": 0.0,
        "max_speed": 0.0,
        "max_total_distance": 0.0,
        "max_stamina": 0.0,
        "min_stamina": 100.0,
    })

    with csv_path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            player_id = row["player_id"]
            team = row["team"]

            speed = safe_float(row["speed_kmh"])
            total_distance = safe_float(row["total_distance_m"])
            stamina = safe_float(row["stamina"])

            player = players[player_id]

            player["frames"] += 1
            player["team_counts"][team] += 1
            player["speed_sum"] += speed
            player["max_speed"] = max(player["max_speed"], speed)
            player["max_total_distance"] = max(
                player["max_total_distance"],
                total_distance
            )
            player["max_stamina"] = max(player["max_stamina"], stamina)
            player["min_stamina"] = min(player["min_stamina"], stamina)

    return players


def get_primary_team(team_counts):
    if not team_counts:
        return "Unknown"

    return max(team_counts, key=team_counts.get)


def print_report(players):
    print()
    print("PLAYER TRACKING ANALYTICS")
    print("=" * 50)
    print(f"Unique player IDs tracked: {len(players)}")
    print()

    sorted_players = sorted(
        players.items(),
        key=lambda item: int(item[0])
    )

    for player_id, stats in sorted_players:
        frames = stats["frames"]

        average_speed = (
            stats["speed_sum"] / frames
            if frames > 0
            else 0.0
        )

        primary_team = get_primary_team(stats["team_counts"])

        print(f"Player ID: {player_id}")
        print(f"  Team: {primary_team}")
        print(f"  Frames tracked: {frames}")
        print(f"  Average speed: {average_speed:.2f} km/h")
        print(f"  Maximum speed: {stats['max_speed']:.2f} km/h")
        print(
            f"  Total distance: "
            f"{stats['max_total_distance']:.2f} m"
        )
        print(
            f"  Stamina range: "
            f"{stats['min_stamina']:.2f}% - "
            f"{stats['max_stamina']:.2f}%"
        )
        print("-" * 50)


def main():
    if not INPUT_FILE.exists():
        print(f"Could not find input file: {INPUT_FILE}")
        print(
            "Run player_tracker.py first so that "
            "player_metrics.csv is generated."
        )
        return

    players = analyse_metrics(INPUT_FILE)

    if not players:
        print("No player tracking data was found in the CSV.")
        return

    print_report(players)


if __name__ == "__main__":
    main()