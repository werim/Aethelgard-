from src.reporting.secret_material_boundary_evidence import (
    SecretMaterialBoundaryClassification,
    SecretMaterialBoundaryEvidence,
    classify_secret_material_boundary_evidence,
    docs_may_claim_live_readiness_from_secret_evidence,
    docs_may_claim_secret_safety,
)


def test_secret_placeholder_evidence_does_not_imply_live_readiness() -> None:
    assessment = classify_secret_material_boundary_evidence(
        SecretMaterialBoundaryEvidence(
            source="source test audit",
            secret_audit_source="rg secret material audit",
            runtime_proof_source="pytest secret guard",
            source_reviewed=True,
            test_reviewed=True,
            runtime_proof_observed=True,
            secret_material_present=True,
            placeholder_or_env_reference_only=True,
        )
    )

    assert (
        assessment.classification
        is SecretMaterialBoundaryClassification.MEASURED_SECRET_PLACEHOLDER_ONLY
    )
    assert assessment.measured
    assert docs_may_claim_secret_safety(assessment)
    assert not docs_may_claim_live_readiness_from_secret_evidence(assessment)


def test_missing_secret_audit_evidence_remains_unavailable() -> None:
    assessment = classify_secret_material_boundary_evidence(
        SecretMaterialBoundaryEvidence(
            source="runtime proof only",
            runtime_proof_source="pytest",
            runtime_proof_observed=True,
        )
    )

    assert (
        assessment.classification
        is SecretMaterialBoundaryClassification.UNAVAILABLE_SECRET_AUDIT
    )
    assert not assessment.measured


def test_user_reported_secrets_not_shared_is_not_measured_proof() -> None:
    assessment = classify_secret_material_boundary_evidence(
        SecretMaterialBoundaryEvidence(
            source="user statement",
            user_reported_secrets_not_shared=True,
        )
    )

    assert (
        assessment.classification
        is SecretMaterialBoundaryClassification.USER_REPORTED_SECRETS_NOT_SHARED
    )
    assert not assessment.measured


def test_exposed_or_requested_secret_material_classifies_as_violation() -> None:
    exposed = classify_secret_material_boundary_evidence(
        SecretMaterialBoundaryEvidence(
            source="repository audit found credential",
            secret_audit_source="rg credential surface",
            source_reviewed=True,
            test_reviewed=True,
            committed_secret_material_present=True,
        )
    )
    requested = classify_secret_material_boundary_evidence(
        SecretMaterialBoundaryEvidence(
            source="prompt audit found secret request",
            secret_request_present=True,
        )
    )

    assert (
        exposed.classification
        is SecretMaterialBoundaryClassification.VIOLATION_SECRET_MATERIAL_EXPOSED
    )
    assert exposed.violation
    assert (
        requested.classification
        is SecretMaterialBoundaryClassification.VIOLATION_SECRET_MATERIAL_EXPOSED
    )
    assert requested.violation


def test_placeholder_secret_evidence_requires_runtime_proof() -> None:
    missing_runtime = classify_secret_material_boundary_evidence(
        SecretMaterialBoundaryEvidence(
            source="source and test audit",
            secret_audit_source="source audit",
            source_reviewed=True,
            test_reviewed=True,
            secret_material_present=True,
            placeholder_or_env_reference_only=True,
        )
    )
    measured = classify_secret_material_boundary_evidence(
        SecretMaterialBoundaryEvidence(
            source="source and test audit",
            secret_audit_source="source audit",
            runtime_proof_source="runtime proof",
            source_reviewed=True,
            test_reviewed=True,
            runtime_proof_observed=True,
            secret_material_present=True,
            placeholder_or_env_reference_only=True,
        )
    )

    assert (
        missing_runtime.classification
        is SecretMaterialBoundaryClassification.UNAVAILABLE_RUNTIME_SECRET_PROOF
    )
    assert (
        measured.classification
        is SecretMaterialBoundaryClassification.MEASURED_SECRET_PLACEHOLDER_ONLY
    )


def test_docs_cannot_claim_secret_safety_without_measured_audit() -> None:
    assessment = classify_secret_material_boundary_evidence(
        SecretMaterialBoundaryEvidence(
            source="documentation audit",
            docs_claim_secret_safety=True,
        )
    )

    assert (
        assessment.classification
        is SecretMaterialBoundaryClassification.UNAVAILABLE_SECRET_AUDIT
    )
    assert not docs_may_claim_secret_safety(assessment)
