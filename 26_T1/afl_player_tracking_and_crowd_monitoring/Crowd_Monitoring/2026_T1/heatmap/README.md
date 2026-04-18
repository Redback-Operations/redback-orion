# Heatmap Generation

## Objective

Visualise crowd density and distribution using heatmaps.

## Recommended Structure

```text
heatmap/
|- README.md
|- main.py
`- output/
```

### Why This Structure

- `main.py` keeps the task simple and easy to understand
- `output/` stores heatmap images, overlays, or generated files
- add `utils.py` only if `main.py` becomes messy or too long

## Correct Approach

- keep the real implementation for this task inside this folder
- write the main heatmap logic in `main.py`
- save generated files inside `output/`
- if helper code starts repeating, then create `utils.py`
- the shared service layer can later call functions from this task folder

## When To Add `utils.py`

Create `utils.py` only when:

- `main.py` becomes hard to read
- helper functions are repeated
- you want to separate small reusable logic such as color mapping or overlay drawing

Do not create extra files too early. Start simple, then split only when needed.

## Scope

- Generate heatmaps from detected people or density values
- Show hotspots and sparse regions
- Save visual outputs for reporting and dashboard use

## Inputs

- Person coordinates or zone density data
- Background frame or image for optional overlay

## Outputs

- Heatmap images
- Optional overlay images or video frames

## Implementation Notes

- Start with sample coordinates if real detections are not ready
- Use a consistent colour scale
- Keep overlays readable and avoid hiding the underlying frame
- Save examples suitable for README or presentation use
- Keep the task folder minimal at the start
- Store reusable helpers in `shared/` only if they are needed by multiple folders

## Suggested Deliverables

- A simple `main.py` script for heatmap generation
- Example heatmap image
- Optional frame overlay showing density distribution
