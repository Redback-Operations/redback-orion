# Fire Detection

## Objective

Detect fire and smoke in stadium footage from extracted frames, and
flag the responsible zone.

## Recommended Structure

```text
fire_detection/
|- README.md
|- SCHEMA.md
|- main.py
`- output/
```

### Why This Structure

- `main.py` keeps the task simple and easy to understand
- `output/` stores sample frames and generated detection JSON when run
  as a demo
- add `utils.py` only if `main.py` becomes messy or too long

## Correct Approach

- keep the real implementation for this task inside this folder
- write the main fire/smoke detection logic in `main.py`
- save generated files inside `output/`
- if helper code starts repeating, then create `utils.py`
- the shared service layer can later call functions from this task
  folder

## Scope

- Classify frames as fire / smoke / neither
- Locate a bounding box around the largest fire-colored region
- Assign a confidence score and a severity bucket
- Attach `camera_id` / `zone_id` so downstream aggregation knows which
  zone the event belongs to

## Inputs

- Frame metadata from the Video Processing task (`video_id`,
  `frames[].frame_id` / `timestamp` / `frame_path`)
- `camera_id` / `zone_id`, supplied by the caller per video (see
  Implementation Notes)

## Outputs

- One detection object per frame: `fire_detected`, `smoke_detected`,
  `confidence`, `severity`, and `bounding_box` when fire is found

See `SCHEMA.md` for the exact JSON shape.

## Implementation Notes

- This uses a classic HSV color-threshold method (no model file to
  download, runs instantly), not a trained detector. It is more prone
  to false positives than an ML approach (stage lighting, orange
  signage, skin tones can all trigger it), and the smoke check is a
  rough brightness/saturation heuristic, not a reliable detector.
- `camera_id` / `zone_id` are not part of the Video Processing frame
  metadata contract. Since one video maps to one fixed camera/zone,
  they're passed in per-video by the caller rather than derived from
  the image itself.
- Running `python main.py` with no arguments builds two synthetic demo
  frames (one plain, one with a painted-in fire-colored patch) and
  runs the detector on them, matching how other task folders are
  runnable standalone. Pass a real frame-metadata JSON path to run
  against actual frames: `python main.py <frame_metadata.json>
  [camera_id] [zone_id]`.

## Suggested Deliverables

- `main.py` implementing the color-threshold fire/smoke detector
- Example output using the built-in demo frames or a sample video
