from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc
LONDON = ZoneInfo("Europe/London")


@dataclass(frozen=True)
class AnalysisWindow:
    """Decision-date range and cutoff for next-day delivery analysis."""

    decision_start: date
    decision_end: date
    default_cutoff: time

    def __post_init__(self) -> None:
        if self.decision_end < self.decision_start:
            raise ValueError("Decision end date must not precede start date")
        if self.default_cutoff.tzinfo is not None:
            raise ValueError("Decision cutoff must be a local Europe/London time")

    @property
    def delivery_start_utc(self) -> datetime:
        """Return the UTC start of the first next-day delivery date."""
        return datetime.combine(
            self.decision_start + timedelta(days=1), time.min, tzinfo=LONDON
        ).astimezone(UTC)

    @property
    def delivery_end_utc(self) -> datetime:
        """Return the exclusive UTC end of the last next-day delivery date."""
        return datetime.combine(
            self.decision_end + timedelta(days=2), time.min, tzinfo=LONDON
        ).astimezone(UTC)

    @property
    def expected_intervals(self) -> int:
        """Count hourly delivery intervals, accounting for UK clock changes."""
        hours = (self.delivery_end_utc - self.delivery_start_utc).total_seconds() / 3600
        return int(hours)