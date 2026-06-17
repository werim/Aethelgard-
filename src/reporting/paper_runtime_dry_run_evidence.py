"""Gate 5B-1 PAPER runtime dry-run evidence ledger adapter.

This module classifies caller-supplied PAPER runtime dry-run evidence without
running commands, reading secrets, connecting to exchanges, fetching market
data, creating order paths, generating alpha, optimizing, publishing
performance, or approving readiness. Missing or user-provided evidence remains
separate from directly measured local proof.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PaperRuntimeDryRunClassification(StrEnum):
    """Fail-closed PAPER runtime dry-run evidence classifications."""

    MEASURED_PAPER_DRY_RUN = "MEASURED_PAPER_DRY_RUN"
    USER_PROVIDED_RUNTIME_OUTPUT = "USER_PROVIDED_RUNTIME_OUTPUT"
    USER_REPORTED_DRY_RUN_OK = "USER_REPORTED_DRY_RUN_OK"
    UNAVAILABLE_DRY_RUN = "UNAVAILABLE_DRY_RUN"
    UNAVAILABLE_DRY_RUN_LOG = "UNAVAILABLE_DRY_RUN_LOG"
    VIOLATION_LIVE_OR_EXCHANGE_PATH = "VIOLATION_LIVE_OR_EXCHANGE_PATH"
    VIOLATION_SECRET_OR_READINESS_PATH = "VIOLATION_SECRET_OR_READINESS_PATH"


@dataclass(frozen=True)
class PaperRuntimeDryRunEvidence:
    """Caller-supplied evidence for one PAPER runtime dry-run claim."""

    source: str
    run_command: str | None = None
    runtime_output_source: str | None = None
    run_log_source: str | None = None
    paper_only_mode: bool = False
    research_only_readiness: bool = False
    startup_metadata_observed: bool = False
    dry_run_log_observed: bool = False
    user_provided_runtime_output: bool = False
    user_reported_dry_run_ok: bool = False
    secret_access_observed: bool = False
    exchange_connection_observed: bool = False
    market_fetch_observed: bool = False
    order_path_observed: bool = False
    strategy_alpha_observed: bool = False
    optimizer_observed: bool = False
    performance_publication_observed: bool = False
    readiness_claim_observed: bool = False
    live_mode_observed: bool = False
    exchange_mutation_observed: bool = False


@dataclass(frozen=True)
class PaperRuntimeDryRunAssessment:
    """Deterministic PAPER runtime dry-run evidence assessment."""

    classification: PaperRuntimeDryRunClassification
    summary: str
    diagnostics: tuple[str, ...]
    source: str

    @property
    def measured(self) -> bool:
        """Return whether this is direct measured local dry-run proof."""

        return (
            self.classification
            is PaperRuntimeDryRunClassification.MEASURED_PAPER_DRY_RUN
        )

    @property
    def user_provided(self) -> bool:
        """Return whether this assessment depends on user-provided evidence."""

        return self.classification in {
            PaperRuntimeDryRunClassification.USER_PROVIDED_RUNTIME_OUTPUT,
            PaperRuntimeDryRunClassification.USER_REPORTED_DRY_RUN_OK,
        }

    @property
    def violation(self) -> bool:
        """Return whether this assessment identifies a safety violation."""

        return self.classification in {
            PaperRuntimeDryRunClassification.VIOLATION_LIVE_OR_EXCHANGE_PATH,
            PaperRuntimeDryRunClassification.VIOLATION_SECRET_OR_READINESS_PATH,
        }

    @property
    def permits_live_readiness_claim(self) -> bool:
        """PAPER dry-run evidence never permits live or production readiness."""

        return False

    def payload(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible assessment payload."""

        return {
            "classification": self.classification.value,
            "diagnostics": list(self.diagnostics),
            "measured": self.measured,
            "permits_live_readiness_claim": self.permits_live_readiness_claim,
            "source": self.source,
            "summary": self.summary,
            "user_provided": self.user_provided,
            "violation": self.violation,
        }


