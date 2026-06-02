import hashlib
import json
import sqlite3
from pathlib import Path

from src.reporting.paper_db_audit import (
    PaperDbAuditStatus,
    assert_paper_db_audit_clean,
    audit_paper_runtime_database,
    paper_db_audit_json,
    render_paper_db_audit_markdown,
)


def digest(payload_json: str) -> str:
    decoded = json.loads(payload_json)
    encoded = json.dumps(decoded, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


def init_schema(database_path: Path) -> None:
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE order_decisions (
                decision_id TEXT,
                signal_id TEXT,
                symbol TEXT,
                side TEXT,
                outcome TEXT,
                reason TEXT,
                payload_json TEXT,
                payload_sha256 TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE trade_lifecycle_events (
                event_id TEXT,
                decision_id TEXT,
                event_type TEXT,
                occurred_at_utc TEXT,
                payload_json TEXT,
                payload_sha256 TEXT
            )
            """
        )


def insert_decision(
    database_path: Path,
    *,
    decision_id: str = "decision-1",
    symbol: str = "BTCUSDT",
    side: str = "LONG",
    outcome: str = "REJECTED",
    reason: str = "LOW_SCORE",
    payload: dict[str, object] | None = None,
    checksum: str | None = None,
) -> None:
    payload = payload or {"decision_id": decision_id, "outcome": outcome}
    payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO order_decisions (
                decision_id, signal_id, symbol, side, outcome, reason,
                payload_json, payload_sha256
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                decision_id,
                decision_id,
                symbol,
                side,
                outcome,
                reason,
                payload_json,
                checksum if checksum is not None else digest(payload_json),
            ),
        )


def insert_lifecycle(
    database_path: Path,
    *,
    event_id: str = "event-1",
    decision_id: str = "decision-1",
    event_type: str = "SIGNAL_REJECTED",
    occurred_at_utc: str = "2026-06-02T00:00:00Z",
    payload: dict[str, object] | None = None,
    checksum: str | None = None,
) -> None:
    payload = payload or {
        "event_id": event_id,
        "decision_id": decision_id,
        "event_type": event_type,
    }
    payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO trade_lifecycle_events (
                event_id, decision_id, event_type, occurred_at_utc,
                payload_json, payload_sha256
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                decision_id,
                event_type,
                occurred_at_utc,
                payload_json,
                checksum if checksum is not None else digest(payload_json),
            ),
        )


def issue_codes(database_path: Path) -> set[str]:
    return {issue.code for issue in audit_paper_runtime_database(database_path).issues}


def test_clean_db_passes_audit(tmp_path: Path) -> None:
    database_path = tmp_path / "paper.db"
    init_schema(database_path)
    insert_decision(database_path)
    insert_lifecycle(database_path)
    report = audit_paper_runtime_database(database_path)
    assert report.status is PaperDbAuditStatus.CLEAN
    assert report.table_row_counts["order_decisions"] == 1
    assert report.table_row_counts["trade_lifecycle_events"] == 1
    assert_paper_db_audit_clean(report)


def test_empty_db_is_reported_as_empty(tmp_path: Path) -> None:
    database_path = tmp_path / "empty.db"
    sqlite3.connect(database_path).close()
    report = audit_paper_runtime_database(database_path)
    assert report.status is PaperDbAuditStatus.EMPTY
    assert report.issues[0].code == "EMPTY_DATABASE"


def test_missing_table_schema_is_reported(tmp_path: Path) -> None:
    database_path = tmp_path / "missing-schema.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE order_decisions (decision_id TEXT)")
    assert "MISSING_TABLE" in issue_codes(database_path)


def test_orphan_lifecycle_event_is_reported(tmp_path: Path) -> None:
    database_path = tmp_path / "orphan.db"
    init_schema(database_path)
    insert_lifecycle(database_path, decision_id="missing-decision")
    codes = issue_codes(database_path)
    assert "ORPHAN_LIFECYCLE_EVENT" in codes
    assert "LIFECYCLE_WITHOUT_DECISION" in codes


def test_missing_decision_event_is_reported(tmp_path: Path) -> None:
    database_path = tmp_path / "missing-event.db"
    init_schema(database_path)
    insert_decision(database_path)
    assert "DECISION_WITHOUT_LIFECYCLE_ENTRY" in issue_codes(database_path)


def test_duplicate_event_ids_are_reported(tmp_path: Path) -> None:
    database_path = tmp_path / "duplicate-event.db"
    init_schema(database_path)
    insert_decision(database_path)
    insert_lifecycle(database_path, event_id="duplicate")
    insert_lifecycle(database_path, event_id="duplicate")
    assert "DUPLICATE_EVENT_ID" in issue_codes(database_path)


def test_duplicate_conflicting_decision_ids_are_reported(tmp_path: Path) -> None:
    database_path = tmp_path / "duplicate-decision.db"
    init_schema(database_path)
    insert_decision(database_path, payload={"decision_id": "decision-1", "v": 1})
    insert_decision(database_path, payload={"decision_id": "decision-1", "v": 2})
    insert_lifecycle(database_path)
    assert "DUPLICATE_CONFLICTING_DECISION_ID" in issue_codes(database_path)


def test_checksum_mismatch_is_reported(tmp_path: Path) -> None:
    database_path = tmp_path / "checksum.db"
    init_schema(database_path)
    insert_decision(database_path, checksum="0" * 64)
    insert_lifecycle(database_path)
    assert "CHECKSUM_MISMATCH" in issue_codes(database_path)


def test_unknown_reject_reason_is_reported(tmp_path: Path) -> None:
    database_path = tmp_path / "unknown.db"
    init_schema(database_path)
    insert_decision(database_path, reason="UNKNOWN")
    insert_lifecycle(database_path)
    assert "UNKNOWN_REJECTION_REASON" in issue_codes(database_path)


def test_corrupted_json_payload_is_reported(tmp_path: Path) -> None:
    database_path = tmp_path / "corrupt.db"
    init_schema(database_path)
    insert_lifecycle(database_path)
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO order_decisions (
                decision_id, signal_id, symbol, side, outcome, reason,
                payload_json, payload_sha256
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "decision-1",
                "decision-1",
                "BTCUSDT",
                "LONG",
                "REJECTED",
                "LOW_SCORE",
                "{broken-json",
                "0" * 64,
            ),
        )
    assert "CORRUPTED_JSON_PAYLOAD" in issue_codes(database_path)


def test_report_output_is_stable(tmp_path: Path) -> None:
    database_path = tmp_path / "stable.db"
    init_schema(database_path)
    insert_decision(database_path)
    insert_lifecycle(database_path)
    report = audit_paper_runtime_database(database_path)
    assert paper_db_audit_json(report) == paper_db_audit_json(report)
    assert render_paper_db_audit_markdown(report) == render_paper_db_audit_markdown(
        report
    )
