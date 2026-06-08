import json

import pytest

from src.backtest.replay import (
    CandleReplayError,
    build_candle_replay,
    candle_replay_metadata_json,
)


def candle(open_time: str, **overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "open_time": open_time,
        "open": "100",
        "high": "110",
        "low": "90",
        "close": "105",
        "volume": "12.5",
    }
    row.update(overrides)
    return row


def valid_rows() -> list[dict[str, object]]:
    return [
        candle("2026-01-01T00:00:00Z"),
        candle("2026-01-01T01:00:00Z", open="105", high="112", low="101"),
        candle("2026-01-01T02:00:00Z", open="106", high="113", low="100"),
    ]


def test_valid_replay_preserves_timestamp_order_and_metadata() -> None:
    replay = build_candle_replay(valid_rows(), symbol="BTCUSDT", timeframe="1h")
    assert [row.open_time for row in replay.iter_rows()] == [
        "2026-01-01T00:00:00Z",
        "2026-01-01T01:00:00Z",
        "2026-01-01T02:00:00Z",
    ]
    assert replay.metadata.validation_status == "VALID"
    assert replay.metadata.row_count == 3
    assert replay.metadata.duplicate_count == 0
    assert replay.metadata.missing_interval_count == 0
    assert len(replay.metadata.dataset_fingerprint) == 64
    assert len(replay.metadata.deterministic_hash) == 64


def test_replay_metadata_json_is_deterministic() -> None:
    first = build_candle_replay(valid_rows()).metadata
    second = build_candle_replay(valid_rows()).metadata
    assert candle_replay_metadata_json(first) == candle_replay_metadata_json(second)
    payload = json.loads(candle_replay_metadata_json(first))
    assert payload["symbol"] == "BTCUSDT"
    assert payload["timeframe"] == "1h"


def test_duplicate_candles_fail_closed() -> None:
    rows = [candle("2026-01-01T00:00:00Z"), candle("2026-01-01T00:00:00Z")]
    with pytest.raises(CandleReplayError, match="duplicate"):
        build_candle_replay(rows)


def test_unsorted_candles_fail_closed() -> None:
    rows = [candle("2026-01-01T01:00:00Z"), candle("2026-01-01T00:00:00Z")]
    with pytest.raises(CandleReplayError, match="strictly increasing"):
        build_candle_replay(rows)


def test_missing_interval_fails_closed_and_is_counted_in_diagnostics() -> None:
    rows = [candle("2026-01-01T00:00:00Z"), candle("2026-01-01T03:00:00Z")]
    replay = build_candle_replay(rows, allow_read_only_diagnostics=True)
    assert replay.metadata.validation_status == "INVALID"
    assert replay.metadata.missing_interval_count == 2
    with pytest.raises(CandleReplayError, match="cannot replay invalid"):
        replay.iter_rows()


def test_non_utc_timestamp_fails_closed() -> None:
    with pytest.raises(CandleReplayError, match="UTC"):
        build_candle_replay([candle("2026-01-01T00:00:00+03:00")])


def test_malformed_ohlcv_fails_closed() -> None:
    with pytest.raises(CandleReplayError, match="malformed OHLC"):
        build_candle_replay([candle("2026-01-01T00:00:00Z", high="99")])


def test_non_positive_price_fails_closed() -> None:
    with pytest.raises(CandleReplayError, match="open must be positive"):
        build_candle_replay([candle("2026-01-01T00:00:00Z", open="0")])


def test_negative_volume_fails_closed() -> None:
    with pytest.raises(CandleReplayError, match="volume cannot be negative"):
        build_candle_replay([candle("2026-01-01T00:00:00Z", volume="-1")])


def test_symbol_and_timeframe_mismatch_fail_closed() -> None:
    with pytest.raises(CandleReplayError, match="symbol mismatch"):
        build_candle_replay([candle("2026-01-01T00:00:00Z")], symbol="ETHUSDT")
    with pytest.raises(CandleReplayError, match="timeframe mismatch"):
        build_candle_replay([candle("2026-01-01T00:00:00Z")], timeframe="5m")


def test_replay_outputs_contain_no_performance_metric_fields() -> None:
    replay = build_candle_replay(valid_rows(), symbol="BTCUSDT", timeframe="1h")
    metadata_payload = json.loads(candle_replay_metadata_json(replay.metadata))
    forbidden_keys = {
        "pnl",
        "profit",
        "loss",
        "returns",
        "return",
        "win_rate",
        "sharpe",
        "drawdown",
        "expectancy",
        "alpha",
        "beta",
        "equity",
        "balance",
        "position",
        "signal",
        "trade",
        "fill",
        "fee",
        "slippage",
        "latency",
        "readiness",
    }

    assert forbidden_keys.isdisjoint(metadata_payload)
    for row in replay.iter_rows():
        assert forbidden_keys.isdisjoint(row.payload())


def test_replay_does_not_import_execution_or_order_paths() -> None:
    import sys

    saved_execution_modules = {
        name: module
        for name, module in list(sys.modules.items())
        if name == "src.execution" or name.startswith("src.execution.")
    }
    for name in saved_execution_modules:
        del sys.modules[name]

    try:
        replay = build_candle_replay(valid_rows(), symbol="BTCUSDT", timeframe="1h")
        list(replay.iter_rows())

        loaded_execution_modules = {
            name
            for name in sys.modules
            if name == "src.execution" or name.startswith("src.execution.")
        }
        loaded_order_modules = {
            name for name in loaded_execution_modules if "order" in name
        }

        assert loaded_execution_modules == set()
        assert loaded_order_modules == set()
    finally:
        sys.modules.update(saved_execution_modules)
