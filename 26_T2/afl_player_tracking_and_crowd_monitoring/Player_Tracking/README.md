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

### Smart broadcast labeller

`scripts/smart_labeller.py` is an OpenCV-based labeller designed to grow the
player/referee dataset from broadcast videos (`data/videos/broadcast_*.mp4`).
It uses a generic COCO YOLO person detector by default (`yolov8s.pt`) and then
classifies each detected person as player or referee/umpire using colour
heuristics. These are proposals only: review and correct them before export.
The tool lets you review and correct boxes frame-by-frame and exports
YOLO-format labels plus the corresponding extracted frames.

Batch auto-label every 30th frame of all broadcast videos into
`data/raw/<video_name>/` (one folder per video):

```bash
python scripts/smart_labeller.py "data/videos/broadcast_*.mp4" \
  --auto --stride 30
```

Batch mode with quality filters (drops transitions, close-ups and duplicate
static shots so you only keep good gameplay frames):

```bash
python scripts/smart_labeller.py "data/videos/broadcast_*.mp4" \
  --auto --stride 30 \
  --min-detections 8 --max-detections 28 --max-box-area-ratio 0.35
```

Speed things up with a smaller model or larger stride:

```bash
python scripts/smart_labeller.py "data/videos/broadcast_*.mp4" \
  --auto --model yolov8n.pt --stride 60
```

Keep detector proposals under `data/raw/`. Never send `--auto` output directly
to a training dataset.

Review only the saved labelled frames (skips everything else). Pressing `n`
marks each frame as reviewed; the state persists in `reviewed.txt`:

```bash
python scripts/smart_labeller.py data/videos/broadcast_stkilda_northmelbourne.mp4 \
  --review
```

Continue a review session you already started (seed the first N as reviewed):

```bash
python scripts/smart_labeller.py data/videos/broadcast_stkilda_northmelbourne.mp4 \
  --review --reviewed-up-to 84
```

Export labelled frames into `reviewed/` and `unreviewed/` subfolders.
Exports are refreshed from the manifest, including revoked approvals. Advancing
in review mode saves corrections; deleting every box saves an explicit negative.

```bash
python scripts/smart_labeller.py data/videos/broadcast_stkilda_northmelbourne.mp4 \
  --split
```

Build a new dataset from all three original raw datasets plus only reviewed
broadcast frames. The builder requires at least 200 GCS/CAR, 194 SS/WB and
176 CAT/HAW matched pairs; restore incomplete downloads before building.
The original 456/114 split stays fixed. The last 20% of reviewed frames form
a broadcast holdout, with a 300-frame gap from the training frames. A second
match is still needed to measure generalisation beyond this broadcast.

```bash
python scripts/build_datasets.py \
  --broadcast-reviewed data/raw/broadcast_stkilda_northmelbourne/reviewed
python scripts/train.py \
  --data datasets/player_ref_broadcast_clean/data.yaml --preflight-only
python scripts/train.py \
  --data datasets/player_ref_broadcast_clean/data.yaml \
  --fine-tune --name broadcast_repaired --epochs 30 --patience 20
```

`--fine-tune` starts from `models/player_ref_best.pt` with AdamW at 0.0001.
All training commands reject missing labels and overlapping train/val images,
and save image/label hashes in the run's `dataset_snapshot.json`. Empty label
files are valid reviewed backgrounds; missing files are a broken dataset.
Use a fresh `--name` on the builder for subsequent dataset versions.

See [the broadcast regression diagnosis](docs/broadcast_diagnosis.md) for the
failed run's cached training evidence and matched validation comparison.

Interactive review and correction of any frame:

```bash
python scripts/smart_labeller.py data/videos/broadcast_stkilda_northmelbourne.mp4
```

See the script's help (`--help`) for keyboard shortcuts and all options.
