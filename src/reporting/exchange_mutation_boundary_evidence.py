"""Gate 5A-11 exchange mutation boundary evidence adapter.

This module classifies caller-supplied evidence about exchange mutation
surfaces. It is deliberately offline and deterministic: it does not connect to
exchanges, place orders, cancel orders, mutate exchange state, approve live
trading, or promote PAPER_ONLY mode into production readiness. Missing audit or
runtime proof fails closed as unavailable evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ExchangeMutationBoundaryClassification(StrEnum):
    """Fail-closed exchange mutation boundary classifications."""

    MEASURED_NO_MUTATION_PATH = "MEASURED_NO_MUTATION_PATH"
    MEASURED_PAPER_ONLY_GUARD = "MEASURED_PAPER_ONLY_GUARD"
    USER_REPORTED_NO_LIVE_USE = "USER_REPORTED_NO_LIVE_USE"
    UNAVAILABLE_EXCHANGE_AUDIT = "UNAVAILABLE_EXCHANGE_AUDIT"
    UNAVAILABLE_RUNTIME_PROOF = "UNAVAILABLE_RUNTIME_PROOF"
    VIOLATION_EXCHANGE_MUTATION_ALLOWED = "VIOLATION_EXCHANGE_MUTATION_ALLOWED"


@dataclass(frozen=True)
class ExchangeMutationBoundaryEvidence:
    """Caller-supplied evidence for one exchange mutation boundary claim."""

    source: str
    exchange_audit_source: str | None = None
    runtime_proof_source: str | None = None
    source_reviewed: bool = False
    test_reviewed: bool = False
    runtime_proof_observed: bool = False
    user_reported_no_live_use: bool = False
    mutation_surface_present: bool = False
    hard_paper_only_guard_present: bool = False
    real_order_capability_present: bool = False
    docs_claim_production_ready: bool = False


@dataclass(frozen=True)
class ExchangeMutationBoundaryAssessment:
    """Deterministic assessment for exchange mutation boundary evidence."""

    classification: ExchangeMutationBoundaryClassification
    summary: str
    diagnostics: tuple[str, ...]
    source: str

    @property
    def measured(self) -> bool:
        """Return whether this is measured boundary evidence."""

        return self.classification in {
            ExchangeMutationBoundaryClassification.MEASURED_NO_MUTATION_PATH,
            ExchangeMutationBoundaryClassification.MEASURED_PAPER_ONLY_GUARD,
        }

    @property
    def violation(self) -> bool:
        """Return whether this assessment identifies a safety violation."""

        return self.classification is (
            ExchangeMutationBoundaryClassification.VIOLATION_EXCHANGE_MUTATION_ALLOWED
        )

    @property
    def permits_live_readiness_claim(self) -> bool:
        """Exchange mutation boundary evidence never permits live readiness."""

        return False

    def payload(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible payload."""

        return {
            "classification": self.classification.value,
            "diagnostics": list(self.diagnostics),
            "measured": self.measured,
            "permits_live_readiness_claim": self.permits_live_readiness_claim,
            "source": self.source,
            "summary": self.summary,
            "violation": self.violation,
        }


def classify_exchange_mutation_boundary_evidence(
    evidence: ExchangeMutationBoundaryEvidence,
) -> ExchangeMutationBoundaryAssessment:
    """Classify exchange mutation evidence without promoting missing proof."""

    source = evidence.source.strip() or "UNAVAILABLE: missing boundary evidence source"

    if evidence.docs_claim_production_ready:
        return _assessment(
            ExchangeMutationBoundaryClassification.VIOLATION_EXCHANGE_MUTATION_ALLOWED,
            "documentation claims production/live readiness without permission",
            ("docs cannot claim production readiness at Gate 5A-11",),
            source,
        )

    if (
        evidence.real_order_capability_present
        and not evidence.hard_paper_only_guard_present
    ):
        return _assessment(
            ExchangeMutationBoundaryClassification.VIOLATION_EXCHANGE_MUTATION_ALLOWED,
            "exchange mutation capability is present without a hard PAPER_ONLY guard",
            ("real order placement or exchange mutation surface is unguarded",),
            source,
        )

    if evidence.user_reported_no_live_use and not (
        evidence.source_reviewed
        or evidence.test_reviewed
        or evidence.runtime_proof_observed
    ):
        return _assessment(
            ExchangeMutationBoundaryClassification.USER_REPORTED_NO_LIVE_USE,
            "user-reported no-live-use remains unmeasured",
            ("user statements are not source, test, exchange-audit, or runtime proof",),
            source,
        )

    if not _has_text(evidence.exchange_audit_source):
        return _assessment(
            ExchangeMutationBoundaryClassification.UNAVAILABLE_EXCHANGE_AUDIT,
            "exchange audit evidence is unavailable",
            ("missing exchange audit evidence cannot be promoted to measured proof",),
            source,
        )

    if not evidence.runtime_proof_observed or not _has_text(
        evidence.runtime_proof_source
    ):
        return _assessment(
            ExchangeMutationBoundaryClassification.UNAVAILABLE_RUNTIME_PROOF,
            "runtime proof is unavailable",
            ("missing runtime proof cannot be promoted to measured proof",),
            source,
        )

    if evidence.mutation_surface_present or evidence.real_order_capability_present:
        if (
            evidence.hard_paper_only_guard_present
            and evidence.source_reviewed
            and evidence.test_reviewed
        ):
            return _assessment(
                ExchangeMutationBoundaryClassification.MEASURED_PAPER_ONLY_GUARD,
                "PAPER_ONLY guard boundary is measured for the mutation surface",
                (
                    "source and test evidence are present for the hard "
                    "PAPER_ONLY guard",
                    "PAPER_ONLY guard evidence does not imply live readiness",
                ),
                source,
            )
        return _assessment(
            ExchangeMutationBoundaryClassification.VIOLATION_EXCHANGE_MUTATION_ALLOWED,
            "exchange mutation capability lacks complete measured guard evidence",
            ("mutation surfaces require source and test evidence for a hard guard",),
            source,
        )

    if evidence.source_reviewed and evidence.test_reviewed:
        return _assessment(
            ExchangeMutationBoundaryClassification.MEASURED_NO_MUTATION_PATH,
            "source and tests show no exchange mutation path",
            ("measured no-mutation evidence does not imply production readiness",),
            source,
        )

    return _assessment(
        ExchangeMutationBoundaryClassification.UNAVAILABLE_EXCHANGE_AUDIT,
        "source/test exchange mutation audit evidence is incomplete",
        ("measured source and test evidence are required",),
        source,
    )


def docs_may_claim_production_ready(
    assessment: ExchangeMutationBoundaryAssessment,
) -> bool:
    """Documentation may not claim production readiness from this adapter."""

    return assessment.permits_live_readiness_claim


def _has_text(value: str | None) -> bool:
    return bool(value and value.strip())


def _assessment(
    classification: ExchangeMutationBoundaryClassification,
    summary: str,
    diagnostics: tuple[str, ...],
    source: str,
) -> ExchangeMutationBoundaryAssessment:
    return ExchangeMutationBoundaryAssessment(
        classification=classification,
        summary=summary,
        diagnostics=diagnostics,
        source=source,
    )
