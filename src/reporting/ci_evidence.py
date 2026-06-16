"""Gate 5A-2 CI evidence adapter.

This module converts caller-supplied CI/status payloads into Gate 5A
`ci_validation` evidence. It is deliberately offline and deterministic: it does
not call GitHub, mutate workflows, compute performance, submit orders, or approve
readiness. Missing or malformed CI evidence remains UNAVAILABLE.
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


class CiEvidenceStatus(StrEnum):
    """CI evidence adapter status values."""

    CI_MEASURED = "CI_MEASURED"
    CI_UNAVAILABLE = "CI_UNAVAILABLE"


class ValidationEvidenceSource(StrEnum):
    """Fail-closed validation evidence source classifications."""

    MEASURED_LOCAL = "MEASURED_LOCAL"
    USER_REPORTED = "USER_REPORTED"
    CONNECTOR_VISIBLE_CI = "CONNECTOR_VISIBLE_CI"
    UNAVAILABLE = "UNAVAILABLE"


class ValidationEvidenceStatus(StrEnum):
    """Validation boundary adapter status values."""

    VALIDATION_MEASURED = "VALIDATION_MEASURED"
    VALIDATION_USER_REPORTED = "VALIDATION_USER_REPORTED"
    VALIDATION_UNAVAILABLE = "VALIDATION_UNAVAILABLE"


@dataclass(frozen=True)
class ConnectorCiSnapshot:
    """Connector-visible CI evidence snapshot for a branch-head commit."""

    commit_sha: str
    workflow_runs: tuple[CiRunEvidence, ...] = ()
    combined_status_state: str | None = None
    status_contexts: tuple[str, ...] = ()
    source: str = ""


@dataclass(frozen=True)
class UserReportedValidationEvidence:
    """User-supplied validation statement or screenshot reference."""

    summary: str
    source: str


@dataclass(frozen=True)
class LocalValidationEvidence:
    """Locally observed validation command evidence."""

    command: str
    exit_code: int
    output_excerpt: str
    source: str


@dataclass(frozen=True)
class ValidationEvidenceBoundaryAssessment:
    """Fail-closed classification for validation evidence provenance."""

    status: ValidationEvidenceStatus
    source_classification: ValidationEvidenceSource
    gate_classification: OperationalEvidenceClassification
    diagnostics: tuple[str, ...]
    evidence_item: OperationalEvidenceItem

    def payload(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible assessment payload."""

        return {
            "diagnostics": list(self.diagnostics),
            "evidence_item": self.evidence_item.payload(),
            "gate_classification": self.gate_classification.value,
            "source_classification": self.source_classification.value,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class CiJobEvidence:
    """Caller-supplied evidence for one required CI job."""

    name: str
    conclusion: str

    def payload(self) -> dict[str, str]:
        """Return a deterministic JSON-compatible job payload."""

        return {"conclusion": self.conclusion, "name": self.name}


@dataclass(frozen=True)
class CiArtifactEvidence:
    """Caller-supplied evidence for one required CI artifact."""

    name: str

    def payload(self) -> dict[str, str]:
        """Return a deterministic JSON-compatible artifact payload."""

        return {"name": self.name}


@dataclass(frozen=True)
class CiRunEvidence:
    """Caller-supplied CI run evidence for one commit/workflow pair."""

    commit_sha: str
    workflow_name: str
    conclusion: str
    source: str
    jobs: tuple[CiJobEvidence, ...]
    artifacts: tuple[CiArtifactEvidence, ...]

    def payload(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible CI run payload."""

        return {
            "artifacts": [artifact.payload() for artifact in self.artifacts],
            "commit_sha": self.commit_sha,
            "conclusion": self.conclusion,
            "jobs": [job.payload() for job in self.jobs],
            "source": self.source,
            "workflow_name": self.workflow_name,
        }


@dataclass(frozen=True)
class CiEvidenceAssessment:
    """Fail-closed CI evidence assessment for Gate 5A `ci_validation`."""

    status: CiEvidenceStatus
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


def assess_ci_evidence_for_gate5a(
    run: CiRunEvidence,
    *,
    required_jobs: Sequence[str],
    required_artifacts: Sequence[str],
) -> CiEvidenceAssessment:
    """Classify CI evidence for Gate 5A and fail closed on any gap."""

    diagnostics = _ci_evidence_diagnostics(run, required_jobs, required_artifacts)
    if diagnostics:
        return _build_assessment(
            status=CiEvidenceStatus.CI_UNAVAILABLE,
            classification=OperationalEvidenceClassification.UNAVAILABLE,
            diagnostics=diagnostics,
            source=run.source,
        )

    summary = (
        f"CI workflow {run.workflow_name} succeeded for commit {run.commit_sha} "
        "with required jobs and artifacts measured"
    )
    return CiEvidenceAssessment(
        status=CiEvidenceStatus.CI_MEASURED,
        classification=OperationalEvidenceClassification.MEASURED,
        diagnostics=(summary,),
        evidence_item=OperationalEvidenceItem(
            blocker_id="ci_validation",
            classification=OperationalEvidenceClassification.MEASURED,
            summary=summary,
            source=run.source,
        ),
    )


def classify_connector_visible_ci_evidence(
    snapshot: ConnectorCiSnapshot,
) -> ValidationEvidenceBoundaryAssessment:
    """Classify connector-visible CI evidence without promoting empty payloads."""

    diagnostics: list[str] = []
    if not snapshot.commit_sha.strip():
        diagnostics.append("connector-visible CI commit_sha is missing")
    if not snapshot.source.strip():
        diagnostics.append("connector-visible CI source is missing")
    if not snapshot.workflow_runs:
        diagnostics.append("connector-visible CI workflow runs are unavailable")
    combined_status = snapshot.combined_status_state
    if combined_status is None or not combined_status.strip():
        diagnostics.append("connector-visible CI combined status is unavailable")
    elif combined_status != "success":
        diagnostics.append(
            "connector-visible CI combined status state is "
            f"{combined_status!r}, not 'success'"
        )
    if not snapshot.status_contexts:
        diagnostics.append("connector-visible CI status contexts are unavailable")

    failed_runs = tuple(
        run
        for run in snapshot.workflow_runs
        if run.commit_sha != snapshot.commit_sha or run.conclusion != "success"
    )
    for run in failed_runs:
        if run.commit_sha != snapshot.commit_sha:
            diagnostics.append(
                f"workflow {run.workflow_name!r} targets {run.commit_sha!r}, "
                f"not {snapshot.commit_sha!r}"
            )
        if run.conclusion != "success":
            diagnostics.append(
                f"workflow {run.workflow_name!r} conclusion is {run.conclusion!r}, "
                "not 'success'"
            )

    if diagnostics:
        return _build_validation_boundary_assessment(
            status=ValidationEvidenceStatus.VALIDATION_UNAVAILABLE,
            source_classification=ValidationEvidenceSource.UNAVAILABLE,
            gate_classification=OperationalEvidenceClassification.UNAVAILABLE,
            diagnostics=tuple(diagnostics),
            source=snapshot.source,
        )

    summary = f"connector-visible CI succeeded for commit {snapshot.commit_sha}"
    return _build_validation_boundary_assessment(
        status=ValidationEvidenceStatus.VALIDATION_MEASURED,
        source_classification=ValidationEvidenceSource.CONNECTOR_VISIBLE_CI,
        gate_classification=OperationalEvidenceClassification.MEASURED,
        diagnostics=(summary,),
        source=snapshot.source,
    )


def classify_user_reported_validation_evidence(
    evidence: UserReportedValidationEvidence,
) -> ValidationEvidenceBoundaryAssessment:
    """Keep screenshots and user statements separate from measured validation."""

    diagnostics = (
        evidence.summary.strip()
        or "user-reported validation evidence has an empty summary",
    )
    return _build_validation_boundary_assessment(
        status=ValidationEvidenceStatus.VALIDATION_USER_REPORTED,
        source_classification=ValidationEvidenceSource.USER_REPORTED,
        gate_classification=OperationalEvidenceClassification.UNAVAILABLE,
        diagnostics=diagnostics,
        source=evidence.source,
    )


def classify_local_validation_evidence(
    evidence: LocalValidationEvidence,
) -> ValidationEvidenceBoundaryAssessment:
    """Classify locally measured command evidence, failing closed on gaps."""

    diagnostics: list[str] = []
    if not evidence.command.strip():
        diagnostics.append("local validation command is missing")
    if evidence.exit_code != 0:
        diagnostics.append(f"local validation exit code is {evidence.exit_code}, not 0")
    if not evidence.output_excerpt.strip():
        diagnostics.append("local validation output excerpt is missing")
    if not evidence.source.strip():
        diagnostics.append("local validation source is missing")
    if diagnostics:
        return _build_validation_boundary_assessment(
            status=ValidationEvidenceStatus.VALIDATION_UNAVAILABLE,
            source_classification=ValidationEvidenceSource.UNAVAILABLE,
            gate_classification=OperationalEvidenceClassification.UNAVAILABLE,
            diagnostics=tuple(diagnostics),
            source=evidence.source,
        )

    summary = f"local validation command measured: {evidence.command}"
    return _build_validation_boundary_assessment(
        status=ValidationEvidenceStatus.VALIDATION_MEASURED,
        source_classification=ValidationEvidenceSource.MEASURED_LOCAL,
        gate_classification=OperationalEvidenceClassification.MEASURED,
        diagnostics=(summary,),
        source=evidence.source,
    )


def _build_validation_boundary_assessment(
    *,
    status: ValidationEvidenceStatus,
    source_classification: ValidationEvidenceSource,
    gate_classification: OperationalEvidenceClassification,
    diagnostics: tuple[str, ...],
    source: str,
) -> ValidationEvidenceBoundaryAssessment:
    safe_source = source.strip() or "UNAVAILABLE: missing validation evidence source"
    summary = (
        "; ".join(diagnostics) if diagnostics else "validation evidence unavailable"
    )
    return ValidationEvidenceBoundaryAssessment(
        status=status,
        source_classification=source_classification,
        gate_classification=gate_classification,
        diagnostics=diagnostics,
        evidence_item=OperationalEvidenceItem(
            blocker_id="ci_validation",
            classification=gate_classification,
            summary=summary,
            source=safe_source,
        ),
    )


def ci_evidence_assessment_json(assessment: CiEvidenceAssessment) -> str:
    """Serialize a CI evidence assessment deterministically."""

    return json.dumps(assessment.payload(), sort_keys=True, separators=(",", ":"))


def _build_assessment(
    *,
    status: CiEvidenceStatus,
    classification: OperationalEvidenceClassification,
    diagnostics: tuple[str, ...],
    source: str,
) -> CiEvidenceAssessment:
    safe_source = source.strip() or "UNAVAILABLE: missing CI evidence source"
    summary = "; ".join(diagnostics) if diagnostics else "CI evidence unavailable"
    return CiEvidenceAssessment(
        status=status,
        classification=classification,
        diagnostics=diagnostics,
        evidence_item=OperationalEvidenceItem(
            blocker_id="ci_validation",
            classification=classification,
            summary=summary,
            source=safe_source,
        ),
    )


def _ci_evidence_diagnostics(
    run: CiRunEvidence,
    required_jobs: Sequence[str],
    required_artifacts: Sequence[str],
) -> tuple[str, ...]:
    diagnostics: list[str] = []

    if not run.commit_sha.strip():
        diagnostics.append("CI evidence commit_sha is missing")
    if not run.workflow_name.strip():
        diagnostics.append("CI evidence workflow_name is missing")
    if run.conclusion != "success":
        diagnostics.append(
            f"CI workflow conclusion is {run.conclusion!r}, not 'success'"
        )
    if not run.source.strip():
        diagnostics.append("CI evidence source is missing")

    required_job_names = _canonical_required_names(required_jobs, "job", diagnostics)
    required_artifact_names = _canonical_required_names(
        required_artifacts, "artifact", diagnostics
    )
    job_by_name = _unique_job_conclusions(run.jobs, diagnostics)
    artifact_names = _unique_artifact_names(run.artifacts, diagnostics)

    for job_name in required_job_names:
        conclusion = job_by_name.get(job_name)
        if conclusion is None:
            diagnostics.append(f"required CI job {job_name!r} is missing")
        elif conclusion != "success":
            diagnostics.append(
                f"required CI job {job_name!r} conclusion is {conclusion!r}, "
                "not 'success'"
            )

    for artifact_name in required_artifact_names:
        if artifact_name not in artifact_names:
            diagnostics.append(f"required CI artifact {artifact_name!r} is missing")

    return tuple(diagnostics)


def _canonical_required_names(
    names: Sequence[str],
    label: str,
    diagnostics: list[str],
) -> tuple[str, ...]:
    canonical_names: list[str] = []
    seen: set[str] = set()
    if not names:
        diagnostics.append(f"required CI {label} list is empty")
    for name in names:
        canonical_name = name.strip()
        if not canonical_name:
            diagnostics.append(f"required CI {label} name is empty")
            continue
        if canonical_name != name:
            diagnostics.append(f"required CI {label} name {name!r} is non-canonical")
        if canonical_name in seen:
            diagnostics.append(f"required CI {label} {canonical_name!r} is duplicated")
        seen.add(canonical_name)
        canonical_names.append(canonical_name)
    return tuple(canonical_names)


def _unique_job_conclusions(
    jobs: Sequence[CiJobEvidence],
    diagnostics: list[str],
) -> dict[str, str]:
    job_by_name: dict[str, str] = {}
    for job in jobs:
        job_name = job.name.strip()
        if not job_name:
            diagnostics.append("CI job name is empty")
            continue
        if job_name != job.name:
            diagnostics.append(f"CI job name {job.name!r} is non-canonical")
        if job_name in job_by_name:
            diagnostics.append(f"CI job {job_name!r} is duplicated")
        job_by_name[job_name] = job.conclusion
    return job_by_name


def _unique_artifact_names(
    artifacts: Sequence[CiArtifactEvidence],
    diagnostics: list[str],
) -> set[str]:
    artifact_names: set[str] = set()
    for artifact in artifacts:
        artifact_name = artifact.name.strip()
        if not artifact_name:
            diagnostics.append("CI artifact name is empty")
            continue
        if artifact_name != artifact.name:
            diagnostics.append(f"CI artifact name {artifact.name!r} is non-canonical")
        if artifact_name in artifact_names:
            diagnostics.append(f"CI artifact {artifact_name!r} is duplicated")
        artifact_names.add(artifact_name)
    return artifact_names
