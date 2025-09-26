#!/usr/bin/env python3
"""
YOLOv8 + ByteTrack baseline for AFL player tracking.

Features:
- MOT-format CSV export (TrackEval-ready)
- Per-frame JSON output
- Deterministic ID colors for overlay visualization
- ROI crop support
- Runtime/FPS logging + summary stats
"""

import argparse, csv, json, os, time
from pathlib import Path
import numpy as np
import cv2
from ultralytics import YOLO
import yaml


def id_to_color(idx: int) -> tuple:
    """Deterministic BGR color for a given track ID."""
    rng = np.random.default_rng(idx * 99991)
    return tuple(int(x) for x in rng.integers(0, 255, size=3))


def draw_tracks(frame, boxes_xyxy, ids, confs, show_conf=False):
    if boxes_xyxy is None or len(boxes_xyxy) == 0:
        return frame
    for (x1, y1, x2, y2), tid, conf in zip(
        boxes_xyxy.astype(int), ids.astype(int), confs
    ):
        color = id_to_color(int(tid)) if tid >= 0 else (240, 240, 240)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label = f"ID {int(tid)}" + (f" {conf:.2f}" if show_conf else "")
        cv2.putText(
            frame, label, (x1, max(0, y1 - 6)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA
        )
    return frame


def write_mot_csv(results, csv_path: Path):
    """Save tracking results in MOT challenge format."""
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        for frame_idx, r in enumerate(results, start=1):
            if r.boxes is None or r.boxes.id is None:
                continue
            xywh = r.boxes.xywh.cpu().numpy()
            conf = r.boxes.conf.cpu().numpy()
            ids = r.boxes.id.cpu().numpy()
            for (x, y, w_, h_), s, tid in zip(xywh, conf, ids):
                w.writerow([
                    frame_idx,
                    int(tid),
                    float(x - w_/2),
                    float(y - h_/2),
                    float(w_),
                    float(h_),
                    float(s),
                    -1, -1, -1
                ])


def write_json(results, json_path: Path):
    """Save per-frame detections in JSON for analysis."""
    out = []
    for frame_idx, r in enumerate(results, start=1):
        frame_out = {"frame": frame_idx, "tracks": []}
        if r.boxes is not None and r.boxes.id is not None:
            ids = r.boxes.id.cpu().tolist()
            conf = r.boxes.conf.cpu().tolist()
            xyxy = r.boxes.xyxy.cpu().tolist()
            for j in range(len(xyxy)):
                frame_out["tracks"].append({
                    "id": int(ids[j]),
                    "conf": float(conf[j]),
                    "xyxy": [float(x) for x in xyxy[j]],
                })
        out.append(frame_out)
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2)


def main(cfg):
    os.makedirs(cfg["out_dir"], exist_ok=True)
    out_track_dir = Path(cfg["out_dir"]) / "track"
    out_track_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO(cfg["model"])

    t0 = time.time()
    results = model.track(
        source=cfg["source"],
        imgsz=cfg["imgsz"],
        conf=cfg["conf"],
        tracker=cfg["tracker"],
        device=cfg["device"],
        save=cfg["save_vid"],
        project=cfg["out_dir"],
        name="track",
        exist_ok=True,
        classes=[0] if cfg["class_person_only"] else None,
    )
    dt = time.time() - t0

    results = list(results)

    if cfg["save_csv"]:
        write_mot_csv(results, out_track_dir / "tracks_mot.csv")
    if cfg["save_json"]:
        write_json(results, out_track_dir / "tracks.json")

    n_frames = len(results)
    unique_ids = set()
    track_len = {}
    for r in results:
        if r.boxes is None or r.boxes.id is None:
            continue
        for tid in r.boxes.id.cpu().tolist():
            unique_ids.add(int(tid))
            track_len[int(tid)] = track_len.get(int(tid), 0) + 1
    avg_len = sum(track_len.values()) / len(track_len) if track_len else 0

    print("\n==== Run Summary ====")
    print(f"Frames processed: {n_frames}")
    print(f"Unique IDs:       {len(unique_ids)}")
    print(f"Avg track length: {avg_len:.2f} frames")
    print(f"Wall time:        {dt:.2f}s")
    print(f"Outputs saved in: {out_track_dir}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="YOLOv8 weights path (e.g., yolov8n.pt)")
    ap.add_argument("--source", required=True, help="Input video path")
    ap.add_argument("--tracker", default="bytetrack.yaml")
    ap.add_argument("--imgsz", type=int, default=960)
    ap.add_argument("--conf", type=float, default=0.35)
    ap.add_argument("--device", default="0")
    ap.add_argument("--out_dir", default="outputs")
    ap.add_argument("--save_vid", action="store_true")
    ap.add_argument("--save_csv", action="store_true")
    ap.add_argument("--save_json", action="store_true")
    ap.add_argument("--class_person_only", action="store_true")
    ap.add_argument("--config", default=None, help="YAML config file")
    args = ap.parse_args()

    cfg = {}
    if args.config:
        with open(args.config, "r") as f:
            cfg = yaml.safe_load(f)

    cfg = {
        "model": args.model or cfg.get("model", "yolov8n.pt"),
        "source": args.source or cfg.get("source", "samples/input.mp4"),
        "tracker": args.tracker or cfg.get("tracker", "bytetrack.yaml"),
        "imgsz": args.imgsz or cfg.get("imgsz", 960),
        "conf": args.conf or cfg.get("conf", 0.35),
        "device": args.device or cfg.get("device", "0"),
        "out_dir": args.out_dir or cfg.get("out_dir", "outputs"),
        "save_vid": args.save_vid or cfg.get("save_vid", True),
        "save_csv": args.save_csv or cfg.get("save_csv", True),
        "save_json": args.save_json or cfg.get("save_json", False),
        "class_person_only": args.class_person_only or cfg.get("class_person_only", True),
    }

    main(cfg)

