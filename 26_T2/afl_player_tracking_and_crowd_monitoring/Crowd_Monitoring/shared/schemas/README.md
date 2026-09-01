# Schemas Folder

This folder defines the agreed API contract for the 3 microservices.

## Purpose

Each schema file should tell the team:

- endpoint name
- exact input JSON
- exact output JSON
- required field names
- expected data types
- what the backend team can rely on

## Schema Files

- `detection_schema.md`
- `analytics_schema.md`
- `intelligence_schema.md`

## Important Rule

- task folders should produce data in these agreed formats
- service files should return these agreed formats
- backend work should use these schema files as the source of truth

Do not change field names without team agreement.

## Note

The JSON below is the integration contract for now. It can be refined later, but all teams should stay consistent with the same structure.
