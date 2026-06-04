"""Research-only backtest foundation and replay boundaries."""

from src.backtest.foundation import (
    REQUIRED_EXECUTION_ASSUMPTIONS,
    BacktestExecutionEvidenceUnavailable,
    BacktestFoundationError,
    BacktestRunMetadata,
    EvidenceClassification,
    ExecutionAssumption,
    ExecutionEvidence,
    assert_can_produce_performance_results,
    backtest_metadata_json,
    unavailable_execution_assumptions,
)
from src.backtest.replay import (
    CandleReplay,
    CandleReplayError,
    CandleReplayMetadata,
    CandleReplayRow,
    build_candle_replay,
    candle_replay_metadata_json,
    candle_replay_rows_json,
)

__all__ = [
    "REQUIRED_EXECUTION_ASSUMPTIONS",
    "BacktestExecutionEvidenceUnavailable",
    "BacktestFoundationError",
    "BacktestRunMetadata",
    "CandleReplay",
    "CandleReplayError",
    "CandleReplayMetadata",
    "CandleReplayRow",
    "EvidenceClassification",
    "ExecutionAssumption",
    "ExecutionEvidence",
    "assert_can_produce_performance_results",
    "backtest_metadata_json",
    "build_candle_replay",
    "candle_replay_metadata_json",
    "candle_replay_rows_json",
    "unavailable_execution_assumptions",
]
