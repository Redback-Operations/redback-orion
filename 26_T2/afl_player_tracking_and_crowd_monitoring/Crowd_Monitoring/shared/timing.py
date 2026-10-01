"""Shared stage-timing helper for benchmark prints across the pipeline.

For timing a whole function call (a "stage") from the outside - not for
profiling loop-internal work, which needs to stay next to the loop it is
measuring to keep its granularity.
"""

import time
from contextlib import contextmanager


@contextmanager
def timed(label, sink, prefix="pipeline", verbose=True):
    """Record wall time for one stage into sink[label] (ms).

    verbose=False records silently, for callers that want to fold the
    number into one report printed later instead of live per-stage output.
    """
    start = time.perf_counter()
    yield
    elapsed_ms = (time.perf_counter() - start) * 1000
    sink[label] = round(elapsed_ms, 1)
    if verbose:
        print(f"[{prefix}] {label:<18} {elapsed_ms / 1000:6.2f}s")
