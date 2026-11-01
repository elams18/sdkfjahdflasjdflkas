from datetime import datetime, timezone

from app.services.analysis import calculate_metrics, hourly_actuals, select_forecast
from app.config import ANALYSIS_WINDOW
from app.data.elexon import Dataset, ElexonClient

UTC = timezone.utc


def test_select_forecast_uses_latest_vintage_not_after_cutoff():
    """Exclude forecast vintages published after the decision cutoff."""
    vintages = [
        (datetime(2026, 1, 1, 9, 30, tzinfo=UTC), 120.0),
        (datetime(2026, 1, 1, 10, 30, tzinfo=UTC), 80.0),
    ]

    assert select_forecast(vintages, datetime(2026, 1, 1, 10, tzinfo=UTC)) == vintages[0]


def test_hourly_actual_averages_two_half_hour_values():
    """Aggregate a complete half-hour pair and omit an incomplete hour."""
    actuals = [
        {
            "startTime": "2026-01-02T00:00:00Z",
            "publishTime": "2026-01-02T01:00:00Z",
            "generation": 100,
        },
        {
            "startTime": "2026-01-02T00:30:00Z",
            "publishTime": "2026-01-02T01:30:00Z",
            "generation": 140,
        },
        {
            "startTime": "2026-01-02T01:00:00Z",
            "publishTime": "2026-01-02T02:00:00Z",
            "generation": 160,
        },
    ]

    assert hourly_actuals(actuals) == {datetime(2026, 1, 2, tzinfo=UTC): 120}


def test_metrics_define_bias_as_forecast_minus_actual():
    """Keep bias signed as forecast minus actual and report coverage."""
    metrics = calculate_metrics([(110, 100), (90, 100)], expected_intervals=4)

    assert metrics == {
        "maeMw": 10.0,
        "rmseMw": 10.0,
        "meanBiasMw": 0.0,
        "matchedIntervals": 2,
        "expectedIntervals": 4,
        "coveragePct": 50.0,
    }


def test_query_bounds_derive_next_day_delivery_range():
    queries = ElexonClient.query_params_for_window(ANALYSIS_WINDOW)

    assert queries[Dataset.FUELHH] == {
        "settlementDateFrom": "2026-01-02",
        "settlementDateTo": "2026-02-01",
        "fuelType": "WIND",
    }
    assert queries[Dataset.WINDFOR]["publishDateTimeFrom"] == "2026-01-01T00:00:00Z"
    assert queries[Dataset.WINDFOR]["publishDateTimeTo"] == "2026-01-31T23:59:59Z"