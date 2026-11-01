from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any

from .analysis import calculate_metrics, hourly_actuals, latest_forecasts, select_forecast
from ..config import ANALYSIS_WINDOW, EXPECTED_INTERVALS
from ..domain.analysis_window import LONDON, UTC


def day_snapshot(
    decision_day: date,
    cutoff: time,
    actual_by_hour: dict[datetime, float],
    forecast_by_hour: dict[datetime, list[tuple[datetime, float]]],
) -> dict[str, Any]:
    """Build one decision-day snapshot with cutoff-safe forecasts and actuals."""
    delivery_day = decision_day + timedelta(days=1)
    cutoff_at = datetime.combine(decision_day, cutoff, LONDON).astimezone(UTC)
    delivery_start = datetime.combine(delivery_day, time.min, LONDON).astimezone(UTC)
    delivery_end = datetime.combine(
        delivery_day + timedelta(days=1), time.min, LONDON
    ).astimezone(UTC)
    intervals: list[dict[str, Any]] = []
    pairs: list[tuple[float, float]] = []

    start = delivery_start
    while start < delivery_end:
        selected = select_forecast(forecast_by_hour.get(start, []), cutoff_at)
        actual = actual_by_hour.get(start)
        forecast = selected[1] if selected else None
        published = selected[0] if selected else None
        error = forecast - actual if forecast is not None and actual is not None else None
        if forecast is not None and actual is not None:
            pairs.append((forecast, actual))
        intervals.append(
            {
                "startTime": start.isoformat().replace("+00:00", "Z"),
                "localTime": start.astimezone(LONDON).strftime("%H:%M"),
                "forecastMw": round(forecast, 1) if forecast is not None else None,
                "actualMw": round(actual, 1) if actual is not None else None,
                "errorMw": round(error, 1) if error is not None else None,
                "publishTime": published.isoformat().replace("+00:00", "Z")
                if published
                else None,
            }
        )
        start += timedelta(hours=1)

    selected_publications = [row["publishTime"] for row in intervals if row["publishTime"]]
    return {
        "decisionDate": decision_day.isoformat(),
        "deliveryDate": delivery_day.isoformat(),
        "cutoffTime": cutoff.strftime("%H:%M"),
        "cutoffTimeZone": "Europe/London",
        "latestPublishTime": max(selected_publications) if selected_publications else None,
        "metrics": calculate_metrics(pairs, len(intervals)),
        "intervals": intervals,
    }


def build_dashboard(
    decision_date: date,
    cutoff_time: time,
    actual_records: list[dict[str, Any]],
    forecast_records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Assemble month-level accuracy and the selected day's hourly profile."""
    actual_by_hour = hourly_actuals(actual_records)
    forecast_by_hour = latest_forecasts(forecast_records)
    first_decision = ANALYSIS_WINDOW.decision_start
    days: list[dict[str, Any]] = []
    month_pairs: list[tuple[float, float]] = []
    selected_day: dict[str, Any] | None = None

    while first_decision <= ANALYSIS_WINDOW.decision_end:
        snapshot = day_snapshot(first_decision, cutoff_time, actual_by_hour, forecast_by_hour)
        days.append({key: value for key, value in snapshot.items() if key != "intervals"})
        month_pairs.extend(
            (row["forecastMw"], row["actualMw"])
            for row in snapshot["intervals"]
            if row["forecastMw"] is not None and row["actualMw"] is not None
        )
        if first_decision == decision_date:
            selected_day = snapshot
        first_decision += timedelta(days=1)

    month_metrics = calculate_metrics(month_pairs, EXPECTED_INTERVALS)
    return {
        "decisionDate": decision_date.isoformat(),
        "deliveryDate": (decision_date + timedelta(days=1)).isoformat(),
        "cutoffTime": cutoff_time.strftime("%H:%M"),
        "cutoffTimeZone": "Europe/London",
        "dataResolution": "Hourly forecasts; actuals are the mean of two half-hourly FUELHH values.",
        "monthMetrics": month_metrics,
        "days": days,
        "selectedDay": selected_day,
        "source": "Elexon BMRS FUELHH and WINDFOR",
        "historicalDataAvailable": month_metrics["matchedIntervals"] > 0,
    }