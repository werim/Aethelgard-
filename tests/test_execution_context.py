import json
from dataclasses import replace

import pytest

from src.execution.context import (
    ExecutionAssumptionSnapshot,
    ExecutionContextAssumption,
    ExecutionContextDecisionOutcome,
    ExecutionContextError,
    ExecutionContextInput,
    ExecutionContextStatus,
    assert_execution_context_usable,
    build_execution_context_snapshot,
    execution_context_audit_evidence,
    execution_context_json,
    unavailable_execution_context_assumptions,
)
from src.execution.effective_rr import TradeSide
from src.persistence.audit import EvidenceClassification


def available_assumptions() -> tuple[ExecutionAssumptionSnapshot, ...]:
    return (
        ExecutionAssumptionSnapshot(
            name=ExecutionContextAssumption.SPREAD,
            value=0.0002,
            source="fixture-spread",
        ),
        ExecutionAssumptionSnapshot(
            name=ExecutionContextAssumption.FEE,
            value=0.0004,
            source="fixture-fee",
        ),
        ExecutionAssumptionSnapshot(
            name=ExecutionContextAssumption.SLIPPAGE,
            value=0.0003,
            source="fixture-slippage",
        ),
        ExecutionAssumptionSnapshot(
            name=ExecutionContextAssumption.LATENCY,
            value="100ms modeled",
            source="fixture-latency",
        ),
        ExecutionAssumptionSnapshot(
            name=ExecutionContextAssumption.FUNDING,
            value="unmeasured-not-zero",
            source="fixture-funding",
        ),
    )


def full_context() -> ExecutionContextInput:
    return ExecutionContextInput(
        decision_id="decision-4c-001",
        outcome=ExecutionContextDecisionOutcome.REJECTED,
        symbol="BTCUSDT",
        side=TradeSide.LONG,
        timestamp_utc="2026-06-02T04:40:00Z",
        price_source="binance_futures_mark_price_fixture",
        entry_reference_price=100.0,
        stop_reference_price=95.0,
        take_profit_reference_price=112.5,
        assumptions=available_assumptions(),
    )


def test_fully_populated_context_is_valid_and_serializable() -> None:
    snapshot = build_execution_context_snapshot(full_context())
    assert snapshot.status is ExecutionContextStatus.VALID
    assert snapshot.reason_codes == ("EXECUTION_CONTEXT_VALID",)
    assert_execution_context_usable(snapshot)
    payload = json.loads(execution_context_json(snapshot))
    assert payload["symbol"] == "BTCUSDT"
    assert [item["name"] for item in payload["assumptions"]] == sorted(
        assumption.value for assumption in ExecutionContextAssumption
    )


@pytest.mark.parametrize(
    ("assumption", "reason"),
    [
        (
            ExecutionContextAssumption.SPREAD,
            "SPREAD_ASSUMPTION_UNAVAILABLE",
        ),
        (
            ExecutionContextAssumption.FEE,
            "FEE_ASSUMPTION_UNAVAILABLE",
        ),
        (
            ExecutionContextAssumption.SLIPPAGE,
            "SLIPPAGE_ASSUMPTION_UNAVAILABLE",
        ),
    ],
)
def test_missing_execution_cost_assumption_remains_unavailable(
    assumption: ExecutionContextAssumption,
    reason: str,
) -> None:
    assumptions = tuple(
        (
            ExecutionAssumptionSnapshot(
                name=item.name,
                unavailable_reason="not measured",
            )
            if item.name is assumption
            else item
        )
        for item in available_assumptions()
    )
    snapshot = build_execution_context_snapshot(
        replace(full_context(), assumptions=assumptions)
    )
    assert snapshot.status is ExecutionContextStatus.UNAVAILABLE
    assert reason in snapshot.reason_codes
    with pytest.raises(ExecutionContextError, match="not usable"):
        assert_execution_context_usable(snapshot)


