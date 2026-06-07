"""Execution-cost evidence boundary for research-only metrics.

Gate 4D classifies execution-cost evidence before any net performance,
expectancy, strategy-comparison, optimizer-input, or readiness statement may be
published. Unknown costs remain unavailable; they are never converted to zero.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from json import dumps
from math import isfinite


class CostEvidenceError(ValueError):
    """Raised when execution-cost evidence is malformed or unsafe."""


class CostEvidenceClassification(StrEnum):
    """Execution-cost evidence quality classification."""

    MEASURED = "MEASURED"
    MODELED = "MODELED"
    UNAVAILABLE = "UNAVAILABLE"


class CostEvidenceCategory(StrEnum):
    """Execution-cost categories required before net metric publication."""

    FEES = "fees"
    SLIPPAGE = "slippage"
    SPREAD = "spread"
    FUNDING = "funding"
    LATENCY = "latency"


REQUIRED_COST_EVIDENCE_CATEGORIES: tuple[CostEvidenceCategory, ...] = (
    CostEvidenceCategory.FEES,
    CostEvidenceCategory.SLIPPAGE,
    CostEvidenceCategory.SPREAD,
    CostEvidenceCategory.FUNDING,
    CostEvidenceCategory.LATENCY,
)


@dataclass(frozen=True)
class CostEvidenceRecord:
    """One explicit execution-cost evidence record.

    The record is intentionally small and auditable. `UNAVAILABLE` records cannot
    carry numeric values, so absent costs cannot seep into calculations as zero.
    """

    category: CostEvidenceCategory
    classification: CostEvidenceClassification
    source: str
    value: float | str | None = None
    unit: str | None = None
    observed_at: str | None = None
    observation_window: str | None = None
    assumptions: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    unavailable_reason: str | None = None

    def validate(self) -> None:
        """Validate this record without substituting missing cost values."""

        _require_non_empty("source", self.source)
        if self.classification is CostEvidenceClassification.UNAVAILABLE:
            if self.value is not None:
                raise CostEvidenceError(
                    f"{self.category.value} unavailable evidence cannot carry value"
                )
            if self.unit is not None:
                raise CostEvidenceError(
                    f"{self.category.value} unavailable evidence cannot carry unit"
                )
            if not self.unavailable_reason or not self.unavailable_reason.strip():
                raise CostEvidenceError(
                    f"{self.category.value} unavailable evidence requires reason"
                )
            return
        if self.unavailable_reason is not None:
            raise CostEvidenceError(
                f"{self.category.value} available evidence cannot carry "
                "unavailable_reason"
            )
        if self.value is None:
            raise CostEvidenceError(
                f"{self.category.value} {self.classification.value} evidence "
                "requires value"
            )
        if isinstance(self.value, float) and not isfinite(self.value):
            raise CostEvidenceError(f"{self.category.value} value must be finite")
        _require_non_empty("unit", self.unit)
        if self.observed_at is None and self.observation_window is None:
            raise CostEvidenceError(
                f"{self.category.value} evidence requires timestamp or observation "
                "window"
            )
        if self.classification is CostEvidenceClassification.MODELED:
            _require_strings(
                f"{self.category.value} modeled evidence requires assumptions",
                self.assumptions,
            )
        if self.classification is CostEvidenceClassification.MEASURED:
            _require_strings(
                f"{self.category.value} measured evidence requires limitations",
                self.limitations,
            )

    def payload(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible payload."""

        self.validate()
        return {
            "assumptions": list(self.assumptions),
            "category": self.category.value,
            "classification": self.classification.value,
            "limitations": list(self.limitations),
            "observation_window": self.observation_window,
            "observed_at": self.observed_at,
            "source": self.source,
            "unit": self.unit,
            "unavailable_reason": self.unavailable_reason,
            "value": self.value,
        }


CostEvidenceIterable = Iterable[CostEvidenceRecord]
CostEvidenceMapping = Mapping[CostEvidenceCategory, CostEvidenceRecord]
CostEvidenceRecords = CostEvidenceIterable | CostEvidenceMapping
RequiredCostCategories = Sequence[CostEvidenceCategory]


