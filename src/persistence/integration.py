"""Integration helpers for local research audit persistence boundaries.

This module links an immutable decision audit record to a SQLite audit event.
It remains a research-only persistence helper: it does not generate decisions,
run backtests, approve execution, submit orders, or certify readiness.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from src.persistence.audit import DecisionAuditRecord, PersistedAuditRecord, append_decision_audit
from src.persistence.events import (
    AuditEventIntegrityError,
    AuditEventRecord,
    AuditEventType,
    PersistedAuditEvent,
    append_audit_event,
    list_audit_events,
)


@dataclass(frozen=True)
class PersistedDecisionAuditEvent:
    """Verified file audit record and matching database audit event."""

    audit: PersistedAuditRecord
    event: PersistedAuditEvent


def _record_digest(record: DecisionAuditRecord) -> str:
    payload = record.canonical_payload()
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _event_id_for_decision_audit(
    decision_id: str,
    decision_audit_sha256: str,
) -> str:
    identity = f"{decision_id}:{decision_audit_sha256}"
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


def _preflight_event_identity(
    record: DecisionAuditRecord,
    database_path: Path,
    expected_event_id: str,
) -> None:
    if not database_path.exists():
        return
    for persisted in list_audit_events(database_path):
        event = persisted.event
        if (
            event.decision_id == record.decision_id
            and event.event_type is AuditEventType.DECISION_AUDIT_APPENDED
            and event.event_id != expected_event_id
        ):
            raise AuditEventIntegrityError(
                "A conflicting database audit event already exists for this decision."
            )


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

    record_digest = _record_digest(record)
    event_id = _event_id_for_decision_audit(record.decision_id, record_digest)
    _preflight_event_identity(record, database_path, event_id)
    persisted_audit = append_decision_audit(record, audit_directory)
    event = AuditEventRecord(
        event_id=event_id,
        event_type=AuditEventType.DECISION_AUDIT_APPENDED,
        occurred_at_utc=occurred_at_utc or record.recorded_at_utc,
        decision_id=record.decision_id,
        payload=_event_payload(persisted_audit),
    )
    persisted_event = append_audit_event(database_path, event)
    return PersistedDecisionAuditEvent(audit=persisted_audit, event=persisted_event)
