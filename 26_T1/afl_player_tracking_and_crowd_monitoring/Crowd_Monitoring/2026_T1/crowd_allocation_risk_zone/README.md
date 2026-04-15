# Crowd Allocation & Risk Zone Planning

## Objective

Assess crowd safety risk levels across zones and provide recommendations for crowd allocation and management strategies to prevent dangerous situations.

## Recommended Structure

```text
crowd_allocation_risk_zone/
|- README.md
|- main.py
`- output/
```

### Why This Structure

- `main.py` keeps the task simple and easy to understand
- `output/` stores risk reports, flagged zones, or recommendation files
- add `utils.py` only if `main.py` becomes messy or too long

## Correct Approach

- keep the real implementation for this task inside this folder
- write the main risk assessment logic in `main.py`
- save generated files inside `output/`
- if helper code starts repeating, then create `utils.py`
- the shared service layer can later call functions from this task folder

## When To Add `utils.py`

Create `utils.py` only when:

- `main.py` becomes hard to read
- helper functions are repeated
- you want to separate small reusable logic such as threshold checks or recommendation rules

Do not create extra files too early. Start simple, then split only when needed.

## Scope

- Identify high-risk zones based on crowd density thresholds
- Assess cumulative risk factors (density, behavior, movement patterns)
- Create risk zone maps for different crowd levels
- Suggest crowd allocation strategies to balance load
- Develop evacuation or crowd control recommendations

## Inputs

- Per-zone density counts from density_zoning task
- Crowd behaviour analysis from crowd_behaviour_analytics task
- Zone definitions and capacity data
- Historical incident or risk data (if available)

## Outputs

- Risk zone classifications (low, medium, high, critical)
- Risk heatmaps with threshold indicators
- Crowd allocation recommendations
- Safety alerts and warnings
- Evacuation route suggestions (if applicable)

## Implementation Notes

- Define clear density thresholds for each risk level per zone
- Combine density metrics with behavior flags to assess risk
- Keep allocation recommendations practical and implementable
- Focus first on identifying critical zones, then suggest improvements
- Document risk thresholds and decision logic clearly
- Keep the task folder minimal at the start
- Store reusable helpers in `shared/` only if they are needed by multiple folders

## Suggested Deliverables

- A simple `main.py` script for risk assessment
- Allocation recommendation report (JSON/CSV)
- Risk threshold configuration file
- Examples showing critical scenarios and responses
