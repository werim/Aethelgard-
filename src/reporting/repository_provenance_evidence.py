"""Gate 5A-10 repository provenance evidence adapter.

This module classifies caller-supplied repository provenance evidence for PR,
branch-head, merge, and ancestry claims. It is deliberately offline and
deterministic: it does not call GitHub, refresh branches, mutate workflows,
change runtime behavior, submit orders, or approve readiness. Missing remote
or compare evidence remains explicitly unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RepositoryProvenanceClassification(StrEnum):
    """Fail-closed repository provenance classifications."""

    USER_REPORTED_PR = "USER_REPORTED_PR"
    USER_REPORTED_COMMIT = "USER_REPORTED_COMMIT"
    MEASURED_PR_VISIBLE = "MEASURED_PR_VISIBLE"
    MEASURED_BRANCH_HEAD = "MEASURED_BRANCH_HEAD"
    MEASURED_BRANCH_CONTAINS = "MEASURED_BRANCH_CONTAINS"
    MEASURED_MERGED_TO_BRANCH = "MEASURED_MERGED_TO_BRANCH"
    UNAVAILABLE_PR_VISIBILITY = "UNAVAILABLE_PR_VISIBILITY"
    UNAVAILABLE_BRANCH_REFRESH = "UNAVAILABLE_BRANCH_REFRESH"
    UNAVAILABLE_MERGE_EVIDENCE = "UNAVAILABLE_MERGE_EVIDENCE"


@dataclass(frozen=True)
class RepositoryProvenanceAssessment:
    """Deterministic assessment for one repository provenance claim."""

    classification: RepositoryProvenanceClassification
    summary: str
    diagnostics: tuple[str, ...]
    source: str

    @property
    def measured(self) -> bool:
        """Return whether this assessment is measured repository evidence."""

        return self.classification in {
            RepositoryProvenanceClassification.MEASURED_PR_VISIBLE,
            RepositoryProvenanceClassification.MEASURED_BRANCH_HEAD,
            RepositoryProvenanceClassification.MEASURED_BRANCH_CONTAINS,
            RepositoryProvenanceClassification.MEASURED_MERGED_TO_BRANCH,
        }

    @property
    def permits_merged_to_branch_claim(self) -> bool:
        """Return whether docs may claim the commit was merged to the branch."""

        return (
            self.classification
            is RepositoryProvenanceClassification.MEASURED_MERGED_TO_BRANCH
        )

    def payload(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible payload."""

        return {
            "classification": self.classification.value,
            "diagnostics": list(self.diagnostics),
            "measured": self.measured,
            "permits_merged_to_branch_claim": self.permits_merged_to_branch_claim,
            "source": self.source,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class UserReportedPullRequestEvidence:
    """User-supplied PR statement or screenshot reference."""

    pr_reference: str
    summary: str
    source: str


@dataclass(frozen=True)
class PullRequestVisibilityEvidence:
    """Measured PR lookup evidence from a connector or API response."""

    pr_reference: str
    visible: bool
    target_branch: str
    source: str


@dataclass(frozen=True)
class BranchHeadEvidence:
    """Measured branch refresh/head evidence from a connector or local remote."""

    branch: str
    commit_sha: str
    refreshed: bool
    source: str


@dataclass(frozen=True)
class CommitAncestryEvidence:
    """Measured compare/ancestry evidence for a commit and target branch."""

    commit_sha: str
    target_branch: str
    branch_contains_commit: bool | None
    merged_to_target_branch: bool | None
    source: str


@dataclass(frozen=True)
class UserReportedCommitEvidence:
    """User-supplied commit statement that is not branch containment evidence."""

    commit_sha: str
    summary: str
    source: str


def classify_user_reported_pr_evidence(
    evidence: UserReportedPullRequestEvidence,
) -> RepositoryProvenanceAssessment:
    """Keep user-reported PR evidence separate from connector-visible PRs."""

    pr_reference = evidence.pr_reference.strip() or "unknown PR"
    diagnostic = (
        evidence.summary.strip() or "user-reported PR evidence has an empty summary"
    )
    return _assessment(
        RepositoryProvenanceClassification.USER_REPORTED_PR,
        summary=f"user-reported PR remains unmeasured: {pr_reference}",
        diagnostics=(diagnostic,),
        source=evidence.source,
    )


def classify_pr_visibility_evidence(
    evidence: PullRequestVisibilityEvidence,
) -> RepositoryProvenanceAssessment:
    """Classify measured PR visibility, failing closed when lookup is missing."""

    diagnostics: list[str] = []
    if not evidence.pr_reference.strip():
        diagnostics.append("PR reference is missing")
    if not evidence.target_branch.strip():
        diagnostics.append("PR target branch is missing")
    if not evidence.source.strip():
        diagnostics.append("PR visibility source is missing")
    if not evidence.visible:
        diagnostics.append("PR lookup is unavailable or did not return a visible PR")

    if diagnostics:
        return _assessment(
            RepositoryProvenanceClassification.UNAVAILABLE_PR_VISIBILITY,
            summary="PR visibility evidence is unavailable",
            diagnostics=tuple(diagnostics),
            source=evidence.source,
        )

    return _assessment(
        RepositoryProvenanceClassification.MEASURED_PR_VISIBLE,
        summary=(
            f"PR {evidence.pr_reference} is connector-visible for "
            f"{evidence.target_branch}"
        ),
        diagnostics=("PR visibility was measured directly",),
        source=evidence.source,
    )


def classify_branch_head_evidence(
    evidence: BranchHeadEvidence,
) -> RepositoryProvenanceAssessment:
    """Classify branch-head refresh evidence without assuming stale data."""

    diagnostics: list[str] = []
    if not evidence.branch.strip():
        diagnostics.append("branch name is missing")
    if not evidence.commit_sha.strip():
        diagnostics.append("branch head commit SHA is missing")
    if not evidence.source.strip():
        diagnostics.append("branch refresh source is missing")
    if not evidence.refreshed:
        diagnostics.append("branch refresh evidence is unavailable")

    if diagnostics:
        return _assessment(
            RepositoryProvenanceClassification.UNAVAILABLE_BRANCH_REFRESH,
            summary="branch-head evidence is unavailable",
            diagnostics=tuple(diagnostics),
            source=evidence.source,
        )

    return _assessment(
        RepositoryProvenanceClassification.MEASURED_BRANCH_HEAD,
        summary=f"branch {evidence.branch} head measured at {evidence.commit_sha}",
        diagnostics=("branch head was measured after refresh",),
        source=evidence.source,
    )


def classify_user_reported_commit_evidence(
    evidence: UserReportedCommitEvidence,
) -> RepositoryProvenanceAssessment:
    """Classify a user-reported commit without promoting it to dev evidence."""

    commit_sha = evidence.commit_sha.strip() or "unknown commit"
    diagnostic = (
        evidence.summary.strip() or "user-reported commit evidence has an empty summary"
    )
    return _assessment(
        RepositoryProvenanceClassification.USER_REPORTED_COMMIT,
        summary=f"user-reported commit remains unmeasured: {commit_sha}",
        diagnostics=(diagnostic,),
        source=evidence.source,
    )


def classify_commit_ancestry_evidence(
    evidence: CommitAncestryEvidence,
) -> RepositoryProvenanceAssessment:
    """Classify branch containment/merge evidence from measured compare data."""

    diagnostics: list[str] = []
    if not evidence.commit_sha.strip():
        diagnostics.append("commit SHA is missing")
    if not evidence.target_branch.strip():
        diagnostics.append("target branch is missing")
    if not evidence.source.strip():
        diagnostics.append("compare/ancestry source is missing")
    if evidence.branch_contains_commit is None:
        diagnostics.append("branch containment compare evidence is unavailable")
    if evidence.merged_to_target_branch is None:
        diagnostics.append("merge evidence is unavailable")

    if diagnostics:
        return _assessment(
            RepositoryProvenanceClassification.UNAVAILABLE_MERGE_EVIDENCE,
            summary="commit ancestry evidence is unavailable",
            diagnostics=tuple(diagnostics),
            source=evidence.source,
        )

    if evidence.branch_contains_commit is False:
        return _assessment(
            RepositoryProvenanceClassification.UNAVAILABLE_MERGE_EVIDENCE,
            summary="target branch containment was not measured as true",
            diagnostics=(
                f"{evidence.target_branch} does not contain {evidence.commit_sha}",
            ),
            source=evidence.source,
        )

    if evidence.merged_to_target_branch is False:
        return _assessment(
            RepositoryProvenanceClassification.MEASURED_BRANCH_CONTAINS,
            summary=(
                f"{evidence.target_branch} contains {evidence.commit_sha}; "
                "merge evidence is not measured as true"
            ),
            diagnostics=("branch containment is measured but merge is not proven",),
            source=evidence.source,
        )

    return _assessment(
        RepositoryProvenanceClassification.MEASURED_MERGED_TO_BRANCH,
        summary=f"{evidence.commit_sha} is measured merged to {evidence.target_branch}",
        diagnostics=("branch containment and merge evidence are measured",),
        source=evidence.source,
    )


def docs_may_claim_merged_to_branch(
    assessment: RepositoryProvenanceAssessment,
) -> bool:
    """Allow merged-to-branch documentation only on measured merge evidence."""

    return assessment.permits_merged_to_branch_claim


def _assessment(
    classification: RepositoryProvenanceClassification,
    *,
    summary: str,
    diagnostics: tuple[str, ...],
    source: str,
) -> RepositoryProvenanceAssessment:
    safe_source = source.strip() or "UNAVAILABLE: missing repository provenance source"
    return RepositoryProvenanceAssessment(
        classification=classification,
        summary=summary,
        diagnostics=diagnostics,
        source=safe_source,
    )
