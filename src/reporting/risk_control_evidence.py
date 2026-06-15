"""Gate 5A-5 risk-control enforcement evidence adapter.

This module converts caller-supplied risk-control policy evidence into a Gate 5A
`risk_control_enforcement` evidence item. It is deliberately offline and
deterministic: it does not run a PAPER runtime, compute performance, submit
orders, mutate exchange state, change strategy logic, or approve readiness.
Missing, malformed, or unenforced policy evidence remains UNAVAILABLE.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from src.reporting.operational_evidence import (
    OperationalEvidenceClassification,
    OperationalEvidenceItem,
)


class RiskControlEvidenceStatus(StrEnum):
    """Risk-control evidence adapter status values."""

    ENFORCEMENT_MEASURED = "ENFORCEMENT_MEASURED"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class RiskControlPolicyEvidence:
    """Caller-supplied evidence for one risk-control policy."""

    policy_id: str
    enforced: bool

    def payload(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible policy payload."""

        return {"enforced": self.enforced, "policy_id": self.policy_id}


@dataclass(frozen=True)
class RiskControlEnforcementEvidence:
    """Caller-supplied risk-control enforcement evidence bundle."""

    source: str
    required_policy_ids: tuple[str, ...]
    observed_policies: tuple[RiskControlPolicyEvidence, ...]

    def payload(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible evidence payload."""

        return {
            "observed_policies": [policy.payload() for policy in self.observed_policies],
            "required_policy_ids": list(self.required_policy_ids),
            "source": self.source,
        }


@dataclass(frozen=True)
class RiskControlEvidenceAssessment:
    """Fail-closed Gate 5A assessment for risk-control enforcement evidence."""

    status: RiskControlEvidenceStatus
    classification: OperationalEvidenceClassification
    diagnostics: tuple[str, ...]
    evidence_item: OperationalEvidenceItem

    def payload(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible assessment payload."""

        return {
            "classification": self.classification.value,
            "diagnostics": list(self.diagnostics),
            "evidence_item": self.evidence_item.payload(),
            "status": self.status.value,
        }


def assess_risk_control_enforcement_for_gate5a(
    evidence: RiskControlEnforcementEvidence | None,
    *,
    source: str = "",
) -> RiskControlEvidenceAssessment:
    """Classify risk-control enforcement evidence for Gate 5A."""

    diagnostics = _risk_control_diagnostics(evidence, fallback_source=source)
    if diagnostics:
        return _build_assessment(
            status=RiskControlEvidenceStatus.UNAVAILABLE,
            classification=OperationalEvidenceClassification.UNAVAILABLE,
            diagnostics=diagnostics,
            source=_evidence_source(evidence, fallback_source=source),
        )

    if evidence is None:
        raise AssertionError("Evidence must be present after diagnostics pass.")
    required_count = len(evidence.required_policy_ids)
    summary = (
        "Risk-control enforcement measured for "
        f"{required_count} required policy evidence item(s)"
    )
    return RiskControlEvidenceAssessment(
        status=RiskControlEvidenceStatus.ENFORCEMENT_MEASURED,
        classification=OperationalEvidenceClassification.MEASURED,
        diagnostics=(summary,),
        evidence_item=OperationalEvidenceItem(
            blocker_id="risk_control_enforcement",
            classification=OperationalEvidenceClassification.MEASURED,
            summary=summary,
            source=evidence.source,
        ),
    )


def risk_control_evidence_assessment_json(
    assessment: RiskControlEvidenceAssessment,
) -> str:
    """Serialize a risk-control evidence assessment deterministically."""

    return json.dumps(assessment.payload(), sort_keys=True, separators=(",", ":"))


def _risk_control_diagnostics(
    evidence: RiskControlEnforcementEvidence | None,
    *,
    fallback_source: str,
) -> tuple[str, ...]:
    diagnostics: list[str] = []

    if evidence is None:
        if not fallback_source.strip():
            diagnostics.append("risk-control evidence source is missing")
        diagnostics.append("risk-control enforcement evidence is unavailable")
        return tuple(diagnostics)

    if not evidence.source.strip():
        diagnostics.append("risk-control evidence source is missing")

    required_policy_ids = _canonical_policy_ids(
        evidence.required_policy_ids,
        label="required",
        diagnostics=diagnostics,
    )
    observed_by_id = _observed_policy_map(evidence.observed_policies, diagnostics)

    for policy_id in required_policy_ids:
        enforced = observed_by_id.get(policy_id)
        if enforced is None:
            diagnostics.append(f"required risk-control policy {policy_id!r} is missing")
        elif not enforced:
            diagnostics.append(
                f"required risk-control policy {policy_id!r} is not enforced"
            )

    return tuple(diagnostics)


def _canonical_policy_ids(
    policy_ids: Sequence[str],
    *,
    label: str,
    diagnostics: list[str],
) -> tuple[str, ...]:
    canonical_policy_ids: list[str] = []
    seen: set[str] = set()
    if not policy_ids:
        diagnostics.append(f"{label} risk-control policy list is empty")
    for policy_id in policy_ids:
        canonical_policy_id = policy_id.strip()
        if not canonical_policy_id:
            diagnostics.append(f"{label} risk-control policy id is empty")
            continue
        if canonical_policy_id != policy_id:
            diagnostics.append(
                f"{label} risk-control policy id {policy_id!r} is non-canonical"
            )
        if canonical_policy_id in seen:
            diagnostics.append(
                f"{label} risk-control policy {canonical_policy_id!r} is duplicated"
            )
        seen.add(canonical_policy_id)
        canonical_policy_ids.append(canonical_policy_id)
    return tuple(canonical_policy_ids)


def _observed_policy_map(
    observed_policies: Sequence[RiskControlPolicyEvidence],
    diagnostics: list[str],
) -> dict[str, bool]:
    observed_by_id: dict[str, bool] = {}
    if not observed_policies:
        diagnostics.append("observed risk-control policy evidence list is empty")
    for policy in observed_policies:
        policy_id = policy.policy_id.strip()
        if not policy_id:
            diagnostics.append("observed risk-control policy id is empty")
            continue
        if policy_id != policy.policy_id:
            diagnostics.append(
                f"observed risk-control policy id {policy.policy_id!r} is non-canonical"
            )
        if policy_id in observed_by_id:
            diagnostics.append(f"observed risk-control policy {policy_id!r} is duplicated")
        observed_by_id[policy_id] = policy.enforced
    return observed_by_id


def _build_assessment(
    *,
    status: RiskControlEvidenceStatus,
    classification: OperationalEvidenceClassification,
    diagnostics: tuple[str, ...],
    source: str,
) -> RiskControlEvidenceAssessment:
    safe_source = source.strip() or "UNAVAILABLE: missing risk-control source"
    summary = "; ".join(diagnostics) if diagnostics else "risk-control unavailable"
    return RiskControlEvidenceAssessment(
        status=status,
        classification=classification,
        diagnostics=diagnostics,
        evidence_item=OperationalEvidenceItem(
            blocker_id="risk_control_enforcement",
            classification=classification,
            summary=summary,
            source=safe_source,
        ),
    )


def _evidence_source(
    evidence: RiskControlEnforcementEvidence | None,
    *,
    fallback_source: str,
) -> str:
    if evidence is None:
        return fallback_source
    return evidence.source
