# Shared Folder

This folder contains common project components that can be reused by all team members.

## Purpose

Use this folder for items that should not be duplicated inside individual task folders.

Current shared structure:

- `services/` - FastAPI service layer: the 3 agreed microservices plus the full-pipeline endpoint
- `config/` - shared JSON settings read by task folders
- `schemas/` - shared request and response formats and data contracts
- `timing.py` - `timed()` stage-timing helper used by the service layer

## `timing.py`

A context manager that records how long a block takes (wall time, in ms) into a dict:

```python
from shared.timing import timed

timings = {}
with timed("crowd_detection", timings, prefix="detection", verbose=False):
    result = detect_crowd(video)
# timings == {"crowd_detection": 1234.5}
```

- `verbose=True` (default) prints `[prefix] label  1.23s` as soon as the block finishes
- `verbose=False` records the time without printing; the service layer uses this and prints everything in one `PIPELINE BENCHMARK` report at the end
- use it to time whole stages from outside. Timing inside a loop should stay next to that loop

## Example

If the detection team defines one JSON output format and the analytics team needs to read it, that format should be documented in `schemas/` so both teams follow the same structure.

If all services need the same confidence threshold or input path setting, keep it in `config/`.

If the backend team needs a reusable service module for one of the 3 microservices, place that code in `services/`.
