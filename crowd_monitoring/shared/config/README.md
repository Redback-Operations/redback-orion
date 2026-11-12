# Config Folder

This folder stores shared configuration used across services and team tasks.

Keeping settings here helps the team avoid hardcoding values in many scripts.
If a setting changes, it can be updated in one place instead of multiple files.

## Current Files

### `video_processing_config.json`

Read by `video_processing/main.py`.

```json
{
  "output_resolution": [640, 640],
  "extracted_frames_dir": "video_processing/data/extracted_frames",
  "enable_tiling": true,
  "tile_rows": 8,
  "tile_columns": 12,
  "tile_overlap": 0.20
}
```

| Key | Meaning |
|-----|---------|
| `output_resolution` | Not currently read by any code. Frames are extracted at source resolution |
| `extracted_frames_dir` | Where extracted frames are written (relative to `crowd_monitoring/`) |
| `enable_tiling` | Generate tile metadata for each frame. `crowd_detection` uses it for tiled detection |
| `tile_rows` / `tile_columns` | Tile grid. 8×12 keeps distant spectators large enough for the 640 px detector |
| `tile_overlap` | Fraction of overlap between neighbouring tiles. Must be large enough that a person on a seam fits whole in at least one tile |

### `crowd_region_preprocessing_config.json`

Read by `crowd_region_preprocessing/main.py`.

```json
{
  "focused_frames_dir": "crowd_region_preprocessing/output/focused_frames",
  "write_focused_frames": false,
  "exclude_polygons_normalized": [[[0.0036, 0.5741], [0.1161, 0.6588], "..."]]
}
```

| Key | Meaning |
|-----|---------|
| `exclude_polygons_normalized` | Polygons (0-1 fractions of width/height) to black out before detection, such as the roof, signage and rails. Generate them with `python -m crowd_region_preprocessing.pick_region` |
| `write_focused_frames` | Also save masked JPEGs for debugging or the UI |
| `focused_frames_dir` | Where those JPEGs go |

See `crowd_region_preprocessing/README.md` for details.

## Settings Kept Elsewhere

Crowd detection and behaviour analytics settings are **not** in this folder. They
live in each module's `config.py` or module constants, and most can be
overridden with environment variables:

- `crowd_detection/config.py` - `CROWD_DEVICE`, `CROWD_DETECT_STRIDE`, `CROWD_SKIP_EMPTY_TILES`, `CROWD_DETECT_MAX_WIDTH`, confidence/IoU thresholds, tiling switches
- `crowd_behaviour_analytics/` - `CROWD_TREND_*`, `CROWD_POSE_REFINEMENT`, `CROWD_TRACK_BUCKET`, `CROWD_MOTION_ANNOTATION_MAX_FRAMES`, `CROWD_MOTION_FLOW_WIDTH`

See each module's README for the full list.
