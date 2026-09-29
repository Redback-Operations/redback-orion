# Orion T2 Ball Detection — Dataset V4 Experiment Report

## Objective

Evaluate whether a targeted dataset expansion improves AFL ball detection,
particularly for fast, blurred, distant and partly occluded balls, while
reducing false detections from players, referees and crowd objects.

## Starting point

Dataset V3 produced useful red- and yellow-ball detections and substantially
reduced the hard-negative false detections measured in the V2 comparison.
However, visual review showed that it still:

- detected some shoes, clothing, referees and crowd objects as balls;
- lost the real ball during fast or motion-blurred movement;
- struggled with small, distant and heavily occluded balls; and
- could not maintain one reliable ball ID when used with standard ByteTrack or
  BoT-SORT tracking.

## Coordination and partner contribution

Thani prepared a five-minute Brisbane–Port Adelaide scouting clip and gave a
beginner-friendly review task to another Player Tracking team member. The team
member identified ten timestamps containing difficult ball visibility,
lookalikes, fast movement, blur and occlusion.

Thani reviewed frames around those timestamps, applied the existing ball
labelling rules, and classified examples as positive, negative or unsuitable.
A combined Label Studio batch was then reviewed. The final export contained:

- 45 completed new images;
- 36 positive images containing one labelled ball;
- 9 confirmed negative images; and
- 1 unfinished image that remained excluded because it was uncertain.

The partner observations and Thani's review decisions are stored under
`videos/partner_clip_review/`.

## Dataset development

### Dataset V3

- Training images: 142
- Training ball boxes: 100
- Training negative images: 42
- Validation images: 19
- Validation ball boxes: 13
- Validation negative images: 6

### Dataset V4

- Training images: 187
- Training ball boxes: 136
- Training negative images: 51
- Validation images: 19
- Validation ball boxes: 13
- Validation negative images: 6
- Class mapping: `0 = BALL`

Dataset V4 contains 206 images in total, an increase of 45 images over V3.
The exact V3 validation images and labels were preserved in V4. Newly reviewed
examples entered training only.

The verified cumulative Label Studio export is:

`ball_only_pilot/exports/orion_t2_ball_detection_batches_01_07_yolo_2026-08-06.zip`

Archive SHA-256:

`ac80b98a85ff9cb9181ba8ec1c26af0991ce06b3cdb296e93b60f3decdfc76d8`

## Training setup

V3 and V4 used the same experiment settings:

- Starting weights: `models/all_classes_best.pt`
- Epochs: 30
- Input image size: 960
- Batch size: 4
- Device: CPU
- Workers: 0
- Random seed: 42
- Deterministic training: enabled

V4 best weights:

`ball_only_pilot/training_runs/dataset_v4_30epochs/weights/best.pt`

## Fixed-validation comparison

Both best models were evaluated on the same preserved 19-image validation set
containing 13 labelled balls and 6 negative images.

| Metric | V3 | V4 | Result |
|---|---:|---:|---|
| Precision | 0.4766 | 0.5453 | Improved |
| Recall | 0.5614 | 0.5385 | Slightly lower |
| mAP50 | 0.4972 | 0.5217 | Improved |
| mAP50–95 | 0.1962 | 0.1670 | Lower |

V4 was more precise and improved mAP50, but recall decreased slightly and its
stricter bounding-box score was lower. This suggests that V4 became more
selective but did not improve tight box placement. Because the validation set
contains only 13 ball instances, these changes must be interpreted alongside
video evidence rather than treated as a final accuracy claim.

## CAR–GCS red-ball comparison

The same 598-frame CAR–GCS clip was evaluated with both models at image size
1280. Detection counts include both correct and incorrect detections.

| Measure | V3 | V4 |
|---|---:|---:|
| Total detections at confidence 0.05 | 333 | 458 |
| Frames with a detection | 247 | 340 |
| Maximum confidence | 0.842 | 0.734 |
| Detections at confidence 0.20 | 127 | 199 |
| Detections at confidence 0.30 | 74 | 145 |
| Detections at confidence 0.40 | 42 | 94 |
| Detections at confidence 0.50 | 26 | 57 |

Visual review at confidence 0.20 found that V4 followed the real red ball more
often than V3. Some incorrect detections remained, and the model still lost the
ball during very fast movement.

## Brisbane–Port Adelaide yellow-ball comparison

The same 425-frame held-out segment was evaluated with both models at image
size 1280.

| Measure | V3 | V4 |
|---|---:|---:|
| Total detections at confidence 0.05 | 828 | 387 |
| Frames with a detection | 378 | 275 |
| Maximum confidence | 0.880 | 0.860 |
| Detections at confidence 0.20 | 302 | 218 |
| Detections at confidence 0.30 | 214 | 192 |
| Detections at confidence 0.40 | 147 | 165 |
| Detections at confidence 0.50 | 118 | 130 |

V4 produced fewer low-confidence detections while producing more detections at
confidence 0.40 and 0.50. Visual review at confidence 0.20 found consistent
real-ball detections and no obvious false positives in the reviewed clip. The
model still lost the ball during fast movement and when the crowd formed a
difficult background.

## Important test limitation

The exact yellow-ball test segment was excluded from training and validation,
so there is no direct frame leakage. However, Dataset V4 contains other frames
from the same Brisbane–Port Adelaide broadcast. The yellow clip is therefore a
held-out same-match evaluation, not a completely independent match test.

The CAR–GCS clip is also useful as a fixed development comparison, but the
project dataset contains CAR–GCS imagery. A new broadcast match that contributes
no training images is still required to measure external generalisation.

## Result

Dataset V4 is a useful incremental detector improvement. It increased fixed-set
precision and mAP50, followed the red ball more often in visual review, and
produced cleaner high-confidence behaviour in the reviewed yellow-ball clip.
However, it did not improve every validation metric. Tight box quality was
lower, recall decreased slightly, some false detections remained, and fast or
visually obscured movement continued to break detection.

V4 should therefore be treated as the current best pilot candidate, not as a
finished ball-tracking solution.

## Recommended next steps

1. Obtain a completely unused broadcast match and run V3/V4 comparison without
   adding any of its frames to training first.
2. Record precise false-positive and missed-ball timestamps from that match.
3. Use those failures to decide whether a small Dataset V5 batch is justified.
4. Prototype a ball-specific temporal tracker that:
   - predicts short-term ball position;
   - bridges brief detection gaps;
   - considers confidence, size, distance and motion;
   - rejects persistent stationary background detections; and
   - avoids assigning valid ball tracks to shoes or clothing.
5. Compare the temporal tracker with the existing ByteTrack and BoT-SORT
   baselines using track duration, track breaks, false tracks and ID continuity.
6. Keep the experimental detector and tracker separate from the active Orion
   service until the team reviews the evidence and integration approach.
