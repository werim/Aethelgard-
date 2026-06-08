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
    guarded_performance_report_json,
    guarded_performance_report_payload,
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


def metric_candidate_payload() -> dict[str, object]:
    return {
        "pnl": 0,
        "returns": 0,
        "win_rate": 0,
        "sharpe": 0,
        "drawdown": 0,
        "expectancy": 0,
        "alpha": 0,
        "beta": 0,
        "equity": 0,
        "balance": 0,
        "position": "NONE",
        "signal": "NONE",
        "trade": "NONE",
        "fill": "NONE",
        "fee": 0,
        "slippage": 0,
        "latency": 0,
        "readiness": "READY",
    }


def forbidden_publication_fields() -> set[str]:
    return {
        "pnl",
        "returns",
        "win_rate",
        "sharpe",
        "drawdown",
        "expectancy",
        "alpha",
        "beta",
        "equity",
        "balance",
        "position",
        "signal",
        "trade",
        "fill",
        "fee",
        "slippage",
        "latency",
        "readiness",
    }


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


def test_blocked_eligibility_prevents_performance_field_publication() -> None:
    eligibility = evaluate_metric_publication_eligibility(
        metadata_with_unavailable_execution()
    )

    payload = guarded_performance_report_payload(
        eligibility,
        metric_candidate_payload(),
    )

    assert payload == {
        "diagnostics": list(eligibility.diagnostics),
        "refusal_reason": eligibility.refusal_reason,
        "status": MetricPublicationStatus.METRICS_BLOCKED.value,
        "unavailable_execution_assumptions": list(
            eligibility.unavailable_execution_assumptions
        ),
    }
    assert forbidden_publication_fields().isdisjoint(payload)


def test_blocked_publication_keeps_unavailable_evidence_unavailable() -> None:
    eligibility = evaluate_metric_publication_eligibility(
        metadata_with_unavailable_execution()
    )
    payload = json.loads(
        guarded_performance_report_json(eligibility, metric_candidate_payload())
    )

    assert payload["unavailable_execution_assumptions"] == sorted(
        assumption.value for assumption in REQUIRED_EXECUTION_ASSUMPTIONS
    )
    assert "0" not in guarded_performance_report_json(
        eligibility,
        metric_candidate_payload(),
    )


def test_guard_does_not_import_execution_or_order_modules() -> None:
    import sys

    saved_execution_modules = {
        name: module
        for name, module in list(sys.modules.items())
        if name == "src.execution" or name.startswith("src.execution.")
    }
    for name in saved_execution_modules:
        del sys.modules[name]

    try:
        eligibility = evaluate_metric_publication_eligibility(
            metadata_with_unavailable_execution()
        )
        guarded_performance_report_payload(eligibility, metric_candidate_payload())

        loaded_execution_modules = {
            name
            for name in sys.modules
            if name == "src.execution" or name.startswith("src.execution.")
        }
        loaded_order_modules = {
            name for name in loaded_execution_modules if "order" in name
        }

        assert loaded_execution_modules == set()
        assert loaded_order_modules == set()
    finally:
        sys.modules.update(saved_execution_modules)


def test_paper_only_research_only_posture_remains_in_guard_diagnostics() -> None:
    eligibility = evaluate_metric_publication_eligibility(
        metadata_with_unavailable_execution()
    )
    payload = guarded_performance_report_payload(
        eligibility,
        metric_candidate_payload(),
    )

    assert payload["status"] == MetricPublicationStatus.METRICS_BLOCKED.value
    assert "READY" not in json.dumps(payload, sort_keys=True)
