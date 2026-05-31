"""Reconciliation scan for local file and database audit persistence.

This module reads existing research-only persistence evidence and reports
file/database mismatch states. It does not repair evidence, generate decisions,
run backtests, approve execution, submit orders, or certify readiness.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from src.persistence.audit import PersistedAuditRecord, discover_decision_audits
from src.persistence.events import (
    AuditEventType,
    PersistedAuditEvent,
    list_audit_events,
)
from src.persistence.integration import (
    decision_audit_event_id,
    decision_audit_event_payload,
)


class PersistenceReconciliationError(ValueError):
    """Raised when local persistence evidence does not reconcile cleanly."""


class ReconciliationIssueType(StrEnum):
    """Mismatch states admitted by the Gate 2D reconciliation scan."""

    MISSING_DATABASE_EVENT = "MISSING_DATABASE_EVENT"
    MISSING_FILE_AUDIT = "MISSING_FILE_AUDIT"
    DATABASE_EVENT_MISMATCH = "DATABASE_EVENT_MISMATCH"


class ReconciliationReportStatus(StrEnum):
    """Fail-closed publication status for a reconciliation report surface."""

    CONSISTENT = "CONSISTENT"
    INCONSISTENT = "INCONSISTENT"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class ReconciliationIssue:
    """One fail-closed mismatch between file audit and database event evidence."""

    issue_type: ReconciliationIssueType
    decision_id: str
    event_id: str | None
    detail: str


@dataclass(frozen=True)
class PersistenceReconciliationReport:
    """Summary of a local file/database persistence reconciliation scan."""

    matched_decision_ids: tuple[str, ...]
    issues: tuple[ReconciliationIssue, ...]

    @property
    def is_consistent(self) -> bool:
        """Return True only when all discovered local evidence matched exactly."""

        return not self.issues

    def fail_closed(self) -> None:
        """Reject use of local persistence evidence when mismatch states exist."""

        if self.issues:
            issue_names = ", ".join(issue.issue_type.value for issue in self.issues)
            raise PersistenceReconciliationError(
                "Persistence reconciliation found mismatch states: " + issue_names
            )


def _decision_audit_events(
    database_path: Path,
) -> tuple[PersistedAuditEvent, ...]:
    if not database_path.exists():
        return ()
    return tuple(
        persisted
        for persisted in list_audit_events(database_path)
        if persisted.event.event_type is AuditEventType.DECISION_AUDIT_APPENDED
    )


def _event_matches_audit(
    audit: PersistedAuditRecord,
    event: PersistedAuditEvent,
) -> bool:
    expected_event_id = decision_audit_event_id(
        audit.record.decision_id,
        audit.record_sha256,
    )
    expected_payload = decision_audit_event_payload(audit)
    return (
        event.event.event_id == expected_event_id
        and event.event.decision_id == audit.record.decision_id
        and event.event.payload == expected_payload
        and event.event.operating_mode == "PAPER_ONLY"
        and event.event.readiness == "RESEARCH_ONLY"
    )


def reconcile_decision_audit_events(
    audit_directory: Path,
    database_path: Path,
) -> PersistenceReconciliationReport:
    """Scan local audit files and database events for exact evidence alignment.

    Missing, orphaned, corrupt, or mismatched evidence is reported as a
    fail-closed issue. Corrupt file or database rows still raise through the
    underlying readback validators rather than being normalized away.
    """

    audits = discover_decision_audits(audit_directory)
    events = _decision_audit_events(database_path)
    audit_by_decision = {audit.record.decision_id: audit for audit in audits}
    event_by_decision = {event.event.decision_id: event for event in events}
    issues: list[ReconciliationIssue] = []
    matched: list[str] = []

    for decision_id, audit in sorted(audit_by_decision.items()):
        event = event_by_decision.get(decision_id)
        expected_event_id = decision_audit_event_id(decision_id, audit.record_sha256)
        if event is None:
            issues.append(
                ReconciliationIssue(
                    issue_type=ReconciliationIssueType.MISSING_DATABASE_EVENT,
                    decision_id=decision_id,
                    event_id=expected_event_id,
                    detail=(
                        "Verified decision audit file has no matching "
                        "database event."
                    ),
                )
            )
            continue
        if not _event_matches_audit(audit, event):
            issues.append(
                ReconciliationIssue(
                    issue_type=ReconciliationIssueType.DATABASE_EVENT_MISMATCH,
                    decision_id=decision_id,
                    event_id=event.event.event_id,
                    detail=(
                        "Database event identity or payload does not match the "
                        "verified decision audit file."
                    ),
                )
            )
            continue
        matched.append(decision_id)

    for decision_id, event in sorted(event_by_decision.items()):
        if decision_id not in audit_by_decision:
            issues.append(
                ReconciliationIssue(
                    issue_type=ReconciliationIssueType.MISSING_FILE_AUDIT,
                    decision_id=decision_id,
                    event_id=event.event.event_id,
                    detail=(
                        "Database event has no matching verified decision "
                        "audit file."
                    ),
                )
            )

    return PersistenceReconciliationReport(
        matched_decision_ids=tuple(matched),
        issues=tuple(issues),
    )


def assert_decision_audit_events_reconciled(
    audit_directory: Path,
    database_path: Path,
) -> PersistenceReconciliationReport:
    """Return the reconciliation report only if evidence is fully consistent."""

    report = reconcile_decision_audit_events(audit_directory, database_path)
    report.fail_closed()
    return report


def _zero_issue_counts() -> dict[str, int]:
    return {issue_type.value: 0 for issue_type in ReconciliationIssueType}


def _issue_counts(
    report: PersistenceReconciliationReport,
) -> dict[str, int]:
    counts = _zero_issue_counts()
    for issue in report.issues:
        counts[issue.issue_type.value] += 1
    return counts


def _report_status(
    report: PersistenceReconciliationReport | None,
) -> ReconciliationReportStatus:
    if report is None:
        return ReconciliationReportStatus.UNAVAILABLE
    if report.is_consistent:
        return ReconciliationReportStatus.CONSISTENT
    return ReconciliationReportStatus.INCONSISTENT


def _issue_sort_key(issue: ReconciliationIssue) -> tuple[str, str, str]:
    return (issue.issue_type.value, issue.decision_id, issue.event_id or "")


def reconciliation_report_payload(
    report: PersistenceReconciliationReport | None,
    *,
    unavailable_reason: str | None = None,
) -> dict[str, object]:
    """Return deterministic JSON-compatible reconciliation report payload.

    Passing ``None`` records that reconciliation evidence is unavailable rather
    than silently treating a missing scan as a clean result.
    """

    status = _report_status(report)
    if status is ReconciliationReportStatus.UNAVAILABLE:
        reason = unavailable_reason or "Reconciliation scan was not available."
        return {
            "schema_version": 1,
            "status": status.value,
            "matched_count": 0,
            "matched_decision_ids": [],
            "issue_count": 0,
            "issue_counts": _zero_issue_counts(),
            "issues": [],
            "unavailable_reason": reason,
        }
    if report is None:
        raise AssertionError("Reconciliation report should be present here.")
    issues = [
        {
            "issue_type": issue.issue_type.value,
            "decision_id": issue.decision_id,
            "event_id": issue.event_id,
            "detail": issue.detail,
        }
        for issue in sorted(report.issues, key=_issue_sort_key)
    ]
    return {
        "schema_version": 1,
        "status": status.value,
        "matched_count": len(report.matched_decision_ids),
        "matched_decision_ids": sorted(report.matched_decision_ids),
        "issue_count": len(report.issues),
        "issue_counts": _issue_counts(report),
        "issues": issues,
        "unavailable_reason": None,
    }


def reconciliation_report_json(
    report: PersistenceReconciliationReport | None,
    *,
    unavailable_reason: str | None = None,
) -> str:
    """Serialize reconciliation report payload as deterministic JSON."""

    payload = reconciliation_report_payload(
        report,
        unavailable_reason=unavailable_reason,
    )
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def reconciliation_report_markdown(
    report: PersistenceReconciliationReport | None,
    *,
    unavailable_reason: str | None = None,
) -> str:
    """Render a deterministic Markdown summary for human review."""

    payload = reconciliation_report_payload(
        report,
        unavailable_reason=unavailable_reason,
    )
    lines = [
        "# Persistence Reconciliation Report",
        "",
        f"- Status: `{payload['status']}`",
        f"- Matched decisions: `{payload['matched_count']}`",
        f"- Issues: `{payload['issue_count']}`",
        "",
        "## Issue counts",
        "",
    ]
    issue_counts = payload["issue_counts"]
    if not isinstance(issue_counts, dict):
        raise AssertionError("Issue counts payload must be a mapping.")
    for issue_type in sorted(issue_counts):
        lines.append(f"- `{issue_type}`: `{issue_counts[issue_type]}`")
    reason = payload["unavailable_reason"]
    if reason is not None:
        lines.extend(["", "## Unavailable evidence", "", str(reason)])
    issues = payload["issues"]
    if issues:
        lines.extend(["", "## Issues", ""])
        for raw_issue in issues:
            if not isinstance(raw_issue, dict):
                raise AssertionError("Issue payload must be a mapping.")
            lines.extend(
                [
                    f"### `{raw_issue['issue_type']}`",
                    "",
                    f"- Decision ID: `{raw_issue['decision_id']}`",
                    f"- Event ID: `{raw_issue['event_id']}`",
                    f"- Detail: {raw_issue['detail']}",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"
