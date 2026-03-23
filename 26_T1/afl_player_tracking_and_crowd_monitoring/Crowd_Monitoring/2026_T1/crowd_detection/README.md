# Crowd Detection

## Objective

Detect spectators in stadium footage using a person-level detection pipeline.

## Recommended Structure

```text
crowd_detection/
|- README.md
|- main.py
`- output/
```

### Why This Structure

- `main.py` keeps the task simple and easy to understand
- `output/` stores detections, sample visuals, or exported results
- add `utils.py` only if `main.py` becomes messy or too long

## Correct Approach

- keep the real implementation for this task inside this folder
- write the main detection logic in `main.py`
- save generated files inside `output/`
- if helper code starts repeating, then create `utils.py`
- the shared service layer can later call functions from this task folder

## When To Add `utils.py`

Create `utils.py` only when:

- `main.py` becomes hard to read
- helper functions are repeated
- you want to separate small reusable logic such as model loading or output formatting

Do not create extra files too early. Start simple, then split only when needed.

## Scope

- Run person detection on frames or video
- Focus on detecting spectators rather than general scene objects
- Compare results against the previous segmentation-based approach where useful
- Prepare detection outputs for density and zone analysis

## Inputs

- Extracted video frames
- Sample stadium footage

## Outputs

- Bounding boxes for detected people
- Confidence scores
- Structured detection results for later tasks

## Implementation Notes

- Use YOLOv8 through Ultralytics
- Start with the `person` class only
- Save outputs in a simple format such as JSON or CSV
- Record known failure cases such as occlusion, distance, and low lighting
- Keep the task folder minimal at the start
- Store reusable helpers in `shared/` only if they are needed by multiple folders

## Suggested Deliverables

- A simple `main.py` script for person detection
- Sample visual output with boxes drawn on frames
- A saved set of person coordinates or detections
