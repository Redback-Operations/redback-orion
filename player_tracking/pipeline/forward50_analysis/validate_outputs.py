"""Check consistency and print concise validation statistics for a completed run."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def validate(output_dir: Path) -> None:
    player_path = output_dir / "player_positions.csv"
    occupancy_path = output_dir / "zone_occupancy.csv"
    players = list(csv.DictReader(player_path.open(encoding="utf-8")))
    occupancy = list(csv.DictReader(occupancy_path.open(encoding="utf-8")))
    by_frame: dict[str, list[dict]] = {}
    for row in players:
        by_frame.setdefault(row["frame"], []).append(row)

    mismatches = []
    for summary in occupancy:
        rows = by_frame.get(summary["frame"], [])
        actual_inside = sum(row["inside_forward50"].lower() == "true" for row in rows)
        if actual_inside != int(summary["total_inside_forward50"]):
            mismatches.append(summary["frame"])

    zones = Counter(row["zone"] for row in players)
    unique_ids = len({row["player_id"] for row in players})
    inside = sum(row["inside_forward50"].lower() == "true" for row in players)
    assigned = inside - zones["unassigned"]
    assignment_rate = assigned / inside if inside else 0.0

    print("Forward-50 output validation")
    print(f"Processed frames: {len(occupancy)}")
    print(f"Player detection rows: {len(players)}")
    print(f"Unique tracking IDs: {unique_ids}")
    print(f"Inside Forward 50: {inside}")
    print(f"Zone assignment rate: {assignment_rate:.2%}")
    print(f"Zone totals: {dict(zones)}")
    print(f"Frame total mismatches: {len(mismatches)}")
    if mismatches:
        raise SystemExit(f"Validation failed for frames: {mismatches[:10]}")
    print("VALIDATION PASSED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("output"))
    args = parser.parse_args()
    validate(args.output)

