import json
from dataclasses import replace
from pathlib import Path
from typing import cast

import pytest

from src.persistence.audit import (
    AuditEvidenceItem,
    AuditIntegrityError,
    DecisionAuditRecord,
    DecisionOutcome,
    EvidenceClassification,
    append_decision_audit,
    discover_decision_audits,
    read_decision_audit,
)

DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


def record(
    *,
    decision_id: str = "decision_001",
    outcome: DecisionOutcome = DecisionOutcome.REJECTED,
    evidence: tuple[AuditEvidenceItem, ...] | None = None,
    operating_mode: str = "PAPER_ONLY",
) -> DecisionAuditRecord:
    return DecisionAuditRecord(
        decision_id=decision_id,
        recorded_at_utc="2026-05-29T12:00:00Z",
        symbol="BTCUSDT",
        timeframe="1m",
        outcome=outcome,
        reason_codes=("INSUFFICIENT_EXECUTION_EVIDENCE",),
        dataset_sha256=DIGEST_A,
        artifact_sha256=DIGEST_B,
        evidence=evidence
        or (
            AuditEvidenceItem(
                name="dataset_integrity",
                classification=EvidenceClassification.MEASURED,
                value="verified",
                source_ref="artifact_sha256:" + DIGEST_B,
            ),
            AuditEvidenceItem(
                name="spread_bps",
                classification=EvidenceClassification.UNAVAILABLE,
                reason="No orderbook snapshot is available at this gate.",
            ),
        ),
        operating_mode=operating_mode,
    )


def test_rejected_decision_is_persisted_and_verified_after_readback(
    tmp_path: Path,
) -> None:
    persisted = append_decision_audit(record(), tmp_path)

    restored = read_decision_audit(persisted.path)
    discovered = discover_decision_audits(tmp_path)

    assert restored.record.outcome is DecisionOutcome.REJECTED
    assert restored.record_sha256 == persisted.record_sha256
    assert discovered == (restored,)
    assert persisted.path.name.startswith("decision_001.")


def test_identical_append_is_idempotent_without_creating_duplicate_record(
    tmp_path: Path,
) -> None:
    first = append_decision_audit(record(), tmp_path)
    second = append_decision_audit(record(), tmp_path)

    assert first == second
    assert len(list(tmp_path.glob("*.audit.json"))) == 1


def test_conflicting_record_for_existing_decision_id_fails_closed(
    tmp_path: Path,
) -> None:
    append_decision_audit(record(), tmp_path)

    with pytest.raises(AuditIntegrityError, match="different immutable"):
        append_decision_audit(record(outcome=DecisionOutcome.NO_ACTION), tmp_path)


def test_altered_record_bytes_fail_checksum_verification(tmp_path: Path) -> None:
    persisted = append_decision_audit(record(), tmp_path)
    decoded = cast(object, json.loads(persisted.path.read_text(encoding="utf-8")))
    assert isinstance(decoded, dict)
    payload = cast(dict[str, object], decoded)
    raw_record = payload["record"]
    assert isinstance(raw_record, dict)
    stored_record = cast(dict[str, object], raw_record)
    stored_record["reason_codes"] = ["TAMPERED"]
    persisted.path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(AuditIntegrityError, match="checksum"):
        read_decision_audit(persisted.path)


def test_unavailable_evidence_cannot_hide_a_supplied_value(tmp_path: Path) -> None:
    evidence = (
        AuditEvidenceItem(
            name="spread_bps",
            classification=EvidenceClassification.UNAVAILABLE,
            value="0",
            reason="not captured",
        ),
    )

    with pytest.raises(AuditIntegrityError, match="Unavailable evidence"):
        append_decision_audit(record(evidence=evidence), tmp_path)


def test_measured_evidence_requires_source_reference(tmp_path: Path) -> None:
    evidence = (
        AuditEvidenceItem(
            name="dataset_integrity",
            classification=EvidenceClassification.MEASURED,
            value="verified",
        ),
    )

    with pytest.raises(AuditIntegrityError, match="source reference"):
        append_decision_audit(record(evidence=evidence), tmp_path)


def test_non_utc_timestamp_and_non_paper_mode_fail_closed(tmp_path: Path) -> None:
    not_utc = replace(record(), recorded_at_utc="2026-05-29T15:00:00+03:00")
    with pytest.raises(AuditIntegrityError, match="must use UTC"):
        append_decision_audit(not_utc, tmp_path)

    with pytest.raises(AuditIntegrityError, match="PAPER_ONLY"):
        append_decision_audit(record(operating_mode="LIVE"), tmp_path)
