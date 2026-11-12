# Crowd Behaviour Analytics

## Objective

Analyse how the crowd changes and moves over time, and flag behaviour that may
indicate risk (surges, running, reverse flow, unusual motion).

## Where It Sits in the Pipeline

```text
crowd_detection -> density_zoning / heatmap -> crowd_behaviour_analytics -> crowd_allocation_risk_zone
```

`analyze_behaviour(input_data)` is called from `shared/services/crowd_pipeline_service.py`
and `shared/services/crowd_intelligence_service.py`. Input and output formats are in
[SCHEMA.md](SCHEMA.md).

## Structure

```text
crowd_behaviour_analytics/
|- README.md
|- SCHEMA.md
|- main.py                # analyze_behaviour(): runs every stage below
|- feature_extraction.py  # zone density features, crowd_state trend, density_level
|- vision_analysis.py     # optical-flow motion features
|- tracking.py            # person tracking, movement states, motion annotations
|- pose_analysis.py       # optional YOLO-pose check on walking tracks
|- anomaly_model.py       # IsolationForest motion anomalies
|- event_detection.py     # event_flags from all of the above
|- output/<video_id>/     # annotated motion frames
```

## How It Works

1. **Density features**: average/max density, variation, hotspots (zones with density ≥ 0.6) and total people, calculated from the `zones` produced by density_zoning.
2. **Crowd state (trend)**: `classify_density_trend` looks at the per-frame `person_count` values and returns the `crowd_state`:
   - It only uses frames where the detector actually ran (`detected != false`), so reused counts don't hide changes.
   - It drops the first few detected frames, because the detector under-counts at the start.
   - It compares the mean of the first third with the mean of the last third.
   - A relative change of at least +15% gives `increasing_density`, at most -15% gives `dispersing`, and anything else is `stable`. With too few samples the state is `stable`.
   - The relative change is also returned as `density_trend_delta`.
3. **Density level (static)**: the older weighted density score is kept as `density_level`. It describes how dense the crowd is now, not whether that is changing.
4. **Motion features**: Farneback optical flow runs over up to 8 people-annotated frames. Each frame is downscaled to `CROWD_MOTION_FLOW_WIDTH` first, and the magnitudes are scaled back up so the thresholds still apply.
5. **Tracking**: detections are linked across frames by IoU and centroid distance, and each track is classified as `stationary`, `walking` or `running`. Nearby tracks are found through a grid index (`CROWD_TRACK_BUCKET`), which gives the same result as a full scan, just faster.
6. **Pose refinement (optional)**: when `CROWD_POSE_REFINEMENT` is enabled, walking tracks are checked by YOLO-pose leg movement, and tracks with too little leg motion are reclassified as stationary. It's off by default because it is the slowest stage in the pipeline.
7. **Anomalies**: an IsolationForest over per-track motion features flags unusual tracks.
8. **Events**: combines everything into `event_flags`: `overcrowding_spike`, `sudden_gathering`, `crowd_dispersing`, `running_detection`, `walking_detection`, `stationary_detection`, `reverse_flow`, `crowd_surge`, `motion_anomaly`.
9. **Annotations**: running and walking tracks (or stationary ones if nothing moves) are drawn onto the frames with the most such tracks. Only the top `CROWD_MOTION_ANNOTATION_MAX_FRAMES` frames are drawn and saved to `output/<video_id>/`, and their paths are returned in `artifact_paths`.

## Configuration

All settings are environment variables. The defaults are the recommended values.

| Variable | Default | Effect |
|----------|---------|--------|
| `CROWD_TREND_WARMUP` | `3` | Detected frames dropped from the start before measuring the trend. |
| `CROWD_TREND_THRESHOLD` | `0.15` | Relative change needed for `increasing_density` / `dispersing`. |
| `CROWD_TREND_MIN_SAMPLES` | `6` | With fewer detected frames than this (after the warm-up frames are dropped), `crowd_state` is `stable`. |
| `CROWD_POSE_REFINEMENT` | off | `1`/`true`/`yes`/`on` enables pose checks on walking tracks. The pose model comes from `yolov8n-pose.pt` / `yolov8s-pose.pt` in this folder or the project root. |
| `CROWD_TRACK_BUCKET` | `true` | Grid index for track matching. `false` uses the full scan; the output is identical. |
| `CROWD_MOTION_ANNOTATION_MAX_FRAMES` | `3` | Number of motion frames to annotate. `0` annotates every frame. |
| `CROWD_MOTION_FLOW_WIDTH` | `640` | Width frames are resized to before optical flow. `0` keeps full resolution. |

## Notes

- Because crowd_detection only runs the detector every `CROWD_DETECT_STRIDE` frames, only those frames have a `people_annotated_frame_path`. Optical flow and annotations therefore use detected frames only.
- `crowd_state` values are unchanged (`stable`, `increasing_density`, `dispersing`), so downstream consumers don't need changes. Code that relied on the old density-score meaning of `crowd_state` should switch to `density_level`.
