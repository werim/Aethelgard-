"""SQLite-backed append-only audit-event ledger for research evidence.

This module records persistence events only. It does not generate signals, run
backtests, approve execution, submit orders, or certify PAPER/LIVE readiness.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import cast

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_EVENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,96}$")
_DECISION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
_SCHEMA_VERSION = 1


class AuditEventIntegrityError(ValueError):
    """Raised when a database-backed audit event cannot be trusted."""


class AuditEventType(StrEnum):
    """Research-only audit event types admitted by the Gate 2B boundary."""

    DECISION_AUDIT_APPENDED = "DECISION_AUDIT_APPENDED"


@dataclass(frozen=True)
class AuditEventRecord:
    """One append-only research audit event with explicit checksum identity."""

    event_id: str
    event_type: AuditEventType
    occurred_at_utc: str
    decision_id: str
    payload: dict[str, object]
    operating_mode: str = "PAPER_ONLY"
    readiness: str = "RESEARCH_ONLY"
    schema_version: int = _SCHEMA_VERSION

    def validate(self) -> None:
        if not _EVENT_ID_PATTERN.fullmatch(self.event_id):
            raise AuditEventIntegrityError(
                "event_id must be a safe non-empty identifier."
            )
        if not _DECISION_ID_PATTERN.fullmatch(self.decision_id):
            raise AuditEventIntegrityError(
                "decision_id must be a safe non-empty identifier."
            )
        try:
            moment = datetime.fromisoformat(self.occurred_at_utc.replace("Z", "+00:00"))
        except ValueError as exc:
            raise AuditEventIntegrityError(
                "occurred_at_utc must be an ISO-8601 timestamp."
            ) from exc
        if moment.tzinfo is None or moment.utcoffset() != UTC.utcoffset(None):
            raise AuditEventIntegrityError("occurred_at_utc must use UTC.")
        if self.operating_mode != "PAPER_ONLY" or self.readiness != "RESEARCH_ONLY":
            raise AuditEventIntegrityError(
                "Audit events must remain PAPER_ONLY/RESEARCH_ONLY."
            )
        if self.schema_version != _SCHEMA_VERSION:
            raise AuditEventIntegrityError("Unsupported audit-event schema version.")
        if not self.payload:
            raise AuditEventIntegrityError("Audit event payload is required.")
        _canonical_payload_bytes(self.payload)

    @property
    def payload_sha256(self) -> str:
        self.validate()
        return hashlib.sha256(_canonical_payload_bytes(self.payload)).hexdigest()


@dataclass(frozen=True)
class PersistedAuditEvent:
    """Verified database row for one immutable audit event."""

    event: AuditEventRecord
    payload_sha256: str


_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    occurred_at_utc TEXT NOT NULL,
    decision_id TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    operating_mode TEXT NOT NULL,
    readiness TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    created_at_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE(decision_id, event_type)
);
"""


def _canonical_payload_bytes(payload: dict[str, object]) -> bytes:
    try:
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    except (TypeError, ValueError) as exc:
        raise AuditEventIntegrityError(
            "Audit event payload must be deterministic JSON evidence."
        ) from exc


