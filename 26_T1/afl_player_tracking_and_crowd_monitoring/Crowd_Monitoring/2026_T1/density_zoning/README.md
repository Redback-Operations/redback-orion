# Density And Zoning

## Objective

Estimate crowd density and distribution across different stadium zones.

## Recommended Structure

```text
density_zoning/
|- README.md
|- main.py
`- output/
```

### Why This Structure

- `main.py` keeps the task simple and easy to understand
- `output/` stores zone counts, density values, or summary files
- add `utils.py` only if `main.py` becomes messy or too long

## Correct Approach

- keep the real implementation for this task inside this folder
- write the main density and zoning logic in `main.py`
- save generated files inside `output/`
- if helper code starts repeating, then create `utils.py`
- the shared service layer can later call functions from this task folder

## When To Add `utils.py`

Create `utils.py` only when:

- `main.py` becomes hard to read
- helper functions are repeated
- you want to separate small reusable logic such as zone mapping or density calculations

Do not create extra files too early. Start simple, then split only when needed.

## Scope

- Count detected people
- Divide the frame or stadium view into logical zones
- Measure per-zone crowd load
- Normalize density values for comparison

## Inputs

- Person detections from the crowd detection task
- Zone definitions or a simple grid layout

## Outputs

- Per-zone counts
- Density values
- Summary tables for downstream analytics

## Implementation Notes

- Start with a simple grid-based zoning approach
- Use detected person positions such as bounding-box centers
- Keep the first version deterministic and easy to inspect
- Make the zone layout configurable if possible
- Keep the task folder minimal at the start
- Store reusable helpers in `shared/` only if they are needed by multiple folders

## Suggested Deliverables

- A simple `main.py` script that maps people into zones
- A table of zone counts and densities
- Example output using sample coordinates or detections
