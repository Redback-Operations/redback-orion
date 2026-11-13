# AFL Player Speed, Acceleration & Team Tracking Pipeline

Offline per-player metric extraction for AFL match footage.

This pipeline consumes a tracking JSON  plus the source match video, and emits:

- an annotated video with team colouring, per-player ID, and live speed overlays
- a per-frame CSV containing player kinematic metrics
- a tracking JSON that matches the existing team endpoint schema and adds:
  `speed_mps`, `speed_kmh`, `accel_mps2`,
  `distance_m`, and `total_distance_m`
- a per-player summary block inside the JSON containing:
  total distance, maximum speed, and peak acceleration

Built on top of Quan's `color_detection_cli.py` and the team's upstream
tracking pipeline. This component extends the existing tracking system by
adding speed, acceleration, distance estimation, centroid smoothing,
and output metric generation.

## Pipeline overview

```
YOLOv11 + ByteTrack/Botsort player tracking
            ↓
    Tracking JSON
            ↓
PASS 1 — load upstream player tracking JSON
            ↓
bbox auto-rescaling + centroid smoothing
            ↓
speed, acceleration and distance estimation
            ↓
annotated video + CSV + metrics JSON
            ↓
PASS 2 — bbox auto-rescale → centroid smoothing → speed/accel/distance
            ↓
   Annotated video + CSV + tracking JSON
```

---

## CLI usage

Required arguments are the input video and the upstream tracking JSON.
Everything else has sane defaults.

### Basic

```bash
python3 speed_acceleration_cli.py \
    --input_video afl_video.mp4 \
    --tracking_json clustered_tracking.json
```

Outputs are written to `./outputs/` (configurable with `--output_folder`)
with filenames derived from the input video stem:

```
outputs/
├── afl_video_metrics.mp4   # annotated video
├── afl_video_metrics.csv   # per-frame metrics
└── afl_video_metrics.json  # full tracking JSON + summary
```

### Headless run (no preview window)

```bash
python3 speed_acceleration_cli.py \
    --input_video afl_video.mp4 \
    --tracking_json afl_video_tracking.json \
    --no_display
```

### Custom output folder + tuned clustering

```bash
python3 speed_acceleration_cli.py \
    --input_video afl_video.mp4 \
    --tracking_json afl_video_tracking.json \
    --output_folder match01_outputs \
    --clusters 4 \
    --process_every 3 \
    --min_box_width 25 \
    --min_box_height 50
```

### Early-exit when tracking JSON ends before the video does

```bash
python3 speed_acceleration_cli.py \
    --input_video afl_video.mp4 \
    --tracking_json afl_video_tracking.json \
    --max_frames 1900 \
    --no_display
```

---

## CLI parameters

| Parameter                  | Default     | What it does                                                                              |
| -------------------------- | ----------- | ----------------------------------------------------------------------------------------- |
| `--input_video`            | *(required)*| Source match video.                                                                       |
| `--tracking_json`          | *(required)*| Tracking JSON produced by upstream tracker.                                               |
| `--output_folder`          | `outputs`   | Output directory. Auto-created.                                                           |
| `--clusters`               | `3`         | KMeans cluster count (typically 3 = Team A / Team B / Umpire).                            |
| `--process_every`          | `2`         | PASS 1 samples every Nth frame for colour features.                                       |
| `--min_box_width`          | `20`        | Minimum bbox width for a detection to contribute features.                                |
| `--min_box_height`         | `35`        | Minimum bbox height for a detection to contribute features.                               |
| `--min_samples_per_track`  | `5`         | Minimum feature samples required for a track to enter clustering.                         |
| `--pixel_to_meter`         | `0.02`      | Flat metres-per-pixel constant. See *Limitations*.                                        |
| `--smoothing_window`       | `5`         | Frames of moving-average smoothing on bbox centroids before computing speed/accel.        |
| `--max_speed_kmh`          | `40`        | Frame-to-frame speed above this is treated as tracker jitter and clamped to 0.            |
| `--max_accel_mps2`         | `15`        | Acceleration above this (absolute value) is clamped to 0. Elite humans peak ~10 m/s².    |
| `--max_frames`             | `0`         | If > 0, stop after this many frames. Useful when tracking JSON is shorter than the video. |
| `--no_display`             | off         | Disable live `cv2.imshow` preview. Required for headless / server runs.                   |

---

## Required input JSON schema

