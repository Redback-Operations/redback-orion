# Video Processing

## Objective

Prepare stadium footage so it can be used consistently by downstream crowd analysis tasks.

## Scope

- Load input videos
- Read frames using OpenCV
- Sample or extract frames at a usable interval
- Save processed frames for later tasks if needed
- Validate that video input quality is sufficient

## Inputs

- Raw stadium video files
- Optional sample clips for testing

## Outputs

- Extracted frames
- Basic metadata such as frame count, resolution, and FPS

## Implementation Notes

- Use OpenCV for video loading and frame extraction
- Keep file naming predictable
- Start with a small test clip before processing longer videos
- Store reusable helpers in `shared/` when possible

## Suggested Deliverables

- A script or notebook that extracts frames from a video
- A short note on frame sampling strategy
- Example output for one sample video
