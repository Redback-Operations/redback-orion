# Forward-50 Player Location Analysis

## Project Overview

This project analyses behind-goal Australian football footage and converts player detections into structured location and zone data. It uses YOLO to detect people, BoT-SORT to track them across frames and manually calibrated polygons to divide the Forward 50 into positional zones.

## How It Works

1. The user loads a football video.
2. The Forward-50 boundary and five zones are manually calibrated.
3. YOLO detects people in each video frame.
4. BoT-SORT assigns tracking IDs.
5. The program calculates each person's location using the bottom-centre of their bounding box.
6. The location is checked against the Forward-50 and zone polygons.
7. The results are saved to video, CSV and JSON files.

The estimated ground location is calculated using:

```python
ground_x = (x1 + x2) / 2
ground_y = y2
```

The bottom-centre point is used because it provides an estimate of where the player's feet meet the ground.

## Positional Zones

The five Forward-50 zones are:

- `left_pocket`
- `left_half_forward`
- `central_corridor`
- `right_half_forward`
- `right_pocket`

The program can also return:

- `outside` - the player is outside the calibrated Forward 50.
- `unassigned` - the player is inside the Forward 50 but does not fall within a calibrated zone.

Zone assignment occurs for every processed frame, so a player's zone can change as they move.

## Main Files

- `forward50_tracker.py` - runs detection, tracking and zone assignment.
- `calibrate_zones.py` - allows the user to define the Forward-50 and zone boundaries.
- `geometry.py` - contains the location and polygon calculations.
- `validate_outputs.py` - validates the generated CSV data.
- `config.example.json` - contains the model, processing and zone settings.
- `tests/test_geometry.py` - contains the automated geometry tests.

## Installation

Python 3.10-3.12 is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.json config.json
```

The first tracking run may download the selected pretrained YOLO model.

## Calibrating a Video

The camera view must be calibrated before analysis:

```bash
python calibrate_zones.py \
  --video input/joondalup.mp4 \
  --config config.json \
  --time 0
```

The calibration tool asks the user to outline:

1. The full Forward-50 boundary
2. Left pocket
3. Left half-forward
4. Central corridor
5. Right half-forward
6. Right pocket

Click at least three points around each boundary and press **Enter** to save it. Press **U** to undo the previous point or **Escape** to cancel. Different camera views should use separate configuration files.

## Running the Program

```bash
python forward50_tracker.py \
  --video input/joondalup.mp4 \
  --config config.json \
  --output output
```

## Outputs

The program produces:

- `annotated_forward50.mp4` - shows tracking IDs, ground points and zone labels.
- `player_positions.csv` - contains each detection's frame, ID, confidence, bounding box, ground location and zone.
- `zone_occupancy.csv` - contains the number of detected players in each zone per frame.
- `run_summary.json` - contains processing information, results and limitations.

## Testing and Validation

Run the automated tests using:

```bash
python -m unittest discover -s tests -v
```

Validate the output data using:

```bash
python validate_outputs.py --output output
```

The outputs should also be visually checked to confirm that the calculated ground points appear near the players' feet and that the displayed zone labels match the CSV records. The pipeline has been tested on multiple behind-goal videos with different camera views.

## Planned Umpire Exclusion

The current YOLO model detects the general person class, so umpires can sometimes be included as players. Umpire exclusion is planned but is not implemented in the current version.

The proposed method is to crop the clothing area of each detected person and use colour analysis to classify the detection as a `player`, `umpire` or `uncertain`. Detections that confidently match the configured umpire uniform colours will be excluded from player and zone totals, while uncertain detections will remain but be flagged for review.

The feature will be tested using manually labelled sample frames to measure how many umpires are correctly removed and whether any actual players are incorrectly excluded.

## Current Limitations

- Locations are image-based estimates rather than exact GPS coordinates.
- Different camera positions currently require separate manual calibrations.
- Camera movement can make fixed zone polygons inaccurate.
- Players can receive new tracking IDs after occlusion or leaving the frame.
- Umpires and other people may be detected as players.
- Labels can overlap when several players are close together.

## Future Improvements

- Implement and test umpire exclusion.
- Reduce tracking-ID switches.
- Improve handling of camera movement.
- Add team and jersey-number information where reliable.
- Produce a summarized zone for each tracked player.
- Add `job_id` and `video_id` fields for backend integration.
- Connect the pipeline to the Project Orion upload workflow.
