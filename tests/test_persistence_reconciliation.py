from pathlib import Path

import pytest

from src.persistence.audit import (
    AuditEvidenceItem,
    DecisionAuditRecord,
    DecisionOutcome,
    EvidenceClassification,
    append_decision_audit,
)
from src.persistence.events import (
    AuditEventRecord,
    AuditEventType,
    append_audit_event,
)
from src.persistence.integration import append_decision_audit_event
from src.persistence.reconciliation import (
    PersistenceReconciliationError,
    ReconciliationIssueType,
    assert_decision_audit_events_reconciled,
    reconcile_decision_audit_events,
)

DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


def record(decision_id: str = "decision_001") -> DecisionAuditRecord:
    return DecisionAuditRecord(
        decision_id=decision_id,
        recorded_at_utc="2026-05-31T05:30:00Z",
        symbol="BTCUSDT",
        timeframe="1m",
        outcome=DecisionOutcome.REJECTED,
        reason_codes=("INSUFFICIENT_EXECUTION_EVIDENCE",),
        dataset_sha256=DIGEST_A,
        artifact_sha256=DIGEST_B,
        evidence=(
            AuditEvidenceItem(
                name="dataset_integrity",
                classification=EvidenceClassification.MEASURED,
                value="verified",
                source_ref="artifact_sha256:" + DIGEST_B,
            ),
            AuditEvidenceItem(
                name="latency_ms",
                classification=EvidenceClassification.UNAVAILABLE,
                reason="No runtime latency measurement is available at this gate.",
            ),
        ),
    )


def test_reconciliation_reports_consistent_integrated_evidence(
    tmp_path: Path,
) -> None:
    audit_dir = tmp_path / "audits"
    db = tmp_path / "audit-events.sqlite3"
    append_decision_audit_event(record(), audit_dir, db)

    report = assert_decision_audit_events_reconciled(audit_dir, db)

    assert report.is_consistent
    assert report.matched_decision_ids == ("decision_001",)
    assert report.issues == ()


def test_reconciliation_reports_missing_database_event(tmp_path: Path) -> None:
    audit_dir = tmp_path / "audits"
    db = tmp_path / "audit-events.sqlite3"
    append_decision_audit(record(), audit_dir)

    report = reconcile_decision_audit_events(audit_dir, db)

    assert not report.is_consistent
    assert report.issues[0].issue_type is ReconciliationIssueType.MISSING_DATABASE_EVENT
    assert report.issues[0].decision_id == "decision_001"


def test_reconciliation_reports_missing_file_audit(tmp_path: Path) -> None:
    audit_dir = tmp_path / "audits"
    db = tmp_path / "audit-events.sqlite3"
    append_decision_audit_event(record(), audit_dir, db)
    for path in audit_dir.iterdir():
        path.unlink()

    report = reconcile_decision_audit_events(audit_dir, db)

    assert not report.is_consistent
    assert report.issues[0].issue_type is ReconciliationIssueType.MISSING_FILE_AUDIT
    assert report.issues[0].decision_id == "decision_001"


def test_reconciliation_reports_database_event_mismatch(tmp_path: Path) -> None:
    audit_dir = tmp_path / "audits"
    db = tmp_path / "audit-events.sqlite3"
    append_decision_audit(record(), audit_dir)
    append_audit_event(
        db,
        AuditEventRecord(
            event_id="decision_audit_appended_" + "1" * 32,
            event_type=AuditEventType.DECISION_AUDIT_APPENDED,
            occurred_at_utc="2026-05-31T05:30:00Z",
            decision_id="decision_001",
            payload={"decision_audit_sha256": "wrong"},
        ),
    )

    report = reconcile_decision_audit_events(audit_dir, db)

    assert not report.is_consistent
    assert (
        report.issues[0].issue_type
        is ReconciliationIssueType.DATABASE_EVENT_MISMATCH
    )
    assert report.issues[0].event_id == "decision_audit_appended_" + "1" * 32


def test_reconciliation_assertion_fails_closed_on_mismatch(tmp_path: Path) -> None:
    audit_dir = tmp_path / "audits"
    db = tmp_path / "audit-events.sqlite3"
    append_decision_audit(record(), audit_dir)

    with pytest.raises(PersistenceReconciliationError, match="MISSING_DATABASE_EVENT"):
        assert_decision_audit_events_reconciled(audit_dir, db)