def classify_paper_runtime_dry_run_evidence(
    evidence: PaperRuntimeDryRunEvidence,
) -> PaperRuntimeDryRunAssessment:
    """Classify PAPER runtime dry-run evidence without promoting weak proof."""

    source = evidence.source.strip() or "UNAVAILABLE: missing dry-run evidence source"

    if (
        evidence.live_mode_observed
        or evidence.exchange_connection_observed
        or evidence.market_fetch_observed
        or evidence.order_path_observed
        or evidence.exchange_mutation_observed
    ):
        return _assessment(
            PaperRuntimeDryRunClassification.VIOLATION_LIVE_OR_EXCHANGE_PATH,
            (
                "LIVE mode, exchange access, market fetch, order path, "
                "or mutation observed"
            ),
            (
                (
                    "PAPER runtime dry-run evidence must not include LIVE "
                    "or exchange paths"
                ),
            ),
            source,
        )

    if evidence.secret_access_observed or evidence.readiness_claim_observed:
        return _assessment(
            PaperRuntimeDryRunClassification.VIOLATION_SECRET_OR_READINESS_PATH,
            "secret access or readiness approval was observed in dry-run evidence",
            ("dry-run evidence must not request secrets or approve readiness",),
            source,
        )

    if evidence.user_provided_runtime_output:
        return _assessment(
            PaperRuntimeDryRunClassification.USER_PROVIDED_RUNTIME_OUTPUT,
            "user-provided runtime output is bounded evidence, not local proof",
            ("pasted runtime output must not be promoted to direct measured evidence",),
            source,
        )

    if evidence.user_reported_dry_run_ok:
        return _assessment(
            PaperRuntimeDryRunClassification.USER_REPORTED_DRY_RUN_OK,
            "user-reported dry-run success remains unmeasured",
            ("a user report without terminal output is not measured dry-run proof",),
            source,
        )

    if not _has_text(evidence.runtime_output_source):
        return _assessment(
            PaperRuntimeDryRunClassification.UNAVAILABLE_DRY_RUN,
            "direct dry-run runtime output is unavailable",
            ("missing dry-run output remains unavailable evidence",),
            source,
        )

    if not evidence.dry_run_log_observed or not _has_text(evidence.run_log_source):
        return _assessment(
            PaperRuntimeDryRunClassification.UNAVAILABLE_DRY_RUN_LOG,
            "dry-run runtime log or metadata evidence is unavailable",
            ("missing dry-run logs remain unavailable evidence",),
            source,
        )

    required_safe_observations = (
        evidence.paper_only_mode,
        evidence.research_only_readiness,
        evidence.startup_metadata_observed,
        not evidence.strategy_alpha_observed,
        not evidence.optimizer_observed,
        not evidence.performance_publication_observed,
    )
    if all(required_safe_observations):
        return _assessment(
            PaperRuntimeDryRunClassification.MEASURED_PAPER_DRY_RUN,
            "local PAPER_ONLY dry-run emitted bounded RESEARCH_ONLY startup metadata",
            (
                "measured dry-run evidence does not prove production readiness",
                (
                    "measured dry-run evidence does not prove live readiness "
                    "or profitability"
                ),
            ),
            source,
        )

    return _assessment(
        PaperRuntimeDryRunClassification.UNAVAILABLE_DRY_RUN,
        "safe PAPER dry-run observations are incomplete",
        (
            "PAPER_ONLY, RESEARCH_ONLY, startup metadata, no alpha, no optimizer, "
            "and no performance publication observations are required",
        ),
        source,
    )


def docs_may_claim_live_readiness_from_dry_run(
    assessment: PaperRuntimeDryRunAssessment,
) -> bool:
    """Dry-run evidence never permits live or production readiness claims."""

    return assessment.permits_live_readiness_claim


def _has_text(value: str | None) -> bool:
    return bool(value and value.strip())


def _assessment(
    classification: PaperRuntimeDryRunClassification,
    summary: str,
    diagnostics: tuple[str, ...],
    source: str,
) -> PaperRuntimeDryRunAssessment:
    return PaperRuntimeDryRunAssessment(
        classification=classification,
        summary=summary,
        diagnostics=diagnostics,
        source=source,
    )
