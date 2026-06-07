from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast
from urllib.error import URLError
from urllib.request import Request

import pytest

import src.data.acquisition as acquisition
from src.data.acquisition import (
    AcquisitionError,
    AcquisitionPolicy,
    ArtifactIntegrityError,
    FetchResponse,
    HistoricalKlineRequest,
    PublicBinanceFuturesTransport,
    TransientTransportError,
    acquire_historical_klines,
    discover_immutable_artifact,
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
    def __init__(self, responses: list[FetchResponse | Exception]) -> None:
        self.responses = list(responses)
        self.params: list[dict[str, str]] = []

    def fetch(self, params: Mapping[str, str], timeout_seconds: float) -> FetchResponse:
        assert timeout_seconds > 0
        self.params.append(dict(params))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def request() -> HistoricalKlineRequest:
    return HistoricalKlineRequest("BTCUSDT", "1m", 0, 3 * INTERVAL_MS, page_limit=2)


def complete_response() -> FetchResponse:
    return FetchResponse(200, [row(0), row(INTERVAL_MS), row(2 * INTERVAL_MS)], {})


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
    assert result.artifact.metadata_sha256 in result.artifact.metadata_path.name


def test_rate_limit_is_bounded_and_recorded(tmp_path: Path) -> None:
    slept: list[float] = []
    transport = ScriptedTransport(
        [FetchResponse(429, None, {"Retry-After": "1"}), complete_response()]
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
    result = acquire_historical_klines(
        request(),
        output_directory=tmp_path,
        transport=ScriptedTransport([complete_response()]),
        clock=lambda: NOW,
    )
    with pytest.raises(ArtifactIntegrityError, match="stale"):
        load_immutable_dataset(
            result.artifact, now=NOW + timedelta(hours=1), max_age=timedelta(minutes=15)
        )
    result.artifact.data_path.write_text("{}", encoding="utf-8")
    with pytest.raises(ArtifactIntegrityError, match="checksum"):
        load_immutable_dataset(result.artifact, now=NOW, max_age=timedelta(minutes=15))


def test_tampered_fetch_metadata_fails_checksum_readback(tmp_path: Path) -> None:
    result = acquire_historical_klines(
        request(),
        output_directory=tmp_path,
        transport=ScriptedTransport([complete_response()]),
        clock=lambda: NOW,
    )
    result.artifact.metadata_path.write_text("{}", encoding="utf-8")
    with pytest.raises(ArtifactIntegrityError, match="metadata checksum"):
        load_immutable_dataset(result.artifact, now=NOW, max_age=timedelta(minutes=15))


def test_immutable_write_refuses_conflicting_existing_content(tmp_path: Path) -> None:
    result = acquire_historical_klines(
        request(),
        output_directory=tmp_path,
        transport=ScriptedTransport([complete_response()]),
        clock=lambda: NOW,
    )
    result.artifact.metadata_path.write_text("altered", encoding="utf-8")
    with pytest.raises(ArtifactIntegrityError, match="altered bytes"):
        acquire_historical_klines(
            request(),
            output_directory=tmp_path,
            transport=ScriptedTransport([complete_response()]),
            clock=lambda: NOW,
        )


def test_future_dated_persisted_artifact_fails_closed(tmp_path: Path) -> None:
    result = acquire_historical_klines(
        request(),
        output_directory=tmp_path,
        transport=ScriptedTransport([complete_response()]),
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


def test_transient_transport_error_is_retried_within_budget(tmp_path: Path) -> None:
    slept: list[float] = []
    transport = ScriptedTransport(
        [TransientTransportError("timeout"), complete_response()]
    )
    result = acquire_historical_klines(
        request(),
        output_directory=tmp_path,
        transport=transport,
        policy=AcquisitionPolicy(max_retries=1, retry_backoff_seconds=0.5),
        clock=lambda: NOW,
        sleeper=slept.append,
    )
    assert result.diagnostics.attempts == 2
    assert result.diagnostics.retries == 1
    assert result.diagnostics.transient_transport_failures == 1
    assert result.diagnostics.response_status_codes == (200,)
    assert slept == [0.5]


def test_transient_transport_retry_exhaustion_fails_closed(tmp_path: Path) -> None:
    transport = ScriptedTransport(
        [TransientTransportError("timeout"), TransientTransportError("dns")]
    )
    with pytest.raises(AcquisitionError, match="transient"):
        acquire_historical_klines(
            request(),
            output_directory=tmp_path,
            transport=transport,
            policy=AcquisitionPolicy(max_retries=1),
            clock=lambda: NOW,
            sleeper=lambda seconds: None,
        )


def test_metadata_checksum_can_be_verified_after_restart(tmp_path: Path) -> None:
    result = acquire_historical_klines(
        request(),
        output_directory=tmp_path,
        transport=ScriptedTransport([complete_response()]),
        clock=lambda: NOW,
    )
    recovered = discover_immutable_artifact(result.artifact.data_path)
    assert recovered.metadata_sha256 == result.artifact.metadata_sha256
    loaded = load_immutable_dataset(
        recovered, now=NOW + timedelta(minutes=1), max_age=timedelta(minutes=15)
    )
    assert loaded.dataset_sha256 == result.dataset.dataset_sha256


def test_tampered_metadata_is_rejected_after_restart_discovery(tmp_path: Path) -> None:
    result = acquire_historical_klines(
        request(),
        output_directory=tmp_path,
        transport=ScriptedTransport([complete_response()]),
        clock=lambda: NOW,
    )
    result.artifact.metadata_path.write_text("{}", encoding="utf-8")
    recovered = discover_immutable_artifact(result.artifact.data_path)
    with pytest.raises(ArtifactIntegrityError, match="metadata checksum"):
        load_immutable_dataset(recovered, now=NOW, max_age=timedelta(minutes=15))


def test_missing_checksum_anchor_fails_closed(tmp_path: Path) -> None:
    result = acquire_historical_klines(
        request(),
        output_directory=tmp_path,
        transport=ScriptedTransport([complete_response()]),
        clock=lambda: NOW,
    )
    legacy_metadata_path = tmp_path / f"{result.artifact.artifact_sha256}.metadata.json"
    result.artifact.metadata_path.rename(legacy_metadata_path)
    with pytest.raises(ArtifactIntegrityError, match="anchor"):
        discover_immutable_artifact(result.artifact.data_path)


def test_retry_diagnostics_include_transport_failures(tmp_path: Path) -> None:
    result = acquire_historical_klines(
        request(),
        output_directory=tmp_path,
        transport=ScriptedTransport(
            [TransientTransportError("reset"), complete_response()]
        ),
        policy=AcquisitionPolicy(max_retries=1),
        clock=lambda: NOW,
        sleeper=lambda seconds: None,
    )
    metadata = result.artifact.metadata_path.read_text(encoding="utf-8")
    assert '"transient_transport_failures":1' in metadata


def test_public_transport_uses_get_without_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class Response:
        status = 200
        headers: Mapping[str, str] = {}

        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return b"[]"

    def fake_urlopen(request: object, timeout: float) -> Response:
        captured["request"] = request
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr(acquisition, "urlopen", fake_urlopen)
    response = PublicBinanceFuturesTransport().fetch({"symbol": "BTCUSDT"}, 1.0)
    request_object = cast(Request, captured["request"])
    assert response.status_code == 200
    assert isinstance(request_object, Request)
    assert request_object.get_method() == "GET"
    assert request_object.full_url.startswith(acquisition.PUBLIC_KLINES_URL)
    assert request_object.get_header("Authorization") is None
    assert request_object.get_header("X-MBX-APIKEY") is None


def test_public_transport_wraps_url_failure_as_transient(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_urlopen(request: object, timeout: float) -> object:
        raise URLError("connection reset")

    monkeypatch.setattr(acquisition, "urlopen", fail_urlopen)
    with pytest.raises(TransientTransportError, match="before response"):
        PublicBinanceFuturesTransport().fetch({"symbol": "BTCUSDT"}, 1.0)
