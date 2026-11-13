# === annotation_converter.py ===
# Convert Basil's event annotations into a flat CSV
# Keeps "None" rows so we preserve full frame coverage

import argparse
import pandas as pd
import ast
from pathlib import Path

def parse_args():
    ap = argparse.ArgumentParser(description="Convert Basil annotation export into flat CSV")
    ap.add_argument("--in", dest="inp", required=True, help="Raw annotations CSV (export from Basil)")
    ap.add_argument("--out", dest="out", required=True, help="Output parsed CSV")
    return ap.parse_args()

def extract_event(cell):
    """
    Each 'annotations' cell contains a JSON-like string with event info.
    Example:
      "[{'result': [{'value': {'choices': ['Kick']}}]}]"
    """
    try:
        parsed = ast.literal_eval(cell)
        if isinstance(parsed, list) and parsed:
            res = parsed[0].get("result", [])
            if res:
                choices = res[0].get("value", {}).get("choices", [])
                if choices:
                    return choices[0].lower().strip()
    except Exception:
        return None
    return None

def main():
    args = parse_args()
    df = pd.read_csv(args.inp)

    if "annotations" not in df.columns or "data.image" not in df.columns:
        raise ValueError("Expected columns 'annotations' and 'data.image' in input file")

    # Extract event_name
    df["event_name"] = df["annotations"].apply(extract_event)

    # Ensure lowercase, and fill missing with "none"
    df["event_name"] = df["event_name"].fillna("none").astype(str)

    # Derive frame_id from filename
    df["frame_id"] = (
        df["data.image"]
        .str.extract(r"frame_(\d+)\.png")[0]
        .astype(int)
    )

    # Keep essential cols
    out_df = df[["frame_id", "event_name"]].sort_values("frame_id").reset_index(drop=True)

    # Save
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(args.out, index=False)
    print(f"✅ Parsed annotations with {len(out_df)} rows → {args.out}")

if __name__ == "__main__":
    main()