@dataclass(frozen=True)
class CostEvidenceGateResult:
    """Structured fail-closed result for execution-cost metric gating."""

    passed: bool
    blocking_categories: tuple[CostEvidenceCategory, ...]
    unavailable_categories: tuple[CostEvidenceCategory, ...]
    modeled_categories: tuple[CostEvidenceCategory, ...]
    measured_categories: tuple[CostEvidenceCategory, ...]
    diagnostics: tuple[str, ...]
    can_publish_net_metrics: bool
    can_publish_gross_metrics: bool
    readiness_allowed: bool
    metric_label: str
    evidence: tuple[CostEvidenceRecord, ...]

    def payload(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible gate payload."""

        return {
            "blocking_categories": [item.value for item in self.blocking_categories],
            "can_publish_gross_metrics": self.can_publish_gross_metrics,
            "can_publish_net_metrics": self.can_publish_net_metrics,
            "diagnostics": list(self.diagnostics),
            "evidence": [record.payload() for record in self.evidence],
            "measured_categories": [item.value for item in self.measured_categories],
            "metric_label": self.metric_label,
            "modeled_categories": [item.value for item in self.modeled_categories],
            "passed": self.passed,
            "readiness_allowed": self.readiness_allowed,
            "unavailable_categories": [
                item.value for item in self.unavailable_categories
            ],
        }


def evaluate_cost_evidence_gate(
    evidence_records: CostEvidenceRecords,
    *,
    required_categories: RequiredCostCategories = REQUIRED_COST_EVIDENCE_CATEGORIES,
    allow_modeled_costs: bool = True,
    gross_metrics_explicitly_labeled: bool = False,
) -> CostEvidenceGateResult:
    """Classify cost evidence before publishing execution-dependent metrics."""

    records = _normalize_records(evidence_records)
    required = tuple(required_categories)
    if len(set(required)) != len(required):
        raise CostEvidenceError("required cost evidence categories must be unique")
    evidence_by_category: dict[CostEvidenceCategory, CostEvidenceRecord] = {}
    for evidence_record in records:
        evidence_record.validate()
        if evidence_record.category in evidence_by_category:
            raise CostEvidenceError(
                f"duplicate cost evidence category: {evidence_record.category.value}"
            )
        evidence_by_category[evidence_record.category] = evidence_record

    diagnostics: list[str] = []
    unavailable: list[CostEvidenceCategory] = []
    measured: list[CostEvidenceCategory] = []
    modeled: list[CostEvidenceCategory] = []
    blocking: list[CostEvidenceCategory] = []

    for category in required:
        category_record = evidence_by_category.get(category)
        if category_record is None:
            unavailable.append(category)
            blocking.append(category)
            diagnostics.append(
                f"{category.value} cost evidence is UNAVAILABLE: missing record"
            )
            continue
        if category_record.classification is CostEvidenceClassification.UNAVAILABLE:
            unavailable.append(category)
            blocking.append(category)
            diagnostics.append(
                f"{category.value} cost evidence is UNAVAILABLE: "
                f"{category_record.unavailable_reason}"
            )
        elif category_record.classification is CostEvidenceClassification.MODELED:
            modeled.append(category)
            diagnostics.append(
                f"{category.value} cost evidence is MODELED; metrics require "
                "modeled-cost labeling"
            )
            if not allow_modeled_costs:
                blocking.append(category)
                diagnostics.append(
                    f"{category.value} modeled cost evidence is not accepted by "
                    "this gate policy"
                )
        elif category_record.classification is CostEvidenceClassification.MEASURED:
            measured.append(category)
        else:  # pragma: no cover - defensive for future enum expansion.
            raise CostEvidenceError(
                "unsupported cost evidence classification: "
                f"{category_record.classification}"
            )

    if not records:
        diagnostics.append("no cost evidence records supplied; fail closed")

    can_publish_net = not unavailable and not blocking
    passed = can_publish_net
    if unavailable:
        diagnostics.append(
            "net performance, expectancy, profitability ranking, optimizer input, "
            "and readiness approval are blocked while cost evidence is UNAVAILABLE"
        )
    if can_publish_net and modeled:
        metric_label = "NET_MODELED_COST_METRICS"
    elif can_publish_net:
        metric_label = "NET_MEASURED_COST_METRICS"
    else:
        metric_label = "NET_METRICS_UNAVAILABLE"

    return CostEvidenceGateResult(
        passed=passed,
        blocking_categories=tuple(sorted(blocking, key=lambda item: item.value)),
        unavailable_categories=tuple(sorted(unavailable, key=lambda item: item.value)),
        modeled_categories=tuple(sorted(modeled, key=lambda item: item.value)),
        measured_categories=tuple(sorted(measured, key=lambda item: item.value)),
        diagnostics=tuple(diagnostics),
        can_publish_net_metrics=can_publish_net,
        can_publish_gross_metrics=gross_metrics_explicitly_labeled,
        readiness_allowed=False,
        metric_label=metric_label,
        evidence=tuple(sorted(records, key=lambda item: item.category.value)),
    )


def assert_can_publish_net_metrics(result: CostEvidenceGateResult) -> None:
    """Fail closed before net metrics when the cost-evidence gate did not pass."""

    if not result.can_publish_net_metrics:
        blocked = ", ".join(item.value for item in result.blocking_categories)
        raise CostEvidenceError(
            "cannot publish net metrics with insufficient execution-cost evidence: "
            f"{blocked}"
        )


def unavailable_cost_evidence(
    reason: str,
    *,
    source: str = "caller did not provide execution-cost evidence",
) -> tuple[CostEvidenceRecord, ...]:
    """Build explicit unavailable records for all Gate 4D cost categories."""

    _require_non_empty("reason", reason)
    return tuple(
        CostEvidenceRecord(
            category=category,
            classification=CostEvidenceClassification.UNAVAILABLE,
            source=source,
            unavailable_reason=reason,
        )
        for category in REQUIRED_COST_EVIDENCE_CATEGORIES
    )


def cost_evidence_gate_json(result: CostEvidenceGateResult) -> str:
    """Serialize a cost-evidence gate result deterministically."""

    return dumps(result.payload(), sort_keys=True, separators=(",", ":"))


def render_cost_evidence_markdown(result: CostEvidenceGateResult) -> str:
    """Render explicit execution-cost evidence diagnostics for reports."""

    rows = [
        "| Category | Classification | Value | Unit | Source | Diagnostics |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    evidence_by_category = {record.category: record for record in result.evidence}
    for category in REQUIRED_COST_EVIDENCE_CATEGORIES:
        category_record = evidence_by_category.get(category)
        if category_record is None:
            rows.append(
                f"| `{category.value}` | `UNAVAILABLE` |  |  |  | " "missing record |"
            )
            continue
        value = "" if category_record.value is None else str(category_record.value)
        unit = "" if category_record.unit is None else category_record.unit
        diagnostic_parts = [
            *category_record.assumptions,
            *category_record.limitations,
        ]
        if category_record.unavailable_reason:
            diagnostic_parts.append(category_record.unavailable_reason)
        diagnostics = "; ".join(diagnostic_parts)
        rows.append(
            f"| `{category_record.category.value}` | "
            f"`{category_record.classification.value}` | "
            f"{value} | {unit} | {category_record.source} | {diagnostics} |"
        )
    diagnostics = "\n".join(f"- {item}" for item in result.diagnostics)
    return "\n".join(
        [
            "## Gate 4D execution-cost evidence",
            "",
            f"- Gate passed: `{result.passed}`",
            f"- Net metrics: `{result.metric_label}`",
            f"- Readiness allowed: `{result.readiness_allowed}`",
            "",
            *rows,
            "",
            "### Diagnostics",
            "",
            diagnostics or "- No diagnostics emitted.",
        ]
    )


def _normalize_records(
    evidence_records: CostEvidenceRecords,
) -> tuple[CostEvidenceRecord, ...]:
    if isinstance(evidence_records, Mapping):
        return tuple(evidence_records.values())
    return tuple(evidence_records)


def _require_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise CostEvidenceError(f"{name} is required")


def _require_strings(message: str, values: tuple[str, ...]) -> None:
    if not values or any(not value.strip() for value in values):
        raise CostEvidenceError(message)
