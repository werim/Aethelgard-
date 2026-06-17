"""Gate 5B-0 PAPER runtime safe-startup preflight evidence adapter.

This module classifies caller-supplied local startup/preflight evidence. It is
offline and deterministic: it does not read secrets, inspect environment
credentials, connect to Binance or any exchange, fetch market data, generate
signals, create or cancel orders, mutate external state, approve readiness, or
make performance claims. Missing startup or runtime-log proof fails closed as
unavailable evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PaperRuntimePreflightClassification(StrEnum):
    """Fail-closed PAPER runtime startup/preflight classifications."""

    MEASURED_SAFE_STARTUP = "MEASURED_SAFE_STARTUP"
    USER_REPORTED_STARTUP_OK = "USER_REPORTED_STARTUP_OK"
    UNAVAILABLE_STARTUP_RUN = "UNAVAILABLE_STARTUP_RUN"
    UNAVAILABLE_RUNTIME_LOG = "UNAVAILABLE_RUNTIME_LOG"
    VIOLATION_LIVE_RUNTIME_ENABLED = "VIOLATION_LIVE_RUNTIME_ENABLED"
    VIOLATION_SECRET_OR_EXCHANGE_ACCESS = "VIOLATION_SECRET_OR_EXCHANGE_ACCESS"


@dataclass(frozen=True)
class PaperRuntimePreflightEvidence:
    """Caller-supplied evidence for one local PAPER startup/preflight claim."""

    source: str
    startup_command: str | None = None
    runtime_log_source: str | None = None
    startup_run_observed: bool = False
    startup_exit_code: int | None = None
    runtime_log_observed: bool = False
    paper_only_mode_observed: bool = False
    readiness_not_approved_observed: bool = False
    no_secret_access_observed: bool = False
    no_exchange_connection_observed: bool = False
    no_market_fetch_observed: bool = False
    no_order_path_observed: bool = False
    no_strategy_alpha_observed: bool = False
    no_optimizer_observed: bool = False
    user_reported_startup_ok: bool = False
    live_mode_enabled: bool = False
    readiness_approval_present: bool = False
    secret_access_attempted: bool = False
    credentials_required: bool = False
    exchange_connection_attempted: bool = False
    market_fetch_attempted: bool = False
    order_placement_or_cancel_attempted: bool = False
    external_state_mutation_attempted: bool = False
    strategy_alpha_executed: bool = False
    optimizer_executed: bool = False


@dataclass(frozen=True)
class PaperRuntimePreflightAssessment:
    """Deterministic assessment for PAPER runtime startup/preflight evidence."""

    classification: PaperRuntimePreflightClassification
    summary: str
    diagnostics: tuple[str, ...]
    source: str

    @property
    def measured(self) -> bool:
        """Return whether this assessment is measured safe-startup evidence."""

        return (
            self.classification
            is PaperRuntimePreflightClassification.MEASURED_SAFE_STARTUP
        )

    @property
    def violation(self) -> bool:
        """Return whether this assessment identifies a safety violation."""

        return self.classification in {
            PaperRuntimePreflightClassification.VIOLATION_LIVE_RUNTIME_ENABLED,
            PaperRuntimePreflightClassification.VIOLATION_SECRET_OR_EXCHANGE_ACCESS,
        }

    @property
    def permits_readiness_approval(self) -> bool:
        """PAPER startup evidence never permits readiness approval."""

        return False

    def payload(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible payload."""

        return {
            "classification": self.classification.value,
            "diagnostics": list(self.diagnostics),
            "measured": self.measured,
            "permits_readiness_approval": self.permits_readiness_approval,
            "source": self.source,
            "summary": self.summary,
            "violation": self.violation,
        }


