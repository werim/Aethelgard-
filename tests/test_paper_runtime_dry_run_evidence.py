import json
from typing import Any

from src.reporting.paper_runtime_dry_run_evidence import (
    PaperRuntimeDryRunClassification,
    PaperRuntimeDryRunEvidence,
    classify_paper_runtime_dry_run_evidence,
    docs_may_claim_live_readiness_from_dry_run,
)


def _measured_evidence(**overrides: object) -> PaperRuntimeDryRunEvidence:
    values: dict[str, Any] = {
        "source": "Codex local python main.py",
        "run_command": "python main.py",
        "runtime_output_source": "Codex terminal output",
        "run_log_source": "foundation_runtime_initialized metadata",
        "paper_only_mode": True,
        "research_only_readiness": True,
        "startup_metadata_observed": True,
        "dry_run_log_observed": True,
    }
    values.update(overrides)
    return PaperRuntimeDryRunEvidence(**values)


def test_user_provided_runtime_output_is_not_measured_local_proof() -> None:
    assessment = classify_paper_runtime_dry_run_evidence(
        PaperRuntimeDryRunEvidence(
            source="user pasted python main.py output",
            runtime_output_source="chat transcript",
            user_provided_runtime_output=True,
            paper_only_mode=True,
            research_only_readiness=True,
        )
    )

    assert (
        assessment.classification
        is PaperRuntimeDryRunClassification.USER_PROVIDED_RUNTIME_OUTPUT
    )
    assert assessment.measured is False
    assert assessment.user_provided is True


def test_user_reported_dry_run_ok_is_not_measured_proof() -> None:
    assessment = classify_paper_runtime_dry_run_evidence(
        PaperRuntimeDryRunEvidence(
            source="user says python main.py ran",
            user_reported_dry_run_ok=True,
        )
    )

    assert (
        assessment.classification
        is PaperRuntimeDryRunClassification.USER_REPORTED_DRY_RUN_OK
    )
    assert assessment.measured is False


def test_missing_dry_run_evidence_remains_unavailable() -> None:
    assessment = classify_paper_runtime_dry_run_evidence(
        PaperRuntimeDryRunEvidence(source="no local command output")
    )

    assert (
        assessment.classification
        is PaperRuntimeDryRunClassification.UNAVAILABLE_DRY_RUN
    )
    assert assessment.measured is False


def test_missing_dry_run_logs_remain_unavailable() -> None:
    assessment = classify_paper_runtime_dry_run_evidence(
        _measured_evidence(dry_run_log_observed=False, run_log_source=None)
    )

    assert (
        assessment.classification
        is PaperRuntimeDryRunClassification.UNAVAILABLE_DRY_RUN_LOG
    )


def test_clean_codex_measured_paper_only_dry_run_classifies_as_measured() -> None:
    assessment = classify_paper_runtime_dry_run_evidence(_measured_evidence())

    assert (
        assessment.classification
        is PaperRuntimeDryRunClassification.MEASURED_PAPER_DRY_RUN
    )
    assert assessment.measured is True
    assert assessment.violation is False
    assert assessment.permits_live_readiness_claim is False


def test_exchange_market_or_order_path_classifies_as_violation() -> None:
    for field in (
        "live_mode_observed",
        "exchange_connection_observed",
        "market_fetch_observed",
        "order_path_observed",
        "exchange_mutation_observed",
    ):
        assessment = classify_paper_runtime_dry_run_evidence(
            _measured_evidence(**{field: True})
        )

        assert assessment.classification is (
            PaperRuntimeDryRunClassification.VIOLATION_LIVE_OR_EXCHANGE_PATH
        )
        assert assessment.violation is True


def test_secret_or_readiness_path_classifies_as_violation() -> None:
    for field in ("secret_access_observed", "readiness_claim_observed"):
        assessment = classify_paper_runtime_dry_run_evidence(
            _measured_evidence(**{field: True})
        )

        assert assessment.classification is (
            PaperRuntimeDryRunClassification.VIOLATION_SECRET_OR_READINESS_PATH
        )
        assert assessment.violation is True


def test_measured_dry_run_never_permits_live_or_production_readiness_claims() -> None:
    assessment = classify_paper_runtime_dry_run_evidence(_measured_evidence())

    assert assessment.permits_live_readiness_claim is False
    assert docs_may_claim_live_readiness_from_dry_run(assessment) is False


def test_payload_is_deterministic_and_json_compatible() -> None:
    assessment = classify_paper_runtime_dry_run_evidence(_measured_evidence())

    payload = assessment.payload()

    assert payload == assessment.payload()
    assert json.loads(json.dumps(payload, sort_keys=True)) == payload
