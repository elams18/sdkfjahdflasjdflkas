import httpx
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

from app.config import ANALYSIS_WINDOW
from app.data import elexon
from app.data.elexon import Dataset


def test_month_data_cache_expires_and_supports_explicit_refresh(monkeypatch):
    now = [100.0]
    calls = []

    monkeypatch.setattr(elexon, "monotonic", lambda: now[0])
    client = elexon.ElexonClient(cache_ttl_seconds=10)

    def fake_fetch(dataset, params):
        calls.append(dataset)
        return [{"dataset": dataset.value}]

    monkeypatch.setattr(client, "fetch_dataset", fake_fetch)

    initial = client.load_window(ANALYSIS_WINDOW)
    assert client.load_window(ANALYSIS_WINDOW) is initial
    assert calls == [Dataset.FUELHH, Dataset.WINDFOR]

    now[0] += client.cache_ttl_seconds + 1
    expired = client.load_window(ANALYSIS_WINDOW)
    assert expired is not initial
    assert len(calls) == 4

    refreshed = client.load_window(ANALYSIS_WINDOW, refresh=True)
    assert refreshed is not expired
    assert len(calls) == 6


def test_fetch_dataset_retries_transient_server_errors(monkeypatch):
    client = elexon.ElexonClient(max_retries=1, retry_backoff_seconds=0)
    responses = [
        httpx.Response(503, request=httpx.Request("GET", "https://example.test")),
        httpx.Response(
            200,
            json=[{"generation": 123}],
            request=httpx.Request("GET", "https://example.test"),
        ),
    ]
    calls = []

    def fake_get(url, *, params, timeout):
        calls.append((url, params, timeout))
        return responses.pop(0)

    monkeypatch.setattr(elexon.httpx, "get", fake_get)
    monkeypatch.setattr(elexon, "sleep", lambda _: None)

    records = client.fetch_dataset(Dataset.WINDFOR, {"fuelType": "WIND"})

    assert records == [{"generation": 123}]
    assert len(calls) == 2
    assert calls[0][0] == "https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream"


def test_retry_after_parses_delta_seconds_and_http_date(monkeypatch):
    waits = []
    client = elexon.ElexonClient(max_retry_wait_seconds=60)
    monkeypatch.setattr(elexon, "sleep", waits.append)

    assert client._wait_before_retry(0, "5") is True
    assert waits == [5]

    retry_at = datetime.now(timezone.utc) + timedelta(seconds=5)
    assert client._wait_before_retry(0, format_datetime(retry_at, usegmt=True)) is True
    assert 0 <= waits[1] <= 5


def test_retry_after_longer_than_automatic_wait_is_not_retried(monkeypatch):
    client = elexon.ElexonClient(
        max_retries=1,
        max_retry_wait_seconds=10,
        retry_backoff_seconds=0,
    )
    calls = []
    response = httpx.Response(
        429,
        headers={"Retry-After": "60"},
        request=httpx.Request("GET", "https://example.test"),
    )

    monkeypatch.setattr(elexon.httpx, "get", lambda *args, **kwargs: calls.append(1) or response)
    monkeypatch.setattr(elexon, "sleep", lambda _: None)

    try:
        client.fetch_dataset(Dataset.WINDFOR, {})
    except httpx.HTTPStatusError as error:
        assert error.response.status_code == 429
    else:
        raise AssertionError("Expected the upstream rate-limit response to be surfaced")

    assert calls == [1]