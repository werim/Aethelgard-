from dataclasses import replace
from pathlib import Path

import pytest

from src.persistence.audit import (
    AuditEvidenceItem,
    DecisionAuditRecord,
    DecisionOutcome,
    EvidenceClassification,
    discover_decision_audits,
)
from src.persistence.events import AuditEventIntegrityError, list_audit_events
from src.persistence.integration import append_decision_audit_event

DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


def record(
    *,
    decision_id: str = "decision_001",
    operating_mode: str = "PAPER_ONLY",
) -> DecisionAuditRecord:
    return DecisionAuditRecord(
        decision_id=decision_id,
        recorded_at_utc="2026-05-30T18:00:00Z",
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
                name="spread_bps",
                classification=EvidenceClassification.UNAVAILABLE,
                reason="No orderbook snapshot is available at this gate.",
            ),
        ),
        operating_mode=operating_mode,
    )


def test_decision_audit_append_records_matching_database_event(
    tmp_path: Path,
) -> None:
    audit_dir = tmp_path / "audits"
    db = tmp_path / "audit-events.sqlite3"

    integrated = append_decision_audit_event(record(), audit_dir, db)
    discovered_audits = discover_decision_audits(audit_dir)
    listed_events = list_audit_events(db)

    assert discovered_audits == (integrated.audit,)
    assert listed_events == (integrated.event,)
    assert integrated.event.event.decision_id == integrated.audit.record.decision_id
    assert integrated.event.event.payload["decision_audit_sha256"] == integrated.audit.record_sha256
    assert integrated.event.event.payload["decision_audit_filename"] == integrated.audit.path.name
    assert integrated.event.event.payload["decision_claim_filename"] == integrated.audit.claim_path.name
    assert integrated.event.event.payload["artifact_sha256"] == DIGEST_B
    assert integrated.event.event.payload["evidence_classifications"] == [
        "MEASURED",
        "UNAVAILABLE",
    ]
    assert integrated.event.event.payload["unavailable_evidence"] == ["spread_bps"]


def test_decision_audit_event_append_is_idempotent(tmp_path: Path) -> None:
    audit_dir = tmp_path / "audits"
    db = tmp_path / "audit-events.sqlite3"

    first = append_decision_audit_event(record(), audit_dir, db)
    second = append_decision_audit_event(record(), audit_dir, db)

    assert first == second
    assert len(discover_decision_audits(audit_dir)) == 1
    assert len(list_audit_events(db)) == 1


def test_integration_fails_closed_on_non_paper_record(tmp_path: Path) -> None:
    audit_dir = tmp_path / "audits"
    db = tmp_path / "audit-events.sqlite3"

    with pytest.raises(ValueError, match="PAPER_ONLY"):
        append_decision_audit_event(record(operating_mode="BAD_MODE"), audit_dir, db)

    assert not audit_dir.exists()
    assert not db.exists()


def test_integration_preflights_database_overlap_before_file_write(
    tmp_path: Path,
) -> None:
    audit_dir = tmp_path / "audits"
    db = tmp_path / "audit-events.sqlite3"
    append_decision_audit_event(record(), audit_dir, db)

    changed_record = replace(record(), recorded_at_utc="2026-05-30T18:01:00Z")
    with pytest.raises(AuditEventIntegrityError, match="conflicting database"):
        append_decision_audit_event(changed_record, audit_dir, db)

    assert len(discover_decision_audits(audit_dir)) == 1
    assert len(list_audit_events(db)) == 1
