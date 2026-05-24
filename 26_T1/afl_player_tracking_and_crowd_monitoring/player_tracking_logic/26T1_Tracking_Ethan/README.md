# YOLO AFL Player Tracking Pipeline

This project provides a modular YOLO-based player tracking pipeline for AFL match footage. It detects players frame by frame, assigns tracking IDs, draws annotated trajectories, exports a backend-readable JSON file, and writes a CSV file with approximate movement metrics.

The current implementation is designed for practical testing on short AFL clips. It works best on continuous footage with no camera cut. For broadcast footage with camera movement, zoom changes, overlap, and occlusion, the results should be treated as a useful prototype rather than a fully reliable player re-identification system.

## 1. How to run

### 1.1 Prepare the folders

Place the video you want to detect in:

```text
data/videos/
```

Place the YOLO model you want to use in:

```text
models/
```

Example structure:

```text
player_tracking_project/
├── main.py
├── data/
│   └── videos/
│       └── video.mp4
├── models/
│   └── yolo11x.pt
├── outputs/
└── player_tracking/
    ├── config.py
    ├── detector.py
    ├── tracker.py
    ├── appearance.py
    ├── jersey_cluster.py
    ├── metrics.py
    ├── geometry.py
    ├── video_processor.py
    └── visualizer.py
```

The `outputs/` folder will be created automatically when the pipeline runs.

### 1.2 Check the model classes

Before running the tracker, check the class IDs in your model:

```bash
python -c 'from ultralytics import YOLO; m=YOLO("models/your_model.pt"); print(m.names)'
```

Example for a custom SS vs WB model:

```text
{0: 'REF', 1: 'SS', 2: 'WB'}
```

Example for a general YOLO model such as `yolo11x.pt`:

```text
0 = person
```

The class IDs from this output determine how you should set `player_classes` in `config.py`.

### 1.3 Set `player_classes` in `config.py`

Open `player_tracking/config.py` and update this line:

```python
player_classes: List[int] = field(default_factory=lambda: [0])
```

Use the class IDs that should be tracked.

Examples:

| Model type | Example model class meaning | Recommended `player_classes` |
|---|---|---|
| General YOLO model | `0 = person` | `[0]` |
| Custom team model, players only | `1 = SS`, `2 = WB` | `[1, 2]` |
| Custom team model, including referee | `0 = REF`, `1 = SS`, `2 = WB` | `[0, 1, 2]` |

Important: `player_classes` only controls which YOLO classes are accepted from the detector. It does not automatically decide how the label is written into the JSON or visualisation. That is controlled in `detector.py`.

### 1.4 Set the class output behaviour in `detector.py`

Open `player_tracking/detector.py` and find the `detections.append(...)` block inside `parse_yolo_detections()`.

The current version forces every accepted detection to be treated as one generic player:

```python
# "class_id": class_id,
"class_id": 0,
# "class_name": get_class_name_from_model(model, class_id),
"class_name": "PLAYER",
```

There are two recommended ways to use this section.

#### Option A: Use one generic `PLAYER` label

Use this when the model is only used to find players, or when the team/referee class labels are not important for the final output.

Keep this version:

```python
"class_id": 0,
"class_name": "PLAYER",
```

This is suitable for a general model such as `yolo11x.pt`, where class `0` is usually `person`. In this mode, all accepted detections are shown as `PLAYER`, and team separation is mainly handled later by jersey colour clustering.

Example configuration:

```python
player_classes: List[int] = field(default_factory=lambda: [0])
```

#### Option B: Keep the original YOLO class labels

Use this when the model has meaningful custom classes and you want the output JSON/video to preserve them.

For example, if the model classes are:

```text
0 = REF
1 = SS
2 = WB
```

change the block in `detector.py` to:

```python
"class_id": class_id,
"class_name": get_class_name_from_model(model, class_id),
```

and remove or comment out the forced generic version:

```python
# "class_id": 0,
# "class_name": "PLAYER",
```

Then choose the matching classes in `config.py`:

```python
player_classes: List[int] = field(default_factory=lambda: [0, 1, 2])
```

or, if you only want SS and WB players:

```python
player_classes: List[int] = field(default_factory=lambda: [1, 2])
```

