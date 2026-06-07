import sqlite3
from dataclasses import replace
from pathlib import Path
from typing import cast

import pytest

from src.persistence.events import (
    AuditEventIntegrityError,
    AuditEventRecord,
    AuditEventType,
    append_audit_event,
    initialize_audit_event_store,
    list_audit_events,
    read_audit_event,
)

DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


def database_path(tmp_path: Path) -> Path:
    return tmp_path / "audit-events.sqlite3"


def event(
    *,
    event_id: str = "event_001",
    decision_id: str = "decision_001",
    operating_mode: str = "PAPER_ONLY",
    payload: dict[str, object] | None = None,
) -> AuditEventRecord:
    return AuditEventRecord(
        event_id=event_id,
        event_type=AuditEventType.DECISION_AUDIT_APPENDED,
        occurred_at_utc="2026-05-30T14:00:00Z",
        decision_id=decision_id,
        payload=payload
        or {
            "decision_audit_sha256": DIGEST_A,
            "artifact_sha256": DIGEST_B,
            "evidence_classification": "MEASURED",
        },
        operating_mode=operating_mode,
    )


def test_audit_event_store_initializes_empty_schema(tmp_path: Path) -> None:
    db = database_path(tmp_path)

    initialize_audit_event_store(db)

    with sqlite3.connect(db) as connection:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    assert ("audit_events",) in tables
    assert list_audit_events(db) == ()


def test_audit_event_is_persisted_and_verified_after_readback(tmp_path: Path) -> None:
    db = database_path(tmp_path)

    persisted = append_audit_event(db, event())
    restored = read_audit_event(db, "event_001")
    listed = list_audit_events(db)

    assert persisted == restored
    assert listed == (restored,)
    assert restored.event.decision_id == "decision_001"
    assert restored.payload_sha256 == restored.event.payload_sha256


def test_identical_append_is_idempotent(tmp_path: Path) -> None:
    db = database_path(tmp_path)

    first = append_audit_event(db, event())
    second = append_audit_event(db, event())

    assert first == second
    assert len(list_audit_events(db)) == 1


def test_conflicting_event_id_fails_closed(tmp_path: Path) -> None:
    db = database_path(tmp_path)
    append_audit_event(db, event())

    changed = replace(event(), payload={"decision_audit_sha256": DIGEST_B})
    with pytest.raises(AuditEventIntegrityError, match="different immutable"):
        append_audit_event(db, changed)


def test_second_event_for_same_decision_and_type_fails_closed(tmp_path: Path) -> None:
    db = database_path(tmp_path)
    append_audit_event(db, event())

    with pytest.raises(AuditEventIntegrityError, match="decision and type"):
        append_audit_event(db, event(event_id="event_002"))


def test_tampered_payload_digest_fails_readback(tmp_path: Path) -> None:
    db = database_path(tmp_path)
    append_audit_event(db, event())

    with sqlite3.connect(db) as connection:
        connection.execute(
            "UPDATE audit_events SET payload_json = ? WHERE event_id = ?",
            ('{"decision_audit_sha256":"tampered"}', "event_001"),
        )

    with pytest.raises(AuditEventIntegrityError, match="checksum"):
        read_audit_event(db, "event_001")


def test_non_utc_timestamp_and_non_paper_mode_fail_closed(tmp_path: Path) -> None:
    db = database_path(tmp_path)

    not_utc = replace(event(), occurred_at_utc="2026-05-30T17:00:00+03:00")
    with pytest.raises(AuditEventIntegrityError, match="must use UTC"):
        append_audit_event(db, not_utc)

    with pytest.raises(AuditEventIntegrityError, match="PAPER_ONLY"):
        append_audit_event(db, event(operating_mode="LIVE"))


def test_payload_must_be_deterministic_json_mapping(tmp_path: Path) -> None:
    db = database_path(tmp_path)
    bad_payload = cast(dict[str, object], {"unserializable": {"nested"}})

    with pytest.raises(AuditEventIntegrityError, match="deterministic JSON"):
        append_audit_event(db, event(payload=bad_payload))
