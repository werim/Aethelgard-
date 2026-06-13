import json

import pytest

from src.reporting.operational_evidence import (
    DeploymentBlockerStatus,
    OperationalDeploymentStatus,
    OperationalEvidenceClassification,
    OperationalEvidenceGateError,
    OperationalEvidenceItem,
    assert_operational_deployment_not_blocked,
    evaluate_operational_evidence_gate,
    operational_evidence_gate_json,
    render_deployment_blocker_matrix_markdown,
)


def _measured_items() -> tuple[OperationalEvidenceItem, ...]:
    return tuple(
        OperationalEvidenceItem(
            blocker_id=blocker_id,
            classification=OperationalEvidenceClassification.MEASURED,
            summary=f"measured evidence for {blocker_id}",
            source="test fixture",
        )
        for blocker_id in (
            "audit_trail_integrity",
            "ci_validation",
            "data_freshness",
            "execution_cost_evidence",
            "paper_runtime_reconciliation",
            "risk_control_enforcement",
        )
    )


def test_gate5a_blocks_when_required_evidence_is_missing() -> None:
    result = evaluate_operational_evidence_gate(())

    assert result.status is OperationalDeploymentStatus.DEPLOYMENT_BLOCKED
    assert result.paper_deployment_blocked is True
    assert all(row.status is DeploymentBlockerStatus.BLOCKED for row in result.matrix)
    assert any(
        "execution_cost_evidence evidence is missing" in diagnostic
        for diagnostic in result.diagnostics
    )

    with pytest.raises(OperationalEvidenceGateError):
        assert_operational_deployment_not_blocked(result)


def test_gate5a_blocks_modeled_or_unavailable_evidence() -> None:
    evidence = list(_measured_items())
    evidence[3] = OperationalEvidenceItem(
        blocker_id="execution_cost_evidence",
        classification=OperationalEvidenceClassification.MODELED,
        summary="modeled fee table only",
        source="test fixture",
    )

    result = evaluate_operational_evidence_gate(tuple(evidence))
    cost_row = next(
        row for row in result.matrix if row.blocker_id == "execution_cost_evidence"
    )

    assert result.paper_deployment_blocked is True
    assert cost_row.status is DeploymentBlockerStatus.BLOCKED
    assert cost_row.evidence_classification is OperationalEvidenceClassification.MODELED
    assert "requires MEASURED evidence" in cost_row.diagnostics[0]


def test_gate5a_clears_only_when_all_blockers_have_measured_evidence() -> None:
    result = evaluate_operational_evidence_gate(_measured_items())

    assert result.status is OperationalDeploymentStatus.DEPLOYMENT_NOT_BLOCKED
    assert result.paper_deployment_blocked is False
    assert all(row.status is DeploymentBlockerStatus.CLEARED for row in result.matrix)
    assert_operational_deployment_not_blocked(result)


def test_gate5a_json_is_deterministic_and_contains_no_performance_metrics() -> None:
    result = evaluate_operational_evidence_gate(_measured_items())
    payload = json.loads(operational_evidence_gate_json(result))

    assert list(payload) == [
        "diagnostics",
        "matrix",
        "paper_deployment_blocked",
        "status",
    ]
    forbidden = {"pnl", "profit", "returns", "sharpe", "drawdown", "win_rate"}
    payload_keys = set(payload) | {key for row in payload["matrix"] for key in row}

    assert forbidden.isdisjoint(payload_keys)


def test_gate5a_markdown_preserves_safety_boundary_text() -> None:
    result = evaluate_operational_evidence_gate(())
    markdown = render_deployment_blocker_matrix_markdown(result)

    assert "PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY" in markdown
    assert "Unknown execution costs are not zero" in markdown
    assert "Backtest performance alone does not prove production readiness" in markdown
