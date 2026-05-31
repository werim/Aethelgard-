from pathlib import Path

import pytest

from src.persistence.reconciliation import (
    PersistenceReconciliationError,
    PersistenceReconciliationReport,
    ReconciliationIssue,
    ReconciliationIssueType,
    ReconciliationReportStatus,
    persist_reconciliation_report_artifact,
    read_reconciliation_report_artifact,
)


def inconsistent_report() -> PersistenceReconciliationReport:
    return PersistenceReconciliationReport(
        matched_decision_ids=("decision_001",),
        issues=(
            ReconciliationIssue(
                issue_type=ReconciliationIssueType.MISSING_DATABASE_EVENT,
                decision_id="decision_002",
                event_id="decision_audit_appended_2222",
                detail="Verified decision audit file has no matching database event.",
            ),
        ),
    )


def test_persist_reconciliation_report_artifact_round_trips(
    tmp_path: Path,
) -> None:
    persisted = persist_reconciliation_report_artifact(
        tmp_path,
        inconsistent_report(),
    )

    verified = read_reconciliation_report_artifact(persisted.metadata_path)

    assert verified == persisted
    assert verified.status is ReconciliationReportStatus.INCONSISTENT
    assert verified.json_path.name.startswith("reconciliation-report-")
    assert verified.json_sha256 in verified.json_path.name
    assert verified.json_sha256 in verified.markdown_path.name
    assert verified.metadata_sha256 in verified.metadata_path.name


def test_persist_reconciliation_report_artifact_is_idempotent(
    tmp_path: Path,
) -> None:
    first = persist_reconciliation_report_artifact(tmp_path, inconsistent_report())
    second = persist_reconciliation_report_artifact(tmp_path, inconsistent_report())

    assert second == first
    assert len(list(tmp_path.iterdir())) == 3


def test_persist_reconciliation_report_artifact_handles_unavailable(
    tmp_path: Path,
) -> None:
    persisted = persist_reconciliation_report_artifact(
        tmp_path,
        None,
        unavailable_reason="Audit database unavailable during scan.",
    )

    assert persisted.status is ReconciliationReportStatus.UNAVAILABLE
    assert "Audit database unavailable" in persisted.markdown_path.read_text(
        encoding="utf-8"
    )


def test_read_reconciliation_report_artifact_detects_json_tampering(
    tmp_path: Path,
) -> None:
    persisted = persist_reconciliation_report_artifact(tmp_path, inconsistent_report())
    persisted.json_path.write_text('{"status":"CONSISTENT"}', encoding="utf-8")

    with pytest.raises(PersistenceReconciliationError, match="JSON checksum"):
        read_reconciliation_report_artifact(persisted.metadata_path)


def test_read_reconciliation_report_artifact_detects_markdown_tampering(
    tmp_path: Path,
) -> None:
    persisted = persist_reconciliation_report_artifact(tmp_path, inconsistent_report())
    persisted.markdown_path.write_text("tampered\n", encoding="utf-8")

    with pytest.raises(PersistenceReconciliationError, match="Markdown checksum"):
        read_reconciliation_report_artifact(persisted.metadata_path)


def test_read_reconciliation_report_artifact_detects_metadata_tampering(
    tmp_path: Path,
) -> None:
    persisted = persist_reconciliation_report_artifact(tmp_path, inconsistent_report())
    persisted.metadata_path.write_text("{}", encoding="utf-8")

    with pytest.raises(PersistenceReconciliationError, match="Metadata checksum"):
        read_reconciliation_report_artifact(persisted.metadata_path)


def test_persist_reconciliation_report_artifact_rejects_conflicting_file(
    tmp_path: Path,
) -> None:
    persisted = persist_reconciliation_report_artifact(tmp_path, inconsistent_report())
    persisted.json_path.write_text("conflict", encoding="utf-8")

    with pytest.raises(PersistenceReconciliationError, match="conflicting artifact"):
        persist_reconciliation_report_artifact(tmp_path, inconsistent_report())