Use this option for a custom model such as `best(SSvsWB).pt` if you want the output to show `REF`, `SS`, and `WB` instead of only `PLAYER`.

### 1.5 Run the pipeline

Example command:

```bash
python main.py \
  --video data/videos/video.mp4 \
  --model models/yolo11x.pt \
  --output-video outputs/yolo11x_player_track.mp4 \
  --output-json outputs/yolo11x_player_track.json \
  --output-csv outputs/yolo11x_player_metrics.csv
```

The file names above are only examples. Change them to match the real video name and model name in your project.

For example, if your video is called `SSvsWB_15s.mp4` and your model is `best(SSvsWB).pt`, use those exact names in the command.

### 1.6 Optional runtime parameters

The command-line parameters can be adjusted for different videos, models, and output names.

| Argument | Purpose |
|---|---|
| `--video` | Input video path. The video should be placed in `data/videos/`. |
| `--model` | YOLO model path. The model should be placed in `models/`. |
| `--output-video` | Path for the annotated output video. |
| `--output-json` | Path for the backend-readable tracking JSON file. |
| `--output-csv` | Path for the movement metrics CSV file. |
| `--seconds` | Number of seconds to process from the beginning of the video. |
| `--conf` | YOLO confidence threshold. Increase it to reduce false detections; decrease it if real players are missed. |
| `--imgsz` | YOLO inference image size. Larger values may improve detection but run slower. |
| `--clusters` | Number of jersey colour clusters for offline grouping. Use `2` for two teams, or `3` if referees/other groups are included. |
| `--min-samples-per-track` | Minimum number of jersey colour samples required before a track can be clustered. |
| `--pixel-to-meter` | Approximate pixel-to-metre conversion for CSV metrics. This is only meaningful after calibration. |

Example with extra parameters:

```bash
python main.py \
  --video data/videos/video.mp4 \
  --model models/yolo11x.pt \
  --output-video outputs/yolo11x_player_track.mp4 \
  --output-json outputs/yolo11x_player_track.json \
  --output-csv outputs/yolo11x_player_metrics.csv \
  --seconds 15 \
  --conf 0.25 \
  --imgsz 640 \
  --clusters 3
```

## 2. Current output location

The current output videos and related demonstration materials are stored in this Panopto folder:

[Current player tracking outputs](https://deakin.au.panopto.com/Panopto/Pages/Sessions/List.aspx?folderID=0d5d83cf-ff13-4ff8-b546-b2d90048fcc6)

These outputs show the current tracking behaviour, including the annotated video, tracking IDs, trajectory lines, and colour-based grouping results.

## 3. Current status and practical conclusion

### What works well now

- The pipeline works well on short AFL clips when there is no camera cut.
- The current testing result is strongest on an approximately 15-second SS vs WB segment with a continuous camera view.
- The tracker can keep IDs more stable by combining centre distance, IoU, movement direction, appearance features, duplicate filtering, and ambiguous-match handling.
- The output video is useful for visual inspection of tracking quality.
- The JSON output can be used by the backend team as a structured reference for future integration.
- The CSV output provides approximate distance and speed values, but these are still image-space estimates.

### Main limitation

AFL broadcast footage is difficult for long-term player tracking because:

- the camera keeps moving;
- players become very small in wide shots;
- players overlap frequently during contests;
- the camera angle and scale change across shots;
- the detector may miss or duplicate players;
- the same player may look very different after a camera cut.

Because of this, long-term ID consistency across broadcast camera changes is not realistic with this lightweight tracking pipeline alone.

### Best practical solution

The best solution is still to use a fixed camera angle that continuously captures the whole field. If that setup is available, most of these problems can be solved, including speed calculation, distance calculation, and heatmap generation.

With a fixed full-field camera, player positions can be mapped more consistently, and the exported tracking data becomes much more meaningful for backend analytics.

### Jersey numbers and faces

Detecting jersey numbers or faces does not seem realistic in this scenario. In AFL broadcast footage, players are usually too small, blurred, occluded, or facing away from the camera.

Jersey colour is more practical than jersey number or face detection, but it should still be treated as a supporting cue rather than a perfect identity method.

## 4. Main features

- YOLO-based player detection.
- Configurable model path and video path.
- Configurable YOLO class filtering through `player_classes`.
- Persistent tracking ID assignment.
- Fixed initial class label for each tracking ID.
- Centre-distance, IoU, direction, and appearance-based matching.
- Duplicate detection suppression.
- Ambiguous-match rejection to reduce unsafe ID switches.
- Short missing-track tolerance for temporary occlusion.
- Torso-region appearance feature extraction.
- Offline jersey colour clustering after tracking.
- Annotated output video with tracking IDs, labels, confidence values, and trajectory trails.
- JSON export for backend use.
- CSV export for approximate distance and speed metrics.

## 5. Main file descriptions

| File | Method and role |
|---|---|
| `main.py` | Provides the command-line entry point. It reads the video path, model path, output paths, and runtime parameters, then builds the tracking configuration. |
| `config.py` | Stores default paths and all main tuning parameters, including `player_classes`, confidence threshold, tracking thresholds, matching weights, jersey clustering settings, and metrics settings. |
| `video_processor.py` | Controls the full processing workflow: validate paths, load YOLO, read video frames, run detection, update tracks, apply jersey clustering, render the final video, and export JSON/CSV files. |
| `detector.py` | Converts raw YOLO results into detection dictionaries. It filters detections by class, extracts bbox/centre/confidence, adds appearance and jersey features, and removes likely duplicate boxes. |
| `tracker.py` | Maintains tracking IDs across frames. It matches new detections to existing tracks using distance, IoU, direction consistency, and appearance similarity. It also handles missing tracks, ambiguous matches, and new-track creation. |
| `appearance.py` | Extracts compact visual features from the torso region of each bbox. One feature is used online for ID matching, and another is used offline for jersey colour clustering. |
| `jersey_cluster.py` | Groups tracked players by jersey colour after tracking. It uses each track's collected jersey samples, computes a representative feature, standardises features, and applies KMeans clustering. |
| `metrics.py` | Exports approximate movement statistics for each tracking ID, including observed frames, first/last timestamp, total pixel distance, estimated distance, and speed values. |
| `geometry.py` | Provides helper functions for bbox centre calculation, IoU, Euclidean distance, cosine similarity, direction cost, and bbox conversion. |
| `visualizer.py` | Draws the final tracking output, including bounding boxes, tracking IDs, class labels, confidence values, centre points, and trajectory trails. |

## 6. Pipeline overview

### Detection stage

For each frame, the pipeline:

1. runs YOLO inference;
2. keeps only classes listed in `player_classes`;
3. converts each valid YOLO box into a detection record;
4. extracts appearance and jersey colour features;
5. suppresses likely duplicate detections.

### Tracking stage

The tracker compares current detections with existing tracks using four signals:

- centre distance;
- bbox IoU;
- movement direction consistency;
- appearance similarity.

A detection is assigned to an existing track only when the match is confident enough. If the match is uncertain, the tracker avoids forcing the update, which helps reduce ID switches during overlap.

### Jersey clustering stage

After tracking is complete, the pipeline clusters tracks using jersey colour features collected over the video. This is done after tracking, not frame by frame, so each ID can use multiple torso colour samples.

The cluster labels are automatic labels such as:

```text
Team_0
Team_1
Team_2
Unknown
```

These labels should be checked visually before mapping them to real team names.

### Export stage

The pipeline exports:

```text
outputs/*.mp4
outputs/*.json
outputs/*.csv
```

The exact output file names depend on the command-line arguments used when running `main.py`.

## 7. Output files

### Annotated video

The output video shows:

- tracking ID;
- fixed initial class label;
- confidence score;
- bounding box;
- centre point;
- recent trajectory trail;
- colour-based visual grouping.

### JSON output

The JSON file is the main structured output for backend integration.

Top-level information includes:

- input video path;
- model path;
- output paths;
- FPS;
- total frames;
- processed frames;
- video resolution;
- configured `player_classes`;
- jersey clustering summary;
- all tracking records.

Each track includes:

- `track_id`;
- `initial_class_id`;
- `initial_class_name`;
- `cluster_id`;
- `cluster_team`;
- `jersey_sample_count`;
- `representative_jersey_feature`;
- per-frame bbox, centre, confidence, raw detected class, fixed initial class, and cluster fields.

This structure allows the backend team to reconstruct bbox history, confidence history, centre-position history, first/last observed time, and colour-based grouping for each player ID.

### CSV metrics output

The CSV file contains one row per tracking ID. It includes:

- track ID;
- cluster information;
- initial class;
- number of observed frames;
- first and last frame/time;
- total movement distance in pixels;
- approximate converted distance;
- average speed;
- maximum speed.

Important: distance and speed are calculated from image coordinates. They should not be treated as accurate real-world values when the camera is moving or when the perspective changes.

## 8. Practical tuning advice

Useful parameters in `config.py`:

| Parameter | Meaning |
|---|---|
| `max_distance` | Maximum expected centre movement in pixels. Larger values allow faster motion but may increase wrong matches during overlap. |
| `max_missing` | Number of frames a track can be missing before it is removed. Increase it for short occlusions. |
| `duplicate_center_distance` | Distance used to remove duplicated detections around the same player. |
| `new_track_suppression_distance` | Prevents creating a new ID when a detection is close to an existing track but not confidently matched. |
| `distance_weight` | Weight for centre-distance matching. |
| `iou_weight` | Weight for bbox overlap matching. Useful when the camera is stable. |
| `direction_weight` | Weight for movement direction consistency. Useful for fast movement. |
| `appearance_weight` | Weight for visual similarity. Useful when jersey colour helps distinguish players. |
| `match_cost_threshold` | Maximum allowed matching cost. Lower values make matching stricter. |
| `ambiguity_margin` | Controls how close the best and second-best matches can be before the match is rejected as ambiguous. |
| `jersey_clusters` | Number of KMeans jersey colour clusters. |
| `pixel_to_meter` | Approximate conversion used only for CSV metrics. |

General advice:

- Use a short continuous clip with no camera cut for the most stable results.
- Use the correct `player_classes` for the selected model.
- Use generic `PLAYER` labels when the model is only used as a person detector.
- Restore original YOLO class labels in `detector.py` when the model has meaningful team/referee classes.
- Use `--clusters 2` for two teams.
- Use `--clusters 3` if referees or another visual group should be separated.
- Increase `max_missing` if tracks disappear briefly during overlap.
- Increase `new_track_suppression_distance` if duplicate IDs appear near the same player.
- Decrease `match_cost_threshold` if unsafe ID matches are being accepted.
- Tune `pixel_to_meter` only after field/camera calibration.

## 9. Limitations

This is a practical lightweight tracking pipeline, not a full player re-identification system.

Current limitations:

- ID stability is good mainly inside a continuous shot with no camera switch.
- ID consistency across broadcast camera cuts is not reliable.
- Camera movement makes raw image-space trajectories unstable.
- Speed, distance, and heatmap values are only approximate without field-coordinate mapping.
- Jersey colour features can fail when teams have visually similar kits.
- Players may be too small or blurred for reliable appearance features.
- Heavy overlap can still cause missed detections or ID switches.
- KMeans cluster labels are automatic and must be checked manually.
- Jersey number detection is not realistic for most AFL broadcast frames.
- Face detection or face recognition is not realistic for this video setting.

## 10. Recommended future direction

The strongest future improvement is not only changing the tracking algorithm. The video capture setup is more important.

Recommended setup:

```text
fixed camera angle
continuous full-field view
minimal zooming
no broadcast camera cuts
stable frame scale
```

With this setup, the project can more realistically support:

- stable ID tracking;
- field-coordinate mapping;
- accurate speed calculation;
- accurate distance calculation;
- reliable heatmap generation;
- better backend analytics.

If only broadcast footage is available, possible technical improvements include:

- homography transformation;
- camera registration;
- optical-flow-based camera motion compensation;
- Kalman filtering;
- ByteTrack or DeepSORT-style tracking;
- stronger ReID features;
- a tracking evaluation metric for ID switches, missing tracks, duplicate IDs, and trajectory stability.

However, these methods still cannot fully solve the problem if the camera frequently changes view or players disappear from the frame.

## 11. Recommended handover files

For team review and backend reference, share:

```text
outputs/*.mp4
outputs/*.json
outputs/*.csv
```

The video is useful for visual checking. The JSON file is the main backend-readable output. The CSV file is useful for approximate movement metrics, but speed and distance values should be interpreted carefully unless the video comes from a fixed calibrated camera.
