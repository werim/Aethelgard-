import json

from src.persistence.reconciliation import (
    PersistenceReconciliationReport,
    ReconciliationIssue,
    ReconciliationIssueType,
)
from src.reporting.audit_runtime_evidence import (
    AuditRuntimeEvidenceStatus,
    assess_audit_runtime_reconciliation_for_gate5a,
    audit_runtime_evidence_assessment_json,
)
from src.reporting.operational_evidence import (
    REQUIRED_OPERATIONAL_BLOCKERS,
    OperationalDeploymentStatus,
    OperationalEvidenceClassification,
    OperationalEvidenceItem,
    evaluate_operational_evidence_gate,
)


def _consistent_report() -> PersistenceReconciliationReport:
    return PersistenceReconciliationReport(
        matched_decision_ids=("decision-1", "decision-2"),
        issues=(),
    )


def test_audit_runtime_evidence_is_measured_when_reconciled() -> None:
    assessment = assess_audit_runtime_reconciliation_for_gate5a(
        _consistent_report(),
        source="reconciliation artifact abc123",
    )

    assert assessment.status is AuditRuntimeEvidenceStatus.RECONCILED
    assert assessment.classification is OperationalEvidenceClassification.MEASURED
    assert {item.blocker_id for item in assessment.evidence_items} == {
        "audit_trail_integrity",
        "paper_runtime_reconciliation",
    }
    assert "2 matched decision" in assessment.diagnostics[0]


def test_audit_runtime_evidence_is_unavailable_without_report() -> None:
    assessment = assess_audit_runtime_reconciliation_for_gate5a(
        None,
        source="reconciliation artifact missing",
    )

    assert assessment.status is AuditRuntimeEvidenceStatus.UNAVAILABLE
    assert assessment.classification is OperationalEvidenceClassification.UNAVAILABLE
    assert "report is unavailable" in assessment.diagnostics[0]


def test_audit_runtime_evidence_is_unavailable_with_reconciliation_issue() -> None:
    report = PersistenceReconciliationReport(
        matched_decision_ids=("decision-1",),
        issues=(
            ReconciliationIssue(
                issue_type=ReconciliationIssueType.MISSING_DATABASE_EVENT,
                decision_id="decision-2",
                event_id="event-2",
                detail="missing database event",
            ),
        ),
    )

    assessment = assess_audit_runtime_reconciliation_for_gate5a(
        report,
        source="reconciliation artifact abc123",
    )

    assert assessment.status is AuditRuntimeEvidenceStatus.UNAVAILABLE
    assert (
        assessment.evidence_items[0].classification
        is OperationalEvidenceClassification.UNAVAILABLE
    )
    assert "MISSING_DATABASE_EVENT" in assessment.diagnostics[0]


def test_audit_runtime_evidence_is_unavailable_without_matched_decisions() -> None:
    assessment = assess_audit_runtime_reconciliation_for_gate5a(
        PersistenceReconciliationReport(matched_decision_ids=(), issues=()),
        source="reconciliation artifact empty",
    )

    assert assessment.status is AuditRuntimeEvidenceStatus.UNAVAILABLE
    assert "no matched decision audits" in assessment.diagnostics[0]


def test_audit_runtime_evidence_rewrites_missing_source_as_unavailable() -> None:
    assessment = assess_audit_runtime_reconciliation_for_gate5a(
        _consistent_report(),
        source=" ",
    )

    assert assessment.status is AuditRuntimeEvidenceStatus.UNAVAILABLE
    assert (
        assessment.evidence_items[0].source
        == "UNAVAILABLE: missing audit/runtime source"
    )


def test_audit_runtime_evidence_items_can_feed_gate5a_rows() -> None:
    assessment = assess_audit_runtime_reconciliation_for_gate5a(
        _consistent_report(),
        source="reconciliation artifact abc123",
    )
    assessment_by_blocker = {
        item.blocker_id: item for item in assessment.evidence_items
    }
    evidence_items = tuple(
        (
            assessment_by_blocker[blocker_id]
            if blocker_id in assessment_by_blocker
            else OperationalEvidenceItem(
                blocker_id=blocker_id,
                classification=OperationalEvidenceClassification.MEASURED,
                summary=f"measured evidence for {blocker_id}",
                source="test fixture",
            )
        )
        for blocker_id in REQUIRED_OPERATIONAL_BLOCKERS
    )

    result = evaluate_operational_evidence_gate(evidence_items)

    assert result.status is OperationalDeploymentStatus.DEPLOYMENT_NOT_BLOCKED
    assert result.paper_deployment_blocked is False


def test_audit_runtime_evidence_json_has_no_performance_metrics() -> None:
    assessment = assess_audit_runtime_reconciliation_for_gate5a(
        _consistent_report(),
        source="reconciliation artifact abc123",
    )
    payload = json.loads(audit_runtime_evidence_assessment_json(assessment))

    assert list(payload) == [
        "classification",
        "diagnostics",
        "evidence_items",
        "status",
    ]
    forbidden = {"pnl", "profit", "returns", "sharpe", "drawdown", "win_rate"}
    item_keys = {key for item in payload["evidence_items"] for key in item}

    assert forbidden.isdisjoint(set(payload) | item_keys)
