from collections.abc import Sequence

import pytest

from src.data.klines import (
    DatasetProvenance,
    DataValidationError,
    validate_historical_klines,
)

INTERVAL_MS = 60_000


def provenance(fetched_at: str = "2026-05-25T12:00:00Z") -> DatasetProvenance:
    return DatasetProvenance(
        source="BINANCE_FUTURES_REST",
        symbol="BTCUSDT",
        timeframe="1m",
        fetched_at_utc=fetched_at,
        request_parameters={"interval": "1m", "limit": "2"},
    )


def row(open_time_ms: int, *, high: str = "101", close: str = "100.5") -> list[object]:
    return [
        open_time_ms,
        "100",
        high,
        "99",
        close,
        "12.3",
        open_time_ms + INTERVAL_MS - 1,
        "1234.5",
        31,
        "6.0",
        "601.0",
        "0",
    ]


def validate(rows: Sequence[Sequence[object]]) -> str:
    dataset = validate_historical_klines(
        rows, provenance=provenance(), interval_ms=INTERVAL_MS
    )
    return dataset.dataset_sha256


def test_valid_klines_are_normalized_and_hashed_deterministically() -> None:
    rows = [row(0), row(INTERVAL_MS)]
    first = validate_historical_klines(
        rows, provenance=provenance(), interval_ms=INTERVAL_MS
    )
    second = validate_historical_klines(
        rows,
        provenance=provenance("2026-05-25T12:01:00+00:00"),
        interval_ms=INTERVAL_MS,
    )
    assert first.row_count == 2
    assert first.dataset_sha256 == second.dataset_sha256
    assert first.evidence_classification == "MEASURED"


def test_duplicate_timestamp_fails_closed() -> None:
    with pytest.raises(DataValidationError, match="Duplicate"):
        validate([row(0), row(0)])


def test_missing_candle_gap_fails_closed() -> None:
    with pytest.raises(DataValidationError, match="Missing candle"):
        validate([row(0), row(2 * INTERVAL_MS)])


def test_out_of_range_price_fails_closed() -> None:
    with pytest.raises(DataValidationError, match="close_price"):
        validate([row(0, high="100", close="101")])


def test_non_utc_provenance_timestamp_fails_closed() -> None:
    with pytest.raises(DataValidationError, match="must use UTC"):
        validate_historical_klines(
            [row(0)],
            provenance=provenance("2026-05-25T15:00:00+03:00"),
            interval_ms=INTERVAL_MS,
        )


def test_incorrect_candle_close_timestamp_fails_closed() -> None:
    malformed = row(0)
    malformed[6] = INTERVAL_MS
    with pytest.raises(DataValidationError, match="close_time_ms"):
        validate([malformed])
