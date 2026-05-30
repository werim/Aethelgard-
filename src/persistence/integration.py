"""Integration helpers for local research audit persistence boundaries.

This module links an immutable decision audit record to a SQLite audit event.
It remains a research-only persistence helper: it does not generate decisions,
run backtests, approve execution, submit orders, or certify readiness.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from src.persistence.audit import DecisionAuditRecord, PersistedAuditRecord, append_decision_audit
from src.persistence.events import (
    AuditEventRecord,
    AuditEventType,
    PersistedAuditEvent,
    append_audit_event,
)


@dataclass(frozen=True)
class PersistedDecisionAuditEvent:
    """Verified file audit record and matching database audit event."""

    audit: PersistedAuditRecord
    event: PersistedAuditEvent


def _event_id_for_decision_audit(audit: PersistedAuditRecord) -> str:
    identity = f"{audit.record.decision_id}:{audit.record_sha256}"
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:32]
    return f"decision_audit_appended_{digest}"


def _event_payload(audit: PersistedAuditRecord) -> dict[str, object]:
    record = audit.record
    return {
        "decision_audit_sha256": audit.record_sha256,
        "decision_audit_filename": audit.path.name,
        "decision_claim_filename": audit.claim_path.name,
        "dataset_sha256": record.dataset_sha256,
        "artifact_sha256": record.artifact_sha256,
        "outcome": record.outcome.value,
        "reason_codes": list(record.reason_codes),
        "evidence_classifications": [
            item.classification.value for item in record.evidence
        ],
        "unavailable_evidence": [
            item.name for item in record.evidence if item.classification.value == "UNAVAILABLE"
        ],
    }


def append_decision_audit_event(
    record: DecisionAuditRecord,
    audit_directory: Path,
    database_path: Path,
    *,
    occurred_at_utc: str | None = None,
) -> PersistedDecisionAuditEvent:
    """Persist a decision audit record and its matching research audit event.

    The file audit record remains the immutable evidence object. The SQLite row
    records that the local file evidence was appended. This helper preserves the
    existing local boundaries and does not provide cross-store transactions or
    external notarization.
    """

    persisted_audit = append_decision_audit(record, audit_directory)
    event = AuditEventRecord(
        event_id=_event_id_for_decision_audit(persisted_audit),
        event_type=AuditEventType.DECISION_AUDIT_APPENDED,
        occurred_at_utc=occurred_at_utc or record.recorded_at_utc,
        decision_id=record.decision_id,
        payload=_event_payload(persisted_audit),
    )
    persisted_event = append_audit_event(database_path, event)
    return PersistedDecisionAuditEvent(audit=persisted_audit, event=persisted_event)
