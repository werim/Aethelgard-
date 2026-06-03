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
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


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
            "issues": [issue.payload() for issue in _sorted_issues(self.issues)],
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

    artifact_directory = _artifact_directory_text(audit_artifact_directory)
    if not database_path.exists():
        return _report(
            database_path,
            PaperDbAuditStatus.UNAVAILABLE,
            {},
            (
                _issue(
                    "DATABASE_FILE_MISSING",
                    "sqlite",
                    "database",
                    evidence="UNAVAILABLE",
                ),
            ),
            artifact_directory,
        )

    issues: list[PaperDbAuditIssue] = []
    table_row_counts: dict[str, int] = {}
    with _connect_read_only(database_path) as connection:
        tables = _table_names(connection)
        if not tables:
            return _report(
                database_path,
                PaperDbAuditStatus.EMPTY,
                {},
                (
                    _issue(
                        "EMPTY_DATABASE", "sqlite", "database", evidence="UNAVAILABLE"
                    ),
                ),
                artifact_directory,
            )
        for table in sorted(tables):
            table_row_counts[table] = _row_count(connection, table)
        issues.extend(_missing_table_issues(tables))
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
    return _report(
        database_path, status, table_row_counts, tuple(issues), artifact_directory
    )


def paper_db_audit_json(report: PaperDbAuditReport) -> str:
    """Serialize a paper DB audit report deterministically."""

    return json.dumps(report.payload(), sort_keys=True, separators=(",", ":"))


def render_paper_db_audit_markdown(report: PaperDbAuditReport) -> str:
    """Render a stable human-readable paper DB audit report."""

    lines = ["# Paper Runtime DB Audit", "", f"- Status: `{report.status.value}`"]
    lines.append(f"- Database: `{report.database_path}`")
    if report.artifact_directory is not None:
        lines.append(f"- Artifact directory: `{report.artifact_directory}`")
    lines.extend(["", "## Table row counts", ""])
    if report.table_row_counts:
        lines.extend(
            f"- `{table}`: {count}"
            for table, count in sorted(report.table_row_counts.items())
        )
    else:
        lines.append("- `UNAVAILABLE`: no table counts")
    lines.extend(["", "## Issues", ""])
    if report.issues:
        lines.extend(
            f"- `{issue.code}` `{issue.table}` `{issue.record_id}`: "
            f"{issue.detail} ({issue.evidence})"
            for issue in _sorted_issues(report.issues)
        )
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def assert_paper_db_audit_clean(report: PaperDbAuditReport) -> None:
    """Fail closed when a paper DB audit report contains issues."""

    if report.status is not PaperDbAuditStatus.CLEAN:
        codes = ", ".join(sorted({issue.code for issue in report.issues}))
        raise PaperDbAuditError(f"paper DB audit is not clean: {codes}")


def _report(
    database_path: Path,
    status: PaperDbAuditStatus,
    table_row_counts: Mapping[str, int],
    issues: tuple[PaperDbAuditIssue, ...],
    artifact_directory: str | None,
) -> PaperDbAuditReport:
    return PaperDbAuditReport(
        database_path=str(database_path),
        artifact_directory=artifact_directory,
        status=status,
        table_row_counts=table_row_counts,
        issues=issues,
    )


