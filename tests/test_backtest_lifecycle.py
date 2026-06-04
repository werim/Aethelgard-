import json
from decimal import Decimal

import pytest

from src.backtest.lifecycle import (
    LifecycleState,
    TradeLifecycleSimulationError,
    build_trade_lifecycle_simulation,
    lifecycle_metadata_json,
    lifecycle_transitions_json,
)
from src.backtest.replay import CandleReplay, CandleReplayMetadata, CandleReplayRow


def replay(status: str = "VALID") -> CandleReplay:
    rows = (
        CandleReplayRow(
            symbol="BTCUSDT",
            timeframe="1h",
            open_time="2026-01-01T00:00:00Z",
            open=Decimal("100"),
            high=Decimal("110"),
            low=Decimal("90"),
            close=Decimal("105"),
            volume=Decimal("12.5"),
        ),
        CandleReplayRow(
            symbol="BTCUSDT",
            timeframe="1h",
            open_time="2026-01-01T01:00:00Z",
            open=Decimal("105"),
            high=Decimal("112"),
            low=Decimal("101"),
            close=Decimal("106"),
            volume=Decimal("13"),
        ),
        CandleReplayRow(
            symbol="BTCUSDT",
            timeframe="1h",
            open_time="2026-01-01T02:00:00Z",
            open=Decimal("106"),
            high=Decimal("113"),
            low=Decimal("100"),
            close=Decimal("102"),
            volume=Decimal("14"),
        ),
    )
    return CandleReplay(
        rows=rows,
        metadata=CandleReplayMetadata(
            dataset_fingerprint="a" * 64,
            symbol="BTCUSDT",
            timeframe="1h",
            start_ts="2026-01-01T00:00:00Z",
            end_ts="2026-01-01T02:00:00Z",
            row_count=3,
            missing_interval_count=0,
            duplicate_count=0,
            validation_status=status,
            deterministic_hash="b" * 64,
        ),
    )


def test_entry_and_exit_observations_create_terminal_closed_lifecycle() -> None:
    simulation = build_trade_lifecycle_simulation(
        replay(),
        [
            {
                "event_type": "ENTRY_OBSERVED",
                "event_time": "2026-01-01T00:00:00Z",
                "price": "101",
            },
            {
                "event_type": "EXIT_OBSERVED",
                "event_time": "2026-01-01T02:00:00Z",
                "price": "104",
            },
        ],
        trade_id="trade-001",
    )

    assert simulation.metadata.validation_status == "VALID"
    assert simulation.metadata.terminal_state == LifecycleState.POSITION_OBSERVED_CLOSED
    assert [transition.to_state for transition in simulation.iter_transitions()] == [
        LifecycleState.POSITION_OBSERVED_OPEN,
        LifecycleState.POSITION_OBSERVED_CLOSED,
    ]
    assert "pnl" not in lifecycle_metadata_json(simulation.metadata).lower()


def test_entry_rejected_is_terminal_without_opening_position() -> None:
    simulation = build_trade_lifecycle_simulation(
        replay(),
        [
            {
                "event_type": "ENTRY_REJECTED",
                "event_time": "2026-01-01T00:00:00Z",
                "note": "spread evidence unavailable",
            }
        ],
        trade_id="trade-002",
    )

    assert simulation.metadata.terminal_state == LifecycleState.ENTRY_REJECTED
    assert simulation.metadata.transition_count == 1


def test_timeout_requires_observed_entry_first() -> None:
    with pytest.raises(TradeLifecycleSimulationError, match="without observed entry"):
        build_trade_lifecycle_simulation(
            replay(),
            [
                {
                    "event_type": "TIMEOUT_OBSERVED",
                    "event_time": "2026-01-01T01:00:00Z",
                }
            ],
            trade_id="trade-003",
        )


def test_missing_terminal_state_fails_closed() -> None:
    simulation = build_trade_lifecycle_simulation(
        replay(),
        [
            {
                "event_type": "ENTRY_OBSERVED",
                "event_time": "2026-01-01T00:00:00Z",
            }
        ],
        trade_id="trade-004",
        allow_read_only_diagnostics=True,
    )

    assert simulation.metadata.validation_status == "INVALID"
    assert simulation.metadata.terminal_state == LifecycleState.INVALID
    with pytest.raises(TradeLifecycleSimulationError, match="invalid lifecycle"):
        simulation.iter_transitions()


def test_event_without_replay_candle_fails_closed() -> None:
    with pytest.raises(TradeLifecycleSimulationError, match="no replay candle"):
        build_trade_lifecycle_simulation(
            replay(),
            [
                {
                    "event_type": "ENTRY_OBSERVED",
                    "event_time": "2026-01-01T00:30:00Z",
                },
                {
                    "event_type": "EXIT_OBSERVED",
                    "event_time": "2026-01-01T02:00:00Z",
                },
            ],
            trade_id="trade-005",
        )


def test_duplicate_or_unsorted_events_fail_closed() -> None:
    with pytest.raises(TradeLifecycleSimulationError, match="not increasing"):
        build_trade_lifecycle_simulation(
            replay(),
            [
                {
                    "event_type": "ENTRY_OBSERVED",
                    "event_time": "2026-01-01T01:00:00Z",
                },
                {
                    "event_type": "EXIT_OBSERVED",
                    "event_time": "2026-01-01T00:00:00Z",
                },
            ],
            trade_id="trade-006",
        )


def test_invalid_replay_is_rejected_before_lifecycle_simulation() -> None:
    with pytest.raises(TradeLifecycleSimulationError, match="valid candle replay"):
        build_trade_lifecycle_simulation(
            replay(status="INVALID"),
            [
                {
                    "event_type": "ENTRY_REJECTED",
                    "event_time": "2026-01-01T00:00:00Z",
                }
            ],
            trade_id="trade-007",
        )


def test_price_is_optional_but_cannot_be_non_positive() -> None:
    with pytest.raises(TradeLifecycleSimulationError, match="price must be positive"):
        build_trade_lifecycle_simulation(
            replay(),
            [
                {
                    "event_type": "ENTRY_OBSERVED",
                    "event_time": "2026-01-01T00:00:00Z",
                    "price": "0",
                },
                {
                    "event_type": "EXIT_OBSERVED",
                    "event_time": "2026-01-01T02:00:00Z",
                },
            ],
            trade_id="trade-008",
        )


def test_metadata_and_transition_json_are_deterministic() -> None:
    observations = [
        {"event_type": "ENTRY_OBSERVED", "event_time": "2026-01-01T00:00:00Z"},
        {"event_type": "EXIT_OBSERVED", "event_time": "2026-01-01T02:00:00Z"},
    ]
    first = build_trade_lifecycle_simulation(
        replay(), observations, trade_id="trade-009"
    )
    second = build_trade_lifecycle_simulation(
        replay(), observations, trade_id="trade-009"
    )

    assert lifecycle_metadata_json(first.metadata) == lifecycle_metadata_json(
        second.metadata
    )
    assert lifecycle_transitions_json(first.transitions) == lifecycle_transitions_json(
        second.transitions
    )
    payload = json.loads(lifecycle_metadata_json(first.metadata))
    assert payload["event_count"] == 2
    assert payload["terminal_state"] == "POSITION_OBSERVED_CLOSED"
