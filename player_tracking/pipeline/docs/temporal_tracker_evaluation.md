# Ball-Specific Temporal Tracker — Protected Evaluation

## Purpose

This evaluation measures whether the Version 3 ball-specific temporal tracker
improves on frame-level output from the V4 ball-only detector. It uses a
protected St Kilda–North Melbourne sequence that was not used to train V4 or
tune the tracker.

The work remains an experimental pilot and does not modify the active Project
Orion player-tracking service.

## Ground-truth policy

Fifty consecutive frames were manually reviewed using one class:

```text
0 = BALL
```

The rules were:

- label only the active match ball;
- use one tight, straight bounding box with minimal surrounding content;
- submit an empty annotation when no ball pixels can be identified; and
- exclude genuinely uncertain frames rather than guessing.

| Outcome | Frames |
|---|---:|
| Completed positive frames | 33 |
| Completed empty frames | 10 |
| Uncertain frames excluded | 7 |
| Total reviewed | 50 |

The 43 completed image-label pairs passed class, coordinate, file-pairing and
visual box-quality checks. These frames and labels are evaluation-only and
must never enter training or tracker tuning.

## Evaluation settings

| Setting | Value |
|---|---|
| Detector | V4 ball-only model |
| Detector confidence | 0.05 |
| Inference image size | 1280 |
| Temporal tracker | Algorithm Version 3 |
| Main IoU threshold | 0.30 |
| Additional thresholds | 0.10 and 0.50 |

The detector was run directly on the completed images. Tracker rows from the
frozen holdout run were matched to the original source-frame numbers.

## Main result

| Measure at IoU 0.30 | V4 detector | Temporal tracker |
|---|---:|---:|
| Visible positive frames | 33 | 33 |
| Correctly located visible balls | 29 | 29 |
| Missed visible balls | 4 | 4 |
| Visible-ball recall | 0.8788 | 0.8788 |
| Visually empty frames | 10 | 10 |
| Output on visually empty frames | 3 | 6 |
| Mean IoU for successful frames | 0.8322 | 0.8144 |

At the main threshold, the tracker did not improve visible-ball recall and
produced output on more visually empty frames.

| IoU threshold | Detector recall | Tracker recall |
|---:|---:|---:|
| 0.10 | 0.8788 | 0.9091 |
| 0.30 | 0.8788 | 0.8788 |
| 0.50 | 0.8788 | 0.8182 |

Temporal prediction recovered detector misses at source frames 303 and 343.
However, the tracker failed to preserve valid detector locations at frames 306
and 307. The two recovered frames and two lost frames therefore cancelled each
other at IoU 0.30.

## Limitation

Output on a visually empty frame is not automatically a proven tracking error.
The ball may be fully hidden behind a player, and a motion-based prediction may
still be plausible. Because the true hidden location cannot be observed, these
cases are described as unsupported predictions rather than confirmed false
locations unless separate visual evidence demonstrates drift.

The most reliable comparison is visible-ball localisation. On that measure,
the tracker matched but did not improve the detector at IoU 0.30.

## Decision

The Version 3 temporal tracker remains an experimental prototype. Short
temporal prediction can recover individual detector misses, but the current
implementation does not provide a reliable overall improvement and should not
be integrated into the active Orion service.

The V4 detector remains the recommended model. Protected evaluation data,
model weights and generated results are intentionally excluded from Git.

## Reproducing the evaluation

The evaluation utility is
[`scripts/evaluate_temporal_tracker.py`](../scripts/evaluate_temporal_tracker.py).
It requires explicit paths so no local datasets or models are assumed:

```bash
python scripts/evaluate_temporal_tracker.py \
  --ground-truth path/to/evaluation_ground_truth.zip \
  --model path/to/ball_detector_best.pt \
  --tracker-csv path/to/temporal_tracker_output.csv
```

By default, the script writes a per-frame CSV and JSON summary under
`outputs/temporal_tracker_evaluation/`, which is excluded from Git.

## Next steps

1. Investigate track termination and prediction-confidence decay using
   separate development footage.
2. Explore whether player-overlap information can distinguish occlusion from
   drift onto clothing or officials.
3. Freeze any revised settings before evaluation.
4. Evaluate the revision on a new untouched sequence rather than reusing this
   protected sequence for tuning.