def _connect_read_only(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(f"file:{database_path.resolve()}?mode=ro", uri=True)
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
    return {key: row[key] for key in tuple(row.keys())}


def _missing_table_issues(tables: set[str]) -> tuple[PaperDbAuditIssue, ...]:
    return tuple(
        _issue("MISSING_TABLE", table, "schema", evidence="UNAVAILABLE")
        for table in _REQUIRED_TABLES
        if table not in tables
    )


def _inspect_decision_rows(
    rows: Sequence[Mapping[str, object]]
) -> tuple[PaperDbAuditIssue, ...]:
    issues: list[PaperDbAuditIssue] = []
    counter: Counter[str] = Counter()
    fingerprints: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        row_id = _record_id(row, ("decision_id", "signal_id"))
        decision_id = _optional_text(row, ("decision_id",))
        if decision_id is None:
            issues.append(_issue("MISSING_DECISION_ID", "order_decisions", row_id))
        else:
            counter[decision_id] += 1
            fingerprints[decision_id].add(_row_fingerprint(row))
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
            issues.append(_issue("UNKNOWN_REJECTION_REASON", "order_decisions", row_id))
    for decision_id, count in sorted(counter.items()):
        if count > 1 and len(fingerprints[decision_id]) > 1:
            issues.append(
                _issue(
                    "DUPLICATE_CONFLICTING_DECISION_ID", "order_decisions", decision_id
                )
            )
    return tuple(issues)


def _inspect_lifecycle_rows(
    rows: Sequence[Mapping[str, object]]
) -> tuple[PaperDbAuditIssue, ...]:
    issues: list[PaperDbAuditIssue] = []
    counter: Counter[str] = Counter()
    for row in rows:
        row_id = _record_id(row, ("event_id", "decision_id", "signal_id"))
        event_id = _optional_text(row, ("event_id",))
        if event_id is None:
            issues.append(_issue("MISSING_EVENT_ID", "trade_lifecycle_events", row_id))
        else:
            counter[event_id] += 1
        if _optional_text(row, ("decision_id", "signal_id")) is None:
            issues.append(
                _issue("MISSING_DECISION_REFERENCE", "trade_lifecycle_events", row_id)
            )
    for event_id, count in sorted(counter.items()):
        if count > 1:
            issues.append(
                _issue("DUPLICATE_EVENT_ID", "trade_lifecycle_events", event_id)
            )
    return tuple(issues)


def _inspect_checksum_rows(
    table: str,
    rows: Sequence[Mapping[str, object]],
) -> tuple[PaperDbAuditIssue, ...]:
    issues: list[PaperDbAuditIssue] = []
    for row in rows:
        row_id = _record_id(row, ("event_id", "decision_id", "signal_id"))
        payload_json = _optional_text(row, ("payload_json", "payload"))
        checksum = _optional_text(
            row, ("payload_sha256", "checksum", "record_sha256", "decision_sha256")
        )
        if checksum is None:
            issues.append(_issue("MISSING_CHECKSUM", table, row_id))
            continue
        if payload_json is None:
            issues.append(_issue("CORRUPTED_JSON_PAYLOAD", table, row_id))
            continue
        try:
            digest = _canonical_json_digest(payload_json)
        except (TypeError, ValueError):
            issues.append(_issue("CORRUPTED_JSON_PAYLOAD", table, row_id))
            continue
        if digest != checksum:
            issues.append(_issue("CHECKSUM_MISMATCH", table, row_id))
    return tuple(issues)


def _inspect_decision_lifecycle_links(
    decision_rows: Sequence[Mapping[str, object]],
    lifecycle_rows: Sequence[Mapping[str, object]],
) -> tuple[PaperDbAuditIssue, ...]:
    issues: list[PaperDbAuditIssue] = []
    decision_ids = _ids(decision_rows, ("decision_id",))
    lifecycle_decision_ids = _ids(lifecycle_rows, ("decision_id", "signal_id"))
    for decision_id in sorted(decision_ids - lifecycle_decision_ids):
        issues.append(
            _issue("DECISION_WITHOUT_LIFECYCLE_ENTRY", "order_decisions", decision_id)
        )
    for decision_id in sorted(lifecycle_decision_ids - decision_ids):
        issues.append(
            _issue("LIFECYCLE_WITHOUT_DECISION", "trade_lifecycle_events", decision_id)
        )
        issues.append(
            _issue("ORPHAN_LIFECYCLE_EVENT", "trade_lifecycle_events", decision_id)
        )
    issues.extend(_transition_issues(decision_rows, lifecycle_rows))
    return tuple(issues)


def _transition_issues(
    decision_rows: Sequence[Mapping[str, object]],
    lifecycle_rows: Sequence[Mapping[str, object]],
) -> tuple[PaperDbAuditIssue, ...]:
    events_by_decision: dict[str, set[str]] = defaultdict(set)
    issues: list[PaperDbAuditIssue] = []
    for row in lifecycle_rows:
        decision_id = _optional_text(row, ("decision_id", "signal_id"))
        event_type = _event_type(row)
        if decision_id is not None and event_type is not None:
            events_by_decision[decision_id].add(event_type)
    for row in decision_rows:
        decision_id = _optional_text(row, ("decision_id",))
        if decision_id is None:
            continue
        event_types = events_by_decision.get(decision_id, set())
        if _decision_outcome(row) == "REJECTED" and event_types & _ACTIVE_EVENTS:
            issues.append(
                _issue(
                    "INCONSISTENT_REJECTED_STATE_TRANSITION",
                    "trade_lifecycle_events",
                    decision_id,
                )
            )
        if (
            _decision_outcome(row) == "ACCEPTED"
            and event_types & _TERMINAL_REJECT_EVENTS
        ):
            issues.append(
                _issue(
                    "INCONSISTENT_ACCEPTED_STATE_TRANSITION",
                    "trade_lifecycle_events",
                    decision_id,
                )
            )
    return tuple(issues)


def _inspect_lifecycle_order(
    lifecycle_rows: Sequence[Mapping[str, object]],
) -> tuple[PaperDbAuditIssue, ...]:
    grouped: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in lifecycle_rows:
        if (
            decision_id := _optional_text(row, ("decision_id", "signal_id"))
        ) is not None:
            grouped[decision_id].append(row)
    issues: list[PaperDbAuditIssue] = []
    for decision_id, rows in grouped.items():
        previous = -1
        for row in sorted(rows, key=_lifecycle_sort_key):
            event_type = _event_type(row)
            current = None if event_type is None else _EVENT_ORDER.get(event_type)
            if current is None:
                continue
            if current < previous:
                issues.append(
                    _issue(
                        "LIFECYCLE_EVENT_ORDERING",
                        "trade_lifecycle_events",
                        decision_id,
                    )
                )
                break
            previous = current
    return tuple(issues)


def _inspect_audit_event_links(
    decision_rows: Sequence[Mapping[str, object]],
    audit_event_rows: Sequence[Mapping[str, object]],
) -> tuple[PaperDbAuditIssue, ...]:
    decision_ids = _ids(decision_rows, ("decision_id",))
    return tuple(
        _issue(
            "AUDIT_EVENT_WITHOUT_DECISION",
            "audit_events",
            _record_id(row, ("event_id", "decision_id")),
        )
        for row in audit_event_rows
        if (decision_id := _optional_text(row, ("decision_id",))) is not None
        and decision_id not in decision_ids
    )


def _inspect_audit_artifacts(
    audit_artifact_directory: Path,
    decision_rows: Sequence[Mapping[str, object]],
) -> tuple[PaperDbAuditIssue, ...]:
    if not audit_artifact_directory.exists():
        return (
            _issue(
                "AUDIT_ARTIFACT_DIRECTORY_UNAVAILABLE",
                "audit_artifacts",
                str(audit_artifact_directory),
                evidence="UNAVAILABLE",
            ),
        )
    decision_ids = _ids(decision_rows, ("decision_id",))
    artifact_decision_ids: set[str] = set()
    issues: list[PaperDbAuditIssue] = []
    for path in sorted(audit_artifact_directory.glob("*.audit.json")):
        issues.extend(_inspect_audit_artifact(path, artifact_decision_ids))
    for decision_id in sorted(decision_ids - artifact_decision_ids):
        issues.append(
            _issue(
                "DECISION_WITHOUT_AUDIT_ARTIFACT",
                "audit_artifacts",
                decision_id,
                evidence="UNAVAILABLE",
            )
        )
    return tuple(issues)


def _inspect_audit_artifact(
    path: Path,
    artifact_decision_ids: set[str],
) -> tuple[PaperDbAuditIssue, ...]:
    try:
        decoded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return (_issue("CORRUPTED_JSON_PAYLOAD", "audit_artifacts", path.name),)
    if not isinstance(decoded, dict) or not isinstance(decoded.get("record"), dict):
        return (_issue("CORRUPTED_JSON_PAYLOAD", "audit_artifacts", path.name),)
    record = decoded["record"]
    declared = decoded.get("record_sha256")
    if not isinstance(declared, str) or not declared.strip():
        return (_issue("MISSING_CHECKSUM", "audit_artifacts", path.name),)
    issues = []
    if _canonical_object_digest(record) != declared:
        issues.append(_issue("CHECKSUM_MISMATCH", "audit_artifacts", path.name))
    if isinstance(record.get("decision_id"), str) and record["decision_id"].strip():
        artifact_decision_ids.add(record["decision_id"])
    return tuple(issues)


def _ids(rows: Sequence[Mapping[str, object]], candidates: tuple[str, ...]) -> set[str]:
    return {
        value for row in rows if (value := _optional_text(row, candidates)) is not None
    }


def _lifecycle_sort_key(row: Mapping[str, object]) -> tuple[str, str]:
    timestamp = _optional_text(row, ("occurred_at_utc", "event_ts", "timestamp_utc"))
    return (timestamp or "", _optional_text(row, ("event_id",)) or "")


def _canonical_json_digest(payload_json: str) -> str:
    return _canonical_object_digest(json.loads(payload_json))


def _canonical_object_digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _optional_text(
    row: Mapping[str, object],
    candidates: tuple[str, ...],
) -> str | None:
    for candidate in candidates:
        value = row.get(candidate)
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
        row, ("event_type", "lifecycle_state", "state", "status")
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


def _sorted_issues(
    issues: Sequence[PaperDbAuditIssue],
) -> tuple[PaperDbAuditIssue, ...]:
    return tuple(
        sorted(
            issues,
            key=lambda issue: (issue.code, issue.table, issue.record_id, issue.detail),
        )
    )
