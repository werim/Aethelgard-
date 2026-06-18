"""Gate 5B-4 runtime artifact schema ledger consistency tests."""

from __future__ import annotations

from pathlib import Path

from src.reporting.runtime_artifact_writer import (
    REQUIRED_SAFETY_BOUNDARY,
    REQUIRED_UNAVAILABLE_EVIDENCE,
    runtime_artifact_payload,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = PROJECT_ROOT / "docs/gates/gate5b_runtime_artifact_writer.md"

REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "source",
    "mode",
    "readiness",
    "project_name",
    "random_seed",
    "determinism_scope",
    "safety_boundary",
    "evidence_classification",
    "unavailable_evidence",
}

REQUIRED_SAFETY_DOCUMENTATION_PHRASES = (
    "Gate 5B-4 is a ledger consistency check only.",
    "Local runtime artifacts are evidence artifacts, not production approval.",
    "Runtime artifact schema documentation must not imply live readiness.",
    "Missing evidence remains UNAVAILABLE.",
    "Unknown execution costs are not zero.",
    "Backtest performance alone does not prove production readiness.",
    (
        "No secrets, exchange connection, market fetch, order path, optimizer, "
        "strategy alpha, performance claim, or readiness approval is added."
    ),
)


def _metadata() -> dict[str, object]:
    return {
        "determinism_scope": "caller-supplied startup metadata only",
        "evidence_classification": "MEASURED_PAPER_DRY_RUN",
        "mode": "PAPER_ONLY",
        "project_name": "Aethelgard",
        "random_seed": 42,
        "readiness": "RESEARCH_ONLY",
        "source": "tests/test_runtime_artifact_schema_ledger_consistency.py",
    }


def test_runtime_artifact_documented_schema_matches_writer_payload() -> None:
    payload = runtime_artifact_payload(_metadata())
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert set(payload) >= REQUIRED_TOP_LEVEL_FIELDS
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        assert f"`{field}`" in doc

    safety_boundary = payload["safety_boundary"]
    assert safety_boundary == REQUIRED_SAFETY_BOUNDARY
    for field in REQUIRED_SAFETY_BOUNDARY:
        assert f"`{field}`" in doc

    unavailable_evidence = payload["unavailable_evidence"]
    assert unavailable_evidence == REQUIRED_UNAVAILABLE_EVIDENCE
    for field in REQUIRED_UNAVAILABLE_EVIDENCE:
        assert f"`{field}`" in doc


def test_runtime_artifact_schema_ledger_preserves_safety_phrases() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")

    for phrase in REQUIRED_SAFETY_DOCUMENTATION_PHRASES:
        assert phrase in doc

    assert "CLI wrapper is intentionally deferred" in doc
    assert "does not add a CLI wrapper or change `python main.py` behavior" in doc
