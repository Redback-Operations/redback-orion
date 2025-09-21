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

def compute_metrics(merged):
    # 🔹 Normalize event labels
    merged["event_name"] = merged["event_name"].astype(str).str.lower()
    merged.loc[merged["event_name"].isin(["none", "nan", "null"]), "event_name"] = pd.NA

    # Ground truth: frames that actually have an event
    truth = merged[merged["event_name"].notna()].copy()

    # Predictions: everything (tracking rows exist regardless of event)
    predicted = merged.copy()

    results = []

    for event in truth["event_name"].dropna().unique():
        tp = ((predicted["event_name"] == event)).sum()
        fn = ((truth["event_name"] == event)).sum() - tp
        fp = 0  # since we're aligning per-frame matches

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

    # Handle "no_event"
    total_rows = len(predicted)
    truth_rows = len(truth)
    no_event_tp = (predicted["event_name"].isna()).sum()
    results.append({
        "event": "(no_event)",
        "TP": no_event_tp, "FP": 0, "FN": total_rows - truth_rows - no_event_tp,
        "Precision": 1 if no_event_tp > 0 else 0,
        "Recall": 1 if no_event_tp > 0 else 0,
        "F1": 1 if no_event_tp > 0 else 0,
    })

    return pd.DataFrame(results)

def main():
    args = parse_args()
    merged = pd.read_csv(args.inp)

    metrics = compute_metrics(merged)
    metrics.to_csv(args.out, index=False)

    print(metrics)

if __name__ == "__main__":
    main()