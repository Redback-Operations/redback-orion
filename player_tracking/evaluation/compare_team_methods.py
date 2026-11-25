
"""Compare existing Orion player team-classification methods."""

import argparse
import csv
import sys

from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0, str(ROOT / "orion_player_tracking_studio")
)

from review_tool.core import read_tracking_csv
from review_tool.vision import extract_track_crops, suggest_teams


def read_ground_truth(path):
    """Load manually reviewed reference labels."""

    with path.open(encoding="utf-8-sig", newline="") as f:
        return {
            str(row["track_id"]).strip(): row["team"].strip()
            for row in csv.DictReader(f)
        }


def load_method_a(path):
    """Read existing Method A classification results."""

    predictions = {}

    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            track_id = str(row["player_id"]).strip()
            predictions[track_id] = row["cluster_label"]

    return predictions


def run_method_b(video_path, tracking_path, output_path):
    """Run the existing Studio team classification method."""

    rows = read_tracking_csv(tracking_path)

    class_names = {
        str(row.track_id): row.class_name
        for row in rows
    }

    crops = extract_track_crops(
        str(video_path),
        rows,
        str(output_path)
    )

    predictions = suggest_teams(crops, class_names)

    return {
        str(track_id): team
        for track_id, team in predictions.items()
    }


def majority_mapping(predictions, ground_truth):
    """Map predicted groups to majority reference labels."""

    votes = defaultdict(Counter)

    for track_id, actual_team in ground_truth.items():
        predicted_group = predictions.get(track_id)

        if predicted_group is not None:
            votes[predicted_group][actual_team] += 1

    mapping = {}

    for group, counts in votes.items():
        ranked = counts.most_common()

        # Do not assign an arbitrary label when votes are tied.
        if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
            continue

        mapping[group] = ranked[0][0]

    return mapping


def percentage(numerator, denominator):
    if denominator == 0:
        return "N/A"

    return f"{100 * numerator / denominator:.2f}%"


def evaluate_method(name, predictions, labels, include_umpires):
    """Evaluate accuracy, coverage and missing predictions."""

    eligible = {
        track_id: team
        for track_id, team in labels.items()
        if team.lower() not in {"unknown", "", "unverified"}
        and (include_umpires or team.lower() != "umpire")
    }

    mapping = majority_mapping(predictions, eligible)

    correct = 0
    classified = 0
    missing = 0

    print(f"\n{name}")
    print("-" * 60)
    print("Group mapping:", mapping)

    for track_id, actual in eligible.items():
        raw = predictions.get(track_id)

        if raw is None:
            missing += 1
            print(f"Track {track_id}: missing prediction")
            continue

        classified += 1
        predicted = mapping.get(raw)

        matched = predicted == actual

        if matched:
            correct += 1

        print(
            f"Track {track_id}: actual={actual}, "
            f"group={raw}, mapped={predicted}, "
            f"correct={matched}"
        )

    print("Eligible reference tracks:", len(eligible))
    print("Classified tracks:", classified)
    print("Correct predictions:", correct)
    print("Missing predictions:", missing)

    print(
        "Prediction coverage:",
        percentage(classified, len(eligible))
    )

    print(
        "Mapped agreement on classified tracks:",
        percentage(correct, classified)
    )

    print(
        "Mapped agreement including missing:",
        percentage(correct, len(eligible))
    )


def compare_clip(clip_name):
    """Compare both methods for one prepared clip."""

    video_path = ROOT / "data" / "videos" / f"{clip_name}.mp4"

    output_dir = ROOT / "outputs" / clip_name

    labels_path = (
        ROOT / "evaluation" / "team_labels"
        / f"{clip_name}.csv"
    )

    tracking_path = output_dir / "tracks.csv"

    method_a_path = (
        output_dir / "teams"
        / f"{clip_name}_metrics.csv"
    )

    required_files = [
        video_path,
        labels_path,
        tracking_path,
        method_a_path
    ]

    for path in required_files:
        if not path.is_file():
            raise FileNotFoundError(
                f"Required file not found: {path}"
            )

    labels = read_ground_truth(labels_path)

    method_a = load_method_a(method_a_path)

    method_b = run_method_b(
        video_path,
        tracking_path,
        output_dir / "studio_crops"
    )

    print("\n" + "=" * 60)
    print("CLIP:", clip_name)
    print("=" * 60)

    with tracking_path.open(
        encoding="utf-8-sig", newline=""
    ) as f:
        tracking_counts = Counter(
            row["track_id"] for row in csv.DictReader(f)
        )

    repeated_tracks = {
        track_id
        for track_id, count in tracking_counts.items()
        if count > 1
    }

    print("Unique tracks:", len(tracking_counts))
    print("Repeated-detection tracks:", len(repeated_tracks))

    print("\nRAW PREDICTIONS")

    for track_id in sorted(repeated_tracks, key=int):
        print(
            f"Track {track_id}: "
            f"reference={labels.get(track_id, 'unknown')}, "
            f"A={method_a.get(track_id, 'Missing')}, "
            f"B={method_b.get(track_id, 'Missing')}"
        )

    print("\nREPEATED-TRACK COVERAGE")

    for name, predictions in [
        ("Method A", method_a),
        ("Method B", method_b)
    ]:
        count = sum(
            track_id in predictions
            for track_id in repeated_tracks
        )

        print(
            f"{name}: {count}/{len(repeated_tracks)} "
            f"({percentage(count, len(repeated_tracks))})"
        )

    print("\nPLAYER-ONLY COMPARISON")

    evaluate_method(
        "Method A",
        method_a,
        labels,
        include_umpires=False
    )

    evaluate_method(
        "Method B",
        method_b,
        labels,
        include_umpires=False
    )

    print("\nMETHOD A INCLUDING UMPIRES")

    evaluate_method(
        "Method A",
        method_a,
        labels,
        include_umpires=True
    )

    print("\nUMPIRE HANDLING")

    for track_id, team in labels.items():
        if team.lower() == "umpire":
            print(
                f"Track {track_id}: "
                f"A={method_a.get(track_id, 'Missing')}, "
                f"B={method_b.get(track_id, 'Excluded')}"
            )

    unknown = [
        track_id
        for track_id, team in labels.items()
        if team.lower() in {"unknown", "", "unverified"}
    ]

    print("\nUnverified tracks excluded:", unknown)

    print(
        "Note: majority mapping and scoring use the same "
        "reference labels. These results are descriptive "
        "and do not establish generalisation accuracy."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Compare Orion team classification methods."
    )

    parser.add_argument(
        "clips",
        nargs="+",
        help="Prepared clip names without file extensions"
    )

    args = parser.parse_args()

    for clip in args.clips:
        compare_clip(clip)


if __name__ == "__main__":
    main()
