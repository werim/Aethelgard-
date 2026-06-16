from src.reporting.repository_provenance_evidence import (
    BranchHeadEvidence,
    CommitAncestryEvidence,
    PullRequestVisibilityEvidence,
    RepositoryProvenanceClassification,
    UserReportedCommitEvidence,
    UserReportedPullRequestEvidence,
    classify_branch_head_evidence,
    classify_commit_ancestry_evidence,
    classify_pr_visibility_evidence,
    classify_user_reported_commit_evidence,
    classify_user_reported_pr_evidence,
    docs_may_claim_merged_to_branch,
)


def test_user_reported_pr_is_not_measured_pr_visible() -> None:
    assessment = classify_user_reported_pr_evidence(
        UserReportedPullRequestEvidence(
            pr_reference="#21",
            summary="User says PR #21 was created",
            source="user task prompt",
        )
    )

    assert (
        assessment.classification is RepositoryProvenanceClassification.USER_REPORTED_PR
    )
    assert assessment.payload()["classification"] != "MEASURED_PR_VISIBLE"
    assert not assessment.measured


def test_missing_pr_lookup_is_unavailable_pr_visibility() -> None:
    assessment = classify_pr_visibility_evidence(
        PullRequestVisibilityEvidence(
            pr_reference="#22",
            visible=False,
            target_branch="dev",
            source="GitHub connector PR lookup returned no visible PR",
        )
    )

    assert (
        assessment.classification
        is RepositoryProvenanceClassification.UNAVAILABLE_PR_VISIBILITY
    )
    assert not assessment.measured
    assert any("PR lookup is unavailable" in item for item in assessment.diagnostics)


def test_commit_sha_alone_is_not_merge_evidence() -> None:
    user_commit = classify_user_reported_commit_evidence(
        UserReportedCommitEvidence(
            commit_sha="7f5e6c5440d82321546abd6e4b6ab0cf1b232598",
            summary="User reports commit exists",
            source="user statement",
        )
    )
    ancestry = classify_commit_ancestry_evidence(
        CommitAncestryEvidence(
            commit_sha="7f5e6c5440d82321546abd6e4b6ab0cf1b232598",
            target_branch="dev",
            branch_contains_commit=None,
            merged_to_target_branch=None,
            source="commit SHA only; no compare evidence",
        )
    )

    assert (
        user_commit.classification
        is RepositoryProvenanceClassification.USER_REPORTED_COMMIT
    )
    assert (
        ancestry.classification
        is RepositoryProvenanceClassification.UNAVAILABLE_MERGE_EVIDENCE
    )
    assert not docs_may_claim_merged_to_branch(user_commit)
    assert not docs_may_claim_merged_to_branch(ancestry)


def test_dev_branch_containment_requires_measured_compare_evidence() -> None:
    unavailable = classify_commit_ancestry_evidence(
        CommitAncestryEvidence(
            commit_sha="abc123",
            target_branch="dev",
            branch_contains_commit=None,
            merged_to_target_branch=True,
            source="missing compare response",
        )
    )
    contained = classify_commit_ancestry_evidence(
        CommitAncestryEvidence(
            commit_sha="abc123",
            target_branch="dev",
            branch_contains_commit=True,
            merged_to_target_branch=False,
            source="measured compare response",
        )
    )

    assert (
        unavailable.classification
        is RepositoryProvenanceClassification.UNAVAILABLE_MERGE_EVIDENCE
    )
    assert (
        contained.classification
        is RepositoryProvenanceClassification.MEASURED_BRANCH_CONTAINS
    )
    assert contained.measured
    assert not docs_may_claim_merged_to_branch(contained)


def test_unavailable_remote_evidence_cannot_be_promoted_to_measured() -> None:
    branch = classify_branch_head_evidence(
        BranchHeadEvidence(
            branch="dev",
            commit_sha="abc123",
            refreshed=False,
            source="origin fetch unavailable",
        )
    )
    pr = classify_pr_visibility_evidence(
        PullRequestVisibilityEvidence(
            pr_reference="#22",
            visible=False,
            target_branch="dev",
            source="remote PR lookup unavailable",
        )
    )

    assert (
        branch.classification
        is RepositoryProvenanceClassification.UNAVAILABLE_BRANCH_REFRESH
    )
    assert (
        pr.classification
        is RepositoryProvenanceClassification.UNAVAILABLE_PR_VISIBILITY
    )
    assert not branch.measured
    assert not pr.measured


def test_docs_cannot_claim_merged_to_dev_unless_merge_is_measured() -> None:
    unavailable = classify_commit_ancestry_evidence(
        CommitAncestryEvidence(
            commit_sha="abc123",
            target_branch="dev",
            branch_contains_commit=True,
            merged_to_target_branch=None,
            source="branch compare lacks merge signal",
        )
    )
    merged = classify_commit_ancestry_evidence(
        CommitAncestryEvidence(
            commit_sha="abc123",
            target_branch="dev",
            branch_contains_commit=True,
            merged_to_target_branch=True,
            source="measured branch compare and merge evidence",
        )
    )

    assert not docs_may_claim_merged_to_branch(unavailable)
    assert (
        merged.classification
        is RepositoryProvenanceClassification.MEASURED_MERGED_TO_BRANCH
    )
    assert docs_may_claim_merged_to_branch(merged)
