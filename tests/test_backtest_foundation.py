import json
from dataclasses import replace

import pytest

from src.backtest.foundation import (
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

SHA_A = "a" * 64
SHA_B = "b" * 64


def metadata_with_unavailable_execution() -> BacktestRunMetadata:
    return BacktestRunMetadata(
        run_id="run-20260601-btcusdt-1h",
        dataset_fingerprint=SHA_A,
        symbol="BTCUSDT",
        timeframe="1h",
        start_ts="2026-01-01T00:00:00Z",
        end_ts="2026-02-01T00:00:00Z",
        seed=42,
        config_hash=SHA_B,
        code_version="0.12.0",
        created_at="2026-06-01T23:00:00Z",
        execution_assumptions=unavailable_execution_assumptions(
            "execution evidence has not been measured or modeled"
        ),
    )


def measured_or_modeled_execution() -> dict[ExecutionAssumption, ExecutionEvidence]:
    return {
        assumption: ExecutionEvidence(
            classification=EvidenceClassification.MODELED,
            description=f"{assumption.value} modeled for validation test",
            value="modeled-placeholder",
        )
        for assumption in ExecutionAssumption
    }


def test_metadata_payload_is_deterministic() -> None:
    metadata = metadata_with_unavailable_execution()
    first = backtest_metadata_json(metadata)
    second = backtest_metadata_json(metadata)
    assert first == second
    payload = json.loads(first)
    assert payload["run_id"] == "run-20260601-btcusdt-1h"
    assert list(payload["execution_assumptions"]) == sorted(
        assumption.value for assumption in ExecutionAssumption
    )


def test_unavailable_execution_evidence_blocks_results() -> None:
    metadata = metadata_with_unavailable_execution()
    with pytest.raises(BacktestExecutionEvidenceUnavailable) as excinfo:
        assert_can_produce_performance_results(metadata)
    message = str(excinfo.value)
    assert "fees" in message
    assert "slippage" in message
    assert "orderbook_state" in message


def test_all_required_modeled_or_measured_evidence_passes_guard() -> None:
    metadata = metadata_with_unavailable_execution()
    complete_metadata = replace(
        metadata,
        execution_assumptions=measured_or_modeled_execution(),
    )
    assert_can_produce_performance_results(complete_metadata)


def test_missing_execution_assumption_fails_closed() -> None:
    assumptions = unavailable_execution_assumptions("missing one for test")
    del assumptions[ExecutionAssumption.FEES]
    metadata = replace(
        metadata_with_unavailable_execution(),
        execution_assumptions=assumptions,
    )
    with pytest.raises(BacktestFoundationError, match="missing"):
        metadata.validate()


def test_unavailable_evidence_cannot_carry_zero_value() -> None:
    evidence = ExecutionEvidence(
        classification=EvidenceClassification.UNAVAILABLE,
        description="fees unavailable",
        value=0.0,
        unavailable_reason="not measured",
    )
    with pytest.raises(BacktestFoundationError, match="cannot carry value"):
        evidence.validate()


def test_measured_evidence_requires_source() -> None:
    evidence = ExecutionEvidence(
        classification=EvidenceClassification.MEASURED,
        description="fees measured",
        value=0.0004,
    )
    with pytest.raises(BacktestFoundationError, match="requires a source"):
        evidence.validate()


def test_invalid_hash_fails_closed() -> None:
    metadata = replace(
        metadata_with_unavailable_execution(),
        dataset_fingerprint="not-a-sha",
    )
    with pytest.raises(BacktestFoundationError, match="dataset_fingerprint"):
        metadata.validate()


def test_non_utc_timestamp_fails_closed() -> None:
    metadata = replace(
        metadata_with_unavailable_execution(),
        start_ts="2026-01-01T00:00:00+03:00",
    )
    with pytest.raises(BacktestFoundationError, match="UTC"):
        metadata.validate()


def test_start_must_precede_end() -> None:
    metadata = replace(
        metadata_with_unavailable_execution(),
        start_ts="2026-02-01T00:00:00Z",
        end_ts="2026-01-01T00:00:00Z",
    )
    with pytest.raises(BacktestFoundationError, match="before"):
        metadata.validate()


def test_unavailable_assumption_reason_required() -> None:
    with pytest.raises(BacktestFoundationError, match="reason required"):
        unavailable_execution_assumptions(" ")
