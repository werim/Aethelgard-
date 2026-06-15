import json

from src.reporting.data_freshness_evidence import (
    DataFreshnessEvidence,
    DataFreshnessEvidenceStatus,
    assess_data_freshness_for_gate5a,
    data_freshness_evidence_assessment_json,
)
from src.reporting.operational_evidence import (
    OperationalDeploymentStatus,
    OperationalEvidenceClassification,
    OperationalEvidenceItem,
    evaluate_operational_evidence_gate,
)


def _measured_evidence_item(blocker_id: str) -> OperationalEvidenceItem:
    return OperationalEvidenceItem(
        blocker_id=blocker_id,
        classification=OperationalEvidenceClassification.MEASURED,
        summary=f"{blocker_id} measured evidence",
        source=f"unit://{blocker_id}",
    )


def _complete_gate_evidence(
    data_item: OperationalEvidenceItem,
) -> tuple[OperationalEvidenceItem, ...]:
    return (
        _measured_evidence_item("audit_trail_integrity"),
        _measured_evidence_item("ci_validation"),
        data_item,
        _measured_evidence_item("execution_cost_evidence"),
        _measured_evidence_item("paper_runtime_reconciliation"),
        _measured_evidence_item("risk_control_enforcement"),
    )


def _fresh_data_evidence() -> DataFreshnessEvidence:
    return DataFreshnessEvidence(
        source="unit://data-freshness-report",
        dataset_id="binance_futures_klines_1m",
        expected_selector_id="top_20_usdt_perp_snapshot_a",
        observed_selector_id="top_20_usdt_perp_snapshot_a",
        latest_closed_bar_at_utc="2026-06-15T06:00:00Z",
        observed_age_seconds=30,
        max_age_seconds=120,
    )


def test_measured_data_freshness_evidence_clears_gate5a_blocker() -> None:
    assessment = assess_data_freshness_for_gate5a(_fresh_data_evidence())
    result = evaluate_operational_evidence_gate(
        _complete_gate_evidence(assessment.evidence_item)
    )

    assert assessment.status is DataFreshnessEvidenceStatus.FRESHNESS_MEASURED
    assert assessment.classification is OperationalEvidenceClassification.MEASURED
    assert assessment.evidence_item.blocker_id == "data_freshness"
    assert result.status is OperationalDeploymentStatus.DEPLOYMENT_NOT_BLOCKED


def test_missing_data_freshness_evidence_remains_unavailable() -> None:
    assessment = assess_data_freshness_for_gate5a(
        None,
        source="unit://missing-data-freshness-evidence",
    )

    assert assessment.status is DataFreshnessEvidenceStatus.UNAVAILABLE
    assert assessment.classification is OperationalEvidenceClassification.UNAVAILABLE
    assert assessment.evidence_item.blocker_id == "data_freshness"
    assert "data-freshness evidence is unavailable" in assessment.diagnostics


def test_stale_data_freshness_evidence_remains_unavailable() -> None:
    evidence = DataFreshnessEvidence(
        source="unit://data-freshness-report",
        dataset_id="binance_futures_klines_1m",
        expected_selector_id="top_20_usdt_perp_snapshot_a",
        observed_selector_id="top_20_usdt_perp_snapshot_a",
        latest_closed_bar_at_utc="2026-06-15T06:00:00Z",
        observed_age_seconds=121,
        max_age_seconds=120,
    )

    assessment = assess_data_freshness_for_gate5a(evidence)

    assert assessment.status is DataFreshnessEvidenceStatus.UNAVAILABLE
    assert assessment.classification is OperationalEvidenceClassification.UNAVAILABLE
    assert "data-freshness observed_age_seconds exceeds max_age_seconds" in (
        assessment.diagnostics
    )


def test_selector_mismatch_remains_unavailable() -> None:
    evidence = DataFreshnessEvidence(
        source="unit://data-freshness-report",
        dataset_id="binance_futures_klines_1m",
        expected_selector_id="top_20_usdt_perp_snapshot_a",
        observed_selector_id="top_50_usdt_perp_snapshot_b",
        latest_closed_bar_at_utc="2026-06-15T06:00:00Z",
        observed_age_seconds=30,
        max_age_seconds=120,
    )

    assessment = assess_data_freshness_for_gate5a(evidence)

    assert assessment.status is DataFreshnessEvidenceStatus.UNAVAILABLE
    assert (
        "data selector mismatch: expected 'top_20_usdt_perp_snapshot_a', "
        "observed 'top_50_usdt_perp_snapshot_b'"
    ) in assessment.diagnostics


def test_malformed_data_freshness_evidence_remains_unavailable() -> None:
    evidence = DataFreshnessEvidence(
        source=" ",
        dataset_id=" binance_futures_klines_1m",
        expected_selector_id="",
        observed_selector_id=" top_20_usdt_perp_snapshot_a",
        latest_closed_bar_at_utc="",
        observed_age_seconds=-1,
        max_age_seconds=0,
    )

    assessment = assess_data_freshness_for_gate5a(evidence)

    assert assessment.status is DataFreshnessEvidenceStatus.UNAVAILABLE
    assert "data-freshness evidence source is missing" in assessment.diagnostics
    assert (
        "data-freshness dataset id ' binance_futures_klines_1m' " "is non-canonical"
    ) in assessment.diagnostics
    assert "data-freshness expected selector id is missing" in assessment.diagnostics
    assert "data-freshness latest closed bar timestamp is missing" in (
        assessment.diagnostics
    )
    assert "data-freshness max_age_seconds must be positive" in assessment.diagnostics
    assert "data-freshness observed_age_seconds must be non-negative" in (
        assessment.diagnostics
    )


def test_data_freshness_json_is_deterministic_and_non_performance() -> None:
    assessment = assess_data_freshness_for_gate5a(_fresh_data_evidence())

    payload = json.loads(data_freshness_evidence_assessment_json(assessment))
    encoded = data_freshness_evidence_assessment_json(assessment)

    assert payload["classification"] == "MEASURED"
    assert encoded == data_freshness_evidence_assessment_json(assessment)
    for forbidden in ("pnl", "profit", "returns", "win_rate", "sharpe"):
        assert forbidden not in encoded.lower()
