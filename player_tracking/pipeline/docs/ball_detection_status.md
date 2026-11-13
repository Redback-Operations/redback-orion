# Ball Detection Pilot — Current Status

## Purpose

This work investigates a dedicated AFL ball detector before ball tracking and
trajectory generation are added to Project Orion. It remains an experimental
pilot and does not modify the active player-tracking service.

## Work completed

- Established a baseline showing that the original all-classes model produced
  no BALL detections on a fixed 20-second CAR–GCS clip.
- Audited the existing dataset and found only 29 BALL annotations.
- Defined consistent rules for visible, blurred, distant, held and partly
  occluded balls, as well as negative and uncertain examples.
- Built and evaluated several versioned ball-only datasets and models.
- Expanded Dataset V4 to 206 reviewed images: 187 training images and 19
  preserved validation images.
- Coordinated a beginner-friendly video scouting task with another team member,
  then reviewed and labelled the resulting candidate frames.
- Compared V3 and V4 on unchanged validation images and fixed video clips.
- Tested standard ByteTrack, BoT-SORT and a tuned ByteTrack configuration.
- Developed a ball-specific temporal tracker that bridges short detection gaps
  and rejects implausible track candidates.
- Reviewed and accepted a corrected 29-image yellow-ball batch contributed by
  Fortune after providing specific annotation feedback.
- Built Dataset V5 with 243 training images and the unchanged 19-image V4
  validation set, then completed a separate 30-epoch experiment.
- Compared V5 with V4 on the fixed validation set, the CAR–GCS development clip
  and the protected St Kilda–North Melbourne holdout.

## Current result

V4 improved fixed-set precision from 0.4766 to 0.5453 and mAP50 from 0.4972
to 0.5217. Visual review found that V4 followed the red ball more often and
gave cleaner high-confidence behaviour on the reviewed yellow-ball clip.

V5 increased the reviewed training set using 48 additional positive examples
and 8 additional negative examples. It detected a held ball that V4 missed,
but fixed-set precision fell to 0.4340 and mAP50 fell to 0.3660. On both fixed
video clips, V5 produced more low-confidence activity and visual review found
additional shoe and sock detections. V5 is therefore preserved as a useful
negative experiment and does not replace V4.

The detector is not finished. It can still lose the ball during fast or
occluded movement and can sometimes confuse shoes, clothing, referees or crowd
objects with the ball. The validation set is small, and the reviewed videos are
development or same-match tests rather than fully independent match evidence.

Standard trackers did not maintain one reliable ball identity. Lower tracking
thresholds admitted more false detections, while higher thresholds caused the
real ball track to break. The ball-specific temporal prototype rejected more
false tracks than the standard configurations, but its stricter filtering also
reduced real-ball coverage. Tracking therefore remains a separate experimental
phase based on the V4 detector.

## Documentation

- [`ball_detection_pilot.md`](ball_detection_pilot.md) — initial baseline and
  first labelling pilot.
- [`ball_labeling_guidelines.md`](ball_labeling_guidelines.md) — annotation and
  quality-review rules.
- [`ball_detection_v4_experiment.md`](ball_detection_v4_experiment.md) —
  Dataset V4 training and evaluation evidence.
- [`dataset_v5_experiment_report.md`](dataset_v5_experiment_report.md) —
  Dataset V5 construction, evaluation and the decision to retain V4.
- [`../configs/bytetrack_ball.yaml`](../configs/bytetrack_ball.yaml) — tuned
  experimental tracker configuration.

## Evidence storage

Full match videos, labelled datasets, Label Studio exports, model weights,
training runs and annotated evidence videos are intentionally excluded from
Git because they are large experimental artifacts. The experiment report
records dataset counts, settings, comparisons and important limitations.

## Next phase

1. Keep V4 as the detector baseline and preserve V5 as a documented negative
   experiment.
2. Continue the ball-specific temporal tracker using frozen V4 weights.
3. Measure real-ball coverage, predicted gap frames, false tracks and track
   continuity using the unchanged comparison clips.
4. Define how ball coordinates, confidence and trajectory output could be
   exposed without modifying the active service prematurely.
5. Present the detector and tracker evidence to the Player Tracking team before
   proposing integration.
