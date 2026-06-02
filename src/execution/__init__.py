"""Research-only execution evidence helpers."""

from src.execution.effective_rr import (
    EffectiveRRError,
    EffectiveRRInput,
    EffectiveRRResult,
    EffectiveRRStatus,
    TradeSide,
    assert_effective_rr_valid,
    canonical_effective_rr,
    effective_rr_audit_evidence,
    effective_rr_report_row,
)

__all__ = [
    "EffectiveRRError",
    "EffectiveRRInput",
    "EffectiveRRResult",
    "EffectiveRRStatus",
    "TradeSide",
    "assert_effective_rr_valid",
    "canonical_effective_rr",
    "effective_rr_audit_evidence",
    "effective_rr_report_row",
]
