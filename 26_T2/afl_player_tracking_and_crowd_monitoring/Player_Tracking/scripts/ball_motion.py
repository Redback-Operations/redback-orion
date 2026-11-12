"""Motion checks for the experimental ball tracker; standard library only.

Fits recent detector observations, never feeds predictions back into the fit.
Uncertainty is a heuristic pixel distance, not a statistical confidence interval.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import hypot, sqrt


@dataclass(frozen=True)
class Observation:
    frame: int
    x: float
    y: float
    scale: float


@dataclass(frozen=True)
class Forecast:
    center: tuple[float, float] | None
    velocity: tuple[float, float]
    residual_px: float
    uncertainty_px: float
    allowed: bool
    reason: str


def forecast(observations, target_frame, *, width, height,
             max_gap=6, min_observations=3, max_span=12,
             residual_ratio=0.5, uncertainty_ratio=1.0):
    """Anchor a linear fit at the latest observation and judge extrapolation."""
    recent = list(observations)
    if not recent:
        return Forecast(None, (0.0, 0.0), 0.0, 0.0, False, "no_history")
    if any(b.frame <= a.frame for a, b in zip(recent, recent[1:])):
        raise ValueError("Observation frame numbers must strictly increase")
    last = recent[-1]
    if target_frame <= last.frame:
        raise ValueError("Forecast must follow the last observation")
    recent = [o for o in recent if last.frame - o.frame <= max_span]
    if len(recent) < min_observations:
        return Forecast(None, (0.0, 0.0), 0.0, 0.0, False, "insufficient_history")
    times = [o.frame - last.frame for o in recent]
    mean_t = sum(times) / len(times)
    mean_x = sum(o.x for o in recent) / len(recent)
    mean_y = sum(o.y for o in recent) / len(recent)
    denominator = sum((t - mean_t) ** 2 for t in times)
    vx = sum((t - mean_t) * (o.x - mean_x)
             for t, o in zip(times, recent)) / denominator
    vy = sum((t - mean_t) * (o.y - mean_y)
             for t, o in zip(times, recent)) / denominator
    residual = sqrt(sum(
        (o.x - (mean_x + vx * (t - mean_t))) ** 2
        + (o.y - (mean_y + vy * (t - mean_t))) ** 2
        for t, o in zip(times, recent)) / len(recent))
    local_velocities = [
        ((b.x - a.x) / (b.frame - a.frame),
         (b.y - a.y) / (b.frame - a.frame))
        for a, b in zip(recent, recent[1:])
    ]
    variation = sqrt(sum((x - vx) ** 2 + (y - vy) ** 2
                         for x, y in local_velocities) / len(local_velocities))
    gap = target_frame - last.frame
    center = (last.x + vx * gap, last.y + vy * gap)
    scale = max(last.scale, 1.0)
    # A small floor prevents a perfect fit from implying certainty indefinitely.
    uncertainty = residual + gap * (variation + 0.05 * scale)
    reason = "consistent_motion"
    if gap > max_gap:
        reason = "gap_limit"
    elif not (0 <= center[0] < width and 0 <= center[1] < height):
        reason = "outside_frame"
    elif residual > residual_ratio * scale:
        reason = "inconsistent_motion"
    elif uncertainty > uncertainty_ratio * scale:
        reason = "uncertain_motion"
    return Forecast(center, (vx, vy), residual, uncertainty,
                    reason == "consistent_motion", reason)
