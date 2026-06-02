"""Execution context snapshots for research-only decisions.

This module records explicit execution context evidence for accepted or rejected
research decisions. It does not simulate fills, assume execution quality, submit
orders, run PAPER loops, or certify readiness.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from json import dumps
from re import fullmatch

from src.execution.effective_rr import TradeSide
from src.persistence.audit import (
    AuditEvidenceItem,
)
from src.persistence.audit import (
    EvidenceClassification as AuditEvidenceClassification,
)


class ExecutionContextError(ValueError):
    """Raised when execution context evidence is incomplete or unsafe."""


class ExecutionContextStatus(StrEnum):
    """Availability state for a decision execution context snapshot."""

    VALID = "VALID"
    INVALID = "INVALID"
    UNAVAILABLE = "UNAVAILABLE"


class ExecutionContextAssumption(StrEnum):
    """Execution-cost assumptions that must not silently become zero."""

    SPREAD = "spread"
    FEE = "fee"
    SLIPPAGE = "slippage"
    LATENCY = "latency"
    FUNDING = "funding"


class ExecutionContextDecisionOutcome(StrEnum):
    """Decision outcomes admitted by this research-only context boundary."""

    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ExecutionAssumptionSnapshot:
    """One explicit execution assumption value or unavailable reason."""

    name: ExecutionContextAssumption
    value: float | str | None = None
    source: str | None = None
    unavailable_reason: str | None = None

    @property
    def available(self) -> bool:
        return self.unavailable_reason is None

    def validate(self) -> None:
        if self.available:
            if self.value is None:
                raise ExecutionContextError(
                    f"{self.name.value} assumption requires an explicit value."
                )
            if isinstance(self.value, float) and not math.isfinite(self.value):
                raise ExecutionContextError(
                    f"{self.name.value} assumption must be finite."
                )
            if self.source is None or not self.source.strip():
                raise ExecutionContextError(
                    f"{self.name.value} assumption requires a source."
                )
            return
        if self.value is not None:
            raise ExecutionContextError(
                f"{self.name.value} unavailable assumption cannot carry value."
            )
        if self.source is not None:
            raise ExecutionContextError(
                f"{self.name.value} unavailable assumption cannot carry source."
            )
        if self.unavailable_reason is None or not self.unavailable_reason.strip():
            raise ExecutionContextError(
                f"{self.name.value} unavailable assumption requires reason."
            )

    def payload(self) -> dict[str, object]:
        self.validate()
        return {
            "name": self.name.value,
            "available": self.available,
            "value": self.value,
            "source": self.source,
            "unavailable_reason": self.unavailable_reason,
        }


@dataclass(frozen=True)
class ExecutionContextInput:
    """Raw caller-provided execution context references for one decision."""

    decision_id: str
    outcome: ExecutionContextDecisionOutcome
    symbol: str
    side: TradeSide
    timestamp_utc: str | None
    price_source: str
    entry_reference_price: float | None
    stop_reference_price: float | None
    take_profit_reference_price: float | None
    assumptions: tuple[ExecutionAssumptionSnapshot, ...]
    market_input_available: bool = True
    market_input_stale: bool = False
    market_input_unavailable_reason: str | None = None


@dataclass(frozen=True)
class ExecutionContextSnapshot:
    """Validated execution context snapshot with fail-closed diagnostics."""

    status: ExecutionContextStatus
    decision_id: str
    outcome: ExecutionContextDecisionOutcome
    symbol: str
    side: TradeSide
    timestamp_utc: str | None
    price_source: str
    entry_reference_price: float | None
    stop_reference_price: float | None
    take_profit_reference_price: float | None
    assumptions: tuple[ExecutionAssumptionSnapshot, ...]
    reason_codes: tuple[str, ...]

    def payload(self) -> dict[str, object]:
        return {
            "status": self.status.value,
            "decision_id": self.decision_id,
            "outcome": self.outcome.value,
            "symbol": self.symbol,
            "side": self.side.value,
            "timestamp_utc": self.timestamp_utc,
            "price_source": self.price_source,
            "entry_reference_price": self.entry_reference_price,
            "stop_reference_price": self.stop_reference_price,
            "take_profit_reference_price": self.take_profit_reference_price,
            "assumptions": [
                assumption.payload()
                for assumption in sorted(
                    self.assumptions,
                    key=lambda item: item.name.value,
                )
            ],
            "reason_codes": list(self.reason_codes),
        }


REQUIRED_EXECUTION_CONTEXT_ASSUMPTIONS: tuple[ExecutionContextAssumption, ...] = (
    ExecutionContextAssumption.SPREAD,
    ExecutionContextAssumption.FEE,
    ExecutionContextAssumption.SLIPPAGE,
    ExecutionContextAssumption.LATENCY,
    ExecutionContextAssumption.FUNDING,
)


def unavailable_execution_context_assumptions(
    reason: str,
) -> tuple[ExecutionAssumptionSnapshot, ...]:
    """Build explicit unavailable execution-cost assumptions."""

    if not reason.strip():
        raise ExecutionContextError(
            "unavailable execution context assumption reason required"
        )
    return tuple(
        ExecutionAssumptionSnapshot(name=assumption, unavailable_reason=reason)
        for assumption in REQUIRED_EXECUTION_CONTEXT_ASSUMPTIONS
    )


def build_execution_context_snapshot(
    raw_context: ExecutionContextInput,
) -> ExecutionContextSnapshot:
    """Validate and classify one execution context snapshot."""

    _validate_context_identity(raw_context)
    assumption_reasons = _validate_assumptions(raw_context.assumptions)
    reason_codes = [
        *_price_reference_reasons(raw_context),
        *_market_input_reasons(raw_context),
        *assumption_reasons,
    ]
    status = ExecutionContextStatus.VALID
    critical_reasons = {
        "MISSING_TIMESTAMP",
        "MISSING_ENTRY_REFERENCE_PRICE",
        "MISSING_STOP_REFERENCE_PRICE",
        "MISSING_TAKE_PROFIT_REFERENCE_PRICE",
        "MARKET_INPUT_UNAVAILABLE",
        "MARKET_INPUT_STALE",
        "INVALID_ENTRY_REFERENCE_PRICE",
        "INVALID_STOP_REFERENCE_PRICE",
        "INVALID_TAKE_PROFIT_REFERENCE_PRICE",
    }
    if raw_context.timestamp_utc is None:
        reason_codes.insert(0, "MISSING_TIMESTAMP")
    if reason_codes:
        if any(reason in critical_reasons for reason in reason_codes):
            status = ExecutionContextStatus.INVALID
        else:
            status = ExecutionContextStatus.UNAVAILABLE
    else:
        reason_codes = ["EXECUTION_CONTEXT_VALID"]
    return ExecutionContextSnapshot(
        status=status,
        decision_id=raw_context.decision_id,
        outcome=raw_context.outcome,
        symbol=raw_context.symbol,
        side=raw_context.side,
        timestamp_utc=raw_context.timestamp_utc,
        price_source=raw_context.price_source,
        entry_reference_price=raw_context.entry_reference_price,
        stop_reference_price=raw_context.stop_reference_price,
        take_profit_reference_price=raw_context.take_profit_reference_price,
        assumptions=raw_context.assumptions,
        reason_codes=tuple(reason_codes),
    )


def assert_execution_context_usable(snapshot: ExecutionContextSnapshot) -> None:
    """Fail closed unless critical execution context fields are valid."""

    if snapshot.status is not ExecutionContextStatus.VALID:
        joined = ", ".join(snapshot.reason_codes)
        raise ExecutionContextError(f"execution context is not usable: {joined}")


def execution_context_json(snapshot: ExecutionContextSnapshot) -> str:
    """Serialize an execution context snapshot deterministically."""

    return dumps(snapshot.payload(), sort_keys=True, separators=(",", ":"))


def execution_context_audit_evidence(
    snapshot: ExecutionContextSnapshot,
) -> tuple[AuditEvidenceItem, ...]:
    """Build decision-audit evidence from the execution context snapshot."""

    source_ref = "src.execution.context.build_execution_context_snapshot"
    if snapshot.status is ExecutionContextStatus.VALID:
        return (
            AuditEvidenceItem(
                name="execution_context",
                classification=AuditEvidenceClassification.MODELED,
                value=execution_context_json(snapshot),
                source_ref=source_ref,
            ),
            AuditEvidenceItem(
                name="execution_context_status",
                classification=AuditEvidenceClassification.MODELED,
                value=snapshot.status.value,
                source_ref=source_ref,
            ),
        )
    return (
        AuditEvidenceItem(
            name="execution_context",
            classification=AuditEvidenceClassification.UNAVAILABLE,
            reason=",".join(snapshot.reason_codes),
        ),
        AuditEvidenceItem(
            name="execution_context_status",
            classification=AuditEvidenceClassification.MODELED,
            value=snapshot.status.value,
            source_ref=source_ref,
        ),
    )


def _validate_context_identity(raw_context: ExecutionContextInput) -> None:
    if not fullmatch(r"[A-Za-z0-9_-]{1,64}", raw_context.decision_id):
        raise ExecutionContextError("decision_id must be a safe non-empty identifier.")
    if not fullmatch(r"[A-Z0-9]{5,20}", raw_context.symbol):
        raise ExecutionContextError("symbol must use uppercase exchange notation.")
    if not raw_context.price_source.strip():
        raise ExecutionContextError("price_source is required.")
    if raw_context.timestamp_utc is not None:
        _validate_utc_timestamp(raw_context.timestamp_utc)


def _validate_assumptions(
    assumptions: tuple[ExecutionAssumptionSnapshot, ...],
) -> tuple[str, ...]:
    required = set(REQUIRED_EXECUTION_CONTEXT_ASSUMPTIONS)
    received = {assumption.name for assumption in assumptions}
    if received != required:
        missing = sorted(assumption.value for assumption in required - received)
        extra = sorted(assumption.value for assumption in received - required)
        raise ExecutionContextError(
            f"execution context assumptions must match required set; "
            f"missing={missing}; extra={extra}"
        )
    reasons: list[str] = []
    for assumption in assumptions:
        assumption.validate()
        if not assumption.available:
            reasons.append(f"{assumption.name.value.upper()}_ASSUMPTION_UNAVAILABLE")
    return tuple(reasons)


def _price_reference_reasons(raw_context: ExecutionContextInput) -> tuple[str, ...]:
    reasons: list[str] = []
    price_fields = (
        ("MISSING_ENTRY_REFERENCE_PRICE", raw_context.entry_reference_price),
        ("MISSING_STOP_REFERENCE_PRICE", raw_context.stop_reference_price),
        (
            "MISSING_TAKE_PROFIT_REFERENCE_PRICE",
            raw_context.take_profit_reference_price,
        ),
    )
    for missing_reason, price in price_fields:
        if price is None:
            reasons.append(missing_reason)
        elif not math.isfinite(price) or price <= 0:
            reasons.append(missing_reason.replace("MISSING", "INVALID"))
    return tuple(reasons)


def _market_input_reasons(raw_context: ExecutionContextInput) -> tuple[str, ...]:
    reasons: list[str] = []
    if not raw_context.market_input_available:
        if (
            raw_context.market_input_unavailable_reason is None
            or not raw_context.market_input_unavailable_reason.strip()
        ):
            raise ExecutionContextError(
                "market_input_unavailable_reason is required when market input "
                "is unavailable."
            )
        reasons.append("MARKET_INPUT_UNAVAILABLE")
    if raw_context.market_input_stale:
        reasons.append("MARKET_INPUT_STALE")
    return tuple(reasons)


def _validate_utc_timestamp(timestamp: str) -> None:
    if not fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", timestamp):
        raise ExecutionContextError(
            "timestamp_utc must be UTC ISO-8601 seconds ending with 'Z'."
        )
