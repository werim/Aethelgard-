import json

from src.reporting.operational_evidence import (
    OperationalDeploymentStatus,
    OperationalEvidenceClassification,
    OperationalEvidenceItem,
    evaluate_operational_evidence_gate,
)
from src.reporting.risk_control_evidence import (
    RiskControlEnforcementEvidence,
    RiskControlEvidenceStatus,
    RiskControlPolicyEvidence,
    assess_risk_control_enforcement_for_gate5a,
    risk_control_evidence_assessment_json,
)

REQUIRED_POLICIES = (
    "max_position_notional",
    "max_daily_loss",
    "circuit_breaker",
)


def _measured_evidence_item(blocker_id: str) -> OperationalEvidenceItem:
    return OperationalEvidenceItem(
        blocker_id=blocker_id,
        classification=OperationalEvidenceClassification.MEASURED,
        summary=f"{blocker_id} measured evidence",
        source=f"unit://{blocker_id}",
    )


def _complete_gate_evidence(
    risk_item: OperationalEvidenceItem,
) -> tuple[OperationalEvidenceItem, ...]:
    return (
        _measured_evidence_item("audit_trail_integrity"),
        _measured_evidence_item("ci_validation"),
        _measured_evidence_item("data_freshness"),
        _measured_evidence_item("execution_cost_evidence"),
        _measured_evidence_item("paper_runtime_reconciliation"),
        risk_item,
    )


def test_measured_risk_control_evidence_clears_gate5a_blocker() -> None:
    evidence = RiskControlEnforcementEvidence(
        source="unit://risk-policy-evidence",
        required_policy_ids=REQUIRED_POLICIES,
        observed_policies=tuple(
            RiskControlPolicyEvidence(policy_id=policy_id, enforced=True)
            for policy_id in REQUIRED_POLICIES
        ),
    )

    assessment = assess_risk_control_enforcement_for_gate5a(evidence)
    result = evaluate_operational_evidence_gate(
        _complete_gate_evidence(assessment.evidence_item)
    )

    assert assessment.status is RiskControlEvidenceStatus.ENFORCEMENT_MEASURED
    assert assessment.classification is OperationalEvidenceClassification.MEASURED
    assert assessment.evidence_item.blocker_id == "risk_control_enforcement"
    assert result.status is OperationalDeploymentStatus.DEPLOYMENT_NOT_BLOCKED


def test_missing_risk_control_evidence_remains_unavailable() -> None:
    assessment = assess_risk_control_enforcement_for_gate5a(
        None,
        source="unit://missing-risk-evidence",
    )

    assert assessment.status is RiskControlEvidenceStatus.UNAVAILABLE
    assert assessment.classification is OperationalEvidenceClassification.UNAVAILABLE
    assert assessment.evidence_item.blocker_id == "risk_control_enforcement"
    assert "risk-control enforcement evidence is unavailable" in assessment.diagnostics


def test_unenforced_required_policy_remains_unavailable() -> None:
    evidence = RiskControlEnforcementEvidence(
        source="unit://risk-policy-evidence",
        required_policy_ids=REQUIRED_POLICIES,
        observed_policies=(
            RiskControlPolicyEvidence("max_position_notional", True),
            RiskControlPolicyEvidence("max_daily_loss", False),
            RiskControlPolicyEvidence("circuit_breaker", True),
        ),
    )

    assessment = assess_risk_control_enforcement_for_gate5a(evidence)

    assert assessment.status is RiskControlEvidenceStatus.UNAVAILABLE
    assert assessment.classification is OperationalEvidenceClassification.UNAVAILABLE
    assert "required risk-control policy 'max_daily_loss' is not enforced" in (
        assessment.diagnostics
    )


def test_missing_required_policy_remains_unavailable() -> None:
    evidence = RiskControlEnforcementEvidence(
        source="unit://risk-policy-evidence",
        required_policy_ids=REQUIRED_POLICIES,
        observed_policies=(
            RiskControlPolicyEvidence("max_position_notional", True),
            RiskControlPolicyEvidence("circuit_breaker", True),
        ),
    )

    assessment = assess_risk_control_enforcement_for_gate5a(evidence)

    assert assessment.status is RiskControlEvidenceStatus.UNAVAILABLE
    assert "required risk-control policy 'max_daily_loss' is missing" in (
        assessment.diagnostics
    )


def test_malformed_policy_ids_remain_unavailable() -> None:
    evidence = RiskControlEnforcementEvidence(
        source=" ",
        required_policy_ids=("max_position_notional", " max_daily_loss", ""),
        observed_policies=(
            RiskControlPolicyEvidence("max_position_notional", True),
            RiskControlPolicyEvidence("max_position_notional", True),
            RiskControlPolicyEvidence(" circuit_breaker", True),
        ),
    )

    assessment = assess_risk_control_enforcement_for_gate5a(evidence)

    assert assessment.status is RiskControlEvidenceStatus.UNAVAILABLE
    assert "risk-control evidence source is missing" in assessment.diagnostics
    assert "required risk-control policy id ' max_daily_loss' is non-canonical" in (
        assessment.diagnostics
    )
    assert "required risk-control policy id is empty" in assessment.diagnostics
    assert "observed risk-control policy 'max_position_notional' is duplicated" in (
        assessment.diagnostics
    )


def test_risk_control_evidence_json_is_deterministic_and_non_performance() -> None:
    assessment = assess_risk_control_enforcement_for_gate5a(
        RiskControlEnforcementEvidence(
            source="unit://risk-policy-evidence",
            required_policy_ids=REQUIRED_POLICIES,
            observed_policies=tuple(
                RiskControlPolicyEvidence(policy_id=policy_id, enforced=True)
                for policy_id in REQUIRED_POLICIES
            ),
        )
    )

    payload = json.loads(risk_control_evidence_assessment_json(assessment))
    encoded = risk_control_evidence_assessment_json(assessment)

    assert payload["classification"] == "MEASURED"
    assert encoded == risk_control_evidence_assessment_json(assessment)
    for forbidden in ("pnl", "profit", "returns", "win_rate", "sharpe"):
        assert forbidden not in encoded.lower()
