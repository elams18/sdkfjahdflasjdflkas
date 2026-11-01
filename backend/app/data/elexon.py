from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from email.utils import parsedate_to_datetime
from enum import StrEnum
from threading import Lock
from time import monotonic, sleep
from typing import Any

import httpx

from ..config import (
    API_BASE,
    ANALYSIS_WINDOW,
    ELEXON_CACHE_TTL_SECONDS,
    ELEXON_MAX_RETRIES,
    ELEXON_MAX_RETRY_WAIT_SECONDS,
    ELEXON_RETRY_BACKOFF_SECONDS,
    ELEXON_TIMEOUT_SECONDS,
)
from ..domain.analysis_window import AnalysisWindow, LONDON, UTC


class Dataset(StrEnum):
    """Elexon datasets used by this application."""

    FUELHH = "FUELHH"
    WINDFOR = "WINDFOR"


def parse_records(payload: Any) -> list[dict[str, Any]]:
    """Normalize supported Elexon response shapes into record dictionaries."""
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("data", "results", "records"):
            if isinstance(payload.get(key), list):
                return [row for row in payload[key] if isinstance(row, dict)]
    raise ValueError("Unexpected Elexon response format")


class ElexonClient:
    """Retrieve and briefly cache Elexon datasets using configurable retries."""

    def __init__(
        self,
        api_base_url: str = API_BASE,
        timeout_seconds: float = ELEXON_TIMEOUT_SECONDS,
        max_retries: int = ELEXON_MAX_RETRIES,
        retry_backoff_seconds: float = ELEXON_RETRY_BACKOFF_SECONDS,
        max_retry_wait_seconds: float = ELEXON_MAX_RETRY_WAIT_SECONDS,
        cache_ttl_seconds: float = ELEXON_CACHE_TTL_SECONDS,
    ) -> None:
        if not api_base_url.strip():
            raise ValueError("Elexon API base URL must not be empty")
        if (
            timeout_seconds <= 0
            or retry_backoff_seconds < 0
            or max_retry_wait_seconds < 0
            or cache_ttl_seconds < 0
        ):
            raise ValueError("Timeout must be positive and backoff/cache TTL must not be negative")
        if max_retries < 0:
            raise ValueError("Maximum retries must not be negative")

        self.api_base_url = api_base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.max_retry_wait_seconds = max_retry_wait_seconds
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: dict[
            AnalysisWindow,
            tuple[float, tuple[list[dict[str, Any]], list[dict[str, Any]]]],
        ] = {}
        self._cache_lock = Lock()

    def fetch_dataset(
        self, dataset: Dataset, params: dict[str, str]
    ) -> list[dict[str, Any]]:
        """Fetch one dataset, retrying transient transport, 429, and server errors."""
        url = f"{self.api_base_url}/datasets/{dataset.value}/stream"
        for attempt in range(self.max_retries + 1):
            try:
                response = httpx.get(url, params=params, timeout=self.timeout_seconds)
            except httpx.TransportError:
                if attempt >= self.max_retries or not self._wait_before_retry(attempt):
                    raise
                continue

            if response.status_code == 429 or response.status_code >= 500:
                if attempt < self.max_retries and self._wait_before_retry(
                    attempt, response.headers.get("Retry-After")
                ):
                    continue

            response.raise_for_status()
            return parse_records(response.json())

        raise RuntimeError("Elexon request exhausted retries without a response")

    def load_window(
        self, window: AnalysisWindow = ANALYSIS_WINDOW, *, refresh: bool = False
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Fetch actual and forecast records for a decision window, using a TTL cache."""
        now = monotonic()
        with self._cache_lock:
            cached = self._cache.get(window)
            if not refresh and cached is not None and now < cached[0]:
                return cached[1]

        query_params = self.query_params_for_window(window)
        actuals = self.fetch_dataset(Dataset.FUELHH, query_params[Dataset.FUELHH])
        forecasts = self.fetch_dataset(Dataset.WINDFOR, query_params[Dataset.WINDFOR])
        result = actuals, forecasts

        with self._cache_lock:
            self._cache[window] = (monotonic() + self.cache_ttl_seconds, result)
        return result

    @staticmethod
    def query_params_for_window(window: AnalysisWindow) -> dict[Dataset, dict[str, str]]:
        """Build Elexon's source-specific filters for the decision-date window."""
        publish_start = datetime.combine(
            window.decision_start, time.min, tzinfo=LONDON
        ).astimezone(UTC)
        publish_end = datetime.combine(
            window.decision_end + timedelta(days=1), time.min, tzinfo=LONDON
        ).astimezone(UTC) - timedelta(seconds=1)
        return {
            Dataset.FUELHH: {
                "settlementDateFrom": (window.decision_start + timedelta(days=1)).isoformat(),
                "settlementDateTo": (window.decision_end + timedelta(days=1)).isoformat(),
                "fuelType": "WIND",
            },
            Dataset.WINDFOR: {
                "publishDateTimeFrom": publish_start.isoformat().replace("+00:00", "Z"),
                "publishDateTimeTo": publish_end.isoformat().replace("+00:00", "Z"),
            },
        }

    def _wait_before_retry(self, attempt: int, retry_after: str | None = None) -> bool:
        delay = self.retry_backoff_seconds * (2**attempt)
        if retry_after is not None:
            requested_delay = self._retry_after_seconds(retry_after)
            if requested_delay is not None:
                delay = max(delay, requested_delay)
        if delay > self.max_retry_wait_seconds:
            return False
        sleep(delay)
        return True

    @staticmethod
    def _retry_after_seconds(value: str) -> float | None:
        """Parse Retry-After as either delta seconds or an HTTP date."""
        try:
            return max(0.0, float(value))
        except ValueError:
            pass
        try:
            retry_at = parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return None
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())