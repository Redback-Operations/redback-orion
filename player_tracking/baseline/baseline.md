# Player Tracking Baseline Metrics

## 1. Overview

This baseline evaluates the existing player detection and tracking pipeline using two AFL broadcast clips from different matches. The purpose is to understand the current tracking performance, identify weaknesses and establish measurements for comparison with future improvements.

Two clips of approximately 60 seconds each were selected.

## 2. Test Environment

| Component | Specification |
|---|---|
| Device | MacBook Air |
| Processor | Apple M4 |
| CPU cores | 10 (4 performance, 6 efficiency) |
| RAM | 16 GB |
| Operating system | macOS 26.6.2 |
| Python | 3.11.9 |
| Video frame rate | 25 FPS |
| Detection confidence | 0.3 |
| Tracker | ByteTrack |
| Model | player_ref_best.pt |

## 3. Baseline Videos

| Match | Clip | Duration | Resolution |
|---|---|---|---|
| Essendon vs Hawthorn | baseline_essendon_hawthorn.mp4 | 60 seconds | 1920×1080 |
| St Kilda vs North Melbourne | baseline_stkilda_northmelbourne.mp4 | 60 seconds | 1920×1080 |

Both clips were extracted from the original full-match broadcast videos using FFmpeg, starting at approximately 10 minutes into each match.

## 4. Tracking Configuration

Both clips were processed using the same model, confidence threshold and ByteTrack configuration.

Command used:

```bash
python player_tracking/analysis_pipeline/detect_and_track.py player_tracking/baseline/videos/baseline_essendon_hawthorn.mp4 --tracker player_tracking/analysis_pipeline/configs/afl_broadcast_bytetrack.yaml --conf 0.3

python player_tracking/analysis_pipeline/detect_and_track.py player_tracking/baseline/videos/baseline_stkilda_northmelbourne.mp4 --tracker player_tracking/analysis_pipeline/configs/afl_broadcast_bytetrack.yaml --conf 0.3
```

Both videos processed successfully, with 1,499 frames processed per clip.

## 5. Automated Evaluation Results

| Metric | Essendon vs Hawthorn | St Kilda vs North Melbourne |
|---|---:|---:|
| Detections | 5,805 | 15,283 |
| Unique track IDs | 155 | 184 |
| Class-track segments | 155 | 184 |
| Tracks per minute | 155.10 | 184.12 |
| Short-lived tracks | 67 (43.2%) | 47 (25.5%) |
| Mean frame confidence | 0.514 | 0.523 |
| Sudden count-change events | 6 | 9 |
| Suspected re-associations | 0 | 0 |

These metrics provide an indication of tracking quality. Short-lived tracks and tracks per minute are fragmentation indicators, not confirmed ID-switch measurements.

## 6. Visual Inspection and Observations

### Essendon vs Hawthorn

- Most of the main players were detected and had tracking boxes.
- Some background players were not highlighted consistently.
- Player number 15 was assigned tracking ID 763 from approximately 30 to 40 seconds.
- The same player was then assigned ID 853 for the remainder of the clip.
- This suggests an ID switch where the tracker lost the original identity and created a new track.

### St Kilda vs North Melbourne

- At approximately 14 seconds, tracking ID 8 appeared to be assigned to multiple players.
- Tracking boxes disappeared when players overlapped.
- Some players were not consistently highlighted with detection boxes.
- Tracking appeared less reliable during crowded gameplay and player interactions.

## 7. Main Issues Identified

1. **ID switches:** The same player can receive a different tracking ID during a clip.
2. **Player overlap:** Tracking boxes can disappear when players overlap.
3. **Missed detections:** Some players, particularly those in the background, are not detected consistently.
4. **Duplicate ID concerns:** Multiple players appeared to share the same tracking ID during visual inspection.
5. **Tracking fragmentation:** A high proportion of short-lived tracks was observed, particularly in the Essendon vs Hawthorn clip.

## 8. Conclusion

The baseline testing shows that the current pipeline can successfully detect and track many players across AFL broadcast footage. Both clips processed successfully using the existing model and ByteTrack configuration.

However, visual inspection identified issues with ID consistency, overlapping players and missed background detections. The Essendon vs Hawthorn clip also had a higher proportion of short-lived tracks.

These results provide a starting point for future improvements. The same clips and evaluation settings can be reused to compare tracking performance after changes to the model, tracker or configuration.

## 9. Generated Outputs

The following files were generated during testing:

- `player_tracking/outputs/baseline_essendon_hawthorn_player_ref_best.mp4`
- `player_tracking/outputs/baseline_essendon_hawthorn_player_ref_best.csv`
- `player_tracking/outputs/baseline_essendon_hawthorn.md`
- `player_tracking/outputs/baseline_essendon_hawthorn.json`
- `player_tracking/outputs/baseline_stkilda_northmelbourne_player_ref_best.mp4`
- `player_tracking/outputs/baseline_stkilda_northmelbourne_player_ref_best.csv`
- `player_tracking/outputs/baseline_stkilda_northmelbourne.md`
- `player_tracking/outputs/baseline_stkilda_northmelbourne.json`