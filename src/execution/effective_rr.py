"""Canonical effective reward-risk calculation for research decisions.

This module validates entry, stop, and take-profit references and produces the
single canonical effective RR payload used by decision audit evidence and reports.
It does not generate signals, simulate fills, allocate risk, place orders, or make
profitability/readiness claims.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from src.persistence.audit import (
    AuditEvidenceItem,
    EvidenceClassification as AuditEvidenceClassification,
)


class EffectiveRRError(ValueError):
    """Raised when effective RR evidence cannot be trusted."""


class TradeSide(StrEnum):
    """Supported research decision directions."""

    LONG = "LONG"
    SHORT = "SHORT"


class EffectiveRRStatus(StrEnum):
    """Availability state for canonical effective RR evidence."""

    VALID = "VALID"
    INVALID = "INVALID"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class EffectiveRRInput:
    """Raw price references required for canonical effective RR calculation."""

    side: TradeSide
    entry_price: float | None
    stop_price: float | None
    take_profit_price: float | None
    raw_expected_rr: float | None = None
    raw_expected_rr_source: str | None = None
    tolerance: float = 1e-9

    def validate(self) -> None:
        if self.tolerance < 0 or not math.isfinite(self.tolerance):
            raise EffectiveRRError("RR tolerance must be finite and non-negative.")
        if self.raw_expected_rr is not None and not math.isfinite(self.raw_expected_rr):
            raise EffectiveRRError("raw_expected_rr must be finite when provided.")
        if self.raw_expected_rr is not None and self.raw_expected_rr <= 0:
            raise EffectiveRRError("raw_expected_rr must be positive when provided.")
        if self.raw_expected_rr is not None and not self.raw_expected_rr_source:
            raise EffectiveRRError(
                "raw_expected_rr_source is required when raw RR is provided."
            )


@dataclass(frozen=True)
class EffectiveRRResult:
    """Canonical effective RR result plus raw inputs and rejection diagnostics."""

    status: EffectiveRRStatus
    side: TradeSide
    entry_price: float | None
    stop_price: float | None
    take_profit_price: float | None
    risk_distance: float | None
    reward_distance: float | None
    effective_rr: float | None
    raw_expected_rr: float | None
    reason_codes: tuple[str, ...]

    def payload(self) -> dict[str, object]:
        """Return deterministic JSON-compatible effective RR evidence."""

        return {
            "status": self.status.value,
            "side": self.side.value,
            "entry_price": self.entry_price,
            "stop_price": self.stop_price,
            "take_profit_price": self.take_profit_price,
            "risk_distance": self.risk_distance,
            "reward_distance": self.reward_distance,
            "effective_rr": self.effective_rr,
            "raw_expected_rr": self.raw_expected_rr,
            "reason_codes": list(self.reason_codes),
        }


def canonical_effective_rr(inputs: EffectiveRRInput) -> EffectiveRRResult:
    """Compute one canonical effective RR value from entry/stop/take-profit."""

    inputs.validate()
    missing = _missing_price_reasons(inputs)
    if missing:
        return _unavailable(inputs, missing)
    assert inputs.entry_price is not None
    assert inputs.stop_price is not None
    assert inputs.take_profit_price is not None
    non_finite = _non_finite_price_reasons(inputs)
    if non_finite:
        return _invalid(inputs, non_finite, None, None, None)
    risk_distance, reward_distance = _distances(inputs)
    invalid_reasons: list[str] = []
    if risk_distance <= 0:
        invalid_reasons.append("INVALID_STOP_DISTANCE")
    if reward_distance <= 0:
        invalid_reasons.append("INVALID_REWARD_DISTANCE")
    if invalid_reasons:
        return _invalid(inputs, tuple(invalid_reasons), risk_distance, reward_distance, None)
    effective_rr = reward_distance / risk_distance
    if not math.isfinite(effective_rr) or effective_rr <= 0:
        return _invalid(
            inputs,
            ("INVALID_EFFECTIVE_RR",),
            risk_distance,
            reward_distance,
            None,
        )
    if (
        inputs.raw_expected_rr is not None
        and abs(inputs.raw_expected_rr - effective_rr) > inputs.tolerance
    ):
        return _invalid(
            inputs,
            ("RAW_EXPECTED_RR_MISMATCH",),
            risk_distance,
            reward_distance,
            effective_rr,
        )
    return EffectiveRRResult(
        status=EffectiveRRStatus.VALID,
        side=inputs.side,
        entry_price=inputs.entry_price,
        stop_price=inputs.stop_price,
        take_profit_price=inputs.take_profit_price,
        risk_distance=risk_distance,
        reward_distance=reward_distance,
        effective_rr=effective_rr,
        raw_expected_rr=inputs.raw_expected_rr,
        reason_codes=("EFFECTIVE_RR_VALID",),
    )


def assert_effective_rr_valid(result: EffectiveRRResult) -> None:
    """Fail closed unless canonical effective RR is valid and available."""

    if result.status is not EffectiveRRStatus.VALID or result.effective_rr is None:
        joined = ", ".join(result.reason_codes)
        raise EffectiveRRError(f"effective RR is not valid: {joined}")


def effective_rr_audit_evidence(result: EffectiveRRResult) -> tuple[AuditEvidenceItem, ...]:
    """Build decision-audit evidence from the canonical effective RR result."""

    if result.status is EffectiveRRStatus.VALID:
        assert result.effective_rr is not None
        return (
            AuditEvidenceItem(
                name="effective_rr",
                classification=AuditEvidenceClassification.MODELED,
                value=_float_text(result.effective_rr),
                source_ref="src.execution.effective_rr.canonical_effective_rr",
            ),
            AuditEvidenceItem(
                name="effective_rr_status",
                classification=AuditEvidenceClassification.MODELED,
                value=result.status.value,
                source_ref="src.execution.effective_rr.canonical_effective_rr",
            ),
        )
    return (
        AuditEvidenceItem(
            name="effective_rr",
            classification=AuditEvidenceClassification.UNAVAILABLE,
            reason=",".join(result.reason_codes),
        ),
        AuditEvidenceItem(
            name="effective_rr_status",
            classification=AuditEvidenceClassification.MODELED,
            value=result.status.value,
            source_ref="src.execution.effective_rr.canonical_effective_rr",
        ),
    )


def effective_rr_report_row(result: EffectiveRRResult) -> dict[str, object]:
    """Return report-ready RR fields sourced from the canonical result."""

    payload = result.payload()
    return {
        "effective_rr_status": payload["status"],
        "effective_rr": payload["effective_rr"],
        "raw_expected_rr": payload["raw_expected_rr"],
        "effective_rr_reason_codes": payload["reason_codes"],
    }


def _missing_price_reasons(inputs: EffectiveRRInput) -> tuple[str, ...]:
    reasons: list[str] = []
    if inputs.entry_price is None:
        reasons.append("MISSING_ENTRY_PRICE")
    if inputs.stop_price is None:
        reasons.append("MISSING_STOP_PRICE")
    if inputs.take_profit_price is None:
        reasons.append("MISSING_TAKE_PROFIT_PRICE")
    return tuple(reasons)


def _non_finite_price_reasons(inputs: EffectiveRRInput) -> tuple[str, ...]:
    reasons: list[str] = []
    prices = {
        "ENTRY_PRICE_NON_FINITE": inputs.entry_price,
        "STOP_PRICE_NON_FINITE": inputs.stop_price,
        "TAKE_PROFIT_PRICE_NON_FINITE": inputs.take_profit_price,
    }
    for reason, price in prices.items():
        assert price is not None
        if not math.isfinite(price):
            reasons.append(reason)
    return tuple(reasons)


def _distances(inputs: EffectiveRRInput) -> tuple[float, float]:
    assert inputs.entry_price is not None
    assert inputs.stop_price is not None
    assert inputs.take_profit_price is not None
    if inputs.side is TradeSide.LONG:
        return (
            inputs.entry_price - inputs.stop_price,
            inputs.take_profit_price - inputs.entry_price,
        )
    return (
        inputs.stop_price - inputs.entry_price,
        inputs.entry_price - inputs.take_profit_price,
    )


def _unavailable(inputs: EffectiveRRInput, reasons: tuple[str, ...]) -> EffectiveRRResult:
    return EffectiveRRResult(
        status=EffectiveRRStatus.UNAVAILABLE,
        side=inputs.side,
        entry_price=inputs.entry_price,
        stop_price=inputs.stop_price,
        take_profit_price=inputs.take_profit_price,
        risk_distance=None,
        reward_distance=None,
        effective_rr=None,
        raw_expected_rr=inputs.raw_expected_rr,
        reason_codes=reasons,
    )


def _invalid(
    inputs: EffectiveRRInput,
    reasons: tuple[str, ...],
    risk_distance: float | None,
    reward_distance: float | None,
    effective_rr: float | None,
) -> EffectiveRRResult:
    return EffectiveRRResult(
        status=EffectiveRRStatus.INVALID,
        side=inputs.side,
        entry_price=inputs.entry_price,
        stop_price=inputs.stop_price,
        take_profit_price=inputs.take_profit_price,
        risk_distance=risk_distance,
        reward_distance=reward_distance,
        effective_rr=effective_rr,
        raw_expected_rr=inputs.raw_expected_rr,
        reason_codes=reasons,
    )


def _float_text(value: float) -> str:
    return format(value, ".12g")
