import json

import pytest

from src.reporting.phase_closure import (
    ClosureEvidenceClassification,
    PersistenceAuditPhaseClosure,
    PhaseClosureStatus,
    persistence_audit_phase_closure,
    phase_closure_json,
    phase_closure_markdown,
    phase_closure_payload,
)


def test_persistence_audit_phase_closure_is_research_only() -> None:
    closure = persistence_audit_phase_closure()

    assert closure.status is PhaseClosureStatus.CLOSED_FOR_RESEARCH_USE
    assert closure.operating_mode == "PAPER_ONLY"
    assert closure.readiness == "RESEARCH_ONLY"
    assert tuple(gate.gate for gate in closure.completed_gates) == (
        "2A",
        "2B",
        "2C",
        "2D",
        "2E",
        "2F",
    )
    assert all(
        gate.evidence_classification is ClosureEvidenceClassification.MEASURED
        for gate in closure.completed_gates
    )


def test_phase_closure_payload_blocks_runtime_capabilities() -> None:
    payload = phase_closure_payload()

    assert payload["status"] == "CLOSED_FOR_RESEARCH_USE"
    assert payload["operating_mode"] == "PAPER_ONLY"
    assert payload["readiness"] == "RESEARCH_ONLY"
    assert "backtesting" in payload["blocked_capabilities"]
    assert "execution_simulation" in payload["blocked_capabilities"]
    assert "paper_runtime_loop" in payload["blocked_capabilities"]
    assert "live_trading" in payload["blocked_capabilities"]
    assert "profitability_claims" in payload["blocked_capabilities"]
    assert "execution realism remains unavailable" in payload["next_phase"]


def test_phase_closure_json_is_deterministic_and_safe() -> None:
    first = phase_closure_json()
    second = phase_closure_json()

    assert second == first
    parsed = json.loads(first)
    assert parsed["schema_version"] == 1
    assert parsed["status"] == "CLOSED_FOR_RESEARCH_USE"
    assert parsed["completed_gates"][-1]["validation"] == (
        "PR #8 head validation run #63 succeeded before Gate 2G."
    )


def test_phase_closure_markdown_records_limits() -> None:
    markdown = phase_closure_markdown()

    assert "# Persistence/Audit Phase Closure" in markdown
    assert "### Gate 2F" in markdown
    assert "## Blocked capabilities" in markdown
    assert "`live_trading`" in markdown
    assert "## Unresolved risks" in markdown
    assert "not proven" in markdown


def test_phase_closure_fails_closed_for_unsafe_mode() -> None:
    safe = persistence_audit_phase_closure()
    unsafe = PersistenceAuditPhaseClosure(
        status=safe.status,
        operating_mode="LIVE",
        readiness=safe.readiness,
        completed_gates=safe.completed_gates,
        blocked_capabilities=safe.blocked_capabilities,
        unresolved_risks=safe.unresolved_risks,
        next_phase=safe.next_phase,
    )

    with pytest.raises(ValueError, match="Unsafe operating mode"):
        phase_closure_payload(unsafe)


def test_phase_closure_fails_closed_for_blocked_status() -> None:
    safe = persistence_audit_phase_closure()
    blocked = PersistenceAuditPhaseClosure(
        status=PhaseClosureStatus.BLOCKED,
        operating_mode=safe.operating_mode,
        readiness=safe.readiness,
        completed_gates=safe.completed_gates,
        blocked_capabilities=safe.blocked_capabilities,
        unresolved_risks=safe.unresolved_risks,
        next_phase=safe.next_phase,
    )

    with pytest.raises(ValueError, match="blocked"):
        phase_closure_payload(blocked)
