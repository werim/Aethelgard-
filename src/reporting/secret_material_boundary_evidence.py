"""Gate 5A-12 secret material boundary evidence adapter.

This module classifies caller-supplied evidence about secret material handling.
It is deliberately offline and deterministic: it does not read environment
variables, request credentials, connect to exchanges, place orders, mutate
exchange state, approve live trading, or promote PAPER_ONLY mode into
production readiness. Missing audit or runtime proof fails closed as unavailable
evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SecretMaterialBoundaryClassification(StrEnum):
    """Fail-closed secret material boundary classifications."""

    MEASURED_NO_SECRET_MATERIAL = "MEASURED_NO_SECRET_MATERIAL"
    MEASURED_SECRET_PLACEHOLDER_ONLY = "MEASURED_SECRET_PLACEHOLDER_ONLY"
    USER_REPORTED_SECRETS_NOT_SHARED = "USER_REPORTED_SECRETS_NOT_SHARED"
    UNAVAILABLE_SECRET_AUDIT = "UNAVAILABLE_SECRET_AUDIT"
    UNAVAILABLE_RUNTIME_SECRET_PROOF = "UNAVAILABLE_RUNTIME_SECRET_PROOF"
    VIOLATION_SECRET_MATERIAL_EXPOSED = "VIOLATION_SECRET_MATERIAL_EXPOSED"


@dataclass(frozen=True)
class SecretMaterialBoundaryEvidence:
    """Caller-supplied evidence for one secret material boundary claim."""

    source: str
    secret_audit_source: str | None = None
    runtime_proof_source: str | None = None
    source_reviewed: bool = False
    test_reviewed: bool = False
    runtime_proof_observed: bool = False
    user_reported_secrets_not_shared: bool = False
    secret_material_present: bool = False
    placeholder_or_env_reference_only: bool = False
    committed_secret_material_present: bool = False
    docs_or_logs_expose_secret: bool = False
    secret_request_present: bool = False
    docs_claim_secret_safety: bool = False


@dataclass(frozen=True)
class SecretMaterialBoundaryAssessment:
    """Deterministic assessment for secret material boundary evidence."""

    classification: SecretMaterialBoundaryClassification
    summary: str
    diagnostics: tuple[str, ...]
    source: str

    @property
    def measured(self) -> bool:
        """Return whether this is measured boundary evidence."""

        return self.classification in {
            SecretMaterialBoundaryClassification.MEASURED_NO_SECRET_MATERIAL,
            SecretMaterialBoundaryClassification.MEASURED_SECRET_PLACEHOLDER_ONLY,
        }

    @property
    def violation(self) -> bool:
        """Return whether this assessment identifies a safety violation."""

        return self.classification is (
            SecretMaterialBoundaryClassification.VIOLATION_SECRET_MATERIAL_EXPOSED
        )

    @property
    def permits_live_readiness_claim(self) -> bool:
        """Secret material boundary evidence never permits live readiness."""

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


def classify_secret_material_boundary_evidence(
    evidence: SecretMaterialBoundaryEvidence,
) -> SecretMaterialBoundaryAssessment:
    """Classify secret-material evidence without promoting missing proof."""

    source = evidence.source.strip() or "UNAVAILABLE: missing secret evidence source"

    if evidence.secret_request_present:
        return _assessment(
            SecretMaterialBoundaryClassification.VIOLATION_SECRET_MATERIAL_EXPOSED,
            "secret material was requested or required",
            ("tools and docs must not request or expose secrets",),
            source,
        )

    if evidence.committed_secret_material_present or evidence.docs_or_logs_expose_secret:
        return _assessment(
            SecretMaterialBoundaryClassification.VIOLATION_SECRET_MATERIAL_EXPOSED,
            "secret material is exposed in repository, documentation, or logs",
            ("exposed credentials are release-blocking secret material evidence",),
            source,
        )

    if evidence.docs_claim_secret_safety and not (
        evidence.source_reviewed and evidence.test_reviewed and _has_text(evidence.secret_audit_source)
    ):
        return _assessment(
            SecretMaterialBoundaryClassification.UNAVAILABLE_SECRET_AUDIT,
            "documentation claims secret safety without measured audit evidence",
            ("secret-safety claims require source, test, and audit evidence",),
            source,
        )

    if evidence.user_reported_secrets_not_shared and not (
        evidence.source_reviewed or evidence.test_reviewed or evidence.runtime_proof_observed
    ):
        return _assessment(
            SecretMaterialBoundaryClassification.USER_REPORTED_SECRETS_NOT_SHARED,
            "user-reported secret safety remains unmeasured",
            ("user statements are not source, test, audit, or runtime proof",),
            source,
        )

    if not _has_text(evidence.secret_audit_source):
        return _assessment(
            SecretMaterialBoundaryClassification.UNAVAILABLE_SECRET_AUDIT,
            "secret material audit evidence is unavailable",
            ("missing secret audit evidence cannot be promoted to measured proof",),
            source,
        )

    if evidence.secret_material_present and not evidence.placeholder_or_env_reference_only:
        return _assessment(
            SecretMaterialBoundaryClassification.VIOLATION_SECRET_MATERIAL_EXPOSED,
            "non-placeholder secret material is present",
            ("real credential material must not be present in repository surfaces",),
            source,
        )

    if evidence.placeholder_or_env_reference_only:
        if not evidence.runtime_proof_observed or not _has_text(evidence.runtime_proof_source):
            return _assessment(
                SecretMaterialBoundaryClassification.UNAVAILABLE_RUNTIME_SECRET_PROOF,
                "runtime secret-handling proof is unavailable",
                ("placeholder/env-reference evidence still needs runtime proof",),
                source,
            )
        if evidence.source_reviewed and evidence.test_reviewed:
            return _assessment(
                SecretMaterialBoundaryClassification.MEASURED_SECRET_PLACEHOLDER_ONLY,
                "secret surfaces are limited to placeholders or environment references",
                (
                    "source, test, audit, and runtime evidence are present for "
                    "placeholder-only secret handling",
                    "placeholder-only secret evidence does not imply live readiness",
                ),
                source,
            )
        return _assessment(
            SecretMaterialBoundaryClassification.UNAVAILABLE_SECRET_AUDIT,
            "source/test secret material audit evidence is incomplete",
            ("measured source and test evidence are required",),
            source,
        )

    if evidence.source_reviewed and evidence.test_reviewed:
        return _assessment(
            SecretMaterialBoundaryClassification.MEASURED_NO_SECRET_MATERIAL,
            "source and tests show no secret material path",
            ("measured no-secret evidence does not imply production readiness",),
            source,
        )

    return _assessment(
        SecretMaterialBoundaryClassification.UNAVAILABLE_SECRET_AUDIT,
        "source/test secret material audit evidence is incomplete",
        ("measured source and test evidence are required",),
        source,
    )


def docs_may_claim_secret_safety(
    assessment: SecretMaterialBoundaryAssessment,
) -> bool:
    """Documentation may not claim operational secret safety from this adapter."""

    return False if assessment.violation else assessment.measured


def docs_may_claim_live_readiness_from_secret_evidence(
    assessment: SecretMaterialBoundaryAssessment,
) -> bool:
    """Secret evidence never permits live readiness claims."""

    return assessment.permits_live_readiness_claim


def _has_text(value: str | None) -> bool:
    return bool(value and value.strip())


def _assessment(
    classification: SecretMaterialBoundaryClassification,
    summary: str,
    diagnostics: tuple[str, ...],
    source: str,
) -> SecretMaterialBoundaryAssessment:
    return SecretMaterialBoundaryAssessment(
        classification=classification,
        summary=summary,
        diagnostics=diagnostics,
        source=source,
    )
