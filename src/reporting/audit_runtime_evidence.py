"""Gate 5A-3 audit/runtime reconciliation evidence adapter.

This module converts caller-supplied persistence reconciliation reports into
Gate 5A evidence items for audit trail integrity and PAPER runtime
reconciliation. It is deliberately offline and deterministic: it does not read
local databases, mutate audit artifacts, run a PAPER runtime, submit orders,
compute performance, or approve readiness.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from src.persistence.reconciliation import PersistenceReconciliationReport
from src.reporting.operational_evidence import (
    OperationalEvidenceClassification,
    OperationalEvidenceItem,
)


class AuditRuntimeEvidenceStatus(StrEnum):
    """Audit/runtime evidence adapter status values."""

    RECONCILED = "RECONCILED"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class AuditRuntimeEvidenceAssessment:
    """Fail-closed Gate 5A evidence assessment for audit/runtime evidence."""

    status: AuditRuntimeEvidenceStatus
    classification: OperationalEvidenceClassification
    diagnostics: tuple[str, ...]
    evidence_items: tuple[OperationalEvidenceItem, ...]

    def payload(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible assessment payload."""

        return {
            "classification": self.classification.value,
            "diagnostics": list(self.diagnostics),
            "evidence_items": [item.payload() for item in self.evidence_items],
            "status": self.status.value,
        }


def assess_audit_runtime_reconciliation_for_gate5a(
    report: PersistenceReconciliationReport | None,
    *,
    source: str,
) -> AuditRuntimeEvidenceAssessment:
    """Classify audit/runtime reconciliation evidence for Gate 5A."""

    diagnostics = _audit_runtime_diagnostics(report, source=source)
    if diagnostics:
        return _build_assessment(
            status=AuditRuntimeEvidenceStatus.UNAVAILABLE,
            classification=OperationalEvidenceClassification.UNAVAILABLE,
            diagnostics=diagnostics,
            source=source,
        )

    if report is None:
        raise AssertionError("Report must be present after diagnostics pass.")
    matched_count = len(report.matched_decision_ids)
    summary = (
        "Audit trail and PAPER runtime reconciliation measured for "
        f"{matched_count} matched decision audit event(s)"
    )
    return AuditRuntimeEvidenceAssessment(
        status=AuditRuntimeEvidenceStatus.RECONCILED,
        classification=OperationalEvidenceClassification.MEASURED,
        diagnostics=(summary,),
        evidence_items=_measured_evidence_items(summary=summary, source=source),
    )


def audit_runtime_evidence_assessment_json(
    assessment: AuditRuntimeEvidenceAssessment,
) -> str:
    """Serialize an audit/runtime evidence assessment deterministically."""

    return json.dumps(assessment.payload(), sort_keys=True, separators=(",", ":"))


def _audit_runtime_diagnostics(
    report: PersistenceReconciliationReport | None,
    *,
    source: str,
) -> tuple[str, ...]:
    diagnostics: list[str] = []

    if not source.strip():
        diagnostics.append("audit/runtime reconciliation evidence source is missing")
    if report is None:
        diagnostics.append("audit/runtime reconciliation report is unavailable")
        return tuple(diagnostics)
    if not report.matched_decision_ids:
        diagnostics.append(
            "audit/runtime reconciliation has no matched decision audits"
        )
    for issue in report.issues:
        diagnostics.append(
            f"audit/runtime reconciliation issue {issue.issue_type.value} "
            f"for decision {issue.decision_id}"
        )
    return tuple(diagnostics)


def _build_assessment(
    *,
    status: AuditRuntimeEvidenceStatus,
    classification: OperationalEvidenceClassification,
    diagnostics: tuple[str, ...],
    source: str,
) -> AuditRuntimeEvidenceAssessment:
    safe_source = source.strip() or "UNAVAILABLE: missing audit/runtime source"
    summary = "; ".join(diagnostics) if diagnostics else "audit/runtime unavailable"
    return AuditRuntimeEvidenceAssessment(
        status=status,
        classification=classification,
        diagnostics=diagnostics,
        evidence_items=tuple(
            OperationalEvidenceItem(
                blocker_id=blocker_id,
                classification=classification,
                summary=summary,
                source=safe_source,
            )
            for blocker_id in _AUDIT_RUNTIME_BLOCKERS
        ),
    )


def _measured_evidence_items(
    *,
    summary: str,
    source: str,
) -> tuple[OperationalEvidenceItem, ...]:
    return tuple(
        OperationalEvidenceItem(
            blocker_id=blocker_id,
            classification=OperationalEvidenceClassification.MEASURED,
            summary=summary,
            source=source,
        )
        for blocker_id in _AUDIT_RUNTIME_BLOCKERS
    )


_AUDIT_RUNTIME_BLOCKERS: Sequence[str] = (
    "audit_trail_integrity",
    "paper_runtime_reconciliation",
)
