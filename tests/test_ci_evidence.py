import json

from src.reporting.ci_evidence import (
    CiArtifactEvidence,
    CiEvidenceStatus,
    CiJobEvidence,
    CiRunEvidence,
    assess_ci_evidence_for_gate5a,
    ci_evidence_assessment_json,
)
from src.reporting.operational_evidence import (
    OperationalDeploymentStatus,
    OperationalEvidenceClassification,
    OperationalEvidenceItem,
    REQUIRED_OPERATIONAL_BLOCKERS,
    evaluate_operational_evidence_gate,
)


REQUIRED_JOBS = ("validation (3.11)", "validation (3.12)")
REQUIRED_ARTIFACTS = ("junit-3.11.xml", "junit-3.12.xml")


def _successful_ci_run() -> CiRunEvidence:
    return CiRunEvidence(
        commit_sha="abc123",
        workflow_name="validation",
        conclusion="success",
        source="GitHub Actions run 123",
        jobs=(
            CiJobEvidence(name="validation (3.11)", conclusion="success"),
            CiJobEvidence(name="validation (3.12)", conclusion="success"),
        ),
        artifacts=(
            CiArtifactEvidence(name="junit-3.11.xml"),
            CiArtifactEvidence(name="junit-3.12.xml"),
        ),
    )


def test_ci_evidence_is_measured_when_required_jobs_and_artifacts_succeed() -> None:
    assessment = assess_ci_evidence_for_gate5a(
        _successful_ci_run(),
        required_jobs=REQUIRED_JOBS,
        required_artifacts=REQUIRED_ARTIFACTS,
    )

    assert assessment.status is CiEvidenceStatus.CI_MEASURED
    assert assessment.classification is OperationalEvidenceClassification.MEASURED
    assert assessment.evidence_item.blocker_id == "ci_validation"
    assert assessment.evidence_item.classification is OperationalEvidenceClassification.MEASURED
    assert "required jobs and artifacts measured" in assessment.diagnostics[0]


def test_ci_evidence_is_unavailable_when_required_job_fails() -> None:
    run = _successful_ci_run()
    failed_run = CiRunEvidence(
        commit_sha=run.commit_sha,
        workflow_name=run.workflow_name,
        conclusion=run.conclusion,
        source=run.source,
        jobs=(
            CiJobEvidence(name="validation (3.11)", conclusion="failure"),
            run.jobs[1],
        ),
        artifacts=run.artifacts,
    )

    assessment = assess_ci_evidence_for_gate5a(
        failed_run,
        required_jobs=REQUIRED_JOBS,
        required_artifacts=REQUIRED_ARTIFACTS,
    )

    assert assessment.status is CiEvidenceStatus.CI_UNAVAILABLE
    assert assessment.classification is OperationalEvidenceClassification.UNAVAILABLE
    assert "validation (3.11)" in assessment.diagnostics[0]
    assert assessment.evidence_item.source == "GitHub Actions run 123"


def test_ci_evidence_is_unavailable_when_required_artifact_is_missing() -> None:
    run = _successful_ci_run()
    missing_artifact_run = CiRunEvidence(
        commit_sha=run.commit_sha,
        workflow_name=run.workflow_name,
        conclusion=run.conclusion,
        source=run.source,
        jobs=run.jobs,
        artifacts=(CiArtifactEvidence(name="junit-3.11.xml"),),
    )

    assessment = assess_ci_evidence_for_gate5a(
        missing_artifact_run,
        required_jobs=REQUIRED_JOBS,
        required_artifacts=REQUIRED_ARTIFACTS,
    )

    assert assessment.status is CiEvidenceStatus.CI_UNAVAILABLE
    assert assessment.evidence_item.classification is OperationalEvidenceClassification.UNAVAILABLE
    assert "required CI artifact 'junit-3.12.xml' is missing" in assessment.diagnostics


def test_ci_evidence_is_unavailable_for_malformed_required_payloads() -> None:
    assessment = assess_ci_evidence_for_gate5a(
        _successful_ci_run(),
        required_jobs=(" validation (3.11) ", "validation (3.11)"),
        required_artifacts=(),
    )

    assert assessment.status is CiEvidenceStatus.CI_UNAVAILABLE
    assert any("non-canonical" in diagnostic for diagnostic in assessment.diagnostics)
    assert any("duplicated" in diagnostic for diagnostic in assessment.diagnostics)
    assert any("artifact list is empty" in diagnostic for diagnostic in assessment.diagnostics)


def test_ci_evidence_item_can_feed_gate5a_ci_validation_row() -> None:
    ci_assessment = assess_ci_evidence_for_gate5a(
        _successful_ci_run(),
        required_jobs=REQUIRED_JOBS,
        required_artifacts=REQUIRED_ARTIFACTS,
    )
    evidence_items = tuple(
        ci_assessment.evidence_item
        if blocker_id == "ci_validation"
        else OperationalEvidenceItem(
            blocker_id=blocker_id,
            classification=OperationalEvidenceClassification.MEASURED,
            summary=f"measured evidence for {blocker_id}",
            source="test fixture",
        )
        for blocker_id in REQUIRED_OPERATIONAL_BLOCKERS
    )

    result = evaluate_operational_evidence_gate(evidence_items)

    assert result.status is OperationalDeploymentStatus.DEPLOYMENT_NOT_BLOCKED
    assert result.paper_deployment_blocked is False


def test_ci_evidence_json_is_deterministic_and_contains_no_performance_metrics() -> None:
    assessment = assess_ci_evidence_for_gate5a(
        _successful_ci_run(),
        required_jobs=REQUIRED_JOBS,
        required_artifacts=REQUIRED_ARTIFACTS,
    )
    payload = json.loads(ci_evidence_assessment_json(assessment))

    assert list(payload) == [
        "classification",
        "diagnostics",
        "evidence_item",
        "status",
    ]
    forbidden = {"pnl", "profit", "returns", "sharpe", "drawdown", "win_rate"}
    payload_keys = set(payload) | set(payload["evidence_item"])

    assert forbidden.isdisjoint(payload_keys)
