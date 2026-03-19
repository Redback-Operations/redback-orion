# Crowd Behaviour Analytics

## Objective

Analyse movement patterns in the crowd and detect behaviour that may indicate risk or unusual conditions.

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

## Suggested Deliverables

- A prototype behaviour analysis script
- A few example scenarios or simulated cases
- A list of event definitions used by the module
