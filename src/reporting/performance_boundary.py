"""Minimal performance metric publication boundary.

This module reports only whether performance metrics may be published from a
Gate 4A backtest metadata record. It emits eligibility diagnostics only.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from src.backtest import foundation

_BOUNDARY_EVALUATED_TOKEN = "GATE_4B_BOUNDARY_EVALUATED"


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
    _boundary_token: str = field(default="", init=False, repr=False, compare=False)

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
    metadata: foundation.BacktestRunMetadata,
) -> MetricPublicationEligibility:
    """Fail closed unless Gate 4A permits performance-result publication."""

    try:
        foundation.assert_can_produce_performance_results(metadata)
    except foundation.BacktestExecutionEvidenceUnavailable as exc:
        unavailable = _unavailable_assumption_names(metadata)
        reason = str(exc)
        return _boundary_evaluated_eligibility(
            status=MetricPublicationStatus.METRICS_BLOCKED,
            can_publish_metrics=False,
            unavailable_execution_assumptions=unavailable,
            refusal_reason=reason,
            diagnostics=(reason,),
        )
    except foundation.BacktestFoundationError as exc:
        reason = f"metadata validation failed closed: {exc}"
        return _boundary_evaluated_eligibility(
            status=MetricPublicationStatus.METRICS_BLOCKED,
            can_publish_metrics=False,
            unavailable_execution_assumptions=(),
            refusal_reason=reason,
            diagnostics=(reason,),
        )

    return _boundary_evaluated_eligibility(
        status=MetricPublicationStatus.METRICS_PUBLISHABLE,
        can_publish_metrics=True,
        unavailable_execution_assumptions=(),
        refusal_reason=None,
        diagnostics=(
            "required Gate 4A execution evidence is measured or modeled; "
            "metric eligibility only, no performance metric computed",
        ),
    )


def guarded_performance_report_payload(
    eligibility: MetricPublicationEligibility,
    report_payload: Mapping[str, object],
) -> dict[str, object]:
    """Return a performance payload only after Gate 4B-0 eligibility passes.

    Blocked eligibility fails closed and emits refusal diagnostics only. Candidate
    report fields are deliberately ignored while blocked, so unavailable evidence
    remains unavailable and cannot be introduced as zero.
    """

    if not _was_boundary_evaluated(eligibility):
        return _untrusted_eligibility_report_payload()
    if (
        eligibility.status is not MetricPublicationStatus.METRICS_PUBLISHABLE
        or not eligibility.can_publish_metrics
    ):
        return _blocked_performance_report_payload(eligibility)
    return dict(report_payload)


def metric_publication_eligibility_json(
    eligibility: MetricPublicationEligibility,
) -> str:
    """Serialize metric-publication eligibility deterministically."""

    return json.dumps(eligibility.payload(), sort_keys=True, separators=(",", ":"))


def guarded_performance_report_json(
    eligibility: MetricPublicationEligibility,
    report_payload: Mapping[str, object],
) -> str:
    """Serialize a guarded performance report payload deterministically."""

    payload = guarded_performance_report_payload(eligibility, report_payload)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _boundary_evaluated_eligibility(
    *,
    status: MetricPublicationStatus,
    can_publish_metrics: bool,
    unavailable_execution_assumptions: tuple[str, ...],
    refusal_reason: str | None,
    diagnostics: tuple[str, ...],
) -> MetricPublicationEligibility:
    eligibility = MetricPublicationEligibility(
        status=status,
        can_publish_metrics=can_publish_metrics,
        unavailable_execution_assumptions=unavailable_execution_assumptions,
        refusal_reason=refusal_reason,
        diagnostics=diagnostics,
    )
    object.__setattr__(eligibility, "_boundary_token", _BOUNDARY_EVALUATED_TOKEN)
    return eligibility


def _was_boundary_evaluated(eligibility: MetricPublicationEligibility) -> bool:
    return eligibility._boundary_token == _BOUNDARY_EVALUATED_TOKEN


def _blocked_performance_report_payload(
    eligibility: MetricPublicationEligibility,
) -> dict[str, object]:
    reason = eligibility.refusal_reason or "performance publication blocked"
    diagnostics = eligibility.diagnostics or (reason,)
    return {
        "diagnostics": list(diagnostics),
        "refusal_reason": reason,
        "status": MetricPublicationStatus.METRICS_BLOCKED.value,
        "unavailable_execution_assumptions": list(
            eligibility.unavailable_execution_assumptions
        ),
    }


def _untrusted_eligibility_report_payload() -> dict[str, object]:
    reason = (
        "performance publication blocked: eligibility was not produced by "
        "Gate 4B boundary evaluation"
    )
    return {
        "diagnostics": [reason],
        "refusal_reason": reason,
        "status": MetricPublicationStatus.METRICS_BLOCKED.value,
        "unavailable_execution_assumptions": [],
    }


def _unavailable_assumption_names(
    metadata: foundation.BacktestRunMetadata,
) -> tuple[str, ...]:
    return tuple(
        sorted(
            assumption.value
            for assumption, evidence in metadata.execution_assumptions.items()
            if (
                isinstance(assumption, foundation.ExecutionAssumption)
                and (
                    evidence.classification
                    is foundation.EvidenceClassification.UNAVAILABLE
                )
            )
        )
    )
