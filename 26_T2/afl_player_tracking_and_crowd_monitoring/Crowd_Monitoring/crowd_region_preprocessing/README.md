# Crowd Region Preprocessing

## Objective

Black out fixed, non-crowd parts of the stadium frame (roof, signage, concourse,
foreground rails) before crowd detection runs. This stops the detector wasting time
on those areas and reduces false positives there.

## Approach

The module only excludes regions. You mark the static structures to remove as
polygons, and everything else in the frame is kept.

There are deliberately no "keep" polygons and no automatic field detector:

- A keep region drawn around a moving crowd cuts off real people as soon as they move past its edge.
- The earlier green-field HSV detector also cut out crowd pixels that happened to be greenish.

## How It Works

1. `prepare_crowd_frames(processed_video)` reads `shared/config/crowd_region_preprocessing_config.json`.
2. It builds **one** keep-mask per video from `exclude_polygons_normalized`. The mask is `255` everywhere and `0` inside each exclude polygon. It depends only on the frame size, so it is built once per video, not once per frame.
3. The mask is attached to the video dict as `crowd_mask`, and `crowd_detection` applies it to each frame as it reads it. By default, no masked JPEGs are written.
4. Each frame gets `source_frame_path` (the original frame) and `crowd_focus_metadata.mask_source`, which is `"exclude xN"` or `"keep_all"` when no polygons are configured.

If the frame size can't be determined, the video passes through unmasked. If the
polygons cover the whole frame, a warning is printed.

## Configuration

`shared/config/crowd_region_preprocessing_config.json`:

```json
{
  "focused_frames_dir": "crowd_region_preprocessing/output/focused_frames",
  "write_focused_frames": false,
  "exclude_polygons_normalized": [
    [[0.0036, 0.5741], [0.1161, 0.6588], [0.0693, 0.6852], "..."],
    [[0.0023, 0.013], [0.4461, 0.2565], "..."]
  ]
}
```

| Key | Meaning |
|-----|---------|
| `exclude_polygons_normalized` | List of polygons to black out. Each polygon is a list of `[x, y]` points given as fractions (0-1) of frame width and height, so the same values work at any resolution. A single polygon (`[[x, y], ...]`) is also accepted. Leave it empty to keep the whole frame. |
| `write_focused_frames` | `true` also saves masked JPEGs to `focused_frames_dir` and points each frame's `frame_path` at them. Use this for debugging or the UI; the pipeline doesn't need it. |
| `focused_frames_dir` | Output folder for the masked JPEGs, relative to `crowd_monitoring/`. |

> The polygons are fixed for one camera view. They apply to every video, so
> re-pick them when the camera angle or venue changes.

## Picking Regions: `pick_region.py`

`pick_region.py` is an interactive OpenCV tool. You click polygons on a frame, and it
prints the matching `exclude_polygons_normalized` entry to paste into the config.

### Running It

Run from `crowd_monitoring/`, since it's a module inside the package:

```bash
python -m crowd_region_preprocessing.pick_region            # uses the first extracted frame
python -m crowd_region_preprocessing.pick_region path/to/frame.jpg
```

With no argument, it opens the first frame in `video_processing/data/extracted_frames/`,
falling back to `crowd_region_preprocessing/output/focused_frames/`. Raw frames are
tried first because focused frames already show the previous run's black regions.
Run `video_processing` once beforehand so there is a frame to open, or pass an image
path directly.

Frames wider than 1600 px are shrunk to fit on screen. Clicks are converted back
to full-resolution coordinates.

### Controls

| Input | Action |
|-------|--------|
| Left click | Add a point to the current polygon |
| Right click | Close the current polygon and start a new one |
| `u` | Undo the last point of the current polygon |
| `d` | Delete the most recent polygon |
| `n` | Start a new polygon |
| `r` | Reset (clear every polygon) |
| `s` / Enter | Finish and print the JSON |
| `q` / Esc | Quit without printing |

Completed polygons are filled with a translucent colour, alternating between
green and orange. The top-left counter shows how many polygons are complete and
how many points the current one has.

### Output

Only polygons with at least 3 points are kept. Coordinates are rounded to 4
decimal places:

```text
# from .../extracted_frames/frame_0001.jpg  (1920x1080) - 2 polygon(s)
Trace the fixed structures to REMOVE (roof, signage, concourse, foreground rails).
  "exclude_polygons_normalized": [[[0.0036, 0.5741], ...], [[0.0023, 0.013], ...]]
```

Replace the `exclude_polygons_normalized` line in the config file with the printed
line. The next pipeline run uses the new mask. To check the result, set
`write_focused_frames` to `true` and look in `output/focused_frames/`.

### Tips

- Trace structures that never contain spectators, such as the roof, big screens, advertising boards and rails in the foreground.
- Don't trace the crowd itself or the ground; anything left unmasked is still searched for people.
- Tiles that end up almost entirely masked are skipped by `crowd_detection`, so good exclude polygons also make detection faster.

## Project Structure

```text
crowd_region_preprocessing/
|- README.md
|- main.py            # prepare_crowd_frames(), mask building
|- pick_region.py     # interactive polygon picker
|- output/
   |- focused_frames/ # only when write_focused_frames is true
```
