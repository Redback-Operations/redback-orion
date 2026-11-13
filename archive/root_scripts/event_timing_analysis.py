"""
Event Timing Analysis (Cumulative Only)
---------------------------------------
This script generates a single timeline graph showing the **cumulative count of AFL events**
across the duration of a clip. It helps visualize when events (kick, mark, tackle) occur 
relative to the clip length. 

Inputs:
  --events : Path to synced annotations CSV
  --out-dir: Directory to save results
  --fps    : Frames per second of the video (used to convert frames → seconds)

Outputs (saved in --out-dir):
  - cumulative_timeline.csv : Table of cumulative event counts over time
  - cumulative_timeline.png : Line graph showing cumulative counts
"""

import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def load_data(path: Path, fps: float) -> pd.DataFrame:
    df = pd.read_csv(path)

    # drop invalid/blank events
    df = df[df["event_name"].notna()]
    df = df[df["event_name"].str.lower() != "none"]

    # create time_s if missing
    if "time_s" not in df.columns:
        df["time_s"] = df["frame_id"] / fps

    return df

def cumulative_counts(df: pd.DataFrame, fps: float, clip_len: float):
    times = np.linspace(0, clip_len, int(clip_len * fps) + 1)
    cum = pd.DataFrame(index=times)
    for ev, g in df.groupby("event_name"):
        y, _ = np.histogram(g["time_s"], bins=times)
        y_cum = np.concatenate([[0], y.cumsum()])[: len(times)]
        cum[ev] = y_cum
    return cum

def plot_cumulative(cum: pd.DataFrame, out_dir: Path):
    plt.figure(figsize=(10,6))
    for col in cum.columns:
        plt.plot(cum.index, cum[col], label=col)
    plt.xlabel("Time (s)")
    plt.ylabel("Cumulative Events")
    plt.title("Cumulative Event Timeline")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "cumulative_timeline.png")
    plt.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", required=True, type=Path, help="Synced annotations CSV")
    ap.add_argument("--out-dir", required=True, type=Path, help="Output directory")
    ap.add_argument("--fps", required=True, type=float, help="Frames per second")
    args = ap.parse_args()

    df = load_data(args.events, args.fps)

    # detect clip length
    max_frame = df["frame_id"].max()
    clip_len = max_frame / args.fps
    print(f"Detected clip length: {clip_len:.2f} sec")

    # compute cumulative timeline
    cum = cumulative_counts(df, args.fps, clip_len)

    # save results
    args.out_dir.mkdir(parents=True, exist_ok=True)
    cum.to_csv(args.out_dir / "cumulative_timeline.csv")
    plot_cumulative(cum, args.out_dir)

    print(f"Saved cumulative timeline → {args.out_dir}")

if __name__ == "__main__":
    main()