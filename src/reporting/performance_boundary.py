"""Minimal performance metric publication boundary.

This module reports only whether performance metrics may be published from a
Gate 4A backtest metadata record. It does not replay candles, simulate trades,
model costs, calculate performance, or approve PAPER/LIVE readiness.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum

from src.backtest.foundation import (
    BacktestExecutionEvidenceUnavailable,
    BacktestFoundationError,
    BacktestRunMetadata,
    EvidenceClassification,
    ExecutionAssumption,
    assert_can_produce_performance_results,
)


class MetricPublicationStatus(StrEnum):
    """Status for metric-publication eligibility diagnostics only."""

    METRICS_BLOCKED = "METRICS_BLOCKED"
    METRICS_PUBLISHABLE = "METRICS_PUBLISHABLE"


@dataclass(frozen=True)
class MetricPublicationEligibility:
    """Deterministic diagnostic payload for performance metric eligibility."""

    status: MetricPublicationStatus
    can_publish_metrics: bool
    unavailable_execution_assumptions: tuple[str, ...]
    refusal_reason: str | None
    diagnostics: tuple[str, ...]

    def payload(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible eligibility payload."""

        return {
            "can_publish_metrics": self.can_publish_metrics,
            "diagnostics": list(self.diagnostics),
            "refusal_reason": self.refusal_reason,
            "status": self.status.value,
            "unavailable_execution_assumptions": list(
                self.unavailable_execution_assumptions
            ),
        }


def evaluate_metric_publication_eligibility(
    metadata: BacktestRunMetadata,
) -> MetricPublicationEligibility:
    """Fail closed unless Gate 4A permits performance-result publication."""

    try:
        assert_can_produce_performance_results(metadata)
    except BacktestExecutionEvidenceUnavailable as exc:
        unavailable = _unavailable_assumption_names(metadata)
        reason = str(exc)
        return MetricPublicationEligibility(
            status=MetricPublicationStatus.METRICS_BLOCKED,
            can_publish_metrics=False,
            unavailable_execution_assumptions=unavailable,
            refusal_reason=reason,
            diagnostics=(reason,),
        )
    except BacktestFoundationError as exc:
        reason = f"metadata validation failed closed: {exc}"
        return MetricPublicationEligibility(
            status=MetricPublicationStatus.METRICS_BLOCKED,
            can_publish_metrics=False,
            unavailable_execution_assumptions=(),
            refusal_reason=reason,
            diagnostics=(reason,),
        )

    return MetricPublicationEligibility(
        status=MetricPublicationStatus.METRICS_PUBLISHABLE,
        can_publish_metrics=True,
        unavailable_execution_assumptions=(),
        refusal_reason=None,
        diagnostics=(
            "required Gate 4A execution evidence is measured or modeled; "
            "metric eligibility only, no performance metric computed",
        ),
    )


def metric_publication_eligibility_json(
    eligibility: MetricPublicationEligibility,
) -> str:
    """Serialize metric-publication eligibility deterministically."""

    return json.dumps(eligibility.payload(), sort_keys=True, separators=(",", ":"))


def _unavailable_assumption_names(
    metadata: BacktestRunMetadata,
) -> tuple[str, ...]:
    return tuple(
        sorted(
            assumption.value
            for assumption, evidence in metadata.execution_assumptions.items()
            if (
                isinstance(assumption, ExecutionAssumption)
                and evidence.classification is EvidenceClassification.UNAVAILABLE
            )
        )
    )
