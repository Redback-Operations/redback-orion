# Density And Zoning

## Objective

Estimate crowd density and distribution across different stadium zones.

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

## Suggested Deliverables

- A script that maps people into zones
- A table of zone counts and densities
- Example output using sample coordinates or detections
