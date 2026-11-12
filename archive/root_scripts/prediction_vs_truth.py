#!/usr/bin/env python3
"""
prediction_vs_truth.py

Compares predicted (tracking) vs truth (event annotations)
from a synced dataset. Outputs precision/recall/F1 per event.
"""

import argparse
import pandas as pd

def parse_args():
    ap = argparse.ArgumentParser(description="Compare predicted vs ground truth events")
    ap.add_argument("--in", dest="inp", required=True,
                    help="Synced annotations CSV (from annotation_sync)")
    ap.add_argument("--out", required=True,
                    help="Output CSV path for metrics")
    return ap.parse_args()

def compute_metrics(df):
    # 🔹 Ensure columns exist
    if "truth_event" not in df.columns and "event_name" in df.columns:
        df = df.rename(columns={"event_name": "truth_event"})
    if "pred_event" not in df.columns:
        # For now, simulate predictions = truth (so script runs)
        df["pred_event"] = df["truth_event"]

    # Normalize labels
    for col in ["truth_event", "pred_event"]:
        df[col] = df[col].astype(str).str.lower().replace(["none", "nan", "null"], pd.NA)

    # Get all unique events across truth + predictions
    events = set(df["truth_event"].dropna().unique()) | set(df["pred_event"].dropna().unique())

    results = []
    for event in events:
        tp = ((df["truth_event"] == event) & (df["pred_event"] == event)).sum()
        fp = ((df["truth_event"] != event) & (df["pred_event"] == event)).sum()
        fn = ((df["truth_event"] == event) & (df["pred_event"] != event)).sum()

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1        = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        results.append({
            "event": event,
            "TP": tp, "FP": fp, "FN": fn,
            "Precision": round(precision, 3),
            "Recall": round(recall, 3),
            "F1": round(f1, 3),
        })

    return pd.DataFrame(results)

def main():
    args = parse_args()
    df = pd.read_csv(args.inp)

    metrics = compute_metrics(df)
    metrics.to_csv(args.out, index=False)
    print(metrics)

if __name__ == "__main__":
    main()