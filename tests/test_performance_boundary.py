import json
from dataclasses import replace

from src.backtest.foundation import (
    REQUIRED_EXECUTION_ASSUMPTIONS,
    BacktestRunMetadata,
    EvidenceClassification,
    ExecutionAssumption,
    ExecutionEvidence,
    unavailable_execution_assumptions,
)
from src.reporting.performance_boundary import (
    MetricPublicationStatus,
    evaluate_metric_publication_eligibility,
    metric_publication_eligibility_json,
)

SHA_A = "a" * 64
SHA_B = "b" * 64


def metadata_with_unavailable_execution() -> BacktestRunMetadata:
    return BacktestRunMetadata(
        run_id="run-20260607-btcusdt-1h",
        dataset_fingerprint=SHA_A,
        symbol="BTCUSDT",
        timeframe="1h",
        start_ts="2026-01-01T00:00:00Z",
        end_ts="2026-02-01T00:00:00Z",
        seed=42,
        config_hash=SHA_B,
        code_version="0.20.0",
        created_at="2026-06-07T20:00:00Z",
        execution_assumptions=unavailable_execution_assumptions(
            "execution evidence has not been measured or modeled"
        ),
    )


def measured_or_modeled_execution() -> dict[ExecutionAssumption, ExecutionEvidence]:
    evidence: dict[ExecutionAssumption, ExecutionEvidence] = {}
    for index, assumption in enumerate(REQUIRED_EXECUTION_ASSUMPTIONS):
        if index % 2 == 0:
            evidence[assumption] = ExecutionEvidence(
                classification=EvidenceClassification.MEASURED,
                description=f"{assumption.value} measured for boundary test",
                source="unit-test-ledger",
                value="measured-placeholder",
            )
        else:
            evidence[assumption] = ExecutionEvidence(
                classification=EvidenceClassification.MODELED,
                description=f"{assumption.value} modeled for boundary test",
                value="modeled-placeholder",
            )
    return evidence


def test_unavailable_execution_evidence_blocks_metric_publication() -> None:
    eligibility = evaluate_metric_publication_eligibility(
        metadata_with_unavailable_execution()
    )

    assert eligibility.status is MetricPublicationStatus.METRICS_BLOCKED
    assert eligibility.can_publish_metrics is False
    assert eligibility.unavailable_execution_assumptions == tuple(
        sorted(assumption.value for assumption in REQUIRED_EXECUTION_ASSUMPTIONS)
    )
    assert eligibility.refusal_reason is not None
    assert "cannot produce performance results" in eligibility.refusal_reason


def test_measured_or_modeled_evidence_allows_eligibility_only() -> None:
    metadata = replace(
        metadata_with_unavailable_execution(),
        execution_assumptions=measured_or_modeled_execution(),
    )

    eligibility = evaluate_metric_publication_eligibility(metadata)

    assert eligibility.status is MetricPublicationStatus.METRICS_PUBLISHABLE
    assert eligibility.can_publish_metrics is True
    assert eligibility.unavailable_execution_assumptions == ()
    assert eligibility.refusal_reason is None


def test_unavailable_costs_are_not_converted_to_zero() -> None:
    assumptions = unavailable_execution_assumptions("not measured")
    assumptions[ExecutionAssumption.FEES] = ExecutionEvidence(
        classification=EvidenceClassification.UNAVAILABLE,
        description="fees unavailable",
        value=0.0,
        unavailable_reason="not measured",
    )
    metadata = replace(
        metadata_with_unavailable_execution(),
        execution_assumptions=assumptions,
    )

    eligibility = evaluate_metric_publication_eligibility(metadata)
    payload = eligibility.payload()

    assert eligibility.status is MetricPublicationStatus.METRICS_BLOCKED
    assert eligibility.can_publish_metrics is False
    assert payload["refusal_reason"] == (
        "metadata validation failed closed: unavailable evidence cannot carry value"
    )
    assert "0.0" not in metric_publication_eligibility_json(eligibility)


def test_deterministic_json_output_is_stable() -> None:
    eligibility = evaluate_metric_publication_eligibility(
        metadata_with_unavailable_execution()
    )

    first = metric_publication_eligibility_json(eligibility)
    second = metric_publication_eligibility_json(eligibility)

    assert first == second
    assert list(json.loads(first)) == sorted(json.loads(first))


def test_malformed_metadata_fails_closed() -> None:
    metadata = replace(
        metadata_with_unavailable_execution(),
        dataset_fingerprint="not-a-sha",
    )

    eligibility = evaluate_metric_publication_eligibility(metadata)

    assert eligibility.status is MetricPublicationStatus.METRICS_BLOCKED
    assert eligibility.can_publish_metrics is False
    assert eligibility.refusal_reason is not None
    assert "metadata validation failed closed" in eligibility.refusal_reason


def test_no_performance_metric_fields_are_emitted() -> None:
    eligibility = evaluate_metric_publication_eligibility(
        metadata_with_unavailable_execution()
    )
    payload = json.loads(metric_publication_eligibility_json(eligibility))

    forbidden_fields = {
        "pnl",
        "returns",
        "win_rate",
        "drawdown",
        "sharpe",
        "expectancy",
        "alpha",
        "profit",
        "loss",
    }

    assert forbidden_fields.isdisjoint(payload)
    assert set(payload) == {
        "can_publish_metrics",
        "diagnostics",
        "refusal_reason",
        "status",
        "unavailable_execution_assumptions",
    }
