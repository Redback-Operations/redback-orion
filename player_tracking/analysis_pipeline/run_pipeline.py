#!/usr/bin/env python3
"""Run the whole player tracking pipeline on one video.

Tracks players once, then runs every analytics stage on those tracks and
writes everything to outputs/<video name>/:

    tracks.csv, tracks.mp4     stage 1: every player in every frame
    tracking.json              the same tracks in the JSON shape /tracking returns
    players.csv                one row per player per frame, for the T1 analytics
    teams/                     team from jumper colour (identify_players)
    movement/                  speed and distance per player, trajectory video
    tackles.json               tackle events
    workload.json, heatmaps/   distance, high-speed running, heatmaps
    formation.mp4              team shape overlay
    results.json               summary of everything above, plus any stage errors

If one analytics stage fails, the others still run and results.json records
the error, the same way the backend treats a failed endpoint.

Usage (from player_tracking/):
    python analysis_pipeline/run_pipeline.py data/videos/test_clip_20s.mp4
    python analysis_pipeline/run_pipeline.py data/videos/test_clip_20s.mp4 --max-frames 300
"""

import argparse
import csv
import json
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIPELINE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from analysis_pipeline.detect_and_track import BROADCAST_TRACKER, DEFAULT_MODEL, run as detect_and_track  # noqa: E402
from analysis_pipeline.tracking_json import to_legacy_json, write_player_table  # noqa: E402


def stage_teams(video, tracking_json, out_dir):
    import argparse as ap
    from analysis_pipeline.identify_players.color_detection_cli import run_pipeline

    out_dir.mkdir(exist_ok=True)
    # Same settings player_service's /jersey_color uses.
    run_pipeline(ap.Namespace(
        input_video=str(video), tracking_json=str(tracking_json), output_folder=str(out_dir),
        clusters=3, process_every=1, min_box_width=10, min_box_height=20,
        min_samples_per_track=3, pixel_to_meter=0.1, max_speed_kmh=40, no_display=True,
    ))
    clustered = json.loads(next(out_dir.glob("*_clustered.json")).read_text())
    teams = {}
    for frame in clustered.get("tracking_results", []):
        for p in frame.get("players", []):
            teams.setdefault(str(p["player_id"]), p.get("cluster_label"))
    return {"players_by_cluster": teams, "files": sorted(f.name for f in out_dir.iterdir())}


def stage_movement(video, tracks_csv, out_dir):
    from analysis_pipeline.movement_metrics.config import TrackingConfig
    from analysis_pipeline.movement_metrics.video_processor import process_tracks

    out_dir.mkdir(exist_ok=True)
    config = TrackingConfig(
        video_path=Path(video),
        output_video_path=out_dir / "trajectory.mp4",
        output_json_path=out_dir / "trajectory.json",
        output_csv_path=out_dir / "player_metrics.csv",
        process_seconds=9999,
    )
    result = process_tracks(config, tracks_csv)
    with open(config.output_csv_path, newline="") as f:
        players = list(csv.DictReader(f))
    return {
        "metric_mode": result["movement_metrics"]["metric_mode"],
        "calibration_available": result["movement_metrics"]["calibration_available"],
        "jersey_clustering": result["jersey_clustering"],
        "players": players,
    }


def stage_tackles(players_csv, out_path):
    import pandas as pd
    from analysis_pipeline.tackle_detection import detect_tackles

    _, events = detect_tackles(pd.read_csv(players_csv))
    out_path.write_text(json.dumps({"events": events}, indent=2))
    return {"events": events}


def run_script(script, *args):
    result = subprocess.run([sys.executable, str(script), *map(str, args)],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip().splitlines()[-1])


def stage_workload(players_csv, out_json, heatmap_dir):
    wl = PIPELINE_DIR / "workload_heatmaps"
    run_script(wl / "scripts" / "compute_workload.py", "--tracking", players_csv,
               "--config", wl / "config.yaml", "--out-json", out_json)
    run_script(wl / "scripts" / "generate_heatmaps.py", "--tracking", players_csv,
               "--config", wl / "config.yaml", "--out-dir", heatmap_dir)
    workload = json.loads(Path(out_json).read_text())
    return {"players": workload.get("players", []), "heatmaps": str(heatmap_dir)}


def stage_formation(video, tracking_json, out_video):
    run_script(PIPELINE_DIR / "formation_analysis" / "formation_visualizer_cli.py",
               "--input_video", video, "--input_tracking", tracking_json,
               "--output_video", out_video, "--no_display")
    return {"video": str(out_video)}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("video", type=Path)
    p.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    p.add_argument("--conf", type=float, default=0.3)
    p.add_argument("--max-frames", type=int, default=None, help="stop after N frames (for quick tests)")
    p.add_argument("--out-dir", type=Path, default=None, help="default: outputs/<video name>/")
    args = p.parse_args()

    out = args.out_dir or ROOT / "outputs" / args.video.stem
    out.mkdir(parents=True, exist_ok=True)

    print("1/6 Detecting and tracking players...")
    try:
        info = detect_and_track(args.video, model_path=args.model, tracker=BROADCAST_TRACKER,
                                conf=args.conf, out_dir=out, stem="tracks",
                                max_frames=args.max_frames)
    except (FileNotFoundError, ValueError) as e:
        raise SystemExit(str(e))

    legacy = to_legacy_json(info["csv"], info)
    tracking_json = out / "tracking.json"
    tracking_json.write_text(json.dumps(legacy))
    players_csv = out / "players.csv"
    write_player_table(legacy, players_csv)

    results = {
        "video": str(args.video),
        "model": args.model.name,
        "video_info": legacy["video_info"],
        "processed_frames": info["processed_frames"],
        "track_ids": len({p["player_id"] for f in legacy["tracking_results"] for p in f["players"]}),
        "stages": {},
        "errors": {},
    }

    stages = [
        ("teams", lambda: stage_teams(args.video, tracking_json, out / "teams")),
        ("movement", lambda: stage_movement(args.video, info["csv"], out / "movement")),
        ("tackles", lambda: stage_tackles(players_csv, out / "tackles.json")),
        ("workload", lambda: stage_workload(players_csv, out / "workload.json", out / "heatmaps")),
        ("formation", lambda: stage_formation(args.video, tracking_json, out / "formation.mp4")),
    ]
    for number, (name, stage) in enumerate(stages, start=2):
        print(f"{number}/6 {name}...")
        try:
            results["stages"][name] = stage()
        except Exception as e:  # one failed stage shouldn't stop the others
            results["errors"][name] = f"{type(e).__name__}: {e}"
            print(f"    {name} failed: {e}")
            traceback.print_exc(limit=1)

    (out / "results.json").write_text(json.dumps(results, indent=2, default=str))
    print(f"\nDone. Results in {out}")
    if results["errors"]:
        print(f"Stages with errors: {', '.join(results['errors'])} (details in results.json)")


if __name__ == "__main__":
    main()
