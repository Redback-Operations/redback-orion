## Folder for Player Tracking work

### Tracking quality report

`scripts/analyze_tracking.py` turns the CSV produced by `scripts/track_video.py`
into a Markdown review queue and a machine-readable JSON report. It highlights
short-lived tracks, sudden player-count changes, confidence drops and the worst
timestamps to inspect in the annotated video.

```bash
python scripts/analyze_tracking.py outputs/video_1_player_ref_best.csv \
  --fps 25 --output-prefix outputs/video_1_quality
```

To compare tracker or model configurations, pass the earlier result as a
baseline:

```bash
python scripts/analyze_tracking.py outputs/candidate.csv \
  --baseline outputs/baseline.csv \
  --output-prefix outputs/baseline_vs_candidate
```

The short-lived-track and tracks-per-minute values are fragmentation proxies,
not true ID-switch metrics. Measuring true ID switches requires ground-truth
identity annotations. Camera cuts, replays and graphics can also cause valid
count changes, so the listed timestamps are intended for visual review.
