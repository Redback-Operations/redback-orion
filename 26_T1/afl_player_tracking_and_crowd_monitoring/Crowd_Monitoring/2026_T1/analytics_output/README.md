# Analytics Output

## Objective

Generate structured outputs that can be consumed by the Orion dashboard or related services.

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

## Suggested Deliverables

- A serializer or export script
- Example JSON and CSV output
- A short schema note in this folder or `docs/`
