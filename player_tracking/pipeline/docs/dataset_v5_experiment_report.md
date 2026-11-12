# Orion T2 Ball Detection — Dataset V5 Experiment Report

## Objective

Dataset V5 investigated whether additional reviewed ball examples and
model-selected hard examples could improve the Dataset V4 detector. The main
targets were missed held balls, overlapping players, shoes, socks, clothing and
broadcast graphics that resembled the ball.

This remained a separate experiment. It did not modify the active Project
Orion player-tracking service or replace the Dataset V4 detector.

## Team contribution and review

Fortune contributed a corrected batch of 29 positive yellow-ball examples from
Brisbane Lions–Port Adelaide footage. Thani reviewed the initial submission,
identified loose boxes, outside-ball annotations and replay duplication, gave
specific correction feedback, and completed the final technical and visual
audit.

The corrected partner batch passed the following checks:

- 29 matching image and label files;
- 29 `BALL` boxes using class ID 0;
- no empty or invalid label rows;
- no exact or near duplicates within the batch; and
- no exact or near duplicates against Dataset V4.

Thani also used the Dataset V4 model to mine CAR–GCS frames containing multiple
competing ball predictions. Because one match normally has only one active
ball, these frames exposed shoes, clothing and broadcast graphics that the
model could confuse with the ball. Thirty images were manually reviewed in
Label Studio:

- 19 images received one genuine `BALL` box;
- 8 images were confirmed as empty negative examples; and
- 3 uncertain images remained unfinished and were excluded.

## Dataset construction

Dataset V5 was created as a new folder, leaving Dataset V4 unchanged. The exact
Dataset V4 validation images and labels were preserved byte-for-byte. All new
reviewed examples entered training only.

### Dataset V4

| Split | Images | BALL boxes | Negative images |
|---|---:|---:|---:|
| Train | 187 | 136 | 51 |
| Validation | 19 | 13 | 6 |

### Dataset V5 additions

| Source | Images | BALL boxes | Negative images |
|---|---:|---:|---:|
| Corrected partner batch | 29 | 29 | 0 |
| Competing-detection review | 27 | 19 | 8 |
| Total additions | 56 | 48 | 8 |

### Dataset V5

| Split | Images | BALL boxes | Negative images |
|---|---:|---:|---:|
| Train | 243 | 184 | 59 |
| Validation | 19 | 13 | 6 |

The three unfinished competing-detection images were excluded rather than
being incorrectly treated as negative examples.

Verified cumulative Label Studio export:

`ball_only_pilot/exports/orion_t2_ball_detection_batches_01_07_yolo_2026-08-23.zip`

Archive SHA-256:

`0d6781810296d1271bbfd07e97ff159742f7acd649f5ba3a8133e1397f83a737`

## Training setup

Dataset V5 used the same main experiment conditions as Dataset V4:

- starting weights: `models/all_classes_best.pt`;
- epochs: 30;
- image size: 960;
- batch size: 4;
- device: CPU;
- workers: 0;
- random seed: 42; and
- deterministic training enabled.

A one-epoch smoke test completed successfully before the full run. The full
training run completed all 30 epochs in approximately 2.87 hours and saved
separate `best.pt` and `last.pt` weights.

V5 best weights:

`ball_only_pilot/training_runs/dataset_v5_30epochs/weights/best.pt`

## Fixed-validation comparison

V4 and V5 were evaluated using the same unchanged 19-image validation split,
which contains 13 labelled balls and 6 negative images.

| Metric | V4 | V5 | Result |
|---|---:|---:|---|
| Precision | 0.5453 | 0.4340 | Lower |
| Recall | 0.5385 | 0.5380 | Approximately unchanged |
| mAP50 | 0.5217 | 0.3660 | Lower |
| mAP50–95 | 0.1670 | 0.1370 | Lower |

An intermediate V5 epoch reached a higher mAP50 value, but the standard
Ultralytics `best.pt` selection was retained for consistent model comparison.
The saved V5 best model did not improve the overall fixed-validation result.

## Fixed CAR–GCS video comparison

Both models were tested on the same 598-frame CAR–GCS development clip at image
size 1280. Detection counts include correct and incorrect detections and must
therefore be interpreted alongside visual review.

| Measure | V4 | V5 |
|---|---:|---:|
| Total detections at confidence 0.05 | 458 | 631 |
| Frames with a detection | 340 | 336 |
| Maximum confidence | 0.734 | 0.655 |
| Detections at confidence 0.20 | 199 | 226 |
| Detections at confidence 0.30 | 145 | 126 |
| Detections at confidence 0.40 | 94 | 63 |
| Detections at confidence 0.50 | 57 | 13 |

Visual review found that V5 was noisier and continued to detect shoes and
socks as the ball. It generated more low-confidence predictions while producing
fewer high-confidence predictions than V4.

## Protected St Kilda–North Melbourne holdout

The same 500-frame protected holdout was tested at image size 1280. No frames
from this match were added to any training or validation dataset.

| Measure | V4 | V5 |
|---|---:|---:|
| Total detections at confidence 0.05 | 400 | 717 |
| Frames with a detection | 261 | 322 |
| Maximum confidence | 0.888 | 0.587 |
| Detections at confidence 0.20 | 186 | 226 |
| Detections at confidence 0.30 | 151 | 139 |
| Detections at confidence 0.40 | 132 | 90 |
| Detections at confidence 0.50 | 114 | 26 |

Visual review at confidence 0.20 produced three important findings:

- V5 still falsely detected the yellow referee;
- V5 detected the ball while it was held by the referee, improving a V4 miss;
- V5 recovered the ball after player overlap, as V4 did; and
- V5 produced many additional shoe detections.

V5 therefore improved one difficult held-ball case but reduced overall visual
cleanliness and confidence.

## Interpretation

The V5 additions were strongly positive-heavy: 48 new positive images compared
with only 8 new negative images. This may have increased sensitivity to ball-like
colours and shapes without providing enough diverse negative evidence to
control false detections.

The small fixed validation set also makes individual errors influential, so
video evidence remains essential. Both the validation metrics and visual video
review point in the same direction: V5 is not a reliable improvement over V4.

## Decision

Dataset V4 remains the current best ball-detector pilot. Dataset V5 and its
weights are preserved as a valid experimental result but must not replace V4 or
be integrated into the active Orion service.

The V5 result is useful because it demonstrates that increasing annotation
quantity alone does not guarantee improvement. Dataset composition, negative
diversity and consistent evaluation are critical.

## Recommended next steps

1. Keep Dataset V4 and its best weights as the detector baseline.
2. Preserve Dataset V5, its weights, logs and evidence without using it in the
   temporal tracker.
3. Review V5 false-positive timestamps and identify underrepresented negative
   categories, particularly yellow referees, red shoes, socks and clothing.
4. Collect a balanced negative batch from development footage while keeping
   the St Kilda holdout protected.
5. Avoid another full training run until the negative batch has been reviewed
   and its purpose is clearly documented.
6. Compare any future detector with V4 using the same validation set, inference
   settings and protected video clips.
