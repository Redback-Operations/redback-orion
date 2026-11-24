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
    """Group players into teams by jumper colour (identify_players).

    Writes the clustered tracking JSON, video and metrics CSV into out_dir and returns
    each track's cluster label plus the list of files written.
    """
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
    """Work out speed and distance per player from tracks.csv (movement_metrics).

    Writes trajectory.mp4, trajectory.json and player_metrics.csv into out_dir.
    Returns the per-player rows plus metric_mode and calibration_available,
    which say whether distances are a pixel estimate or calibrated metres.
    """
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
    """Find tackle events with the rule-based detector in tackle_detection.py.

    Writes {"events": [...]} to out_path and returns the same dict.
    """
    import pandas as pd
    from analysis_pipeline.tackle_detection import detect_tackles

    _, events = detect_tackles(pd.read_csv(players_csv))
    out_path.write_text(json.dumps({"events": events}, indent=2))
    return {"events": events}


def run_script(script, *args):
    """Run a stage's command-line script with this Python interpreter.

    Used for stages that only exist as scripts. Raises RuntimeError with the
    last line of the script's output if it exits with an error.
    """
    result = subprocess.run([sys.executable, str(script), *map(str, args)],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip().splitlines()[-1])


def stage_workload(players_csv, out_json, heatmap_dir):
    """Compute workload per player and draw position heatmaps (workload_heatmaps).

    Thresholds come from workload_heatmaps/config.yaml. Writes workload.json
    plus a heatmap PNG and density grid CSV per player, and returns the
    workload rows and the heatmap folder.
    """
    wl = PIPELINE_DIR / "workload_heatmaps"
    run_script(wl / "scripts" / "compute_workload.py", "--tracking", players_csv,
               "--config", wl / "config.yaml", "--out-json", out_json)
    run_script(wl / "scripts" / "generate_heatmaps.py", "--tracking", players_csv,
               "--config", wl / "config.yaml", "--out-dir", heatmap_dir)
    workload = json.loads(Path(out_json).read_text())
    return {"players": workload.get("players", []), "heatmaps": str(heatmap_dir)}


def stage_formation(video, tracking_json, out_video):
    """Draw each team's shape over the video (formation_analysis).

    Writes out_video and returns its path.
    """
    run_script(PIPELINE_DIR / "formation_analysis" / "formation_visualizer_cli.py",
               "--input_video", video, "--input_tracking", tracking_json,
               "--output_video", out_video, "--no_display")
    return {"video": str(out_video)}


def run_all(video, out_dir=None, tracks_csv=None, tracking=None,
            model=DEFAULT_MODEL, conf=0.3, max_frames=None) -> dict:
    """Run every stage on one video, write results.json and return the results.

    Pass tracks_csv and tracking (the /tracking JSON for the same video) to
    reuse saved tracks and skip detection, as player_service does.
    """
    video = Path(video)
    out = Path(out_dir) if out_dir else ROOT / "outputs" / video.stem
    out.mkdir(parents=True, exist_ok=True)

    if tracks_csv and tracking:
        csv_path, legacy = Path(tracks_csv), tracking
        processed = len(legacy["tracking_results"])
    else:
        print("1/6 Detecting and tracking players...")
        info = detect_and_track(video, model_path=model, tracker=BROADCAST_TRACKER,
                                conf=conf, out_dir=out, stem="tracks",
                                max_frames=max_frames)
        csv_path, legacy = info["csv"], to_legacy_json(info["csv"], info)
        processed = info["processed_frames"]

    tracking_json = out / "tracking.json"
    tracking_json.write_text(json.dumps(legacy))
    players_csv = out / "players.csv"
    write_player_table(legacy, players_csv)

    results = {
        "video": str(video),
        "model": Path(model).name,
        "video_info": legacy["video_info"],
        "processed_frames": processed,
        "track_ids": len({p["player_id"] for f in legacy["tracking_results"] for p in f["players"]}),
        "stages": {},
        "errors": {},
    }

    stages = [
        ("teams", lambda: stage_teams(video, tracking_json, out / "teams")),
        ("movement", lambda: stage_movement(video, csv_path, out / "movement")),
        ("tackles", lambda: stage_tackles(players_csv, out / "tackles.json")),
        ("workload", lambda: stage_workload(players_csv, out / "workload.json", out / "heatmaps")),
        ("formation", lambda: stage_formation(video, tracking_json, out / "formation.mp4")),
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
    return results


def main() -> None:
    """Command-line entry point: parse the arguments and call run_all()."""
    p =argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("video", type=Path)
    p.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    p.add_argument("--conf", type=float, default=0.3)
    p.add_argument("--max-frames", type=int, default=None, help="stop after N frames (for quick tests)")
    p.add_argument("--out-dir", type=Path, default=None, help="default: outputs/<video name>/")
    args = p.parse_args()

    out = args.out_dir or ROOT / "outputs" / args.video.stem
    try:
        results = run_all(args.video, out, model=args.model,
                          conf=args.conf, max_frames=args.max_frames)
    except (FileNotFoundError, ValueError) as e:
        raise SystemExit(str(e))

    print(f"\nDone. Results in {out}")
    if results["errors"]:
        print(f"Stages with errors: {', '.join(results['errors'])} (details in results.json)")


if __name__ == "__main__":
    main()
