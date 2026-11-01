from __future__ import annotations

import os
from datetime import date, time
from pathlib import Path

from dotenv import load_dotenv

from .domain.analysis_window import AnalysisWindow

load_dotenv(Path(__file__).parent.parent / "credentials.env")

API_BASE = os.getenv("ELEXON_API_BASE_URL", "https://data.elexon.co.uk/bmrs/api/v1")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
ELEXON_TIMEOUT_SECONDS = float(os.getenv("ELEXON_TIMEOUT_SECONDS", "45"))
ELEXON_MAX_RETRIES = int(os.getenv("ELEXON_MAX_RETRIES", "2"))
ELEXON_RETRY_BACKOFF_SECONDS = float(os.getenv("ELEXON_RETRY_BACKOFF_SECONDS", "0.5"))
ELEXON_MAX_RETRY_WAIT_SECONDS = float(os.getenv("ELEXON_MAX_RETRY_WAIT_SECONDS", "30"))
ELEXON_CACHE_TTL_SECONDS = float(os.getenv("ELEXON_CACHE_TTL_SECONDS", "900"))


ANALYSIS_WINDOW = AnalysisWindow(
    decision_start=date.fromisoformat(os.getenv("DECISION_START_DATE", "2026-01-01")),
    decision_end=date.fromisoformat(os.getenv("DECISION_END_DATE", "2026-01-31")),
    default_cutoff=time.fromisoformat(os.getenv("DECISION_CUTOFF_TIME", "10:00")),
)
EXPECTED_INTERVALS = ANALYSIS_WINDOW.expected_intervals