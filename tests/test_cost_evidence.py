import json
from dataclasses import replace

import pytest

from src.backtest.cost_evidence import (
    CostEvidenceCategory,
    CostEvidenceClassification,
    CostEvidenceError,
    CostEvidenceRecord,
    assert_can_publish_net_metrics,
    cost_evidence_gate_json,
    evaluate_cost_evidence_gate,
    render_cost_evidence_markdown,
    unavailable_cost_evidence,
)


def modeled_record(category: CostEvidenceCategory) -> CostEvidenceRecord:
    return CostEvidenceRecord(
        category=category,
        classification=CostEvidenceClassification.MODELED,
        source="test cost model v1",
        value=0.001,
        unit="rate",
        observation_window="fixture-window",
        assumptions=(f"{category.value} modeled from conservative fixture",),
        limitations=("not measured from live exchange fills",),
    )


def measured_record(category: CostEvidenceCategory) -> CostEvidenceRecord:
    return CostEvidenceRecord(
        category=category,
        classification=CostEvidenceClassification.MEASURED,
        source="persisted paper audit fixture",
        value=0.001,
        unit="rate",
        observed_at="2026-06-05T12:00:00Z",
        limitations=("fixture measurement only",),
    )


def all_measured_records() -> tuple[CostEvidenceRecord, ...]:
    return tuple(measured_record(category) for category in CostEvidenceCategory)


def records_with_unavailable(
    category: CostEvidenceCategory,
) -> tuple[CostEvidenceRecord, ...]:
    return tuple(
        CostEvidenceRecord(
            category=item,
            classification=CostEvidenceClassification.UNAVAILABLE,
            source="test fixture missing evidence",
            unavailable_reason=f"{item.value} not measured or modeled",
        )
        if item is category
        else measured_record(item)
        for item in CostEvidenceCategory
    )


@pytest.mark.parametrize(
    "category",
    [
        CostEvidenceCategory.FEES,
        CostEvidenceCategory.SLIPPAGE,
        CostEvidenceCategory.SPREAD,
    ],
)
def test_missing_required_cost_blocks_net_performance_metrics(
    category: CostEvidenceCategory,
) -> None:
    result = evaluate_cost_evidence_gate(records_with_unavailable(category))
    assert result.passed is False
    assert result.can_publish_net_metrics is False
    assert category in result.blocking_categories
    with pytest.raises(CostEvidenceError, match="cannot publish net metrics"):
        assert_can_publish_net_metrics(result)


def test_missing_funding_blocks_when_funding_is_required() -> None:
    records = records_with_unavailable(CostEvidenceCategory.FUNDING)
    result = evaluate_cost_evidence_gate(records)
    assert CostEvidenceCategory.FUNDING in result.unavailable_categories
    assert result.can_publish_net_metrics is False


def test_missing_latency_blocks_execution_realism_metrics() -> None:
    records = records_with_unavailable(CostEvidenceCategory.LATENCY)
    result = evaluate_cost_evidence_gate(records)
    assert CostEvidenceCategory.LATENCY in result.blocking_categories
    assert result.metric_label == "NET_METRICS_UNAVAILABLE"


def test_unavailable_evidence_is_not_treated_as_zero() -> None:
    record = CostEvidenceRecord(
        category=CostEvidenceCategory.FEES,
        classification=CostEvidenceClassification.UNAVAILABLE,
        source="test fixture",
        value=0.0,
        unavailable_reason="not measured",
    )
    with pytest.raises(CostEvidenceError, match="cannot carry value"):
        record.validate()


def test_modeled_evidence_requires_assumptions_and_labeling() -> None:
    invalid = replace(modeled_record(CostEvidenceCategory.FEES), assumptions=())
    with pytest.raises(CostEvidenceError, match="requires assumptions"):
        invalid.validate()

    records = tuple(modeled_record(category) for category in CostEvidenceCategory)
    result = evaluate_cost_evidence_gate(records)
    assert result.passed is True
    assert result.metric_label == "NET_MODELED_COST_METRICS"
    assert set(result.modeled_categories) == set(CostEvidenceCategory)


def test_measured_evidence_passes_when_all_required_categories_are_present() -> None:
    result = evaluate_cost_evidence_gate(all_measured_records())
    assert result.passed is True
    assert result.can_publish_net_metrics is True
    assert result.metric_label == "NET_MEASURED_COST_METRICS"
    assert set(result.measured_categories) == set(CostEvidenceCategory)
    assert_can_publish_net_metrics(result)


def test_no_cost_evidence_fails_closed() -> None:
    result = evaluate_cost_evidence_gate(())
    assert result.passed is False
    assert set(result.blocking_categories) == set(CostEvidenceCategory)
    assert "no cost evidence records supplied" in " ".join(result.diagnostics)


def test_reporting_shows_unavailable_evidence_clearly() -> None:
    result = evaluate_cost_evidence_gate(
        records_with_unavailable(CostEvidenceCategory.SPREAD),
        gross_metrics_explicitly_labeled=True,
    )
    markdown = render_cost_evidence_markdown(result)
    assert "`spread` | `UNAVAILABLE`" in markdown
    assert "spread not measured or modeled" in markdown
    assert "NET_METRICS_UNAVAILABLE" in markdown
    assert result.can_publish_gross_metrics is True


def test_readiness_approval_remains_blocked_with_unavailable_costs() -> None:
    result = evaluate_cost_evidence_gate(unavailable_cost_evidence("not collected"))
    assert result.readiness_allowed is False
    assert result.can_publish_net_metrics is False


def test_gate_result_serialization_is_deterministic() -> None:
    result = evaluate_cost_evidence_gate(all_measured_records())
    first = cost_evidence_gate_json(result)
    second = cost_evidence_gate_json(result)
    assert first == second
    payload = json.loads(first)
    assert payload["readiness_allowed"] is False
    assert payload["can_publish_net_metrics"] is True
