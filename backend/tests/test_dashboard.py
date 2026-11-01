from datetime import date, time

from app.services.dashboard import build_dashboard


def test_dashboard_builds_empty_metrics_when_no_records_match():
    dashboard = build_dashboard(date(2026, 1, 1), time(10), [], [])

    assert dashboard["historicalDataAvailable"] is False
    assert dashboard["monthMetrics"]["matchedIntervals"] == 0
    assert dashboard["monthMetrics"]["expectedIntervals"] == 744
    assert dashboard["selectedDay"]["metrics"]["matchedIntervals"] == 0


def test_dashboard_aggregates_hourly_forecast_against_half_hour_actuals():
    actuals = [
        {"startTime": "2026-01-02T00:00:00Z", "generation": 100},
        {"startTime": "2026-01-02T00:30:00Z", "generation": 140},
    ]
    forecasts = [
        {
            "startTime": "2026-01-02T00:00:00Z",
            "publishTime": "2026-01-01T09:30:00Z",
            "generation": 130,
        }
    ]

    dashboard = build_dashboard(date(2026, 1, 1), time(10), actuals, forecasts)

    assert dashboard["historicalDataAvailable"] is True
    assert dashboard["monthMetrics"]["maeMw"] == 10
    assert dashboard["monthMetrics"]["matchedIntervals"] == 1
    assert dashboard["selectedDay"]["intervals"][0]["actualMw"] == 120


def test_dashboard_does_not_select_forecast_published_after_cutoff():
    forecasts = [
        {
            "startTime": "2026-01-02T00:00:00Z",
            "publishTime": "2026-01-01T10:01:00Z",
            "generation": 130,
        }
    ]

    dashboard = build_dashboard(date(2026, 1, 1), time(10), [], forecasts)

    interval = dashboard["selectedDay"]["intervals"][0]
    assert interval["forecastMw"] is None
    assert dashboard["historicalDataAvailable"] is False