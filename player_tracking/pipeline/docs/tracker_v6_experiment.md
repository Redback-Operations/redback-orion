# Ball-Specific Temporal Tracker V6

## Objective

Version 6 investigates controlled ball reacquisition after Version 5 was found
to retain stale track memory for too long. The work is a standalone experiment
and does not modify the active Project Orion player-tracking service.

The tracker consumes detections from the V4 ball-only model. Green boxes are
direct detector observations. Orange boxes are short motion-based predictions
and are recorded separately from detections.

## Problem identified in Version 5

An untouched St Kilda–North Melbourne evaluation showed that V5 retained only
10 of 85 correctly visible balls at an IoU threshold of 0.30. The detector had
correctly located 79 of those balls.

Frame-level analysis found that V5 discarded 69 correct detector results. The
median confidence of those discarded detections was 0.710, demonstrating that
weak detector confidence was not the main cause. After six visible prediction
frames, the old track remained active in hidden memory and blocked a new track
from starting until that memory expired.

## Version 6 design

V6 preserves V5's recent-motion fit and filtering rules. It adds a controlled
reacquisition path that becomes available only after the visible prediction
gap has ended.

A stale track can be replaced when:

- a candidate has confidence of at least 0.35;
- candidates appear in three consecutive frames; and
- their centres remain within 3.5% of the frame diagonal.

When confirmed, the old trajectory, velocity and motion history are cleared
before a new track starts. Incomplete candidate sequences are rejected. The
original V5 behaviour remains available when controlled reacquisition is not
enabled.

## Development verification

All 11 existing controlled motion tests passed. On the first 300 CAR–GCS
development frames, V6 produced output identical to V5 because no eligible
reacquisition sequence occurred. This confirmed that enabling the new path did
not disturb behaviour when it was not required.

On the complete 598-frame clip, V6 recorded five reacquisition attempts:

- three successful reacquisitions;
- two rejected incomplete sequences; and
- all three accepted events were visually confirmed as the active ball.

The successful events occurred at approximately 10.39, 13.43 and 17.62
seconds.

## Regression evaluation

The earlier 145-frame St Kilda sequence was reused only as a regression test
because its V5 failure had influenced the V6 design. It is not independent V6
evidence.

| Measure at IoU 0.30 | V5 | V6 |
|---|---:|---:|
| Correct visible-ball frames | 10/85 | 26/85 |
| Visible-ball recall | 0.1176 | 0.3059 |
| Output on labelled-empty frames | 3/60 | 2/60 |
| Empty-frame specificity | 0.9500 | 0.9667 |

V6 gained 22 correct frames and lost six V5 successes, producing a net gain of
16 correctly localised frames. It removed three earlier empty-frame outputs
and introduced two different ones. This supported the controlled-reacquisition
change but did not establish generalisation.

## Frozen final evaluation

V6 code, model and settings were hashed and frozen before the final test. A
previously unused St Kilda–North Melbourne sequence was selected from the raw
video before tracker output was viewed.

One hundred consecutive frames were reviewed:

| Ground-truth outcome | Frames |
|---|---:|
| Completed positive frames | 75 |
| Completed empty frames | 23 |
| Uncertain frames excluded | 2 |

The completed annotations were created before V6 was run and are permanently
excluded from training and tuning.

| Measure at IoU 0.30 | V4 detector | Tracker V6 |
|---|---:|---:|
| Correct visible-ball frames | 72/75 | 37/75 |
| Visible-ball recall | 0.9600 | 0.4933 |
| Output on labelled-empty frames | 3/23 | 6/23 |
| Empty-frame specificity | 0.8696 | 0.7391 |
| Mean IoU for successful frames | 0.7882 | 0.8672 |

V6 produced 37 correct detected frames, 24 wrong-location detected frames, 11
wrong-location predicted frames, six predicted outputs on labelled-empty
frames and three positive frames with no output. None of its 17 evaluated
predicted frames correctly bridged a visible-ball gap at IoU 0.30.

The tracker selected an incorrect object during the early test frames and
maintained that path through detections and predictions. After the stale track
ended, it recovered and correctly followed the ball across many later frames.
Controlled reacquisition did not activate because no candidate sequence met
the frozen confirmation rules while stale memory was active.

## Decision

Controlled reacquisition improved the known V5 failure during development and
regression testing, but V6 did not outperform detector-only output on the
untouched final sequence. Motion prediction also extended some wrong tracks.

V6 must remain an experimental prototype and should not be integrated into the
active Orion service. The V4 detector remains the recommended source of ball
locations for the current pilot.

Future work should prioritise track-start validation and explicit prediction
confidence before further reacquisition tuning. Player-overlap information,
field-of-play filtering and learned association are possible later extensions.
Any revised tracker requires a newly selected untouched evaluation sequence.

