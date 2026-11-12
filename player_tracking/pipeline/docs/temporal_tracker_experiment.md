# Ball-Specific Temporal Tracker Experiment

## Purpose

This experiment investigates whether ball-specific temporal logic can improve
tracking continuity after the V4 ball-only detector produces frame-level
detections. The work remains a standalone pilot and does not modify the active
Project Orion player-tracking service.

The experiment focuses on a single active match ball. It attempts to connect
valid detections, bridge short missed-detection gaps and avoid creating tracks
from visually similar objects such as socks, shorts, referees and inactive
balls outside the field of play.

## Running the prototype

The tracker requires a video and a trained ball-detection model:

```bash
python scripts/track_ball_temporal.py data/videos/example.mp4 --model models/ball_only_best.pt
```

By default, it saves an annotated video, tracking CSV and JSON summary under `outputs/temporal_tracker/`. Model weights and generated outputs are not stored in Git. Green boxes represent detector observations, while orange boxes represent short motion-based predictions.

## Why a ball-specific tracker was investigated

The standard trackers were designed for larger objects that move more smoothly
and remain visible for longer periods. The AFL ball is small, can move rapidly,
can be blurred, and is frequently hidden by players.

Earlier tests on the complete 598-frame CAR–GCS development clip produced the
following results:

| Tracker | Tracked detections | Unique IDs | One-frame tracks | Longest track |
|---|---:|---:|---:|---:|
| Default ByteTrack, confidence 0.20 | 41 | 15 | 13 | 25 frames |
| Default BoT-SORT, confidence 0.20 | 17 | 15 | 13 | 2 frames |
| Tuned ByteTrack, confidence 0.20 | 48 | 14 | 11 | 25 frames |
| Tuned ByteTrack, confidence 0.05 | 49 | 14 | 11 | 26 frames |

Visual review found frequent ID changes. Lowering the threshold admitted many
more incorrect detections, including shoes and shorts, without establishing a
stable ball identity.

## Prototype design

The standalone prototype is implemented in
[`scripts/track_ball_temporal.py`](../scripts/track_ball_temporal.py). It uses the
V4 ball-only detector and writes:

- an annotated video;
- a CSV containing detected and predicted positions;
- a JSON run summary.

Detected positions are shown in green. Short motion-only predictions are shown
in orange and recorded as `predicted` rather than `detected`, so inferred
positions are not presented as detector ground truth.

### Version 1

V1 introduced:

- one active ball track at a time;
- constant-velocity position prediction;
- candidate selection using distance, confidence and box-size consistency;
- six-frame gap bridging;
- rejection of implausibly large or unusually shaped boxes.

### Version 2

V2 added:

- three-frame confirmation before starting a new track;
- 24-frame memory after visible predictions stop;
- rejection of incomplete confirmation sequences.

### Version 3

V3 added stricter active-play safeguards:

- minimum movement before accepting a new track;
- a smaller association-distance gate;
- a maximum 2× box-area change between associated detections;
- rejection counts for unconfirmed and size-inconsistent detections.

## CAR–GCS development comparison

All versions used the same V4 model, 1280-pixel inference size and CAR–GCS
development footage.

### Same 300-frame section

| Measure | V1 | V2 | V3 |
|---|---:|---:|---:|
| Real detection frames | 152 | 147 | 110 |
| Predicted bridge frames | 48 | 56 | 36 |
| Missing frames | 100 | 97 | 154 |
| Track starts | 5 | 3 | 3 |
| Longest track | 87 | 153 | 85 |
| Unconfirmed detection frames rejected | Not recorded | 0 | 31 |

V2 appeared strongest from continuity statistics alone. Visual review showed
that this conclusion was misleading: the longer memory also extended tracks on
a player's sock and head. CSV inspection showed one false track moving only
about one pixel across 24 detections. Another track contained sudden position
jumps of approximately 79–97 pixels and box-area changes greater than 2×.

V3 removed the reviewed sock and head false tracks. It produced less output,
but its output was cleaner. This established an intentional precision-first
policy: leave a frame blank when evidence is weak instead of maintaining a
confident track on the wrong object.

### Complete 598-frame V3 run

| Measure | V3 result |
|---|---:|
| Frames processed | 598 |
| Real detection frames | 151 |
| Predicted bridge frames | 67 |
| Frames with detected or predicted output | 218 |
| Missing frames | 380 |
| Track starts | 8 |
| Longest track | 85 frames |
| Unconfirmed detection frames rejected | 39 |
| Size-change detections rejected | 1 |

