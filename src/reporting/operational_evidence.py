"""Gate 5A operational evidence deployment-blocker matrix.

This module evaluates whether the current PAPER-only research platform has
measured operational evidence for every blocker category required before any
paper deployment claim. It emits blocker diagnostics only. It does not compute
performance, model costs, submit orders, mutate exchange state, or approve LIVE
readiness.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum


class OperationalEvidenceClassification(StrEnum):
    """Evidence classes for Gate 5A operational deployment blockers."""

    MEASURED = "MEASURED"
    MODELED = "MODELED"
    UNAVAILABLE = "UNAVAILABLE"


class DeploymentBlockerStatus(StrEnum):
    """Fail-closed blocker status for each required operational evidence row."""

    BLOCKED = "BLOCKED"
    CLEARED = "CLEARED"


class OperationalDeploymentStatus(StrEnum):
    """Aggregate Gate 5A status for PAPER operational deployment evidence."""

    DEPLOYMENT_BLOCKED = "DEPLOYMENT_BLOCKED"
    DEPLOYMENT_NOT_BLOCKED = "DEPLOYMENT_NOT_BLOCKED"


class OperationalEvidenceGateError(RuntimeError):
    """Raised when Gate 5A deployment blockers remain unresolved."""


@dataclass(frozen=True)
class OperationalEvidenceItem:
    """Caller-supplied evidence for one operational blocker category."""

    blocker_id: str
    classification: OperationalEvidenceClassification
    summary: str
    source: str

    def payload(self) -> dict[str, str]:
        """Return a deterministic JSON-compatible evidence item payload."""

        return {
            "blocker_id": self.blocker_id,
            "classification": self.classification.value,
            "source": self.source,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class DeploymentBlockerMatrixRow:
    """Gate 5A matrix row for a required operational deployment blocker."""

    blocker_id: str
    required_evidence: str
    status: DeploymentBlockerStatus
    evidence_classification: OperationalEvidenceClassification
    diagnostics: tuple[str, ...]
    evidence_summary: str | None = None
    evidence_source: str | None = None

    def payload(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible matrix row payload."""

        return {
            "blocker_id": self.blocker_id,
            "diagnostics": list(self.diagnostics),
            "evidence_classification": self.evidence_classification.value,
            "evidence_source": self.evidence_source,
            "evidence_summary": self.evidence_summary,
            "required_evidence": self.required_evidence,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class OperationalEvidenceGateResult:
    """Aggregate Gate 5A result with deterministic blocker diagnostics."""

    status: OperationalDeploymentStatus
    paper_deployment_blocked: bool
    matrix: tuple[DeploymentBlockerMatrixRow, ...]
    diagnostics: tuple[str, ...]

    def payload(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible Gate 5A result payload."""

        return {
            "diagnostics": list(self.diagnostics),
            "matrix": [row.payload() for row in self.matrix],
            "paper_deployment_blocked": self.paper_deployment_blocked,
            "status": self.status.value,
        }


REQUIRED_OPERATIONAL_BLOCKERS: Mapping[str, str] = {
    "audit_trail_integrity": "append-only audit trail integrity evidence",
    "ci_validation": "exact branch-head CI or local validation evidence",
    "data_freshness": "freshness and selector-consistency evidence",
    "execution_cost_evidence": "fees, spread, slippage, funding, and latency evidence",
    "paper_runtime_reconciliation": "PAPER runtime lifecycle reconciliation evidence",
    "risk_control_enforcement": (
        "risk controls and circuit-breaker enforcement evidence"
    ),
}


def evaluate_operational_evidence_gate(
    evidence_items: Sequence[OperationalEvidenceItem],
) -> OperationalEvidenceGateResult:
    """Evaluate Gate 5A and fail closed unless every blocker is measured."""

    _validate_operational_evidence_items(evidence_items)
    evidence_by_id = {item.blocker_id: item for item in evidence_items}
    rows = tuple(
        _build_matrix_row(blocker_id, required_evidence, evidence_by_id)
        for blocker_id, required_evidence in sorted(
            REQUIRED_OPERATIONAL_BLOCKERS.items()
        )
    )
    blocked_rows = tuple(
        row for row in rows if row.status is DeploymentBlockerStatus.BLOCKED
    )
    diagnostics = tuple(row.diagnostics[0] for row in blocked_rows)

    if blocked_rows:
        return OperationalEvidenceGateResult(
            status=OperationalDeploymentStatus.DEPLOYMENT_BLOCKED,
            paper_deployment_blocked=True,
            matrix=rows,
            diagnostics=diagnostics,
        )

    return OperationalEvidenceGateResult(
        status=OperationalDeploymentStatus.DEPLOYMENT_NOT_BLOCKED,
        paper_deployment_blocked=False,
        matrix=rows,
        diagnostics=(
            "Gate 5A blockers have measured evidence for PAPER operational "
            "deployment diagnostics only; no LIVE readiness or profitability "
            "claim is implied",
        ),
    )


def operational_evidence_gate_json(result: OperationalEvidenceGateResult) -> str:
    """Serialize a Gate 5A result deterministically."""

    return json.dumps(result.payload(), sort_keys=True, separators=(",", ":"))


def render_deployment_blocker_matrix_markdown(
    result: OperationalEvidenceGateResult,
) -> str:
    """Render the Gate 5A deployment blocker matrix as Markdown."""

    lines = [
        "# Gate 5A Operational Evidence Gate",
        "",
        f"Status: `{result.status.value}`",
        f"PAPER deployment blocked: `{result.paper_deployment_blocked}`",
        "Operational classification: `PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY`",
        "",
        "Unknown execution costs are not zero. Missing evidence remains unavailable.",
        "Backtest performance alone does not prove production readiness.",
        "",
        "| Blocker | Required evidence | Classification | Status | Diagnostics |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in result.matrix:
        lines.append(
            "| "
            f"{row.blocker_id} | "
            f"{row.required_evidence} | "
            f"{row.evidence_classification.value} | "
            f"{row.status.value} | "
            f"{'; '.join(row.diagnostics)} |"
        )
    return "\n".join(lines)


def assert_operational_deployment_not_blocked(
    result: OperationalEvidenceGateResult,
) -> None:
    """Raise unless Gate 5A has measured evidence for every blocker."""

    if result.paper_deployment_blocked:
        unresolved = ", ".join(
            row.blocker_id
            for row in result.matrix
            if row.status is DeploymentBlockerStatus.BLOCKED
        )
        raise OperationalEvidenceGateError(
            f"Gate 5A deployment blocked by unresolved evidence: {unresolved}"
        )


def _validate_operational_evidence_items(
    evidence_items: Sequence[OperationalEvidenceItem],
) -> None:
    """Validate caller-supplied evidence before building the blocker matrix."""

    seen: set[str] = set()
    for item in evidence_items:
        blocker_id = item.blocker_id.strip()
        if not blocker_id:
            raise OperationalEvidenceGateError(
                "Gate 5A evidence item has empty blocker_id"
            )
        if blocker_id != item.blocker_id:
            raise OperationalEvidenceGateError(
                f"Gate 5A evidence item has non-canonical blocker_id: {blocker_id}"
            )
        if blocker_id not in REQUIRED_OPERATIONAL_BLOCKERS:
            raise OperationalEvidenceGateError(
                f"Gate 5A evidence item has unsupported blocker_id: {blocker_id}"
            )
        if blocker_id in seen:
            raise OperationalEvidenceGateError(
                f"Gate 5A evidence item has duplicate blocker_id: {blocker_id}"
            )
        if not item.summary.strip():
            raise OperationalEvidenceGateError(
                f"Gate 5A evidence item has empty summary: {blocker_id}"
            )
        if not item.source.strip():
            raise OperationalEvidenceGateError(
                f"Gate 5A evidence item has empty source: {blocker_id}"
            )
        seen.add(blocker_id)


def _build_matrix_row(
    blocker_id: str,
    required_evidence: str,
    evidence_by_id: Mapping[str, OperationalEvidenceItem],
) -> DeploymentBlockerMatrixRow:
    item = evidence_by_id.get(blocker_id)
    if item is None:
        return DeploymentBlockerMatrixRow(
            blocker_id=blocker_id,
            required_evidence=required_evidence,
            status=DeploymentBlockerStatus.BLOCKED,
            evidence_classification=OperationalEvidenceClassification.UNAVAILABLE,
            diagnostics=(f"{blocker_id} evidence is missing",),
        )
    if item.classification is not OperationalEvidenceClassification.MEASURED:
        return DeploymentBlockerMatrixRow(
            blocker_id=blocker_id,
            required_evidence=required_evidence,
            status=DeploymentBlockerStatus.BLOCKED,
            evidence_classification=item.classification,
            diagnostics=(
                f"{blocker_id} requires MEASURED evidence; "
                f"got {item.classification.value}",
            ),
            evidence_summary=item.summary,
            evidence_source=item.source,
        )
    return DeploymentBlockerMatrixRow(
        blocker_id=blocker_id,
        required_evidence=required_evidence,
        status=DeploymentBlockerStatus.CLEARED,
        evidence_classification=item.classification,
        diagnostics=(f"{blocker_id} measured evidence recorded",),
        evidence_summary=item.summary,
        evidence_source=item.source,
    )
