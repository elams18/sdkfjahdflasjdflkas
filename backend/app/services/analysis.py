from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime
from typing import Any

from ..domain.analysis_window import UTC


def parse_timestamp(value: str) -> datetime:
    """Parse an ISO timestamp and normalize it to UTC."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def hourly_actuals(records: list[dict[str, Any]]) -> dict[datetime, float]:
    """Average complete pairs of half-hour FUELHH actuals into hourly values."""
    latest_by_start: dict[datetime, tuple[datetime, float]] = {}
    for row in records:
        try:
            start = parse_timestamp(str(row["startTime"]))
            generation = float(row["generation"])
            published = parse_timestamp(str(row.get("publishTime", row["startTime"])))
        except (KeyError, TypeError, ValueError):
            continue
        if not math.isfinite(generation) or start.minute not in (0, 30):
            continue
        existing = latest_by_start.get(start)
        if existing is None or published > existing[0]:
            latest_by_start[start] = (published, generation)

    halves: dict[datetime, dict[int, float]] = defaultdict(dict)
    for start, (_, generation) in latest_by_start.items():
        hour = start.replace(minute=0, second=0, microsecond=0)
        halves[hour][start.minute] = generation

    return {
        hour: (values[0] + values[30]) / 2
        for hour, values in halves.items()
        if 0 in values and 30 in values
    }


def latest_forecasts(records: list[dict[str, Any]]) -> dict[datetime, list[tuple[datetime, float]]]:
    """Group hourly forecast vintages by their delivery start time."""
    by_start: dict[datetime, list[tuple[datetime, float]]] = defaultdict(list)
    for row in records:
        try:
            start = parse_timestamp(str(row["startTime"]))
            published = parse_timestamp(str(row["publishTime"]))
            generation = float(row["generation"])
        except (KeyError, TypeError, ValueError):
            continue
        if start.minute == 0 and math.isfinite(generation):
            by_start[start].append((published, generation))
    return by_start


def select_forecast(
    vintages: list[tuple[datetime, float]], cutoff: datetime
) -> tuple[datetime, float] | None:
    """Return the latest forecast vintage published no later than the cutoff."""
    eligible = [vintage for vintage in vintages if vintage[0] <= cutoff]
    return max(eligible, key=lambda vintage: vintage[0]) if eligible else None


def calculate_metrics(
    pairs: list[tuple[float, float]], expected_intervals: int
) -> dict[str, float | int]:
    """Calculate absolute error, RMSE, signed bias, and matched coverage."""
    errors = [forecast - actual for forecast, actual in pairs]
    matched = len(errors)
    return {
        "maeMw": round(sum(abs(error) for error in errors) / matched, 1) if matched else 0,
        "rmseMw": round(math.sqrt(sum(error * error for error in errors) / matched), 1)
        if matched
        else 0,
        "meanBiasMw": round(sum(errors) / matched, 1) if matched else 0,
        "matchedIntervals": matched,
        "expectedIntervals": expected_intervals,
        "coveragePct": round(matched / expected_intervals * 100, 1)
        if expected_intervals
        else 0,
    }