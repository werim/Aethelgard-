import json

from src.persistence.reconciliation import (
    PersistenceReconciliationReport,
    ReconciliationIssue,
    ReconciliationIssueType,
    reconciliation_report_json,
    reconciliation_report_markdown,
    reconciliation_report_payload,
)


def inconsistent_report() -> PersistenceReconciliationReport:
    return PersistenceReconciliationReport(
        matched_decision_ids=("decision_002", "decision_001"),
        issues=(
            ReconciliationIssue(
                issue_type=ReconciliationIssueType.MISSING_FILE_AUDIT,
                decision_id="decision_003",
                event_id="decision_audit_appended_3333",
                detail="Database event has no matching verified decision audit file.",
            ),
            ReconciliationIssue(
                issue_type=ReconciliationIssueType.MISSING_DATABASE_EVENT,
                decision_id="decision_004",
                event_id="decision_audit_appended_4444",
                detail="Verified decision audit file has no matching database event.",
            ),
        ),
    )


def test_reconciliation_report_payload_marks_consistent_report() -> None:
    report = PersistenceReconciliationReport(
        matched_decision_ids=("decision_001",),
        issues=(),
    )

    payload = reconciliation_report_payload(report)

    assert payload["schema_version"] == 1
    assert payload["status"] == "CONSISTENT"
    assert payload["matched_count"] == 1
    assert payload["matched_decision_ids"] == ["decision_001"]
    assert payload["issue_count"] == 0
    assert payload["unavailable_reason"] is None


def test_reconciliation_report_payload_counts_and_sorts_issues() -> None:
    payload = reconciliation_report_payload(inconsistent_report())

    assert payload["status"] == "INCONSISTENT"
    assert payload["matched_decision_ids"] == ["decision_001", "decision_002"]
    assert payload["issue_count"] == 2
    assert payload["issue_counts"] == {
        "DATABASE_EVENT_MISMATCH": 0,
        "MISSING_DATABASE_EVENT": 1,
        "MISSING_FILE_AUDIT": 1,
    }
    assert payload["issues"] == [
        {
            "issue_type": "MISSING_DATABASE_EVENT",
            "decision_id": "decision_004",
            "event_id": "decision_audit_appended_4444",
            "detail": "Verified decision audit file has no matching database event.",
        },
        {
            "issue_type": "MISSING_FILE_AUDIT",
            "decision_id": "decision_003",
            "event_id": "decision_audit_appended_3333",
            "detail": "Database event has no matching verified decision audit file.",
        },
    ]


def test_reconciliation_report_payload_marks_unavailable_report() -> None:
    payload = reconciliation_report_payload(
        None,
        unavailable_reason="Audit database could not be read.",
    )

    assert payload["status"] == "UNAVAILABLE"
    assert payload["matched_count"] == 0
    assert payload["issue_count"] == 0
    assert payload["issues"] == []
    assert payload["unavailable_reason"] == "Audit database could not be read."


def test_reconciliation_report_json_is_deterministic() -> None:
    encoded = reconciliation_report_json(inconsistent_report())

    assert encoded == reconciliation_report_json(inconsistent_report())
    decoded = json.loads(encoded)
    assert decoded["status"] == "INCONSISTENT"
    assert decoded["issue_counts"]["MISSING_DATABASE_EVENT"] == 1


def test_reconciliation_report_markdown_is_deterministic() -> None:
    markdown = reconciliation_report_markdown(inconsistent_report())

    assert markdown == reconciliation_report_markdown(inconsistent_report())
    assert "# Persistence Reconciliation Report" in markdown
    assert "- Status: `INCONSISTENT`" in markdown
    assert "- `MISSING_DATABASE_EVENT`: `1`" in markdown
    assert "### `MISSING_FILE_AUDIT`" in markdown


def test_reconciliation_report_markdown_records_unavailable_reason() -> None:
    markdown = reconciliation_report_markdown(
        None,
        unavailable_reason="Reconciliation scan failed closed.",
    )

    assert "- Status: `UNAVAILABLE`" in markdown
    assert "## Unavailable evidence" in markdown
    assert "Reconciliation scan failed closed." in markdown
