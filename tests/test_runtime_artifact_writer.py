"""Gate 5B-3 tests for the offline runtime artifact writer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from src.reporting.runtime_artifact_writer import (
    REQUIRED_SAFETY_BOUNDARY,
    REQUIRED_UNAVAILABLE_EVIDENCE,
    RuntimeArtifactWriterError,
    runtime_artifact_payload,
    write_runtime_artifact,
)


def _metadata() -> dict[str, object]:
    return {
        "determinism_scope": "caller-supplied startup metadata only",
        "evidence_classification": "MEASURED_PAPER_DRY_RUN",
        "generated_at_utc": "2026-06-18T00:00:00Z",
        "mode": "PAPER_ONLY",
        "project_name": "Aethelgard",
        "random_seed": 42,
        "readiness": "RESEARCH_ONLY",
        "source": "tests/test_runtime_artifact_writer.py",
    }


def test_artifact_json_is_deterministic_parseable_and_newline_terminated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    first_path = write_runtime_artifact(
        Path("reports/runtime_startup_latest.json"), _metadata()
    )
    first = first_path.read_text(encoding="utf-8")
    second_path = write_runtime_artifact(
        Path("reports/runtime_startup_latest.json"), _metadata()
    )
    second = second_path.read_text(encoding="utf-8")

    assert first == second
    assert first.endswith("\n")
    assert json.loads(first) == runtime_artifact_payload(_metadata())


def test_artifact_writer_writes_only_bounded_paper_research_safety_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    path = write_runtime_artifact(Path("reports/nested/runtime.json"), _metadata())
    payload = _read(path)

    assert payload["mode"] == "PAPER_ONLY"
    assert payload["readiness"] == "RESEARCH_ONLY"
    assert payload["safety_boundary"] == REQUIRED_SAFETY_BOUNDARY
    assert payload["safety_boundary"]["paper_only"] is True
    assert payload["safety_boundary"]["research_only"] is True
    assert payload["safety_boundary"]["live_trading_enabled"] is False
    assert payload["safety_boundary"]["readiness_approval"] is False


def test_artifact_records_all_unavailable_evidence_explicitly() -> None:
    payload = runtime_artifact_payload(_metadata())

    assert payload["unavailable_evidence"] == REQUIRED_UNAVAILABLE_EVIDENCE
    assert set(_mapping(payload["unavailable_evidence"])) == {
        "ci_workflow_artifacts",
        "exchange_audit",
        "market_data_completeness",
        "execution_realism",
        "profitability",
        "live_readiness",
        "production_readiness",
    }


@pytest.mark.parametrize(
    "forbidden_key",
    [
        "api_key",
        "secret",
        "access_token",
        "pnl",
        "win_rate",
        "sharpe",
        "drawdown",
        "returns",
        "strategy_alpha",
        "profitability_claim",
    ],
)
def test_artifact_rejects_secrets_performance_alpha_and_profitability_claims(
    forbidden_key: str,
) -> None:
    metadata = _metadata() | {forbidden_key: "unsafe"}

    with pytest.raises(RuntimeArtifactWriterError):
        runtime_artifact_payload(metadata)


def test_artifact_does_not_imply_live_or_production_readiness() -> None:
    payload = runtime_artifact_payload(_metadata())

    text = json.dumps(payload, sort_keys=True).lower()
    assert "live_ready" not in text
    assert "production_ready" not in text
    assert payload["readiness"] == "RESEARCH_ONLY"
    assert payload["unavailable_evidence"] == REQUIRED_UNAVAILABLE_EVIDENCE


@pytest.mark.parametrize(
    "unsafe_path",
    [
        Path("runtime.json"),
        Path("data/runtime.json"),
        Path("reports/../runtime.json"),
        Path("reports/runtime.txt"),
        Path("/tmp/runtime.json"),
    ],
)
def test_unsafe_paths_fail_closed(
    unsafe_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(RuntimeArtifactWriterError):
        write_runtime_artifact(unsafe_path, _metadata())


def test_unsafe_runtime_claims_fail_closed() -> None:
    for key, value in (
        ("mode", "LIVE"),
        ("readiness", "PRODUCTION_READY"),
        ("evidence_classification", "PROFITABLE"),
    ):
        metadata = _metadata() | {key: value}
        with pytest.raises(RuntimeArtifactWriterError):
            runtime_artifact_payload(metadata)


def _read(path: Path) -> dict[str, Any]:
    return _mapping(json.loads(path.read_text(encoding="utf-8")))


def _mapping(value: object) -> dict[str, Any]:
    assert isinstance(value, dict)
    return value