def test_missing_latency_and_funding_are_explicitly_unavailable() -> None:
    assumptions = unavailable_execution_context_assumptions("not measured")
    snapshot = build_execution_context_snapshot(
        replace(full_context(), assumptions=assumptions)
    )
    assert snapshot.status is ExecutionContextStatus.UNAVAILABLE
    assert "LATENCY_ASSUMPTION_UNAVAILABLE" in snapshot.reason_codes
    assert "FUNDING_ASSUMPTION_UNAVAILABLE" in snapshot.reason_codes


def test_missing_timestamp_fails_closed() -> None:
    snapshot = build_execution_context_snapshot(
        replace(full_context(), timestamp_utc=None)
    )
    assert snapshot.status is ExecutionContextStatus.INVALID
    assert "MISSING_TIMESTAMP" in snapshot.reason_codes


def test_stale_market_input_fails_closed() -> None:
    snapshot = build_execution_context_snapshot(
        replace(full_context(), market_input_stale=True)
    )
    assert snapshot.status is ExecutionContextStatus.INVALID
    assert "MARKET_INPUT_STALE" in snapshot.reason_codes


def test_unavailable_market_input_requires_reason_and_fails_closed() -> None:
    with pytest.raises(ExecutionContextError, match="unavailable_reason"):
        build_execution_context_snapshot(
            replace(full_context(), market_input_available=False)
        )
    snapshot = build_execution_context_snapshot(
        replace(
            full_context(),
            market_input_available=False,
            market_input_unavailable_reason="book snapshot missing",
        )
    )
    assert snapshot.status is ExecutionContextStatus.INVALID
    assert "MARKET_INPUT_UNAVAILABLE" in snapshot.reason_codes


def test_rejected_decision_still_carries_diagnostic_context() -> None:
    snapshot = build_execution_context_snapshot(
        replace(
            full_context(),
            outcome=ExecutionContextDecisionOutcome.REJECTED,
            assumptions=unavailable_execution_context_assumptions("not measured"),
        )
    )
    payload = snapshot.payload()
    assert payload["outcome"] == "REJECTED"
    assert payload["entry_reference_price"] == 100.0
    assert snapshot.status is ExecutionContextStatus.UNAVAILABLE


@pytest.mark.parametrize(
    ("field", "reason"),
    [
        ("entry", "MISSING_ENTRY_REFERENCE_PRICE"),
        ("stop", "MISSING_STOP_REFERENCE_PRICE"),
        ("take_profit", "MISSING_TAKE_PROFIT_REFERENCE_PRICE"),
    ],
)
def test_missing_critical_price_reference_fails_closed(
    field: str,
    reason: str,
) -> None:
    context = full_context()
    if field == "entry":
        context = replace(context, entry_reference_price=None)
    elif field == "stop":
        context = replace(context, stop_reference_price=None)
    elif field == "take_profit":
        context = replace(context, take_profit_reference_price=None)
    else:
        raise AssertionError("unexpected field fixture")
    snapshot = build_execution_context_snapshot(context)
    assert snapshot.status is ExecutionContextStatus.INVALID
    assert reason in snapshot.reason_codes


def test_unavailable_assumption_cannot_carry_zero_value() -> None:
    snapshot = ExecutionAssumptionSnapshot(
        name=ExecutionContextAssumption.FEE,
        value=0.0,
        unavailable_reason="not measured",
    )
    with pytest.raises(ExecutionContextError, match="cannot carry value"):
        snapshot.validate()


def test_persistence_round_trip_audit_evidence_uses_snapshot_payload() -> None:
    snapshot = build_execution_context_snapshot(full_context())
    evidence = execution_context_audit_evidence(snapshot)
    assert evidence[0].name == "execution_context"
    assert evidence[0].classification is EvidenceClassification.MODELED
    assert evidence[0].value == execution_context_json(snapshot)
    assert evidence[1].value == "VALID"


def test_unavailable_context_audit_evidence_preserves_reason() -> None:
    snapshot = build_execution_context_snapshot(
        replace(full_context(), timestamp_utc=None)
    )
    evidence = execution_context_audit_evidence(snapshot)
    assert evidence[0].classification is EvidenceClassification.UNAVAILABLE
    assert evidence[0].value is None
    assert "MISSING_TIMESTAMP" in str(evidence[0].reason)
