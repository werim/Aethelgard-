"""Read-only paper runtime database audit pack.

This module inspects SQLite paper-runtime evidence and reports integrity issues.
It never repairs rows, deletes data, rewrites events, submits orders, or certifies
PAPER/LIVE readiness.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections import Counter, defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import cast


class PaperDbAuditError(ValueError):
    """Raised when the read-only audit cannot safely inspect evidence."""


class PaperDbAuditStatus(StrEnum):
    """Overall read-only paper database audit result."""

    CLEAN = "CLEAN"
    ISSUES_FOUND = "ISSUES_FOUND"
    EMPTY = "EMPTY"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class PaperDbAuditIssue:
    """One paper database integrity diagnostic."""

    code: str
    table: str
    record_id: str
    detail: str
    evidence: str = "MEASURED"

    def payload(self) -> dict[str, str]:
        return {
            "code": self.code,
            "table": self.table,
            "record_id": self.record_id,
            "detail": self.detail,
            "evidence": self.evidence,
        }


@dataclass(frozen=True)
class PaperDbAuditReport:
    """Read-only paper DB audit report."""

    database_path: str
    status: PaperDbAuditStatus
    table_row_counts: Mapping[str, int]
    issues: tuple[PaperDbAuditIssue, ...]
    artifact_directory: str | None = None

    def payload(self) -> dict[str, object]:
        return {
            "database_path": self.database_path,
            "artifact_directory": self.artifact_directory,
            "status": self.status.value,
            "table_row_counts": {
                key: self.table_row_counts[key] for key in sorted(self.table_row_counts)
            },
            "issues": [
                issue.payload()
                for issue in sorted(
                    self.issues,
                    key=lambda item: (
                        item.code,
                        item.table,
                        item.record_id,
                        item.detail,
                    ),
                )
            ],
        }


_REQUIRED_TABLES = ("order_decisions", "trade_lifecycle_events")
_TERMINAL_REJECT_EVENTS = {"SIGNAL_REJECTED", "ORDER_REJECTED", "ENTRY_TIMEOUT"}
_ACTIVE_EVENTS = {"ENTRY_TRIGGERED", "ORDER_PLACED", "POSITION_OPENED"}
_EVENT_ORDER = {
    "SIGNAL_CREATED": 0,
    "WAITING_ENTRY_ZONE": 1,
    "ENTRY_TRIGGERED": 2,
    "ORDER_PLACED": 3,
    "POSITION_OPENED": 4,
    "POSITION_CLOSED": 5,
    "SIGNAL_REJECTED": 5,
    "ORDER_REJECTED": 5,
    "ENTRY_TIMEOUT": 5,
}


def audit_paper_runtime_database(
    database_path: Path,
    *,
    audit_artifact_directory: Path | None = None,
) -> PaperDbAuditReport:
    """Inspect a paper runtime SQLite database without mutating it."""

    if not database_path.exists():
        return PaperDbAuditReport(
            database_path=str(database_path),
            artifact_directory=_artifact_directory_text(audit_artifact_directory),
            status=PaperDbAuditStatus.UNAVAILABLE,
            table_row_counts={},
            issues=(
                PaperDbAuditIssue(
                    code="DATABASE_FILE_MISSING",
                    table="sqlite",
                    record_id="database",
                    detail="database file is unavailable",
                    evidence="UNAVAILABLE",
                ),
            ),
        )

    issues: list[PaperDbAuditIssue] = []
    table_row_counts: dict[str, int] = {}

    with _connect_read_only(database_path) as connection:
        tables = _table_names(connection)
        if not tables:
            return PaperDbAuditReport(
                database_path=str(database_path),
                artifact_directory=_artifact_directory_text(audit_artifact_directory),
                status=PaperDbAuditStatus.EMPTY,
                table_row_counts={},
                issues=(
                    PaperDbAuditIssue(
                        code="EMPTY_DATABASE",
                        table="sqlite",
                        record_id="database",
                        detail="database contains no tables",
                        evidence="UNAVAILABLE",
                    ),
                ),
            )

        for table in sorted(tables):
            table_row_counts[table] = _row_count(connection, table)

        for required_table in _REQUIRED_TABLES:
            if required_table not in tables:
                issues.append(
                    PaperDbAuditIssue(
                        code="MISSING_TABLE",
                        table=required_table,
                        record_id="schema",
                        detail=f"required table {required_table} is unavailable",
                        evidence="UNAVAILABLE",
                    )
                )

        decision_rows = _rows_or_empty(connection, tables, "order_decisions")
        lifecycle_rows = _rows_or_empty(connection, tables, "trade_lifecycle_events")
        audit_event_rows = _rows_or_empty(connection, tables, "audit_events")

        issues.extend(_inspect_decision_rows(decision_rows))
        issues.extend(_inspect_lifecycle_rows(lifecycle_rows))
        issues.extend(_inspect_checksum_rows("order_decisions", decision_rows))
        issues.extend(_inspect_checksum_rows("trade_lifecycle_events", lifecycle_rows))
        issues.extend(_inspect_checksum_rows("audit_events", audit_event_rows))
        issues.extend(_inspect_decision_lifecycle_links(decision_rows, lifecycle_rows))
        issues.extend(_inspect_lifecycle_order(lifecycle_rows))
        issues.extend(_inspect_audit_event_links(decision_rows, audit_event_rows))

    if audit_artifact_directory is not None:
        issues.extend(_inspect_audit_artifacts(audit_artifact_directory, decision_rows))

    status = PaperDbAuditStatus.CLEAN if not issues else PaperDbAuditStatus.ISSUES_FOUND
    return PaperDbAuditReport(
        database_path=str(database_path),
        artifact_directory=_artifact_directory_text(audit_artifact_directory),
        status=status,
        table_row_counts=table_row_counts,
        issues=tuple(issues),
    )


def paper_db_audit_json(report: PaperDbAuditReport) -> str:
    """Serialize a paper DB audit report deterministically."""

    return json.dumps(report.payload(), sort_keys=True, separators=(",", ":"))


def render_paper_db_audit_markdown(report: PaperDbAuditReport) -> str:
    """Render a stable human-readable paper DB audit report."""

    lines = [
        "# Paper Runtime DB Audit",
        "",
        f"- Status: `{report.status.value}`",
        f"- Database: `{report.database_path}`",
    ]
    if report.artifact_directory is not None:
        lines.append(f"- Artifact directory: `{report.artifact_directory}`")
    lines.extend(["", "## Table row counts", ""])
    if report.table_row_counts:
        for table, count in sorted(report.table_row_counts.items()):
            lines.append(f"- `{table}`: {count}")
    else:
        lines.append("- `UNAVAILABLE`: no table counts")
    lines.extend(["", "## Issues", ""])
    if report.issues:
        for issue in sorted(
            report.issues,
            key=lambda item: (item.code, item.table, item.record_id, item.detail),
        ):
            lines.append(
                f"- `{issue.code}` `{issue.table}` `{issue.record_id}`: "
                f"{issue.detail} ({issue.evidence})"
            )
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def assert_paper_db_audit_clean(report: PaperDbAuditReport) -> None:
    """Fail closed when a paper DB audit report contains issues."""

    if report.status is not PaperDbAuditStatus.CLEAN:
        codes = ", ".join(sorted({issue.code for issue in report.issues}))
        raise PaperDbAuditError(f"paper DB audit is not clean: {codes}")


def _connect_read_only(database_path: Path) -> sqlite3.Connection:
    uri = f"file:{database_path.resolve()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def _artifact_directory_text(audit_artifact_directory: Path | None) -> str | None:
    if audit_artifact_directory is None:
        return None
    return str(audit_artifact_directory)


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _table_names(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()
    return {str(row["name"]) for row in rows}


def _row_count(connection: sqlite3.Connection, table: str) -> int:
    row = connection.execute(
        f"SELECT COUNT(*) AS count FROM {_quote_identifier(table)}"
    ).fetchone()
    if row is None:
        return 0
    return int(row["count"])


def _rows_or_empty(
    connection: sqlite3.Connection,
    tables: set[str],
    table: str,
) -> tuple[dict[str, object], ...]:
    if table not in tables:
        return ()
    rows = connection.execute(
        f"SELECT rowid AS _rowid, * FROM {_quote_identifier(table)}"
    ).fetchall()
    return tuple(_row_to_mapping(row) for row in rows)


def _row_to_mapping(row: sqlite3.Row) -> dict[str, object]:
    return {key: cast(object, row[key]) for key in row.keys()}


def _inspect_decision_rows(
    decision_rows: tuple[dict[str, object], ...],
) -> tuple[PaperDbAuditIssue, ...]:
    issues: list[PaperDbAuditIssue] = []
    decision_counter: Counter[str] = Counter()
    decision_fingerprints: dict[str, set[str]] = defaultdict(set)
    for row in decision_rows:
        row_id = _record_id(row, ("decision_id", "signal_id"))
        decision_id = _optional_text(row, ("decision_id",))
        if decision_id is None:
            issues.append(_issue("MISSING_DECISION_ID", "order_decisions", row_id))
        else:
            decision_counter[decision_id] += 1
            decision_fingerprints[decision_id].add(_row_fingerprint(row))
        if _optional_text(row, ("symbol",)) is None:
            issues.append(_issue("MISSING_SYMBOL", "order_decisions", row_id))
        if _optional_text(row, ("side", "direction")) is None:
            issues.append(_issue("MISSING_SIDE", "order_decisions", row_id))
        reason = _optional_text(
            row,
            ("reason", "reason_code", "reason_codes", "reject_reason", "reject_code"),
        )
        if reason is None:
            issues.append(_issue("MISSING_REASON", "order_decisions", row_id))
        elif _contains_unknown_reason(reason):
            issues.append(
                _issue(
                    "UNKNOWN_REJECTION_REASON",
                    "order_decisions",
                    row_id,
                    detail="UNKNOWN rejection reason leaked into decision row",
                )
            )
    for decision_id, count in sorted(decision_counter.items()):
        if count > 1 and len(decision_fingerprints[decision_id]) > 1:
            issues.append(
                _issue(
                    "DUPLICATE_CONFLICTING_DECISION_ID",
                    "order_decisions",
                    decision_id,
                    detail="decision_id appears with conflicting row content",
                )
            )
    return tuple(issues)


def _inspect_lifecycle_rows(
    lifecycle_rows: tuple[dict[str, object], ...],
) -> tuple[PaperDbAuditIssue, ...]:
    issues: list[PaperDbAuditIssue] = []
    event_counter: Counter[str] = Counter()
    for row in lifecycle_rows:
        row_id = _record_id(row, ("event_id", "decision_id", "signal_id"))
        event_id = _optional_text(row, ("event_id",))
        if event_id is None:
            issues.append(_issue("MISSING_EVENT_ID", "trade_lifecycle_events", row_id))
        else:
            event_counter[event_id] += 1
        if _optional_text(row, ("decision_id", "signal_id")) is None:
            issues.append(
                _issue("MISSING_DECISION_REFERENCE", "trade_lifecycle_events", row_id)
            )
    for event_id, count in sorted(event_counter.items()):
        if count > 1:
            issues.append(
                _issue(
                    "DUPLICATE_EVENT_ID",
                    "trade_lifecycle_events",
                    event_id,
                    detail=f"event_id appears {count} times",
                )
            )
    return tuple(issues)


def _inspect_checksum_rows(
    table: str,
    rows: tuple[dict[str, object], ...],
) -> tuple[PaperDbAuditIssue, ...]:
    issues: list[PaperDbAuditIssue] = []
    for row in rows:
        row_id = _record_id(row, ("event_id", "decision_id", "signal_id"))
        payload_json = _optional_text(row, ("payload_json", "payload"))
        checksum = _optional_text(
            row,
            ("payload_sha256", "checksum", "record_sha256", "decision_sha256"),
        )
        if checksum is None:
            issues.append(
                _issue(
                    "MISSING_CHECKSUM",
                    table,
                    row_id,
                    detail="row lacks checksum evidence",
                )
            )
            continue
        if payload_json is None:
            issues.append(
                _issue(
                    "CORRUPTED_JSON_PAYLOAD",
                    table,
                    row_id,
                    detail="row lacks JSON payload for checksum verification",
                )
            )
            continue
        try:
            digest = _canonical_json_digest(payload_json)
        except (TypeError, ValueError) as exc:
            issues.append(
                _issue(
                    "CORRUPTED_JSON_PAYLOAD",
                    table,
                    row_id,
                    detail=f"payload is not deterministic JSON: {exc}",
                )
            )
            continue
        if digest != checksum:
            issues.append(
                _issue(
                    "CHECKSUM_MISMATCH",
                    table,
                    row_id,
                    detail="payload checksum does not match stored checksum",
                )
            )
    return tuple(issues)


def _inspect_decision_lifecycle_links(
    decision_rows: tuple[dict[str, object], ...],
    lifecycle_rows: tuple[dict[str, object], ...],
) -> tuple[PaperDbAuditIssue, ...]:
    issues: list[PaperDbAuditIssue] = []
    decision_ids = {
        decision_id
        for row in decision_rows
        if (decision_id := _optional_text(row, ("decision_id",))) is not None
    }
    lifecycle_decision_ids = {
        decision_id
        for row in lifecycle_rows
        if (decision_id := _optional_text(row, ("decision_id", "signal_id")))
        is not None
    }
    for decision_id in sorted(decision_ids - lifecycle_decision_ids):
        issues.append(
            _issue(
                "DECISION_WITHOUT_LIFECYCLE_ENTRY",
                "order_decisions",
                decision_id,
                detail="decision has no matching lifecycle event",
            )
        )
    for decision_id in sorted(lifecycle_decision_ids - decision_ids):
        issues.append(
            _issue(
                "LIFECYCLE_WITHOUT_DECISION",
                "trade_lifecycle_events",
                decision_id,
                detail="lifecycle event has no matching decision row",
            )
        )
        issues.append(
            _issue(
                "ORPHAN_LIFECYCLE_EVENT",
                "trade_lifecycle_events",
                decision_id,
                detail="lifecycle event is orphaned from decision evidence",
            )
        )
    lifecycle_events_by_decision: dict[str, set[str]] = defaultdict(set)
    for row in lifecycle_rows:
        decision_id = _optional_text(row, ("decision_id", "signal_id"))
        event_type = _event_type(row)
        if decision_id is not None and event_type is not None:
            lifecycle_events_by_decision[decision_id].add(event_type)
    for row in decision_rows:
        decision_id = _optional_text(row, ("decision_id",))
        if decision_id is None:
            continue
        outcome = _decision_outcome(row)
        event_types = lifecycle_events_by_decision.get(decision_id, set())
        if outcome == "REJECTED" and event_types & _ACTIVE_EVENTS:
            issues.append(
                _issue(
                    "INCONSISTENT_REJECTED_STATE_TRANSITION",
                    "trade_lifecycle_events",
                    decision_id,
                    detail="rejected decision has active lifecycle event",
                )
            )
        if outcome == "ACCEPTED" and event_types & _TERMINAL_REJECT_EVENTS:
            issues.append(
                _issue(
                    "INCONSISTENT_ACCEPTED_STATE_TRANSITION",
                    "trade_lifecycle_events",
                    decision_id,
                    detail="accepted decision has reject lifecycle event",
                )
            )
    return tuple(issues)


def _inspect_lifecycle_order(
    lifecycle_rows: tuple[dict[str, object], ...],
) -> tuple[PaperDbAuditIssue, ...]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in lifecycle_rows:
        decision_id = _optional_text(row, ("decision_id", "signal_id"))
        if decision_id is not None:
            grouped[decision_id].append(row)

    issues: list[PaperDbAuditIssue] = []
    for decision_id, rows in grouped.items():
        ordered_rows = sorted(
            rows,
            key=lambda row: (
                _optional_text(row, ("occurred_at_utc", "event_ts", "timestamp_utc"))
                or "",
                _optional_text(row, ("event_id",)) or "",
            ),
        )
        previous = -1
        for row in ordered_rows:
            event_type = _event_type(row)
            if event_type is None:
                continue
            current = _EVENT_ORDER.get(event_type)
            if current is None:
                continue
            if current < previous:
                issues.append(
                    _issue(
                        "LIFECYCLE_EVENT_ORDERING",
                        "trade_lifecycle_events",
                        decision_id,
                        detail="lifecycle event order decreases by timestamp",
                    )
                )
                break
            previous = current
    return tuple(issues)


def _inspect_audit_event_links(
    decision_rows: tuple[dict[str, object], ...],
    audit_event_rows: tuple[dict[str, object], ...],
) -> tuple[PaperDbAuditIssue, ...]:
    if not audit_event_rows:
        return ()
    issues: list[PaperDbAuditIssue] = []
    decision_ids = {
        decision_id
        for row in decision_rows
        if (decision_id := _optional_text(row, ("decision_id",))) is not None
    }
    for row in audit_event_rows:
        decision_id = _optional_text(row, ("decision_id",))
        row_id = _record_id(row, ("event_id", "decision_id"))
        if decision_id is not None and decision_id not in decision_ids:
            issues.append(
                _issue(
                    "AUDIT_EVENT_WITHOUT_DECISION",
                    "audit_events",
                    row_id,
                    detail="audit event references missing decision row",
                )
            )
    return tuple(issues)


def _inspect_audit_artifacts(
    audit_artifact_directory: Path,
    decision_rows: tuple[dict[str, object], ...],
) -> tuple[PaperDbAuditIssue, ...]:
    if not audit_artifact_directory.exists():
        return (
            PaperDbAuditIssue(
                code="AUDIT_ARTIFACT_DIRECTORY_UNAVAILABLE",
                table="audit_artifacts",
                record_id=str(audit_artifact_directory),
                detail="artifact directory is unavailable",
                evidence="UNAVAILABLE",
            ),
        )
    decision_ids = {
        decision_id
        for row in decision_rows
        if (decision_id := _optional_text(row, ("decision_id",))) is not None
    }
    artifact_decisions: set[str] = set()
    issues: list[PaperDbAuditIssue] = []
    for path in sorted(audit_artifact_directory.glob("*.audit.json")):
        try:
            decoded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            issues.append(
                _issue(
                    "CORRUPTED_JSON_PAYLOAD",
                    "audit_artifacts",
                    path.name,
                    detail=f"artifact cannot be decoded: {exc}",
                )
            )
            continue
        if not isinstance(decoded, dict):
            issues.append(
                _issue(
                    "CORRUPTED_JSON_PAYLOAD",
                    "audit_artifacts",
                    path.name,
                    detail="artifact envelope is not a mapping",
                )
            )
            continue
        record = decoded.get("record")
        if not isinstance(record, dict):
            issues.append(
                _issue(
                    "CORRUPTED_JSON_PAYLOAD",
                    "audit_artifacts",
                    path.name,
                    detail="artifact lacks record mapping",
                )
            )
            continue
        declared = decoded.get("record_sha256")
        if not isinstance(declared, str) or not declared.strip():
            issues.append(_issue("MISSING_CHECKSUM", "audit_artifacts", path.name))
            continue
        digest = _canonical_object_digest(record)
        if digest != declared:
            issues.append(_issue("CHECKSUM_MISMATCH", "audit_artifacts", path.name))
        raw_decision_id = record.get("decision_id")
        if isinstance(raw_decision_id, str) and raw_decision_id.strip():
            artifact_decisions.add(raw_decision_id)
    for decision_id in sorted(decision_ids - artifact_decisions):
        issues.append(
            _issue(
                "DECISION_WITHOUT_AUDIT_ARTIFACT",
                "audit_artifacts",
                decision_id,
                detail="decision row has no matching audit artifact",
                evidence="UNAVAILABLE",
            )
        )
    return tuple(issues)


def _canonical_json_digest(payload_json: str) -> str:
    decoded = json.loads(payload_json)
    return _canonical_object_digest(cast(object, decoded))


def _canonical_object_digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


def _optional_text(row: Mapping[str, object], candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if candidate not in row:
            continue
        value = row[candidate]
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _record_id(row: Mapping[str, object], candidates: tuple[str, ...]) -> str:
    return _optional_text(row, candidates) or f"rowid:{row.get('_rowid', 'UNKNOWN')}"


def _row_fingerprint(row: Mapping[str, object]) -> str:
    return _canonical_object_digest(
        {key: value for key, value in row.items() if key != "_rowid"}
    )


def _contains_unknown_reason(reason: str) -> bool:
    return any(part.strip().upper() == "UNKNOWN" for part in reason.split(","))


def _decision_outcome(row: Mapping[str, object]) -> str | None:
    outcome = _optional_text(row, ("outcome", "decision_status", "status"))
    if outcome is None:
        return None
    return outcome.upper()


def _event_type(row: Mapping[str, object]) -> str | None:
    event_type = _optional_text(
        row,
        ("event_type", "lifecycle_state", "state", "status"),
    )
    if event_type is None:
        return None
    return event_type.upper()


def _issue(
    code: str,
    table: str,
    record_id: str,
    *,
    detail: str | None = None,
    evidence: str = "MEASURED",
) -> PaperDbAuditIssue:
    return PaperDbAuditIssue(
        code=code,
        table=table,
        record_id=record_id,
        detail=detail or code.lower().replace("_", " "),
        evidence=evidence,
    )
