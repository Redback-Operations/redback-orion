# Data Aggregation

## Objective

Combine crowd, fire, and stampede results into one unified per-zone
monitoring record, and export it as JSON and CSV for backend/frontend
integration.

## Relationship to `analytics_output/`

This is a separate, newer task folder — it is not a replacement for
`analytics_output/` (Member 5's task). `analytics_output/` currently
implements a simpler, zone-based export contract; this folder
implements a fuller aggregation across three services (crowd, fire,
stampede). Both currently exist side by side; consolidating them is a
team decision for later, not made by this change.

## Recommended Structure

```text
data_aggregation/
|- README.md
|- SCHEMA.md
|- main.py
|- demo.py
`- output/
```

### Why This Structure

- `main.py` holds the real implementation: `aggregate_stadium_data()`
  combines the three services' results into one record, and
  `export_results()` writes it out as JSON + CSV
- `demo.py` runs the aggregation against the agreed dummy contracts,
  with no other services needed
- `output/` stores the exported `<video_id>_monitoring.json` and
  `<video_id>_zones.csv` files

## Correct Approach

- keep the real implementation for this task inside this folder
- write the main aggregation/export logic in `main.py`
- save generated files inside `output/`
- if helper code starts repeating, then create `utils.py`
- the shared service layer can later call functions from this task
  folder

## Scope

- Take one crowd-detection result plus fire and stampede detection
  lists
- Keep only the most recent detection per zone from fire/stampede
- Merge per zone into a single `fire` / `stampede` / `status` record
- Export the unified structure as JSON, and a flattened per-zone
  summary as CSV

## Inputs

- `crowd_data` — the aggregated crowd-detection result (`summary`,
  `peak_crowd_frame`, `anomaly_visual`, `heatmap`,
  `time_series_chart`, `density_extremes`)
- `fire_data` — `{"video_id": ..., "detections": [...]}` from
  `fire_detection`
- `stampede_data` — `{"video_id": ..., "detections": [...]}` from
  `stampede_detection` (event-level detections, each with `zone_id`)
- `stadium_id` — passed in by the caller; required

## Outputs

- `<video_id>_monitoring.json` — the complete unified structure
- `<video_id>_zones.csv` — flattened per-zone summary for statistics
  and reporting

See `SCHEMA.md` for the exact JSON shape and current limitations.

## Implementation Notes

- Crowd Detection does not currently expose a complete per-zone result
  in its backend-facing response. `density_extremes.person_count` is
  now a per-frame average for the reported highest/lowest zones, but it
  is not a complete stadium-zone dataset. Therefore,
  `zones[*].crowd_count` remains `null` unless Stampede Detection
  supplies a count; `crowd.summary.peak_person_count` remains the
  authoritative overall peak.
- When Crowd Detection supplies `stage_timings_ms`, it is preserved
  inside the unified `crowd` object in the JSON export.
- This remains a standalone prototype — the live backend currently
  gets crowd results directly from `POST /process-crowd-detection`
  rather than through this module.
- Run `python demo.py` to see the aggregation and export run
  end-to-end against sample data with no other services required.

## Suggested Deliverables

- `main.py` implementing `aggregate_stadium_data()` / `export_results()`
- `demo.py` showing it run against the agreed dummy contracts
- Example JSON/CSV output in `output/`
