from src.reporting.exchange_mutation_boundary_evidence import (
    ExchangeMutationBoundaryClassification,
    ExchangeMutationBoundaryEvidence,
    classify_exchange_mutation_boundary_evidence,
    docs_may_claim_production_ready,
)


def test_paper_only_evidence_does_not_imply_live_readiness() -> None:
    assessment = classify_exchange_mutation_boundary_evidence(
        ExchangeMutationBoundaryEvidence(
            source="source and test audit",
            exchange_audit_source="rg exchange mutation audit",
            runtime_proof_source="pytest safety guards",
            source_reviewed=True,
            test_reviewed=True,
            runtime_proof_observed=True,
            mutation_surface_present=True,
            hard_paper_only_guard_present=True,
        )
    )

    assert (
        assessment.classification
        is ExchangeMutationBoundaryClassification.MEASURED_PAPER_ONLY_GUARD
    )
    assert assessment.measured
    assert not assessment.permits_live_readiness_claim
    assert not docs_may_claim_production_ready(assessment)


def test_missing_exchange_audit_evidence_remains_unavailable() -> None:
    assessment = classify_exchange_mutation_boundary_evidence(
        ExchangeMutationBoundaryEvidence(
            source="runtime proof only",
            runtime_proof_source="pytest",
            runtime_proof_observed=True,
        )
    )

    assert (
        assessment.classification
        is ExchangeMutationBoundaryClassification.UNAVAILABLE_EXCHANGE_AUDIT
    )
    assert not assessment.measured


def test_user_reported_no_live_use_is_not_measured_proof() -> None:
    assessment = classify_exchange_mutation_boundary_evidence(
        ExchangeMutationBoundaryEvidence(
            source="user statement",
            user_reported_no_live_use=True,
        )
    )

    assert (
        assessment.classification
        is ExchangeMutationBoundaryClassification.USER_REPORTED_NO_LIVE_USE
    )
    assert not assessment.measured


def test_unguarded_exchange_mutation_surfaces_classify_as_violations() -> None:
    assessment = classify_exchange_mutation_boundary_evidence(
        ExchangeMutationBoundaryEvidence(
            source="source audit found order submission",
            exchange_audit_source="rg order surface",
            runtime_proof_source="pytest missing guard",
            runtime_proof_observed=True,
            source_reviewed=True,
            test_reviewed=True,
            mutation_surface_present=True,
            real_order_capability_present=True,
            hard_paper_only_guard_present=False,
        )
    )

    assert (
        assessment.classification
        is ExchangeMutationBoundaryClassification.VIOLATION_EXCHANGE_MUTATION_ALLOWED
    )
    assert assessment.violation


def test_guarded_paper_only_classifies_measured_only_with_source_and_tests() -> None:
    missing_tests = classify_exchange_mutation_boundary_evidence(
        ExchangeMutationBoundaryEvidence(
            source="source only",
            exchange_audit_source="source audit",
            runtime_proof_source="runtime proof",
            runtime_proof_observed=True,
            source_reviewed=True,
            test_reviewed=False,
            mutation_surface_present=True,
            hard_paper_only_guard_present=True,
        )
    )
    measured = classify_exchange_mutation_boundary_evidence(
        ExchangeMutationBoundaryEvidence(
            source="source and test audit",
            exchange_audit_source="source audit",
            runtime_proof_source="runtime proof",
            runtime_proof_observed=True,
            source_reviewed=True,
            test_reviewed=True,
            mutation_surface_present=True,
            hard_paper_only_guard_present=True,
        )
    )

    assert (
        missing_tests.classification
        is ExchangeMutationBoundaryClassification.VIOLATION_EXCHANGE_MUTATION_ALLOWED
    )
    assert (
        measured.classification
        is ExchangeMutationBoundaryClassification.MEASURED_PAPER_ONLY_GUARD
    )


def test_docs_cannot_claim_production_readiness() -> None:
    assessment = classify_exchange_mutation_boundary_evidence(
        ExchangeMutationBoundaryEvidence(
            source="documentation audit",
            docs_claim_production_ready=True,
        )
    )

    assert (
        assessment.classification
        is ExchangeMutationBoundaryClassification.VIOLATION_EXCHANGE_MUTATION_ALLOWED
    )
    assert not docs_may_claim_production_ready(assessment)
