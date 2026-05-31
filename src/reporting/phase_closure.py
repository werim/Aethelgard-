"""Persistence/audit phase closure review for Aethelgard.

This module publishes a deterministic research-readiness ledger for the
completed local persistence/audit evidence gates. It does not run strategies,
backtests, execution simulation, order routing, risk allocation, or PAPER/LIVE
runtime behavior.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum


class ClosureEvidenceClassification(StrEnum):
    """Evidence labels admitted by the phase-closure ledger."""

    MEASURED = "MEASURED"
    UNVERIFIED = "UNVERIFIED"
    UNAVAILABLE = "UNAVAILABLE"


class PhaseClosureStatus(StrEnum):
    """Fail-closed phase closure status."""

    CLOSED_FOR_RESEARCH_USE = "CLOSED_FOR_RESEARCH_USE"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class GateClosureEvidence:
    """One gate-level closure row with explicit evidence limits."""

    gate: str
    boundary: str
    validation: str
    evidence_classification: ClosureEvidenceClassification
    evidence_limit: str


@dataclass(frozen=True)
class PersistenceAuditPhaseClosure:
    """Deterministic closure ledger for the local persistence/audit phase."""

    status: PhaseClosureStatus
    operating_mode: str
    readiness: str
    completed_gates: tuple[GateClosureEvidence, ...]
    blocked_capabilities: tuple[str, ...]
    unresolved_risks: tuple[str, ...]
    next_phase: str

    def fail_closed(self) -> None:
        """Reject promotion when the closure status or safety posture is unsafe."""

        if self.status is not PhaseClosureStatus.CLOSED_FOR_RESEARCH_USE:
            raise ValueError("Persistence/audit phase closure is blocked.")
        if self.operating_mode != "PAPER_ONLY":
            raise ValueError("Unsafe operating mode in phase closure ledger.")
        if self.readiness != "RESEARCH_ONLY":
            raise ValueError("Unsafe readiness in phase closure ledger.")


_COMPLETED_GATES = (
    GateClosureEvidence(
        gate="2A",
        boundary="Append-only local JSON decision audit records and claim anchors.",
        validation="PR #3 final-head validation run #28 succeeded before Gate 2B.",
        evidence_classification=ClosureEvidenceClassification.MEASURED,
        evidence_limit="Local file evidence only; not external notarization.",
    ),
    GateClosureEvidence(
        gate="2B",
        boundary="Local SQLite research audit-event ledger.",
        validation="PR #4 final-head validation run #48 succeeded before Gate 2C.",
        evidence_classification=ClosureEvidenceClassification.MEASURED,
        evidence_limit="Local database-row evidence only; not a distributed event bus.",
    ),
    GateClosureEvidence(
        gate="2C",
        boundary="Controlled file-audit to database-event append helper.",
        validation="PR #5 final-head validation run #51 succeeded before Gate 2D.",
        evidence_classification=ClosureEvidenceClassification.MEASURED,
        evidence_limit=(
            "Narrows partial-write risk but is not a cross-store transaction "
            "manager."
        ),
    ),
    GateClosureEvidence(
        gate="2D",
        boundary="Read-only file/database persistence reconciliation scan.",
        validation="PR #6 final-head validation run #56 succeeded before Gate 2E.",
        evidence_classification=ClosureEvidenceClassification.MEASURED,
        evidence_limit="Reports mismatch states only; does not repair evidence.",
    ),
    GateClosureEvidence(
        gate="2E",
        boundary=(
            "Deterministic reconciliation report payload, JSON, and Markdown "
            "surface."
        ),
        validation="PR #7 final-head validation run #60 succeeded before Gate 2F.",
        evidence_classification=ClosureEvidenceClassification.MEASURED,
        evidence_limit="Report surface only; does not add operational readiness.",
    ),
    GateClosureEvidence(
        gate="2F",
        boundary=(
            "Local reconciliation report artifact persistence and readback "
            "verification."
        ),
        validation="PR #8 head validation run #63 succeeded before Gate 2G.",
        evidence_classification=ClosureEvidenceClassification.MEASURED,
        evidence_limit=(
            "Local stored-byte evidence only; not adversarial tamper "
            "protection."
        ),
    ),
)

_BLOCKED_CAPABILITIES = (
    "strategy_signal_generation",
    "backtesting",
    "execution_simulation",
    "fill_modeling",
    "risk_allocation",
    "paper_runtime_loop",
    "live_trading",
    "profitability_claims",
)

_UNRESOLVED_RISKS = (
    "Execution costs, spreads, slippage, latency, funding, orderbook state, "
    "and fill quality remain unavailable.",
    "Local checksums and SQLite digests do not protect against complete "
    "evidence-set replacement.",
    "File and database evidence boundaries do not provide atomic cross-store "
    "commit semantics.",
    "Market-data completeness, exchange authenticity, strategy expectancy, "
    "and operational readiness are not proven.",
)


def persistence_audit_phase_closure() -> PersistenceAuditPhaseClosure:
    """Return the deterministic Gate 2G persistence/audit closure ledger."""

    closure = PersistenceAuditPhaseClosure(
        status=PhaseClosureStatus.CLOSED_FOR_RESEARCH_USE,
        operating_mode="PAPER_ONLY",
        readiness="RESEARCH_ONLY",
        completed_gates=_COMPLETED_GATES,
        blocked_capabilities=_BLOCKED_CAPABILITIES,
        unresolved_risks=_UNRESOLVED_RISKS,
        next_phase=(
            "Gate 3 may begin only as a conservative research backtest foundation; "
            "execution realism remains unavailable until explicitly modeled."
        ),
    )
    closure.fail_closed()
    return closure


def phase_closure_payload(
    closure: PersistenceAuditPhaseClosure | None = None,
) -> dict[str, object]:
    """Return a deterministic JSON-compatible phase-closure payload."""

    selected = closure or persistence_audit_phase_closure()
    selected.fail_closed()
    return {
        "schema_version": 1,
        "status": selected.status.value,
        "operating_mode": selected.operating_mode,
        "readiness": selected.readiness,
        "completed_gates": [
            {
                "gate": gate.gate,
                "boundary": gate.boundary,
                "validation": gate.validation,
                "evidence_classification": gate.evidence_classification.value,
                "evidence_limit": gate.evidence_limit,
            }
            for gate in selected.completed_gates
        ],
        "blocked_capabilities": list(selected.blocked_capabilities),
        "unresolved_risks": list(selected.unresolved_risks),
        "next_phase": selected.next_phase,
    }


def phase_closure_json(
    closure: PersistenceAuditPhaseClosure | None = None,
) -> str:
    """Serialize the phase-closure payload as deterministic compact JSON."""

    return json.dumps(
        phase_closure_payload(closure),
        sort_keys=True,
        separators=(",", ":"),
    )


def phase_closure_markdown(
    closure: PersistenceAuditPhaseClosure | None = None,
) -> str:
    """Render the phase-closure payload as deterministic Markdown."""

    payload = phase_closure_payload(closure)
    lines = [
        "# Persistence/Audit Phase Closure",
        "",
        f"- Status: `{payload['status']}`",
        f"- Operating mode: `{payload['operating_mode']}`",
        f"- Readiness: `{payload['readiness']}`",
        "",
        "## Completed gates",
        "",
    ]
    completed_gates = payload["completed_gates"]
    if not isinstance(completed_gates, list):
        raise AssertionError("Completed gates payload must be a list.")
    for raw_gate in completed_gates:
        if not isinstance(raw_gate, dict):
            raise AssertionError("Completed gate payload must be a mapping.")
        lines.extend(
            [
                f"### Gate {raw_gate['gate']}",
                "",
                f"- Boundary: {raw_gate['boundary']}",
                f"- Validation: {raw_gate['validation']}",
                f"- Evidence: `{raw_gate['evidence_classification']}`",
                f"- Limit: {raw_gate['evidence_limit']}",
                "",
            ]
        )
    lines.extend(["## Blocked capabilities", ""])
    blocked = payload["blocked_capabilities"]
    if not isinstance(blocked, list):
        raise AssertionError("Blocked capabilities payload must be a list.")
    for capability in blocked:
        lines.append(f"- `{capability}`")
    lines.extend(["", "## Unresolved risks", ""])
    risks = payload["unresolved_risks"]
    if not isinstance(risks, list):
        raise AssertionError("Unresolved risks payload must be a list.")
    for risk in risks:
        lines.append(f"- {risk}")
    lines.extend(["", "## Next phase", "", str(payload["next_phase"])])
    return "\n".join(lines).rstrip() + "\n"
