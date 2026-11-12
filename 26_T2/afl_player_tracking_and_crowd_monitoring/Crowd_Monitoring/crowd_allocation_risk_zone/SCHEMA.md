# Crowd Allocation Risk Zone Task Schema

## Purpose

This task receives behaviour analysis and analytics data, then returns zone-level risk and recommendations.

## Input JSON

```json
{
  "video_id": "match_01",
  "crowd_state": "increasing_density",
  "zones": [
    {
      "zone_id": "A1",
      "person_count": 8,
      "density": 0.72
    },
    {
      "zone_id": "A2",
      "person_count": 5,
      "density": 0.45
    }
  ]
}
```

## Output JSON

```json
{
  "video_id": "match_01",
  "zones": [
    {
      "zone_id": "A1",
      "risk_level": "high",
      "flagged": true
    },
    {
      "zone_id": "A2",
      "risk_level": "medium",
      "flagged": false
    }
  ],
  "recommendations": [
    "Monitor zone A1 closely",
    "Prepare crowd redirection if density increases further"
  ]
}
```

## Notes

- output of this task must match the risk part of the intelligence service schema
- keep `risk_level`, `flagged`, and `recommendations` stable
