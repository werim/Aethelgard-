from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from src.data.acquisition import (
    AcquisitionError,
    AcquisitionPolicy,
    ArtifactIntegrityError,
    FetchResponse,
    HistoricalKlineRequest,
    acquire_historical_klines,
    load_immutable_dataset,
)

INTERVAL_MS = 60_000
NOW = datetime(2026, 5, 27, 12, 0, tzinfo=UTC)


def row(open_time_ms: int) -> list[object]:
    return [
        open_time_ms,
        "100",
        "101",
        "99",
        "100.5",
        "12.3",
        open_time_ms + INTERVAL_MS - 1,
        "1234.5",
        31,
        "6.0",
        "601.0",
        "0",
    ]


class ScriptedTransport:
    def __init__(self, responses: list[FetchResponse]) -> None:
        self.responses = list(responses)
        self.params: list[dict[str, str]] = []

    def fetch(self, params: Mapping[str, str], timeout_seconds: float) -> FetchResponse:
        assert timeout_seconds > 0
        self.params.append(dict(params))
        return self.responses.pop(0)


def request() -> HistoricalKlineRequest:
    return HistoricalKlineRequest("BTCUSDT", "1m", 0, 3 * INTERVAL_MS, page_limit=2)


def test_acquisition_paginates_persists_and_validates_readback(tmp_path: Path) -> None:
    transport = ScriptedTransport(
        [
            FetchResponse(200, [row(0), row(INTERVAL_MS)], {}),
            FetchResponse(200, [row(2 * INTERVAL_MS)], {}),
        ]
    )
    result = acquire_historical_klines(
        request(), output_directory=tmp_path, transport=transport, clock=lambda: NOW
    )
    assert result.dataset.row_count == 3
    assert result.diagnostics.pages_fetched == 2
    assert transport.params[1]["startTime"] == str(2 * INTERVAL_MS)
    loaded = load_immutable_dataset(
        result.artifact, now=NOW + timedelta(minutes=1), max_age=timedelta(minutes=15)
    )
    assert loaded.dataset_sha256 == result.dataset.dataset_sha256
    assert result.artifact.data_path.exists()
    assert result.artifact.metadata_path.exists()
    assert result.artifact.metadata_sha256


def test_rate_limit_is_bounded_and_recorded(tmp_path: Path) -> None:
    slept: list[float] = []
    transport = ScriptedTransport(
        [
            FetchResponse(429, None, {"Retry-After": "1"}),
            FetchResponse(200, [row(0), row(INTERVAL_MS), row(2 * INTERVAL_MS)], {}),
        ]
    )
    result = acquire_historical_klines(
        request(),
        output_directory=tmp_path,
        transport=transport,
        policy=AcquisitionPolicy(max_retries=1),
        clock=lambda: NOW,
        sleeper=slept.append,
    )
    assert result.diagnostics.retries == 1
    assert result.diagnostics.response_status_codes == (429, 200)
    assert slept == [1.0]


def test_incomplete_empty_page_fails_closed(tmp_path: Path) -> None:
    transport = ScriptedTransport(
        [FetchResponse(200, [row(0)], {}), FetchResponse(200, [], {})]
    )
    with pytest.raises(AcquisitionError, match="ended before"):
        acquire_historical_klines(
            request(), output_directory=tmp_path, transport=transport, clock=lambda: NOW
        )


def test_unsupported_interval_or_misaligned_request_fails_before_fetch(
    tmp_path: Path,
) -> None:
    transport = ScriptedTransport([])
    with pytest.raises(AcquisitionError, match="Unsupported"):
        acquire_historical_klines(
            HistoricalKlineRequest("BTCUSDT", "1M", 0, INTERVAL_MS),
            output_directory=tmp_path,
            transport=transport,
            clock=lambda: NOW,
        )
    with pytest.raises(AcquisitionError, match="align"):
        acquire_historical_klines(
            HistoricalKlineRequest("BTCUSDT", "1m", 1, INTERVAL_MS),
            output_directory=tmp_path,
            transport=transport,
            clock=lambda: NOW,
        )


def test_stale_or_tampered_persisted_artifact_fails_closed(tmp_path: Path) -> None:
    transport = ScriptedTransport(
        [FetchResponse(200, [row(0), row(INTERVAL_MS), row(2 * INTERVAL_MS)], {})]
    )
    result = acquire_historical_klines(
        request(), output_directory=tmp_path, transport=transport, clock=lambda: NOW
    )
    with pytest.raises(ArtifactIntegrityError, match="stale"):
        load_immutable_dataset(
            result.artifact, now=NOW + timedelta(hours=1), max_age=timedelta(minutes=15)
        )
    result.artifact.data_path.write_text("{}", encoding="utf-8")
    with pytest.raises(ArtifactIntegrityError, match="checksum"):
        load_immutable_dataset(result.artifact, now=NOW, max_age=timedelta(minutes=15))


def test_tampered_fetch_metadata_fails_checksum_readback(tmp_path: Path) -> None:
    transport = ScriptedTransport(
        [FetchResponse(200, [row(0), row(INTERVAL_MS), row(2 * INTERVAL_MS)], {})]
    )
    result = acquire_historical_klines(
        request(), output_directory=tmp_path, transport=transport, clock=lambda: NOW
    )
    result.artifact.metadata_path.write_text("{}", encoding="utf-8")
    with pytest.raises(ArtifactIntegrityError, match="metadata checksum"):
        load_immutable_dataset(result.artifact, now=NOW, max_age=timedelta(minutes=15))


def test_immutable_write_refuses_conflicting_existing_content(tmp_path: Path) -> None:
    transport = ScriptedTransport(
        [FetchResponse(200, [row(0), row(INTERVAL_MS), row(2 * INTERVAL_MS)], {})]
    )
    result = acquire_historical_klines(
        request(), output_directory=tmp_path, transport=transport, clock=lambda: NOW
    )
    result.artifact.metadata_path.write_text("altered", encoding="utf-8")
    repeat_transport = ScriptedTransport(
        [FetchResponse(200, [row(0), row(INTERVAL_MS), row(2 * INTERVAL_MS)], {})]
    )
    with pytest.raises(ArtifactIntegrityError, match="altered bytes"):
        acquire_historical_klines(
            request(),
            output_directory=tmp_path,
            transport=repeat_transport,
            clock=lambda: NOW,
        )


def test_future_dated_persisted_artifact_fails_closed(tmp_path: Path) -> None:
    transport = ScriptedTransport(
        [FetchResponse(200, [row(0), row(INTERVAL_MS), row(2 * INTERVAL_MS)], {})]
    )
    result = acquire_historical_klines(
        request(),
        output_directory=tmp_path,
        transport=transport,
        clock=lambda: NOW + timedelta(minutes=1),
    )
    with pytest.raises(ArtifactIntegrityError, match="future-dated"):
        load_immutable_dataset(result.artifact, now=NOW, max_age=timedelta(minutes=15))


def test_retry_exhaustion_fails_closed(tmp_path: Path) -> None:
    transport = ScriptedTransport(
        [FetchResponse(503, None, {}), FetchResponse(503, None, {})]
    )
    with pytest.raises(AcquisitionError, match="exhausted"):
        acquire_historical_klines(
            request(),
            output_directory=tmp_path,
            transport=transport,
            policy=AcquisitionPolicy(max_retries=1),
            clock=lambda: NOW,
            sleeper=lambda seconds: None,
        )
