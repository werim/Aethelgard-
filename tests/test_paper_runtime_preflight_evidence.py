from typing import Any

from src.reporting.paper_runtime_preflight_evidence import (
    PaperRuntimePreflightClassification,
    PaperRuntimePreflightEvidence,
    classify_paper_runtime_preflight_evidence,
    docs_may_claim_runtime_readiness,
)


def _measured_evidence(**overrides: object) -> PaperRuntimePreflightEvidence:
    values: dict[str, Any] = {
        "source": "python main.py observed locally",
        "startup_command": "python main.py",
        "runtime_log_source": "foundation_runtime_initialized JSON metadata",
        "startup_run_observed": True,
        "startup_exit_code": 0,
        "runtime_log_observed": True,
        "paper_only_mode_observed": True,
        "readiness_not_approved_observed": True,
        "no_secret_access_observed": True,
        "no_exchange_connection_observed": True,
        "no_market_fetch_observed": True,
        "no_order_path_observed": True,
        "no_strategy_alpha_observed": True,
        "no_optimizer_observed": True,
    }
    values.update(overrides)
    return PaperRuntimePreflightEvidence(**values)


def test_measured_safe_startup_requires_all_bounded_runtime_observations() -> None:
    assessment = classify_paper_runtime_preflight_evidence(_measured_evidence())

    assert (
        assessment.classification
        is PaperRuntimePreflightClassification.MEASURED_SAFE_STARTUP
    )
    assert assessment.measured is True
    assert assessment.violation is False
    assert assessment.permits_readiness_approval is False
    assert docs_may_claim_runtime_readiness(assessment) is False
    assert assessment.payload()["classification"] == "MEASURED_SAFE_STARTUP"


def test_user_reported_startup_is_not_measured_runtime_proof() -> None:
    assessment = classify_paper_runtime_preflight_evidence(
        PaperRuntimePreflightEvidence(
            source="user says startup is green",
            user_reported_startup_ok=True,
        )
    )

    assert (
        assessment.classification
        is PaperRuntimePreflightClassification.USER_REPORTED_STARTUP_OK
    )
    assert assessment.measured is False


def test_missing_startup_run_stays_unavailable() -> None:
    assessment = classify_paper_runtime_preflight_evidence(
        PaperRuntimePreflightEvidence(source="import-only check")
    )

    assert (
        assessment.classification
        is PaperRuntimePreflightClassification.UNAVAILABLE_STARTUP_RUN
    )


def test_missing_runtime_log_stays_unavailable_after_successful_run() -> None:
    assessment = classify_paper_runtime_preflight_evidence(
        _measured_evidence(runtime_log_observed=False, runtime_log_source=None)
    )

    assert (
        assessment.classification
        is PaperRuntimePreflightClassification.UNAVAILABLE_RUNTIME_LOG
    )


def test_live_mode_or_readiness_approval_is_violation() -> None:
    assessment = classify_paper_runtime_preflight_evidence(
        _measured_evidence(live_mode_enabled=True)
    )

    assert (
        assessment.classification
        is PaperRuntimePreflightClassification.VIOLATION_LIVE_RUNTIME_ENABLED
    )
    assert assessment.violation is True


def test_secret_exchange_fetch_order_or_external_mutation_is_violation() -> None:
    for field in (
        "secret_access_attempted",
        "credentials_required",
        "exchange_connection_attempted",
        "market_fetch_attempted",
        "order_placement_or_cancel_attempted",
        "external_state_mutation_attempted",
    ):
        assessment = classify_paper_runtime_preflight_evidence(
            _measured_evidence(**{field: True})
        )

        assert assessment.classification is (
            PaperRuntimePreflightClassification.VIOLATION_SECRET_OR_EXCHANGE_ACCESS
        )
        assert assessment.violation is True


def test_strategy_alpha_or_optimizer_execution_is_violation() -> None:
    assessment = classify_paper_runtime_preflight_evidence(
        _measured_evidence(optimizer_executed=True)
    )

    assert (
        assessment.classification
        is PaperRuntimePreflightClassification.VIOLATION_LIVE_RUNTIME_ENABLED
    )
