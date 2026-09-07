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

### Broadcast camera motion diagnostic

`scripts/analyze_camera_motion.py` estimates global frame-to-frame image motion
using OpenCV feature tracking and RANSAC. It can be used to identify sections
where camera pans, zooms or other broadcast motion may affect image-space player
movement measurements.

```bash
python scripts/analyze_camera_motion.py data/videos/video_1.mp4 --max-frames 300
```

The current `player_tracker.py` movement metrics use bounding-box positions and
a fixed pixel-to-metre conversion. On moving broadcast footage, camera motion
and perspective changes can therefore affect the reported distance, speed,
acceleration and stamina values. These values should be treated as approximate
until camera or field calibration is applied.

The camera-motion diagnostic measures global image motion only; it does not
currently correct player positions or provide ground-truth physical distances.
