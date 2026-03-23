# Video Processing

## Objective

Prepare stadium footage so it can be used consistently by downstream crowd analysis tasks.

## Recommended Structure

```text
video_processing/
├── README.md
├── main.py
└── output/
```

### Why This Structure

- `main.py` keeps the task simple and easy to understand
- `output/` stores extracted frames or metadata
- add `utils.py` only if `main.py` becomes messy or too long

## Correct Approach

- keep the real implementation for this task inside this folder
- write the main video processing logic in `main.py`
- save generated files inside `output/`
- if helper code starts repeating, then create `utils.py`
- the shared service layer can later call functions from this task folder

## When To Add `utils.py`

Create `utils.py` only when:

- `main.py` becomes hard to read
- helper functions are repeated
- you want to separate small reusable logic such as path checks or frame naming

Do not create extra files too early. Start simple, then split only when needed.

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
- Keep the task folder minimal at the start
- Store reusable helpers in `shared/` only if they are needed by multiple folders

## Suggested Deliverables

- A simple `main.py` script that extracts frames from a video
- A short note on frame sampling strategy
- Example output for one sample video
