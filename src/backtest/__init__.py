"""Research-only backtest foundation boundaries."""

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

__all__ = [
    "REQUIRED_EXECUTION_ASSUMPTIONS",
    "BacktestExecutionEvidenceUnavailable",
    "BacktestFoundationError",
    "BacktestRunMetadata",
    "EvidenceClassification",
    "ExecutionAssumption",
    "ExecutionEvidence",
    "assert_can_produce_performance_results",
    "backtest_metadata_json",
    "unavailable_execution_assumptions",
]