Visual review of the complete development clip found no false tracking on the
previously observed socks, shorts, player heads or inactive outside ball. The
ball was not detected frequently, but useful clean sequences were produced.

## Frozen tracker holdout evaluation

The V3 parameters were frozen before the tracker was run on the 20-second
St Kilda–North Melbourne clip. This clip was not used to tune V1–V3. It had
previously been inspected for detector evaluation, so it is described as a
tracker holdout rather than a completely blind detector test.

The frozen settings included:

- detector confidence: 0.05;
- new-track confidence: 0.15;
- confirmation frames: 3;
- visible prediction gap: 6 frames;
- lost-track memory: 24 frames;
- base association gate: 0.025 of frame diagonal;
- maximum association gate: 0.10 of frame diagonal;
- maximum area change: 2×;
- maximum box area: 0.004 of frame area.

### Quantitative holdout result

| Measure | Frozen V3 result |
|---|---:|
| Frames processed | 500 |
| Real detection frames | 106 |
| Predicted bridge frames | 68 |
| Frames with detected or predicted output | 174 |
| Missing frames | 326 |
| Track starts | 6 |
| Longest track | 51 frames |
| Oversized detections rejected | 53 |
| Size-change detections rejected | 16 |
| Unconfirmed detection frames rejected | 8 |

These counts describe tracker behaviour, not accuracy. Frame-level ball ground
truth was not available for this clip.

### Visual holdout observations

- Around 2 seconds, the detector still classified part of the yellow referee
  as the ball. The tracker did not remove this repeated false detection.
- Around 6 seconds, the visible yellow ball held by the referee was missed.
- Around 13 seconds, the tracker successfully recovered the ball after player
  overlap.
- Outside those cases, visual tracking was generally clean and useful.

The holdout was not used for further parameter tuning after these observations.

## Interpretation

The experiment demonstrates that ball-specific temporal rules can produce
longer useful sequences than the standard tracker baselines and can suppress
several persistent false tracks. It also shows that longer continuity is not
automatically better: V2 achieved the longest numerical track while visibly
following incorrect objects.

V3 is therefore the preferred prototype because it prioritises correctness
over coverage. It is not a finished continuous ball tracker. Its principal
remaining failures originate in the detector:

- yellow referee clothing can be classified as a yellow ball;
- a real ball held against a player or referee can be missed;
- fast, distant or heavily occluded balls still create detection gaps.

A temporal tracker cannot reliably recover a ball when the detector supplies
no usable position, and it cannot always reject a false object that is detected
consistently across multiple frames.

## Limitations

- Tracker parameters were developed on one short CAR–GCS clip.
- The tracker holdout contains only 500 frames from one additional match.
- No frame-by-frame tracking ground truth is available.
- Predicted positions use a simple constant-velocity model.
- The prototype assumes one active match ball.
- The movement-confirmation rule may reject a real ball that is held still.
- Detector colour bias remains visible on yellow clothing and crowd objects.
- This experiment has not been integrated with the Orion backend, frontend or
  player-tracking service.

## Recommended next phase

1. Preserve the St Kilda–North Melbourne clip as holdout evidence and do not
   add its frames to the current training dataset.
2. Add hard-negative examples of yellow referees and visually similar crowd
   objects from separate development footage.
3. Add positive examples of held, distant and partly occluded balls from
   separate footage.
4. Train a future detector version and evaluate it on a new untouched clip.
5. Re-evaluate the frozen temporal rules after detector quality improves.
6. Only then consider a more advanced motion model, field-of-play constraints,
   trajectory smoothing and service integration.

## Evidence locations

- V1 full development output:
  `temporal_tracker_runs/car_gcs_full_v1/`
- V2 300-frame comparison:
  `temporal_tracker_runs/car_gcs_v2_300/`
- V3 300-frame comparison:
  `temporal_tracker_runs/car_gcs_v3_300/`
- V3 full development output:
  `temporal_tracker_runs/car_gcs_v3_full/`
- Frozen V3 tracker holdout:
  `temporal_tracker_runs/stkilda_holdout_v3_frozen/`

Large videos, CSV files, JSON summaries, detector weights and datasets remain
local experimental artifacts and are not stored in Git.