def classify_paper_runtime_preflight_evidence(
    evidence: PaperRuntimePreflightEvidence,
) -> PaperRuntimePreflightAssessment:
    """Classify local startup/preflight evidence without promoting missing proof."""

    source = evidence.source.strip() or "UNAVAILABLE: missing startup evidence source"

    if evidence.live_mode_enabled or evidence.readiness_approval_present:
        return _assessment(
            PaperRuntimePreflightClassification.VIOLATION_LIVE_RUNTIME_ENABLED,
            "LIVE runtime or readiness approval was present during startup",
            ("PAPER startup evidence must not enable LIVE mode or approve readiness",),
            source,
        )

    if (
        evidence.secret_access_attempted
        or evidence.credentials_required
        or evidence.exchange_connection_attempted
        or evidence.market_fetch_attempted
        or evidence.order_placement_or_cancel_attempted
        or evidence.external_state_mutation_attempted
    ):
        return _assessment(
            PaperRuntimePreflightClassification.VIOLATION_SECRET_OR_EXCHANGE_ACCESS,
            (
                "startup attempted secret, exchange, market-data, order, "
                "or external mutation access"
            ),
            (
                (
                    "safe startup must remain offline, credential-free, read-only, "
                    "and non-trading"
                ),
            ),
            source,
        )

    if evidence.strategy_alpha_executed or evidence.optimizer_executed:
        return _assessment(
            PaperRuntimePreflightClassification.VIOLATION_LIVE_RUNTIME_ENABLED,
            "startup executed strategy alpha or optimizer behavior",
            ("safe startup must not execute strategy alpha or optimizer behavior",),
            source,
        )

    if evidence.user_reported_startup_ok and not evidence.startup_run_observed:
        return _assessment(
            PaperRuntimePreflightClassification.USER_REPORTED_STARTUP_OK,
            "user-reported startup success remains unmeasured",
            ("user reports are not direct local startup/runtime-log evidence",),
            source,
        )

    if not evidence.startup_run_observed or evidence.startup_exit_code != 0:
        return _assessment(
            PaperRuntimePreflightClassification.UNAVAILABLE_STARTUP_RUN,
            "direct successful startup run evidence is unavailable",
            ("successful imports or absent runs are not runtime proof",),
            source,
        )

    if not evidence.runtime_log_observed or not _has_text(evidence.runtime_log_source):
        return _assessment(
            PaperRuntimePreflightClassification.UNAVAILABLE_RUNTIME_LOG,
            "startup/runtime metadata log evidence is unavailable",
            ("missing runtime logs remain unavailable startup evidence",),
            source,
        )

    required_observations = (
        evidence.paper_only_mode_observed,
        evidence.readiness_not_approved_observed,
        evidence.no_secret_access_observed,
        evidence.no_exchange_connection_observed,
        evidence.no_market_fetch_observed,
        evidence.no_order_path_observed,
        evidence.no_strategy_alpha_observed,
        evidence.no_optimizer_observed,
    )
    if all(required_observations):
        return _assessment(
            PaperRuntimePreflightClassification.MEASURED_SAFE_STARTUP,
            (
                "local startup completed in PAPER_ONLY mode with bounded "
                "preflight metadata only"
            ),
            (
                "measured safe startup does not prove production readiness",
                (
                    "PAPER_ONLY startup does not prove exchange safety, "
                    "data completeness, or strategy validity"
                ),
            ),
            source,
        )

    return _assessment(
        PaperRuntimePreflightClassification.UNAVAILABLE_STARTUP_RUN,
        "safe startup observations are incomplete",
        (
            (
                "all PAPER-only, no-secret, no-exchange, no-fetch, no-order, "
                "no-alpha, and no-optimizer observations are required"
            ),
        ),
        source,
    )


def docs_may_claim_runtime_readiness(
    assessment: PaperRuntimePreflightAssessment,
) -> bool:
    """Startup/preflight evidence never permits runtime readiness claims."""

    return assessment.permits_readiness_approval


def _has_text(value: str | None) -> bool:
    return bool(value and value.strip())


def _assessment(
    classification: PaperRuntimePreflightClassification,
    summary: str,
    diagnostics: tuple[str, ...],
    source: str,
) -> PaperRuntimePreflightAssessment:
    return PaperRuntimePreflightAssessment(
        classification=classification,
        summary=summary,
        diagnostics=diagnostics,
        source=source,
    )
