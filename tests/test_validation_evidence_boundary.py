from src.reporting.ci_evidence import (
    CiRunEvidence,
    ConnectorCiSnapshot,
    LocalValidationEvidence,
    UserReportedValidationEvidence,
    ValidationEvidenceSource,
    ValidationEvidenceStatus,
    classify_connector_visible_ci_evidence,
    classify_local_validation_evidence,
    classify_user_reported_validation_evidence,
)
from src.reporting.operational_evidence import OperationalEvidenceClassification

MEASURED = OperationalEvidenceClassification.MEASURED
UNAVAILABLE = OperationalEvidenceClassification.UNAVAILABLE


def test_missing_workflow_runs_are_unavailable_not_green_ci() -> None:
    assessment = classify_connector_visible_ci_evidence(
        ConnectorCiSnapshot(
            commit_sha="abc123",
            workflow_runs=(),
            combined_status_state="success",
            status_contexts=("validation",),
            source="GitHub connector lookup for abc123",
        )
    )

    assert assessment.status is ValidationEvidenceStatus.VALIDATION_UNAVAILABLE
    assert assessment.source_classification is ValidationEvidenceSource.UNAVAILABLE
    assert assessment.gate_classification is UNAVAILABLE
    assert assessment.evidence_item.classification is UNAVAILABLE
    assert "workflow runs are unavailable" in assessment.diagnostics[0]


def test_empty_combined_status_is_unavailable_not_validation_success() -> None:
    run = CiRunEvidence(
        commit_sha="abc123",
        workflow_name="validation",
        conclusion="success",
        source="GitHub Actions run 123",
        jobs=(),
        artifacts=(),
    )

    assessment = classify_connector_visible_ci_evidence(
        ConnectorCiSnapshot(
            commit_sha="abc123",
            workflow_runs=(run,),
            combined_status_state="",
            status_contexts=("validation",),
            source="GitHub connector combined status lookup",
        )
    )

    assert assessment.status is ValidationEvidenceStatus.VALIDATION_UNAVAILABLE
    assert assessment.source_classification is ValidationEvidenceSource.UNAVAILABLE
    assert assessment.gate_classification is UNAVAILABLE
    assert any(
        "combined status is unavailable" in item for item in assessment.diagnostics
    )


def test_user_reported_validation_remains_separate_from_measured_evidence() -> None:
    assessment = classify_user_reported_validation_evidence(
        UserReportedValidationEvidence(
            summary="User screenshot says validation run 313 is green",
            source="user-provided screenshot",
        )
    )

    assert assessment.status is ValidationEvidenceStatus.VALIDATION_USER_REPORTED
    assert assessment.source_classification is ValidationEvidenceSource.USER_REPORTED
    assert assessment.gate_classification is UNAVAILABLE
    assert assessment.evidence_item.classification is UNAVAILABLE
    assert "screenshot" in assessment.diagnostics[0]


def test_local_validation_can_be_measured_without_claiming_connector_ci() -> None:
    assessment = classify_local_validation_evidence(
        LocalValidationEvidence(
            command="pytest -q tests/test_validation_evidence_boundary.py",
            exit_code=0,
            output_excerpt="4 passed",
            source="local shell",
        )
    )

    assert assessment.status is ValidationEvidenceStatus.VALIDATION_MEASURED
    assert assessment.source_classification is ValidationEvidenceSource.MEASURED_LOCAL
    assert assessment.gate_classification is MEASURED
