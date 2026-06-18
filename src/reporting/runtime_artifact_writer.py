"""Gate 5B-3 offline runtime evidence artifact writer.

This module writes caller-supplied startup/runtime metadata to a local JSON
artifact under ``reports/`` only. It does not read secrets, environment
variables, network resources, exchange state, market data, orders, strategy
logic, optimizer results, performance, or readiness approvals.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Final

SCHEMA_VERSION: Final[str] = "gate5b-runtime-artifact-writer-v1"
REPORTS_ROOT: Final[Path] = Path("reports")

REQUIRED_SAFETY_BOUNDARY: Final[dict[str, bool]] = {
    "exchange_connection": False,
    "live_trading_enabled": False,
    "market_fetch": False,
    "optimizer": False,
    "order_path": False,
    "paper_only": True,
    "performance_claim": False,
    "readiness_approval": False,
    "research_only": True,
    "secrets_exposed": False,
    "secrets_requested": False,
    "strategy_alpha": False,
}

REQUIRED_UNAVAILABLE_EVIDENCE: Final[dict[str, str]] = {
    "ci_workflow_artifacts": "UNAVAILABLE",
    "exchange_audit": "UNAVAILABLE",
    "execution_realism": "UNAVAILABLE",
    "live_readiness": "UNAVAILABLE",
    "market_data_completeness": "UNAVAILABLE",
    "production_readiness": "UNAVAILABLE",
    "profitability": "UNAVAILABLE",
}

ALLOWED_EVIDENCE_CLASSIFICATIONS: Final[frozenset[str]] = frozenset(
    {
        "MEASURED_PAPER_DRY_RUN",
        "UNAVAILABLE_DRY_RUN",
        "UNAVAILABLE_DRY_RUN_LOG",
        "USER_PROVIDED_RUNTIME_OUTPUT",
    }
)

FORBIDDEN_KEY_FRAGMENTS: Final[tuple[str, ...]] = (
    "alpha",
    "api_key",
    "credential",
    "drawdown",
    "password",
    "pnl",
    "private_key",
    "profit",
    "return",
    "secret",
    "sharpe",
    "token",
    "win_rate",
)

FORBIDDEN_TOP_LEVEL_KEYS: Final[frozenset[str]] = frozenset(
    {
        "api_key",
        "drawdown",
        "pnl",
        "profitability_claim",
        "returns",
        "secret",
        "sharpe",
        "win_rate",
    }
)


class RuntimeArtifactWriterError(ValueError):
    """Raised when runtime artifact evidence is unsafe or unbounded."""


def runtime_artifact_payload(metadata: Mapping[str, object]) -> dict[str, object]:
    """Return a deterministic bounded runtime artifact payload.

    The caller supplies all metadata. This function only validates and copies
    admitted safe fields; it never reads secrets, environment variables,
    network state, exchange state, market data, order state, strategy output,
    optimizer output, performance metrics, or readiness approvals.
    """

    _reject_forbidden_keys(metadata)
    payload: dict[str, object] = {
        "determinism_scope": _required_string(metadata, "determinism_scope"),
        "evidence_classification": _evidence_classification(metadata),
        "mode": _exact_string(metadata, "mode", "PAPER_ONLY"),
        "project_name": _required_string(metadata, "project_name"),
        "random_seed": _required_int(metadata, "random_seed"),
        "readiness": _exact_string(metadata, "readiness", "RESEARCH_ONLY"),
        "safety_boundary": dict(REQUIRED_SAFETY_BOUNDARY),
        "schema_version": SCHEMA_VERSION,
        "source": _required_string(metadata, "source"),
        "unavailable_evidence": dict(REQUIRED_UNAVAILABLE_EVIDENCE),
    }
    timestamp = metadata.get("generated_at_utc", metadata.get("startup_timestamp_utc"))
    if timestamp is not None:
        payload["generated_at_utc"] = _string_value(timestamp, "generated_at_utc")
    return payload


def write_runtime_artifact(path: Path, metadata: Mapping[str, object]) -> Path:
    """Write a deterministic local JSON runtime artifact under ``reports/``."""

    artifact_path = _safe_reports_path(path)
    payload = runtime_artifact_payload(metadata)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return artifact_path


def _safe_reports_path(path: Path) -> Path:
    if path.is_absolute():
        raise RuntimeArtifactWriterError("runtime artifact path must be repo-relative")
    normalized = Path(path)
    if any(part == ".." for part in normalized.parts):
        raise RuntimeArtifactWriterError(
            "runtime artifact path may not escape reports/"
        )
    if not normalized.parts or normalized.parts[0] != REPORTS_ROOT.name:
        raise RuntimeArtifactWriterError("runtime artifact path must be under reports/")
    if normalized.suffix != ".json":
        raise RuntimeArtifactWriterError("runtime artifact must be a JSON file")
    return normalized


def _evidence_classification(metadata: Mapping[str, object]) -> str:
    value = _required_string(metadata, "evidence_classification")
    if value not in ALLOWED_EVIDENCE_CLASSIFICATIONS:
        raise RuntimeArtifactWriterError("unsupported runtime evidence classification")
    return value


def _required_string(metadata: Mapping[str, object], key: str) -> str:
    if key not in metadata:
        raise RuntimeArtifactWriterError(
            f"missing required runtime artifact field: {key}"
        )
    return _string_value(metadata[key], key)


def _string_value(value: object, key: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeArtifactWriterError(f"runtime artifact field must be text: {key}")
    return value


def _exact_string(metadata: Mapping[str, object], key: str, expected: str) -> str:
    value = _required_string(metadata, key)
    if value != expected:
        raise RuntimeArtifactWriterError(f"unsafe runtime artifact field: {key}")
    return value


def _required_int(metadata: Mapping[str, object], key: str) -> int:
    value = metadata.get(key)
    if not isinstance(value, int):
        raise RuntimeArtifactWriterError(f"runtime artifact field must be int: {key}")
    return value


def _reject_forbidden_keys(metadata: Mapping[str, object]) -> None:
    for key in metadata:
        lowered = key.lower().replace("-", "_")
        if key in FORBIDDEN_TOP_LEVEL_KEYS or any(
            fragment in lowered for fragment in FORBIDDEN_KEY_FRAGMENTS
        ):
            raise RuntimeArtifactWriterError(
                "runtime artifact metadata contains forbidden secret/performance field"
            )
