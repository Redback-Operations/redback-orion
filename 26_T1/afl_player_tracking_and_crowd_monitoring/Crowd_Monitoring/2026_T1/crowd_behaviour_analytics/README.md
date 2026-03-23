# Crowd Behaviour Analytics

## Objective

Analyse movement patterns in the crowd and detect behaviour that may indicate risk or unusual conditions.

## Recommended Structure

```text
crowd_behaviour_analytics/
|- README.md
|- main.py
`- output/
```

### Why This Structure

- `main.py` keeps the task simple and easy to understand
- `output/` stores behaviour summaries, flags, or example results
- add `utils.py` only if `main.py` becomes messy or too long

## Correct Approach

- keep the real implementation for this task inside this folder
- write the main behaviour analysis logic in `main.py`
- save generated files inside `output/`
- if helper code starts repeating, then create `utils.py`
- the shared service layer can later call functions from this task folder

## When To Add `utils.py`

Create `utils.py` only when:

- `main.py` becomes hard to read
- helper functions are repeated
- you want to separate small reusable logic such as movement calculations or event checks

Do not create extra files too early. Start simple, then split only when needed.

## Scope

- Analyse crowd movement over time
- Detect sudden crowd movement
- Detect abnormal behaviour
- Detect crowd surges

## Inputs

- Sequential detections across frames
- Optional tracking or motion features

## Outputs

- Behaviour event flags
- Movement summaries
- Data that can support alerting or dashboard visualisation

## Implementation Notes

- Start with simple movement heuristics before advanced models
- Compare position changes across frames
- Focus first on interpretable signals that are easy to validate
- Document assumptions clearly because this task can become ambiguous quickly
- Keep the task folder minimal at the start
- Store reusable helpers in `shared/` only if they are needed by multiple folders

## Suggested Deliverables

- A simple `main.py` script for behaviour analysis
- A few example scenarios or simulated cases
- A list of event definitions used by the module
