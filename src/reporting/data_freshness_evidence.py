"""Gate 5A-6 data-freshness evidence adapter.

This module converts caller-supplied dataset freshness and selector-consistency
facts into a Gate 5A `data_freshness` evidence item. It is deliberately offline
and deterministic: it does not fetch market data, connect to exchanges, compute
performance, model costs, submit orders, mutate exchange state, or approve
readiness. Missing, stale, malformed, or selector-mismatched evidence remains
UNAVAILABLE.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum

from src.reporting.operational_evidence import (
    OperationalEvidenceClassification,
    OperationalEvidenceItem,
)


class DataFreshnessEvidenceStatus(StrEnum):
    """Data-freshness evidence adapter status values."""

    FRESHNESS_MEASURED = "FRESHNESS_MEASURED"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class DataFreshnessEvidence:
    """Caller-supplied data-freshness and selector-consistency evidence."""

    source: str
    dataset_id: str
    expected_selector_id: str
    observed_selector_id: str
    latest_closed_bar_at_utc: str
    observed_age_seconds: int
    max_age_seconds: int

    def payload(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible evidence payload."""

        return {
            "dataset_id": self.dataset_id,
            "expected_selector_id": self.expected_selector_id,
            "latest_closed_bar_at_utc": self.latest_closed_bar_at_utc,
            "max_age_seconds": self.max_age_seconds,
            "observed_age_seconds": self.observed_age_seconds,
            "observed_selector_id": self.observed_selector_id,
            "source": self.source,
        }


@dataclass(frozen=True)
class DataFreshnessEvidenceAssessment:
    """Fail-closed Gate 5A assessment for data-freshness evidence."""

    status: DataFreshnessEvidenceStatus
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


def assess_data_freshness_for_gate5a(
    evidence: DataFreshnessEvidence | None,
    *,
    source: str = "",
) -> DataFreshnessEvidenceAssessment:
    """Classify data-freshness evidence for Gate 5A."""

    diagnostics = _data_freshness_diagnostics(evidence, fallback_source=source)
    if diagnostics:
        return _build_assessment(
            status=DataFreshnessEvidenceStatus.UNAVAILABLE,
            classification=OperationalEvidenceClassification.UNAVAILABLE,
            diagnostics=diagnostics,
            source=_evidence_source(evidence, fallback_source=source),
        )

    if evidence is None:
        raise AssertionError("Evidence must be present after diagnostics pass.")
    summary = (
        "Data freshness measured for dataset "
        f"{evidence.dataset_id!r} at selector {evidence.observed_selector_id!r}"
    )
    return DataFreshnessEvidenceAssessment(
        status=DataFreshnessEvidenceStatus.FRESHNESS_MEASURED,
        classification=OperationalEvidenceClassification.MEASURED,
        diagnostics=(summary,),
        evidence_item=OperationalEvidenceItem(
            blocker_id="data_freshness",
            classification=OperationalEvidenceClassification.MEASURED,
            summary=summary,
            source=evidence.source,
        ),
    )


def data_freshness_evidence_assessment_json(
    assessment: DataFreshnessEvidenceAssessment,
) -> str:
    """Serialize a data-freshness evidence assessment deterministically."""

    return json.dumps(assessment.payload(), sort_keys=True, separators=(",", ":"))


def _data_freshness_diagnostics(
    evidence: DataFreshnessEvidence | None,
    *,
    fallback_source: str,
) -> tuple[str, ...]:
    diagnostics: list[str] = []

    if evidence is None:
        if not fallback_source.strip():
            diagnostics.append("data-freshness evidence source is missing")
        diagnostics.append("data-freshness evidence is unavailable")
        return tuple(diagnostics)

    if not evidence.source.strip():
        diagnostics.append("data-freshness evidence source is missing")
    _require_canonical_text(
        evidence.dataset_id,
        label="dataset id",
        diagnostics=diagnostics,
    )
    expected_selector = _require_canonical_text(
        evidence.expected_selector_id,
        label="expected selector id",
        diagnostics=diagnostics,
    )
    observed_selector = _require_canonical_text(
        evidence.observed_selector_id,
        label="observed selector id",
        diagnostics=diagnostics,
    )
    _require_canonical_text(
        evidence.latest_closed_bar_at_utc,
        label="latest closed bar timestamp",
        diagnostics=diagnostics,
    )

    if (
        expected_selector
        and observed_selector
        and expected_selector != observed_selector
    ):
        diagnostics.append(
            "data selector mismatch: expected "
            f"{expected_selector!r}, observed {observed_selector!r}"
        )
    if evidence.max_age_seconds <= 0:
        diagnostics.append("data-freshness max_age_seconds must be positive")
    if evidence.observed_age_seconds < 0:
        diagnostics.append("data-freshness observed_age_seconds must be non-negative")
    if (
        evidence.max_age_seconds > 0
        and evidence.observed_age_seconds > evidence.max_age_seconds
    ):
        diagnostics.append(
            "data-freshness observed_age_seconds exceeds max_age_seconds"
        )

    return tuple(diagnostics)


def _require_canonical_text(
    value: str,
    *,
    label: str,
    diagnostics: list[str],
) -> str:
    canonical_value = value.strip()
    if not canonical_value:
        diagnostics.append(f"data-freshness {label} is missing")
        return ""
    if canonical_value != value:
        diagnostics.append(f"data-freshness {label} {value!r} is non-canonical")
    return canonical_value


def _build_assessment(
    *,
    status: DataFreshnessEvidenceStatus,
    classification: OperationalEvidenceClassification,
    diagnostics: tuple[str, ...],
    source: str,
) -> DataFreshnessEvidenceAssessment:
    safe_source = source.strip() or "UNAVAILABLE: missing data-freshness source"
    summary = "; ".join(diagnostics) if diagnostics else "data-freshness unavailable"
    return DataFreshnessEvidenceAssessment(
        status=status,
        classification=classification,
        diagnostics=diagnostics,
        evidence_item=OperationalEvidenceItem(
            blocker_id="data_freshness",
            classification=classification,
            summary=summary,
            source=safe_source,
        ),
    )


def _evidence_source(
    evidence: DataFreshnessEvidence | None,
    *,
    fallback_source: str,
) -> str:
    if evidence is None:
        return fallback_source
    return evidence.source