The script accepts the schema produced by the team's tracker:

```json
{
  "video_info": {
    "duration": 619.13,
    "fps": 29.92,
    "total_frames": 17955,
    "resolution": [640, 360]
  },
  "tracking_results": [
    {
      "frame_number": 1,
      "timestamp": 0.0,
      "players": [
        {
          "player_id": 1,
          "team_id": 1,
          "team_name": "GCS",
          "bbox": { "x1": 948, "y1": 310, "x2": 967, "y2": 359 },
          "center": { "x": 958, "y": 334 },
          "confidence": 0.79,
          "width": 19,
          "height": 49
        }
      ]
    }
  ]
}
```

Notes:

- `bbox` may be a dict (`{"x1": ..., "y1": ..., "x2": ..., "y2": ...}`) **or** a 4-element list `[x1, y1, x2, y2]`. Both are accepted.
- Frame numbers may be 0- or 1-indexed; the script doesn't assume.
- If `video_info.resolution` differs from the actual source video size, all bbox coordinates are auto-scaled onto the source video's pixel grid (e.g. tracking ran on a 640×360 downsample but the source is 1280×720).
- Any extra fields on a player record (e.g. `team`, `team_id`, `team_name`, `confidence`, `width`, `height`) are preserved unchanged on the output.

---

## Output tracking JSON schema

The output matches the team endpoint shape, with cluster + kinematic fields appended to each player record.

```json
{
  "video_info": {
    "duration": 600.03,
    "fps": 29.92,
    "total_frames": 17955,
    "resolution": [640, 360]
  },
  "parameters": {
    "pixel_to_meter": 0.02,
    "smoothing_window": 5,
    "max_speed_kmh": 40.0,
    "max_accel_mps2": 15.0,
    "clusters": 3
  },
  "player_summary": [
    {
      "player_id": 850,
      "total_distance_m": 22.80,
      "max_speed_kmh": 39.22,
      "peak_accel_mps2": 14.98,
      "display_team": "Team_1": "Cluster_1"
    }
  ],
  "tracking_results": [
    {
      "frame_number": 55,
      "timestamp": 1.838,
      "players": [
        {
          "player_id": 1,
          "team": "CAR",
          "bbox": { "x1": 958, "y1": 520, "x2": 1006, "y2": 618 },
          "confidence": 0.76,
          "center": { "x": 982, "y": 618 },
          "cluster_id": 1,
          "cluster_label": "Cluster_1",
          "speed_mps": 0.0,
          "speed_kmh": 0.0,
          "accel_mps2": 0.0,
          "distance_m": 0.0,
          "total_distance_m": 0.0
        }
      ]
    }
  ]
}
```

### Output JSON fields

| Field                            | Unit  | Description                                                              |
| -------------------------------- | ----- | ------------------------------------------------------------------------ |
| `video_info`                     |       | Carried through from the input JSON; augmented with `duration` if absent.|
| `parameters`                     |       | Echoes the CLI run config so the output is reproducible.                 |
| `player_summary[]`               |       | One entry per tracked player.                                            |
| `tracking_results[].frame_number`| int   | 1-indexed video frame number.                                            |
| `tracking_results[].timestamp`   | s     | Frame timestamp (carried through, or computed as `frame / fps`).         |
| `players[].player_id`            |       | Track ID from upstream tracker.                                          |
| `players[].team` / `team_id` /   |       | Preserved verbatim from the input JSON.                                  |
| `players[].team_name`            |       |                                                                          |
| `players[].bbox`                 | px    | Bbox in **source video** coordinates (auto-rescaled if needed).          |
| `players[].center`               | px    | Bottom-centre ("feet") of the bbox in source-video coordinates.          |
| `players[].confidence`           |       | Preserved verbatim from the input JSON.                                  |
| `players[].cluster_id`           | int   | KMeans cluster index. `-1` if the track was too short to be clustered.   |
| `players[].cluster_label`        |       | `"Cluster_0"`, `"Cluster_1"`, ... or `"Unclustered"`.                    |
| `players[].speed_mps`            | m/s   | Instantaneous speed (after smoothing + clamps).                          |
| `players[].speed_kmh`            | km/h  | Same speed in km/h.                                                      |
| `players[].accel_mps2`           | m/s²  | First difference of speed / dt; clamped at `±max_accel_mps2`.            |
| `players[].distance_m`           | m     | Distance covered in this single frame.                                   |
| `players[].total_distance_m`     | m     | Cumulative distance for this player so far.                              |