def _connect(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_audit_event_store(database_path: Path) -> None:
    """Create the minimal audit-event schema if absent."""

    with _connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(_SCHEMA)


def _row_to_persisted(row: sqlite3.Row) -> PersistedAuditEvent:
    payload_json = row["payload_json"]
    if not isinstance(payload_json, str):
        raise AuditEventIntegrityError("Audit event payload_json must be text.")
    try:
        decoded = cast(object, json.loads(payload_json))
    except json.JSONDecodeError as exc:
        message = "Audit event payload cannot be decoded."
        raise AuditEventIntegrityError(message) from exc
    if not isinstance(decoded, dict):
        raise AuditEventIntegrityError("Audit event payload must be a mapping.")
    payload = cast(dict[str, object], decoded)
    payload_sha256 = row["payload_sha256"]
    if not isinstance(payload_sha256, str) or not _SHA256_PATTERN.fullmatch(
        payload_sha256
    ):
        raise AuditEventIntegrityError("Audit event payload digest is invalid.")
    actual_digest = hashlib.sha256(_canonical_payload_bytes(payload)).hexdigest()
    if actual_digest != payload_sha256:
        raise AuditEventIntegrityError("Audit event payload checksum failed.")
    try:
        event_type = AuditEventType(str(row["event_type"]))
    except ValueError as exc:
        raise AuditEventIntegrityError("Unsupported audit event type.") from exc
    schema_version = row["schema_version"]
    if not isinstance(schema_version, int):
        raise AuditEventIntegrityError("Audit event schema_version must be an integer.")
    event = AuditEventRecord(
        event_id=str(row["event_id"]),
        event_type=event_type,
        occurred_at_utc=str(row["occurred_at_utc"]),
        decision_id=str(row["decision_id"]),
        payload=payload,
        operating_mode=str(row["operating_mode"]),
        readiness=str(row["readiness"]),
        schema_version=schema_version,
    )
    event.validate()
    if event.payload_sha256 != payload_sha256:
        raise AuditEventIntegrityError("Audit event payload checksum failed.")
    return PersistedAuditEvent(event=event, payload_sha256=payload_sha256)


def read_audit_event(database_path: Path, event_id: str) -> PersistedAuditEvent:
    """Read and verify one audit event by immutable event identity."""

    initialize_audit_event_store(database_path)
    with _connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT event_id, event_type, occurred_at_utc, decision_id, payload_json,
                   payload_sha256, operating_mode, readiness, schema_version
            FROM audit_events
            WHERE event_id = ?
            """,
            (event_id,),
        ).fetchone()
    if row is None:
        raise AuditEventIntegrityError("Audit event does not exist.")
    return _row_to_persisted(row)


def append_audit_event(
    database_path: Path, event: AuditEventRecord
) -> PersistedAuditEvent:
    """Append one immutable audit event, rejecting identity conflicts."""

    event.validate()
    initialize_audit_event_store(database_path)
    payload_json = _canonical_payload_bytes(event.payload).decode("utf-8")
    payload_sha256 = event.payload_sha256
    with _connect(database_path) as connection:
        existing_by_event_id = connection.execute(
            """
            SELECT event_id, event_type, occurred_at_utc, decision_id, payload_json,
                   payload_sha256, operating_mode, readiness, schema_version
            FROM audit_events
            WHERE event_id = ?
            """,
            (event.event_id,),
        ).fetchone()
        if existing_by_event_id is not None:
            persisted = _row_to_persisted(existing_by_event_id)
            if persisted.event != event or persisted.payload_sha256 != payload_sha256:
                raise AuditEventIntegrityError(
                    "A different immutable audit event already exists for event_id."
                )
            return persisted
        existing_by_decision = connection.execute(
            """
            SELECT event_id, event_type, occurred_at_utc, decision_id, payload_json,
                   payload_sha256, operating_mode, readiness, schema_version
            FROM audit_events
            WHERE decision_id = ? AND event_type = ?
            """,
            (event.decision_id, event.event_type.value),
        ).fetchone()
        if existing_by_decision is not None:
            raise AuditEventIntegrityError(
                "A database audit event already exists for this decision and type."
            )
        connection.execute(
            """
            INSERT INTO audit_events (
                event_id, event_type, occurred_at_utc, decision_id, payload_json,
                payload_sha256, operating_mode, readiness, schema_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.event_type.value,
                event.occurred_at_utc,
                event.decision_id,
                payload_json,
                payload_sha256,
                event.operating_mode,
                event.readiness,
                event.schema_version,
            ),
        )
    return read_audit_event(database_path, event.event_id)


def list_audit_events(database_path: Path) -> tuple[PersistedAuditEvent, ...]:
    """Return all verified audit events, failing closed on any corrupt row."""

    initialize_audit_event_store(database_path)
    with _connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT event_id, event_type, occurred_at_utc, decision_id, payload_json,
                   payload_sha256, operating_mode, readiness, schema_version
            FROM audit_events
            ORDER BY occurred_at_utc, event_id
            """
        ).fetchall()
    return tuple(_row_to_persisted(row) for row in rows)
