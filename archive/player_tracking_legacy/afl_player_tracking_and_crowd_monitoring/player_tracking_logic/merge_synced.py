# === merge_synced.py ===
# =============================================================================
# HOW TO RUN MERGE SYNCED DATASETS
#
# Example: combining synced annotations for kick, mark, and tackle
#
# 1. Ensure you have:
#    - kick_synced_annotations.csv
#    - mark_synced_annotations.csv
#    - tackle_synced_annotations.csv
#
# 2. Run in terminal from project root:
#    python merge_synced.py \
#        --inputs data/kick/kick_synced_annotations.csv \
#                data/mark/mark_synced_annotations.csv \
#                data/tackle/tackle_synced_annotations.csv \
#        --out merged_dataset.csv
#
# The script will produce:
#    - merged_dataset.csv (with a source_file column tagging the origin)
# =============================================================================

import argparse
import pandas as pd
import os

# ---- ARGUMENT PARSING ----
def parse_args():
    ap = argparse.ArgumentParser(
        description="Merge multiple synced annotation CSVs into one dataset."
    )
    ap.add_argument("--inputs", nargs="+", required=True,
        help="List of synced annotation CSVs (kick, mark, tackle).")
    ap.add_argument("--out", required=True,
        help="Output merged CSV path.")
    return ap.parse_args()

# ---- MAIN ----
def main():
    args = parse_args()

    dfs = []
    for path in args.inputs:
        if not os.path.exists(path):
            print(f"Missing file: {path}")
            continue
        df = pd.read_csv(path)
        df["source_file"] = os.path.basename(path)  # tag origin of each row
        dfs.append(df)

    if not dfs:
        print("⚠️ No input files found. Exiting.")
        return

    # Concatenate inputs
    merged = pd.concat(dfs, ignore_index=True)

    # Ensure consistent columns
    keep_cols = [
        "event_name","frame_id","player_id","timestamp_s",
        "x1","y1","x2","y2","cx","cy","w","h",
        "confidence","frame_id_matched","source_file"
    ]
    for c in keep_cols:
        if c not in merged.columns:
            merged[c] = pd.NA
    merged = merged[keep_cols]

    # Sort by frame/player/event
    merged = merged.sort_values(
        ["frame_id","player_id","event_name"]
    ).reset_index(drop=True)

    # Save merged dataset
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    merged.to_csv(args.out, index=False)

    print(f"Merged dataset saved → {args.out}")
    print(merged.head(10))

if __name__ == "__main__":
    main()
