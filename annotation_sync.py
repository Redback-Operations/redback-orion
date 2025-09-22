# === annotation_sync.py ===
# =============================================================================
# HOW TO RUN ANNOTATION SYNC
#
# Example: syncing Basil's events with Xuan's parsed tracking
#
# FULL dataset (all frames):
# python annotation_sync.py ^
#   --events data/events_annotations/parsed_event_annotation.csv ^
#   --track data/parsed_tracking.csv ^
#   --out data/synced_annotations/synced_annotations.csv ^
#   --report-dir data/synced_annotations --mode full
#
# EVENT-only dataset (only annotated events, skip "none"):
# python annotation_sync.py ^
#   --events data/events_annotations/parsed_event_annotation.csv ^
#   --track data/parsed_tracking.csv ^
#   --out data/synced_annotations/synced_annotations.csv ^
#   --report-dir data/synced_annotations --mode event
#
# Outputs:
#   - synced_annotations_full.csv   (all frames with tracking merged)
#   - synced_annotations_event.csv  (only annotated events)
#   - sync_summary.json             (match stats)
#   - unmatched_events.csv          (frames without matches)
# =============================================================================

import os, argparse, json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

# -------------------------
# CLI
# -------------------------
def parse_args():
    ap = argparse.ArgumentParser(description="Sync Basil events with Xuan tracking.")
    ap.add_argument("--events", required=True, help="Events CSV (from annotation_converter).")
    ap.add_argument("--track", required=True, help="Parsed tracking CSV (from convert_xuan_json).")
    ap.add_argument("--out", required=True, help="Output CSV base name.")
    ap.add_argument("--report-dir", required=True, help="Directory for reports.")
    ap.add_argument("--frame-window", type=int, default=2, help="± frames for nearest-frame recovery.")
    ap.add_argument("--mode", choices=["full", "event"], default="full",
                    help="Sync mode: 'full' keeps all frames, 'event' keeps only annotated events.")
    return ap.parse_args()

# -------------------------
# Load data
# -------------------------
def load_data(events_path, track_path):
    events_df = pd.read_csv(events_path)
    track_df = pd.read_csv(track_path)

    # enforce expected cols
    if "event_name" not in events_df.columns:
        raise ValueError("Events CSV must have 'event_name' column.")
    if "frame_id" not in events_df.columns:
        raise ValueError("Events CSV must have 'frame_id' column.")

    # normalise types
    events_df["frame_id"] = pd.to_numeric(events_df["frame_id"], errors="coerce").astype("Int64")
    events_df["event_name"] = events_df["event_name"].astype(str).str.lower().str.strip()

    for c in ["frame_id","player_id"]:
        if c in track_df.columns:
            track_df[c] = pd.to_numeric(track_df[c], errors="coerce").astype("Int64")

    return events_df, track_df

# -------------------------
# Sync annotations
# -------------------------
def sync(events_df, track_df, frame_window=2):
    # exact join on frame_id
    merged = events_df.merge(track_df, how="left", on="frame_id", suffixes=("_ev",""))
    exact_hits = merged["x1"].notna().sum()
    print(f"Exact matches: {exact_hits}/{len(events_df)}")

    # nearest frame recovery
    unmatched = merged[merged["x1"].isna()][["frame_id","event_name"]].copy()
    if unmatched.empty:
        return merged

    recovered = []
    grouped = dict(tuple(track_df.groupby("frame_id")))
    for _, row in unmatched.iterrows():
        f = int(row["frame_id"])
        best = None
        best_delta = None
        for d in range(-frame_window, frame_window+1):
            cand = grouped.get(f+d)
            if cand is None:
                continue
            pick = cand.sort_values("confidence", ascending=False).iloc[0].copy()
            delta = abs(d)
            if best is None or delta < best_delta:
                best = pick
                best_delta = delta
        if best is not None:
            r = {"frame_id": f, "event_name": row["event_name"]}
            for c in ["player_id","timestamp_s","x1","y1","x2","y2","cx","cy","w","h","confidence"]:
                r[c] = best.get(c, np.nan)
            r["frame_id_matched"] = best.get("frame_id", f)
            recovered.append(r)

    if recovered:
        rec_df = pd.DataFrame(recovered)
        merged = pd.concat([merged, rec_df], ignore_index=True)

    return merged

# -------------------------
# Summarize sync
# -------------------------
def summarize(events_df, synced_df, report_dir):
    Path(report_dir).mkdir(parents=True, exist_ok=True)

    total = len(events_df)
    # unique events matched at least once
    matched_events = synced_df.groupby(["frame_id", "event_name"])["x1"].apply(lambda x: x.notna().any())
    matched = matched_events.sum()
    unmatched = total - matched

    by_event = events_df["event_name"].value_counts().to_dict()

    print("\n====== Annotation Sync Summary ======")
    print(f"Events total          : {total}")
    print(f"Matched (with boxes)  : {matched}")
    print(f"Unmatched             : {unmatched}")

    # save unmatched list
    unmatched_df = synced_df[synced_df["x1"].isna()][["frame_id","event_name"]]
    unmatched_df.to_csv(Path(report_dir)/"unmatched_events.csv", index=False)

    # save summary json
    report_json = {
        "events_total": total,
        "matched": int(matched),
        "unmatched": int(unmatched),
        "by_event": by_event
    }
    with open(Path(report_dir)/"sync_summary.json", "w") as f:
        json.dump(report_json, f, indent=2)

    print(f"\n📄 Reports saved in {report_dir}")

# -------------------------
# Save outputs
# -------------------------
def save_outputs(synced_df, args):
    out_path = Path(args.out)
    if args.mode == "event":
        synced_df = synced_df[synced_df["event_name"] != "none"].copy()
        out_path = out_path.with_name("synced_annotations_event.csv")
    else:
        out_path = out_path.with_name("synced_annotations_full.csv")

    synced_df.to_csv(out_path, index=False)
    print(f"\n✅ Synced annotations saved → {out_path}")

# -------------------------
# Main
# -------------------------
def main():
    args = parse_args()
    events_df, track_df = load_data(args.events, args.track)
    synced_df = sync(events_df, track_df, frame_window=args.frame_window)
    summarize(events_df, synced_df, args.report_dir)
    save_outputs(synced_df, args)

if __name__ == "__main__":
    main()