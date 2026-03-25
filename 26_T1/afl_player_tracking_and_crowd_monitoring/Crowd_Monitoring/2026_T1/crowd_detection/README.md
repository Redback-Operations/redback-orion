# Crowd Detection

## Objective

Detect spectators in stadium footage using a person-level detection pipeline.

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

## Suggested Deliverables

- A detection script or notebook
- Sample visual output with boxes drawn on frames
- A saved set of person coordinates or detections
