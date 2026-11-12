# Crowd-detection benchmark tools

Comparison tool for crowd-detection weights. It runs several YOLO models over
the same footage under controlled conditions and reports speed, per-frame counts
and, when hand-labelled frames are supplied, accuracy.

The tool is deliberately sceptical about its own output. Most of the design is
about preventing the two failure modes that make detection benchmarks lie:
counting a different class in each column, and treating a raw box count as if it
were a crowd size.

It was a single `benchmark_models.py` script; it is now a small package. `main.py`
is the entry point and everything is run from inside the `benchmarking/`
directory.

## Contents

- [Requirements](#requirements)
- [Layout](#layout)
- [Modules](#modules)
- [Setup](#setup)
- [Modes](#modes)
- [Configuration](#configuration)
- [Ground truth](#ground-truth)
- [Tiled inference](#tiled-inference)
- [Reading the output](#reading-the-output)
- [Results files](#results-files)
- [Caveats](#caveats)
- [Troubleshooting](#troubleshooting)

## Requirements

- Python 3.10+
- `ultralytics`, `torch`, `torchvision`, `opencv-python`
- A GPU is optional. On CPU the tiled path is slow enough that you will want to
  drop `--frames` well below the default.

## Layout

Paths are resolved relative to the package directory
(`SCRIPT_DIR = Path(__file__).resolve().parent` in `config.py`), so there is no
depth-sensitive `parents[N]` index to keep in sync any more. The package expects
to sit next to `crowd_detection/`:

```
Crowd_Monitoring/
  crowd_detection/
      yolov8n_crowdhuman.pt      <- 26T1 baseline weight, referenced in place
  benchmarking/
      main.py                    <- entry point
      config.py core.py measure.py scoring.py tiling.py inspection.py
      extract_truth_frames.py
      videos/
          side.mp4               <- committed sample clip
      results/                   <- timestamped run outputs land here
      yolo11n.pt yolo26n.pt      <- stock COCO weights (auto-downloaded if absent)
```

The `crowd_detection/yolov8n_crowdhuman.pt` weight is referenced in place rather
than copied, to avoid duplicating a binary. If you move `benchmarking/` so it is
no longer a sibling of `crowd_detection/`, fix `MODEL_CROWDHUMAN` in `config.py`.

## Modules

| Module | Responsibility |
| --- | --- |
| `main.py` | Argument parsing and mode dispatch. |
| `config.py` | All constants: `MODELS`, `VIDEO_PATHS`, thresholds, tile geometry, `MODEL_CLASS_OVERRIDES`. Edit this to add a model or clip. |
| `core.py` | Model loading, class-by-name resolution, frame reading, single-frame counting. |
| `measure.py` | The benchmark and sweep loops. |
| `scoring.py` | Ground-truth loading, MAE/RMSE, writing result JSON to `results/`. |
| `tiling.py` | Tile grid and full-resolution tiled inference with cross-tile NMS. |
| `inspection.py` | `--diagnose` and `--show`. |
| `extract_truth_frames.py` | Standalone helper: dumps a handful of frames to `truth_frames/` for hand-labelling. |

## Setup

`side.mp4` is committed under `benchmarking/videos/` and already wired up as a
sample clip. To benchmark against other footage, add clips there and point
`VIDEO_PATHS` (in `config.py`) at them:

```python
VIDEO_PATHS = [
    SCRIPT_DIR / "videos" / "side.mp4",
    SCRIPT_DIR / "videos" / "new_test.mp4",
]
```

Each clip is benchmarked separately. Metrics stay per-clip and ground-truth frame
indices never collide across clips.

Models are declared in the `MODELS` dict in `config.py`. Values are either a
filesystem path (validated up front, so a missing weight fails clearly) or a bare
Ultralytics name (resolved and downloaded on first load). The current set:

```python
MODELS = {
    "26T1 (v8 crowdhuman)": MODEL_CROWDHUMAN,   # local path
    "yolo26n (stock coco)": "yolo26n.pt",       # bare name
    "yolo11n (stock coco)": "yolo11n.pt",       # bare name
}
```

The keys are the labels you pass to `--diagnose` and `--show`.

## Modes

Modes are mutually exclusive and resolved in this order: `--diagnose`, then
`--sweep`, then `--show`, then the default benchmark. Passing more than one means
only the first takes effect. Run everything from the `benchmarking/` directory.

### Default: benchmark

```bash
python main.py
python main.py --frames 100 --truth truth.json
python main.py --compare-tiling --truth truth.json
python main.py --no-save            # print only, don't write results/
```

Runs every model against every video and prints one result dict per run. A
warm-up pass on the same code path precedes timing, so setup overhead is not
counted. Failures are caught per run, so one missing weight does not sink the
batch; skipped runs are summarised at the end.

Unless `--no-save` is passed, the run is also written to
`results/benchmark-<timestamp>.json` along with the settings that produced it.
See [Results files](#results-files).

`--compare-tiling` runs each model both tiled and untiled. That is the only valid
tiling comparison: same model, same clip, one variable changed.

### `--sweep`

```bash
python main.py --sweep --frames 20
```

Prints average per-frame count for every model at confidence 0.05, 0.10, 0.20,
0.35 and 0.50 (`SWEEP_THRESHOLDS`), followed by a stability figure per model.

This is the mode that exposes confidence calibration. A stock COCO model may only
detect crowd members at low confidence, so its count collapses toward zero at a
normal threshold while a domain-tuned model holds steady. A single-threshold
benchmark hides that difference entirely and reads as a capability gap when it is
actually a calibration gap.

Stability is `max - min` average count across the thresholds. Lower is better.
It is internal to each model's own series, so it stays valid even when two
columns are counting different classes.

Sweep ignores `--conf` and `--truth`, and writes nothing to disk. It honours
`--frames` and `--tiled`.

### `--diagnose LABEL`

```bash
python main.py --diagnose "26T1 (v8 crowdhuman)"
```

`LABEL` must be a key of `MODELS`. Inspects one model: its class map, training
`imgsz`, device, resolved target class, tile count for the frame size, and what
it detects on the first frame of each clip at conf 0.35, 0.10 and 0.01.

Two things make this the first stop for a zero-count result:

1. It separates "the model sees nothing" (capability gap) from "the model sees
   things it does not class as your target" (filter or class-mapping issue).
2. It prints median box height per class, which is how you confirm an unnamed
   class map. On the same footage, taller boxes are bodies and shorter ones are
   heads or faces. The rough ratios are head:body about 1:7.5 and face:body about
   1:15.

Run this before committing any `MODEL_CLASS_OVERRIDES` entry. A wrong index
counts the wrong thing without ever raising.

`--diagnose` ignores `--tiled`, `--conf` and `--frames`.

### `--show LABEL`

```bash
python main.py --show "26T1 (v8 crowdhuman)" --conf 0.10
python main.py --show "26T1 (v8 crowdhuman)" --tiled --save
```

`LABEL` must be a key of `MODELS`. Plays each clip with detections drawn and a
header showing model, clip, counted class and threshold. Press `q` to quit; that
ends playback of the remaining clips too.

`--save` also writes `annotated_<model>_<clip>[_tiled].mp4` at full resolution.
`--show-scale` only affects the on-screen window, never inference or the saved
file.

Dropping `--conf` to around 0.10 is how you see what an under-confident stock
model actually perceives. If it draws nothing at 0.35, that is the calibration
result, not a bug.

With `--tiled`, this is the quickest way to check cross-tile NMS: look for boxes
clustering along tile seams or objects double-boxed in the overlap regions.

## Configuration

All of these live in `config.py`.

| Constant | Default | Notes |
| --- | --- | --- |
| `DEFAULT_CONF` | `0.35` | Overridable with `--conf` |
| `DEFAULT_IOU` | `0.30` | Not exposed on the CLI, edit the constant |
| `DEFAULT_N_FRAMES` | `50` | Overridable with `--frames` |
| `DEFAULT_MAX_DET` | `5000` | See below |
| `SWEEP_THRESHOLDS` | `(0.05, 0.10, 0.20, 0.35, 0.50)` | Confidence points for `--sweep` |
| `GROUND_TRUTH_PATH` | `None` | Default for `--truth` when the flag is omitted |
| `TILE_SIZE` | `640` | Should match the model's `imgsz` |
| `TILE_OVERLAP` | `192` | Must exceed the largest object being counted |
| `TILE_BATCH` | `8` | Tiles per forward pass |
| `DEFAULT_SHOW_SCALE` | `0.5` | Display only |

`max_det` is raised from the Ultralytics default of 300 because that default
silently truncates dense frames. A 300-box result under the default is a cap, not
a count. Diagnose warns explicitly when a result hits the cap.

### Class resolution

The target class is resolved by name, not by hardcoded index, so body, head and
face models all work. Order of resolution:

1. An explicit `MODEL_CLASS_OVERRIDES` entry for that label.
2. First match from `COUNT_CLASS_PREFERENCE`, currently `person`, `head`, `face`.
3. The sole class, for a genuine single-class model.
4. Otherwise raise, listing the model's actual class names.

Overrides exist because some weights ship without real class names. Ultralytics
falls back to stringified indices (`{0: '0', 1: '1'}`) when the training YAML had
no `names:` list, and name lookup cannot work against that. The `config.py`
example override maps class 1 of a `yolo26m (crowdpeoplefaces)` weight to `head`,
confirmed by median box height: about 1:6.6 on `new_test.mp4` and 1:5.1 on
`side.mp4`, both in head territory rather than face. That weight is not in the
current `MODELS` set; the entry is kept as a worked example of how to add one.

Every result row carries `counted_class`, because a person count and a head count
are not the same quantity.

## Ground truth

Without `--truth`, the script prints a notice and `avg_count` is a box count, not
accuracy. Supply hand-labelled frames to get MAE and RMSE, the standard
crowd-counting metrics.

`extract_truth_frames.py` is the helper for producing those labels. It writes a
handful of frames (`FRAMES = [0, 10, 20, 30, 40]` by default) from one clip into
`truth_frames/` as JPEGs:

```bash
python extract_truth_frames.py
```

Hand-count each image, then record the counts in a JSON file keyed per clip by
filename stem, so frame 5 in clip A and frame 5 in clip B do not overwrite each
other:

```json
{
  "side":     { "0": 118, "10": 121, "20": 117 },
  "new_test": { "0": 42, "10": 43, "17": 40 }
}
```

Keys are strings in the file and normalised on load: outer keys stay strings,
inner keys become ints. Scoring covers only the labelled frames present within
the range actually read, so labelling frame 200 while running `--frames 50` does
nothing. Clips with no entry are reported as counts only.

Point the run at the file with `--truth path/to/truth.json`, or set
`GROUND_TRUTH_PATH` in `config.py` so it is picked up without the flag.

## Tiled inference

`--tiled` runs one forward pass per tile at native scale instead of a single
downscaled pass over the whole frame. That is the entire point: a 4K frame
resized to 640 loses roughly 97% of its pixels and shrinks heads below the
detector's size floor.

Boxes are reprojected from tile coordinates to frame coordinates, then a global
NMS collapses detections duplicated in the overlap regions.

Two constraints matter:

- `TILE_OVERLAP` must exceed the largest object being counted. An object
  straddling a seam with insufficient overlap is clipped in both tiles, and NMS
  may not merge the two partial boxes. Heads measured about 108px median on
  `side.mp4`, so 192 leaves margin.
- Tiling is a no-op when the frame is no larger than the tile. The script prints
  a note in that case rather than pretending otherwise.

Cost scales with tile count. Drop `--frames` accordingly.

## Reading the output

Benchmark rows look like:

```python
{'label': '26T1 (v8 crowdhuman)', 'video': 'side.mp4',
 'model': 'yolov8n_crowdhuman.pt', 'counted_class': 'person', 'tiled': False,
 'device': 'cpu', 'model_size_mb': 6.2, 'frames_tested': 50,
 'avg_latency_ms': 25.85, 'fps': 38.69, 'avg_count': 21.9,
 'mae': 2.1, 'rmse': 2.8, 'n_labelled': 10}
```

Rows are only cross-comparable where **both** `counted_class` and `tiled` match.
A head count and a body count are different quantities, and so are a tiled and an
untiled count.

`n_tiles` appears on tiled rows. `mae`, `rmse` and `n_labelled` appear only when
truth covered that clip.

The rows are printed to stdout as they complete. In benchmark mode they are also
saved to `results/` unless `--no-save` is passed; `--sweep` prints only.

## Results files

Each default-mode run (without `--no-save`) writes
`results/benchmark-<YYYYMMDD-HHMMSS>.json`:

```json
{
  "timestamp": "20260819-160821",
  "settings": {
    "conf": 0.35, "iou": 0.3, "n_frames": 50,
    "tiled": false, "compare_tiling": false, "truth_supplied": false,
    "tile_size": 640, "tile_overlap": 192,
    "torch": "2.13.0+cpu", "cuda_available": false
  },
  "results": [ /* the same row dicts printed to stdout */ ],
  "skipped": [ { "label": "...", "tiled": false, "video": "..." } ]
}
```

`settings` records everything that affects the numbers (thresholds, frame count,
tiling geometry, torch build, CUDA availability) so a result file is
self-describing and old runs stay interpretable. `skipped` lists runs that failed
and why they are absent from `results`.

## Caveats

These are the ones that will bite an unwary reader of the numbers:

- **More boxes is not more accurate.** Tiling always finds more. The extra
  detections may be genuine small heads recovered at full resolution, or seam
  duplicates and false positives. Those two cases are indistinguishable from the
  count alone. Without `--truth`, a higher tiled count is not evidence that
  tiling is better.
- **`avg_count` is not crowd size.** It is the number of boxes surviving the
  threshold.
- **Low-threshold sweep rows are not ground truth.** Counts at 0.05 include
  duplicates and false positives by design; the point of including them is to
  show the shape of the curve.
- **A capped count is not a measurement.** If a run hits `max_det`, raise it.
- **A wrong class override fails silently.** Verify with `--diagnose` first.

## Troubleshooting

**`Model not found: ...`** - a local path in `MODELS` is wrong, most likely
because `benchmarking/` is no longer a sibling of `crowd_detection/` and
`MODEL_CROWDHUMAN` no longer resolves.

**`No countable class ... found`** - the weight has no `person`/`head`/`face`
class name, probably unnamed classes. Run `--diagnose`, read the median box
heights, then add a `MODEL_CLASS_OVERRIDES` entry.

**`VIDEO_PATHS is empty`** - no clips configured in `config.py`.

**`No frames read from ...`** - the file exists but OpenCV cannot decode it.
Check the codec.

**`argument --diagnose/--show: invalid choice`** - the label must match a key of
`MODELS` exactly, quoting included.

**Every count is 0 at conf 0.35** - not necessarily a broken model. Run `--sweep`
and check whether counts appear at 0.10 or 0.05. If they do, it is calibration.

**Tiled run appears hung** - check the printed tile count. Tiles per frame times
frames is the real work; the default 50 frames is usually far too many when
tiling.
