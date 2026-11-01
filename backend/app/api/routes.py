from __future__ import annotations

import logging
from datetime import date, time
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query

from ..config import ANALYSIS_WINDOW
from ..data.elexon import ElexonClient
from ..services.dashboard import build_dashboard

router = APIRouter()
logger = logging.getLogger(__name__)
elexon_client = ElexonClient()


@router.get("/api/health")
def health() -> dict[str, str]:
    """Report that the API process is responsive."""
    return {"status": "ok"}


@router.get("/api/dashboard")
def dashboard(
    decision_date: date = Query(default=ANALYSIS_WINDOW.decision_start),
    cutoff_time: time = Query(default=ANALYSIS_WINDOW.default_cutoff),
    refresh_data: bool = Query(default=False),
) -> dict[str, Any]:
    """Return month accuracy and the selected decision day's hourly profile."""
    if not ANALYSIS_WINDOW.decision_start <= decision_date <= ANALYSIS_WINDOW.decision_end:
        raise HTTPException(status_code=400, detail="Decision date is outside the configured analysis window")
    if cutoff_time.tzinfo is not None or cutoff_time.second or cutoff_time.microsecond:
        raise HTTPException(status_code=400, detail="Cutoff must be a local HH:MM time")
    try:
        actual_records, forecast_records = elexon_client.load_window(
            ANALYSIS_WINDOW, refresh=refresh_data
        )
    except (httpx.HTTPError, ValueError) as error:
        logger.exception("Elexon data request failed")
        raise HTTPException(
            status_code=502,
            detail="Elexon historical data is temporarily unavailable. Please retry later.",
        ) from error

    return build_dashboard(decision_date, cutoff_time, actual_records, forecast_records)