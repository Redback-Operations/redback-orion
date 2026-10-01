# Orion Player Tracking Studio

Orion Player Tracking Studio is a desktop application for running and reviewing the player tracking workflow. It connects model inference, tracking, video review, team suggestions, jumper number review and player identity correction in one interface.

The studio can process a new match or open tracking results produced earlier. Automatic results remain editable because broadcast footage can contain motion blur, camera cuts, overlapping players and spectators.

## Main features

1. Select a match video and compatible Ultralytics model.

2. Inspect the classes supported by the selected model.

3. Run ByteTrack or BoTSORT with progress, frame limit and stop controls.

4. Create an annotated video and tracking CSV.

5. Load an existing tracking CSV without processing the match again.

6. Play, pause and seek through the match inside the application.

7. Find short tracks, confidence drops, sudden detection count changes and possible reassociations.

8. Jump directly to problem timestamps and record review decisions.

9. Suggest team groups using colour information from several player crops.

10. Read possible jumper numbers using OCR across several frames.

11. Manually correct team names, jumper numbers and player identities.

12. Reconnect fragmented temporary track IDs while checking for overlapping conflicts.

13. Export reviewed tracks, review events and complete project data.

## How the workflow fits together

A detection model finds players or other trained classes in each frame. ByteTrack or BoTSORT links those detections over time and gives each track a temporary ID.

Temporary IDs are useful but they do not confirm a real player identity. A player may leave the camera view, become blocked or disappear during a camera cut. When the player returns, the tracker may assign a different ID.

The studio adds a review stage after tracking. It combines the temporary ID, reviewed team and possible jumper number to help reconnect track fragments. If two proposed fragments overlap in time, the studio marks the identity for review instead of silently accepting the merge.

## Installation

Python 3.11 or 3.12 is recommended.

Open a terminal in this folder and create a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the application.

```bash
python run_orion_tracking_studio.py
```

## Processing a new match

1. Select Choose video and open a match video.

2. Select Choose model and open a compatible model file.

3. Check the model classes shown in the progress area.

4. Select ByteTrack or BoTSORT.

5. Enter a frame limit when only a short test is needed. Leave it empty to process the complete video.

6. Select Start analysis.

The model determines which objects and teams can be recognised. A model trained for specific teams should not be expected to identify unrelated teams correctly. For broader use, select a general player and referee model, then review the team suggestions inside the studio.

New processing results are saved under `outputs/review_runs`.

## Opening existing results

Choose the original video and its matching tracking CSV, then select Load existing results.

The CSV reader accepts these common column names:

1. `frame`, `frame_id` or `frame_number`

2. `track_id`, `player_id` or `id`

3. `class`, `class_name` or `label`

4. `confidence` or `conf`

Bounding boxes use `x1`, `y1`, `x2` and `y2` when available.

## Reviewing tracking problems

The Review page creates a list of timestamps that may need attention.

Short tracks can indicate brief appearances, false detections or fragmented IDs. Confidence drops show frames where the detector was less certain. Detection count changes highlight frames where several detections appeared or disappeared together. Possible reassociations show a track that returned after a gap with a different class.

These events are review suggestions, not accuracy measurements. Camera cuts, replays and graphics can produce valid changes. Select an event to inspect the matching frame, then mark it as Correct, False alarm or Needs review.

## Reviewing teams and jumper numbers

The Players page summarises each temporary track.

Team suggestions use colour features from the central jumper area across several crops. If the selected model already provides team classes, those classes are retained.

Jumper suggestions use OCR on several crops and count repeated digit readings. Small players, motion blur, obstructions and players facing away can reduce OCR quality. Every team and jumper value can therefore be corrected manually.

## Resolving player identities

Tracks with the same reviewed team and jumper number can be connected when their frame ranges do not overlap. Tracks that overlap are marked for review because two visible tracks may represent different players.

The reviewer can also select multiple tracks and enter a confirmed identity manually. The original temporary IDs remain available in the exported data.

## Outputs

The annotated MP4 shows model and tracking results.

`reviewed_tracks.csv` contains track summaries, reviewed team values, jumper numbers and resolved identities.

`review_events.csv` contains problem timestamps and review decisions.

`review_project.json` stores the complete review state for another script or later work.

Player crops used for colour and OCR suggestions are saved under `outputs/review_crops`.

## Current limitations

1. Tracking quality depends on the selected detection model.

2. Colour grouping can be affected by lighting, shadows and similar team uniforms.

3. Jumper OCR is less reliable when players are distant, moving or facing away.

4. Identity suggestions still require human review and are not ground truth measurements.

5. Long broadcasts can take considerable time to process without a supported graphics processor.

## Tests

Run the automated tests from this folder.

```bash
python -m unittest discover -s tests -v
```

The tests cover CSV compatibility, problem event detection, identity merging, overlap protection and result exporting.

## Credits

Sahan Chandimal is the main contributor for the integrated studio, GUI, shared review workflow and identity resolution.

The application connects related repository work from Christopher Abbey, Sri Bandara, Matthew Lewis, Hasini Siddu, Yash Talati and Lê Đông Quân. The Credits window lists the connected areas of work.
