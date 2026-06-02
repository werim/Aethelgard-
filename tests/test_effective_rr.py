import math

import pytest

from src.execution.effective_rr import (
    EffectiveRRError,
    EffectiveRRInput,
    EffectiveRRStatus,
    TradeSide,
    assert_effective_rr_valid,
    canonical_effective_rr,
    effective_rr_audit_evidence,
    effective_rr_report_row,
)
from src.persistence.audit import EvidenceClassification


def test_valid_long_effective_rr_is_canonical() -> None:
    result = canonical_effective_rr(
        EffectiveRRInput(
            side=TradeSide.LONG,
            entry_price=100.0,
            stop_price=95.0,
            take_profit_price=112.5,
            raw_expected_rr=2.5,
            raw_expected_rr_source="fixture",
        )
    )
    assert result.status is EffectiveRRStatus.VALID
    assert result.risk_distance == 5.0
    assert result.reward_distance == 12.5
    assert result.effective_rr == 2.5
    assert_effective_rr_valid(result)


def test_valid_short_effective_rr_is_canonical() -> None:
    result = canonical_effective_rr(
        EffectiveRRInput(
            side=TradeSide.SHORT,
            entry_price=100.0,
            stop_price=104.0,
            take_profit_price=90.0,
        )
    )
    assert result.status is EffectiveRRStatus.VALID
    assert result.risk_distance == 4.0
    assert result.reward_distance == 10.0
    assert result.effective_rr == 2.5


@pytest.mark.parametrize(
    ("entry", "stop", "take_profit"),
    [
        (100.0, 100.0, 110.0),
        (100.0, 101.0, 110.0),
        (100.0, 99.0, 99.0),
    ],
)
def test_invalid_or_non_positive_distances_fail_closed(
    entry: float, stop: float, take_profit: float
) -> None:
    result = canonical_effective_rr(
        EffectiveRRInput(
            side=TradeSide.LONG,
            entry_price=entry,
            stop_price=stop,
            take_profit_price=take_profit,
        )
    )
    assert result.status is EffectiveRRStatus.INVALID
    with pytest.raises(EffectiveRRError, match="effective RR is not valid"):
        assert_effective_rr_valid(result)


def test_non_finite_price_fails_closed() -> None:
    result = canonical_effective_rr(
        EffectiveRRInput(
            side=TradeSide.LONG,
            entry_price=math.inf,
            stop_price=95.0,
            take_profit_price=110.0,
        )
    )
    assert result.status is EffectiveRRStatus.INVALID
    assert "ENTRY_PRICE_NON_FINITE" in result.reason_codes


@pytest.mark.parametrize(
    ("entry", "stop", "take_profit", "reason"),
    [
        (None, 95.0, 110.0, "MISSING_ENTRY_PRICE"),
        (100.0, None, 110.0, "MISSING_STOP_PRICE"),
        (100.0, 95.0, None, "MISSING_TAKE_PROFIT_PRICE"),
    ],
)
def test_missing_references_remain_unavailable(
    entry: float | None,
    stop: float | None,
    take_profit: float | None,
    reason: str,
) -> None:
    result = canonical_effective_rr(
        EffectiveRRInput(
            side=TradeSide.LONG,
            entry_price=entry,
            stop_price=stop,
            take_profit_price=take_profit,
        )
    )
    assert result.status is EffectiveRRStatus.UNAVAILABLE
    assert result.effective_rr is None
    assert reason in result.reason_codes


def test_raw_expected_rr_mismatch_fails_closed_but_keeps_diagnostic() -> None:
    result = canonical_effective_rr(
        EffectiveRRInput(
            side=TradeSide.LONG,
            entry_price=100.0,
            stop_price=95.0,
            take_profit_price=110.0,
            raw_expected_rr=3.0,
            raw_expected_rr_source="legacy-fixture",
        )
    )
    assert result.status is EffectiveRRStatus.INVALID
    assert result.effective_rr == 2.0
    assert result.raw_expected_rr == 3.0
    assert result.reason_codes == ("RAW_EXPECTED_RR_MISMATCH",)


def test_raw_expected_rr_requires_source_and_finite_positive_value() -> None:
    with pytest.raises(EffectiveRRError, match="raw_expected_rr_source"):
        canonical_effective_rr(
            EffectiveRRInput(
                side=TradeSide.LONG,
                entry_price=100.0,
                stop_price=95.0,
                take_profit_price=110.0,
                raw_expected_rr=2.0,
            )
        )
    with pytest.raises(EffectiveRRError, match="positive"):
        canonical_effective_rr(
            EffectiveRRInput(
                side=TradeSide.LONG,
                entry_price=100.0,
                stop_price=95.0,
                take_profit_price=110.0,
                raw_expected_rr=0.0,
                raw_expected_rr_source="fixture",
            )
        )


def test_persistence_and_reporting_use_same_canonical_value() -> None:
    result = canonical_effective_rr(
        EffectiveRRInput(
            side=TradeSide.SHORT,
            entry_price=200.0,
            stop_price=210.0,
            take_profit_price=175.0,
        )
    )
    payload = result.payload()
    evidence = effective_rr_audit_evidence(result)
    report = effective_rr_report_row(result)
    assert payload["effective_rr"] == 2.5
    assert evidence[0].name == "effective_rr"
    assert evidence[0].classification is EvidenceClassification.MODELED
    assert evidence[0].value == "2.5"
    assert report["effective_rr"] == payload["effective_rr"]
    assert report["effective_rr_status"] == payload["status"]


def test_unavailable_rr_audit_evidence_preserves_reason() -> None:
    result = canonical_effective_rr(
        EffectiveRRInput(
            side=TradeSide.LONG,
            entry_price=None,
            stop_price=95.0,
            take_profit_price=110.0,
        )
    )
    evidence = effective_rr_audit_evidence(result)
    assert evidence[0].classification is EvidenceClassification.UNAVAILABLE
    assert evidence[0].value is None
    assert evidence[0].reason == "MISSING_ENTRY_PRICE"