---

## Output CSV schema

`<video>_metrics.csv` — one row per (frame, player_id):

| Column              | Unit  |
| ------------------- | ----- |
| `frame`             | int   |
| `player_id`         |       |
| `cluster_id`        | int   |
| `cluster_label`     |       |
| `team_id`           |       |
| `team_name`         |       |
| `x`                 | px    |
| `y`                 | px    |
| `speed_mps`         | m/s   |
| `speed_kmh`         | km/h  |
| `accel_mps2`        | m/s²  |
| `distance_m`        | m     |
| `total_distance_m`  | m     |

---

## Example output

![Annotated frame with cluster colouring + ID + speed labels](outputs/sample_frame_1686.png)

Each detected player is drawn with their cluster colour, tracker ID, and instantaneous speed in km/h. The HUD shows the current frame number.

---

## How the metrics are computed

1. **Bbox auto-rescale.** If the tracking JSON's declared resolution differs from the source video's, every bbox is scaled onto the source video's pixel grid before anything else.
2. **Bbox → feet position.** Each detection's bbox is converted to a single bottom-centre point `((x1+x2)/2, y2)` — that's the player's ground contact, which is the natural point for trajectory math.
3. **Smoothing.** A 5-frame moving-average window per player ID is applied to the feet coordinates. This removes most of the bbox jitter introduced by the detector.
4. **Speed.** Frame-to-frame Euclidean distance between smoothed positions, multiplied by `pixel_to_meter`, divided by `dt = 1 / fps`.
5. **Acceleration.** First difference of `speed_mps` divided by `dt`. Skipped on the first frame of a track, the frame after a clamp, and the frame after a gap.
6. **Speed clamp.** Frame-to-frame speeds above `--max_speed_kmh` (default 40) are treated as ID-swap or jitter artefacts and replaced with 0. The associated distance is discarded.
7. **Accel clamp.** Accelerations whose absolute value exceeds `--max_accel_mps2` (default 15) are replaced with 0. Elite human peak is ~10 m/s²; 15 is a generous ceiling.
8. **Gap handling.** If a player is seen at frame N and then not again until frame N+5, we don't compute speed across the gap — the trajectory through the missing frames is unknown.

---

## Limitations

- **Flat pixel-to-metre conversion.** The default `0.02 m/px` is a single global constant. For a broadcast camera angle, players near the back of the frame move fewer pixels per metre than those near the front, so absolute speeds will be off by a perspective-dependent factor. *Useful for relative comparisons* (player A vs player B, sprint vs jog) but should not be quoted as ground-truth km/h without a homography. A proper fix is to map the field's four corner-line intersections to plan-view metres and reproject — out of scope here.
- **The clamp ceilings are intentionally aggressive.** With noisy upstream tracking, raw frame-to-frame speed and acceleration easily exceed human physiology. The clamps mean `peak_accel_mps2` values cluster near 15 — the clamp ceiling — for most players. The accel column is best used for *relative* "who had more bursts" comparisons, not absolute biomechanics.
- **No re-identification.** When the upstream tracker swaps IDs (occlusions, fast motion, crowded scenes), this script treats the new ID as a brand-new player. Per-player aggregates are therefore really *per-track* aggregates.
Team labels are inherited from the upstream tracking JSON. Accuracy therefore depends on the quality of the upstream tracking and team classification pipeline.
- **Smoothing introduces latency.** A 5-frame window means peak-speed timestamps are off by ~2 frames (~67 ms at 30 fps). Fine for analytics, not for live officiating.

---

## Files in this folder

| File                          | What it is                                                            |
| ----------------------------- | --------------------------------------------------------------------- |
| `speed_acceleration_cli.py`   | The merged pipeline (this tool).                                      |
| `afl_video.mp4`               | Source match video.                                                   |
| `afl_video_tracking.json`     | Upstream tracking output (detections + IDs per frame).                |
| `outputs/`                    | Default output directory created on first run.                        |

---

## Acknowledgement

Built on top of `color_detection_cli.py` by Quan (Re-Identification team). The jersey clustering, torso ROI extraction, and HSV feature pipeline are unchanged; this script layers speed/acceleration/distance metrics on top, adds bbox auto-rescaling, and reshapes the output JSON to match the team endpoint contract.
