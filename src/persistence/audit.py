"""Append-only audit evidence storage for research decisions.

This module persists research-decision evidence only. It does not generate signals,
approve trades, place orders, or establish PAPER/LIVE readiness.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import cast

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_DECISION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
_SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")
_RECORD_NAME_PATTERN = re.compile(
    r"^(?P<decision>[A-Za-z0-9_-]{1,64})\.(?P<digest>[0-9a-f]{64})\.audit\.json$"
)
_CLAIM_NAME_PATTERN = re.compile(r"^(?P<decision>[A-Za-z0-9_-]{1,64})\.claim$")


class AuditIntegrityError(ValueError):
    """Raised when decision evidence cannot be safely validated or persisted."""


class EvidenceClassification(StrEnum):
    """Explicit provenance class for an item used in a decision audit record."""

    MEASURED = "MEASURED"
    MODELED = "MODELED"
    UNAVAILABLE = "UNAVAILABLE"


class DecisionOutcome(StrEnum):
    """Non-executing outcomes admitted while Gate 2 remains research-only."""

    REJECTED = "REJECTED"
    NO_ACTION = "NO_ACTION"


@dataclass(frozen=True)
class AuditEvidenceItem:
    """One evidence value with an explicit availability/provenance classification."""

    name: str
    classification: EvidenceClassification
    value: str | None = None
    source_ref: str | None = None
    reason: str | None = None

    def validate(self) -> None:
        if not self.name.strip():
            raise AuditIntegrityError("Evidence name is required.")
        if self.classification is EvidenceClassification.UNAVAILABLE:
            if self.value is not None or self.source_ref is not None:
                raise AuditIntegrityError(
                    "Unavailable evidence cannot carry a value or source reference."
                )
            if self.reason is None or not self.reason.strip():
                raise AuditIntegrityError(
                    "Unavailable evidence must record why it is unavailable."
                )
            return
        if self.value is None or not self.value.strip():
            raise AuditIntegrityError(
                "Measured or modeled evidence must retain an explicit value."
            )
        if self.source_ref is None or not self.source_ref.strip():
            raise AuditIntegrityError(
                "Measured or modeled evidence must retain a source reference."
            )

    def canonical_payload(self) -> dict[str, str | None]:
        self.validate()
        return {
            "name": self.name,
            "classification": self.classification.value,
            "value": self.value,
            "source_ref": self.source_ref,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class DecisionAuditRecord:
    """Research-only decision record linked to immutable acquired data evidence."""

    decision_id: str
    recorded_at_utc: str
    symbol: str
    timeframe: str
    outcome: DecisionOutcome
    reason_codes: tuple[str, ...]
    dataset_sha256: str
    artifact_sha256: str
    evidence: tuple[AuditEvidenceItem, ...]
    operating_mode: str = "PAPER_ONLY"
    readiness: str = "RESEARCH_ONLY"
    schema_version: int = 1

    def validate(self) -> None:
        if not _DECISION_ID_PATTERN.fullmatch(self.decision_id):
            raise AuditIntegrityError(
                "decision_id must be a safe non-empty identifier."
            )
        try:
            moment = datetime.fromisoformat(self.recorded_at_utc.replace("Z", "+00:00"))
        except ValueError as exc:
            raise AuditIntegrityError(
                "recorded_at_utc must be an ISO-8601 timestamp."
            ) from exc
        if moment.tzinfo is None or moment.utcoffset() != UTC.utcoffset(None):
            raise AuditIntegrityError("recorded_at_utc must use UTC.")
        if (
            not _SYMBOL_PATTERN.fullmatch(self.symbol)
            or self.symbol != self.symbol.upper()
        ):
            raise AuditIntegrityError("symbol must use uppercase exchange notation.")
        if not self.timeframe.strip():
            raise AuditIntegrityError("timeframe is required.")
        if not self.reason_codes or any(not code.strip() for code in self.reason_codes):
            raise AuditIntegrityError("At least one non-empty reason code is required.")
        if not _SHA256_PATTERN.fullmatch(self.dataset_sha256):
            raise AuditIntegrityError(
                "dataset_sha256 must be a lowercase SHA-256 digest."
            )
        if not _SHA256_PATTERN.fullmatch(self.artifact_sha256):
            raise AuditIntegrityError(
                "artifact_sha256 must be a lowercase SHA-256 digest."
            )
        if self.operating_mode != "PAPER_ONLY" or self.readiness != "RESEARCH_ONLY":
            raise AuditIntegrityError(
                "Audit records must remain PAPER_ONLY/RESEARCH_ONLY."
            )
        if self.schema_version != 1:
            raise AuditIntegrityError("Unsupported decision-audit schema version.")
        if not self.evidence:
            raise AuditIntegrityError("A decision record must retain evidence entries.")
        names: set[str] = set()
        for item in self.evidence:
            item.validate()
            if item.name in names:
                raise AuditIntegrityError("Evidence item names must be unique.")
            names.add(item.name)

    def canonical_payload(self) -> dict[str, object]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "decision_id": self.decision_id,
            "recorded_at_utc": self.recorded_at_utc,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "outcome": self.outcome.value,
            "reason_codes": list(self.reason_codes),
            "dataset_sha256": self.dataset_sha256,
            "artifact_sha256": self.artifact_sha256,
            "operating_mode": self.operating_mode,
            "readiness": self.readiness,
            "evidence": [item.canonical_payload() for item in self.evidence],
        }


@dataclass(frozen=True)
class PersistedAuditRecord:
    """Verified local paths and digest for one immutable decision audit record."""

    path: Path
    claim_path: Path
    record_sha256: str
    record: DecisionAuditRecord


def _canonical_bytes(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _payload_digest(payload: dict[str, object]) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _required_text(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        raise AuditIntegrityError(f"Audit field '{key}' must be text.")
    return value


def _optional_text(payload: dict[str, object], key: str) -> str | None:
    value = payload.get(key)
    if value is not None and not isinstance(value, str):
        raise AuditIntegrityError(f"Audit field '{key}' must be text or null.")
    return value


def _record_from_payload(payload: dict[str, object]) -> DecisionAuditRecord:
    raw_reason_codes = payload.get("reason_codes")
    if not isinstance(raw_reason_codes, list) or not all(
        isinstance(code, str) for code in raw_reason_codes
    ):
        raise AuditIntegrityError("Audit reason_codes must be a text list.")
    raw_evidence = payload.get("evidence")
    if not isinstance(raw_evidence, list):
        raise AuditIntegrityError("Audit evidence must be a list.")
    evidence: list[AuditEvidenceItem] = []
    for raw_item in raw_evidence:
        if not isinstance(raw_item, dict):
            raise AuditIntegrityError("Audit evidence items must be mappings.")
        item = cast(dict[str, object], raw_item)
        try:
            classification = EvidenceClassification(
                _required_text(item, "classification")
            )
        except ValueError as exc:
            raise AuditIntegrityError("Unsupported evidence classification.") from exc
        evidence.append(
            AuditEvidenceItem(
                name=_required_text(item, "name"),
                classification=classification,
                value=_optional_text(item, "value"),
                source_ref=_optional_text(item, "source_ref"),
                reason=_optional_text(item, "reason"),
            )
        )
    try:
        outcome = DecisionOutcome(_required_text(payload, "outcome"))
    except ValueError as exc:
        raise AuditIntegrityError(
            "Unsupported research-only decision outcome."
        ) from exc
    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, int):
        raise AuditIntegrityError("Audit schema_version must be an integer.")
    record = DecisionAuditRecord(
        decision_id=_required_text(payload, "decision_id"),
        recorded_at_utc=_required_text(payload, "recorded_at_utc"),
        symbol=_required_text(payload, "symbol"),
        timeframe=_required_text(payload, "timeframe"),
        outcome=outcome,
        reason_codes=tuple(cast(list[str], raw_reason_codes)),
        dataset_sha256=_required_text(payload, "dataset_sha256"),
        artifact_sha256=_required_text(payload, "artifact_sha256"),
        evidence=tuple(evidence),
        operating_mode=_required_text(payload, "operating_mode"),
        readiness=_required_text(payload, "readiness"),
        schema_version=schema_version,
    )
    record.validate()
    return record


def _read_claim(path: Path) -> str:
    if _CLAIM_NAME_PATTERN.fullmatch(path.name) is None:
        raise AuditIntegrityError("Audit claim filename is invalid.")
    try:
        digest = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError) as exc:
        raise AuditIntegrityError("Audit claim cannot be read.") from exc
    if not _SHA256_PATTERN.fullmatch(digest):
        raise AuditIntegrityError("Audit claim digest is invalid.")
    return digest


def _claim_decision_identity(
    decision_id: str, digest: str, output_directory: Path
) -> Path:
    claim_path = output_directory / f"{decision_id}.claim"
    try:
        with claim_path.open("x", encoding="utf-8") as stream:
            stream.write(digest + "\n")
    except FileExistsError as exc:
        if _read_claim(claim_path) != digest:
            raise AuditIntegrityError(
                "A different immutable audit claim already exists for decision_id."
            ) from exc
    return claim_path


def append_decision_audit(
    record: DecisionAuditRecord, output_directory: Path
) -> PersistedAuditRecord:
    """Persist one immutable research-only decision record, rejecting conflicts."""

    payload = record.canonical_payload()
    digest = _payload_digest(payload)
    output_directory.mkdir(parents=True, exist_ok=True)
    destination = output_directory / f"{record.decision_id}.{digest}.audit.json"
    existing_match: PersistedAuditRecord | None = None
    pattern = f"{record.decision_id}.*.audit.json"
    for existing_path in sorted(output_directory.glob(pattern)):
        existing = read_decision_audit(existing_path)
        if existing.record_sha256 != digest:
            raise AuditIntegrityError(
                "A different immutable audit record already exists for decision_id."
            )
        existing_match = existing
    if existing_match is not None:
        return existing_match
    _claim_decision_identity(record.decision_id, digest, output_directory)
    envelope: dict[str, object] = {"record_sha256": digest, "record": payload}
    encoded = _canonical_bytes(envelope)
    try:
        with destination.open("xb") as stream:
            stream.write(encoded)
    except FileExistsError:
        return read_decision_audit(destination)
    return read_decision_audit(destination)


def read_decision_audit(path: Path) -> PersistedAuditRecord:
    """Read and checksum-verify one checksum-addressed immutable decision record."""

    match = _RECORD_NAME_PATTERN.fullmatch(path.name)
    if match is None:
        raise AuditIntegrityError("Audit filename does not retain checksum identity.")
    try:
        decoded = cast(object, json.loads(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditIntegrityError(
            "Audit record cannot be read as JSON evidence."
        ) from exc
    if not isinstance(decoded, dict):
        raise AuditIntegrityError("Audit envelope must be a mapping.")
    envelope = cast(dict[str, object], decoded)
    raw_record = envelope.get("record")
    if not isinstance(raw_record, dict):
        raise AuditIntegrityError("Audit envelope lacks a record mapping.")
    payload = cast(dict[str, object], raw_record)
    digest = _payload_digest(payload)
    declared_digest = _required_text(envelope, "record_sha256")
    if digest != declared_digest or digest != match.group("digest"):
        raise AuditIntegrityError("Audit checksum verification failed.")
    record = _record_from_payload(payload)
    if record.decision_id != match.group("decision"):
        raise AuditIntegrityError(
            "Audit filename decision identity does not match payload."
        )
    claim_path = path.parent / f"{record.decision_id}.claim"
    if _read_claim(claim_path) != digest:
        raise AuditIntegrityError("Audit claim does not match record checksum.")
    return PersistedAuditRecord(
        path=path, claim_path=claim_path, record_sha256=digest, record=record
    )


def discover_decision_audits(
    output_directory: Path,
) -> tuple[PersistedAuditRecord, ...]:
    """Discover and verify all locally present decision records, failing closed."""

    if not output_directory.exists():
        return ()
    records = [
        read_decision_audit(path)
        for path in sorted(output_directory.glob("*.audit.json"))
    ]
    record_digests = {
        record.record.decision_id: record.record_sha256 for record in records
    }
    for claim_path in sorted(output_directory.glob("*.claim")):
        match = _CLAIM_NAME_PATTERN.fullmatch(claim_path.name)
        if match is None:
            raise AuditIntegrityError("Audit claim filename is invalid.")
        if record_digests.get(match.group("decision")) != _read_claim(claim_path):
            raise AuditIntegrityError("Audit claim lacks its matching verified record.")
    return tuple(records)
