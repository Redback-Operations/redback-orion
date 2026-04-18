# Analytics Output

## Objective

Generate structured outputs that can be consumed by the Orion dashboard or related services.

## Recommended Structure

```text
analytics_output/
|- README.md
|- main.py
`- output/
```

### Why This Structure

- `main.py` keeps the task simple and easy to understand
- `output/` stores generated JSON, CSV, or export files
- add `utils.py` only if `main.py` becomes messy or too long

## Correct Approach

- keep the real implementation for this task inside this folder
- write the main export logic in `main.py`
- save generated files inside `output/`
- if helper code starts repeating, then create `utils.py`
- the shared service layer can later call functions from this task folder

## When To Add `utils.py`

Create `utils.py` only when:

- `main.py` becomes hard to read
- helper functions are repeated
- you want to separate small reusable logic such as JSON formatting or CSV writing

Do not create extra files too early. Start simple, then split only when needed.

## Scope

- Export analysis results in JSON and CSV formats
- Define a clean schema for crowd metrics
- Prepare data for backend and frontend integration

## Inputs

- Detection results
- Density and zoning summaries
- Heatmap metadata if relevant

## Outputs

- JSON files
- CSV files
- A documented output structure

## Implementation Notes

- Keep field names stable and descriptive
- Include timestamps, frame IDs, and zone metrics where useful
- Design the structure so it can be used before full production data exists
- Prefer simple schemas first, then extend only if needed
- Keep the task folder minimal at the start
- Store reusable helpers in `shared/` only if they are needed by multiple folders

## Suggested Deliverables

- A simple `main.py` script for exporting results
- Example JSON and CSV output
- A short schema note in this folder or `docs/`
