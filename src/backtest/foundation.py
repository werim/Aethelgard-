"""Conservative research-only backtest metadata foundation.

This module records reproducible metadata and execution-assumption evidence for
future backtest runs. It does not replay candles, generate signals, simulate
trades, calculate performance, or approve runtime use.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from json import dumps
from re import fullmatch


class BacktestFoundationError(ValueError):
    """Base error for fail-closed backtest foundation validation."""


class BacktestExecutionEvidenceUnavailable(BacktestFoundationError):
    """Raised when performance results are requested without evidence."""


class EvidenceClassification(StrEnum):
    """Evidence quality classification for backtest assumptions."""

    MEASURED = "MEASURED"
    MODELED = "MODELED"
    UNAVAILABLE = "UNAVAILABLE"


class ExecutionAssumption(StrEnum):
    """Execution assumptions required before producing performance evidence."""

    FEES = "fees"
    SLIPPAGE = "slippage"
    SPREADS = "spreads"
    LATENCY = "latency"
    FUNDING = "funding"
    FILL_QUALITY = "fill_quality"
    ORDERBOOK_STATE = "orderbook_state"


REQUIRED_EXECUTION_ASSUMPTIONS: tuple[ExecutionAssumption, ...] = (
    ExecutionAssumption.FEES,
    ExecutionAssumption.SLIPPAGE,
    ExecutionAssumption.SPREADS,
    ExecutionAssumption.LATENCY,
    ExecutionAssumption.FUNDING,
    ExecutionAssumption.FILL_QUALITY,
    ExecutionAssumption.ORDERBOOK_STATE,
)


@dataclass(frozen=True)
class ExecutionEvidence:
    """One explicit evidence record for an execution assumption."""

    classification: EvidenceClassification
    description: str
    source: str | None = None
    value: str | int | float | None = None
    unavailable_reason: str | None = None

    def validate(self) -> None:
        """Validate evidence without silently converting unknowns to zero."""

        if not self.description.strip():
            raise BacktestFoundationError("evidence description is required")
        if self.classification is EvidenceClassification.UNAVAILABLE:
            if self.value is not None:
                raise BacktestFoundationError("unavailable evidence cannot carry value")
            if self.source is not None:
                raise BacktestFoundationError("unavailable evidence cannot carry source")
            if not self.unavailable_reason or not self.unavailable_reason.strip():
                raise BacktestFoundationError("unavailable evidence requires a reason")
            return
        if self.unavailable_reason is not None:
            raise BacktestFoundationError(
                "measured or modeled evidence cannot carry unavailable_reason"
            )
        if self.classification is EvidenceClassification.MEASURED and not self.source:
            raise BacktestFoundationError("measured evidence requires a source")

    def payload(self) -> dict[str, str | int | float | None]:
        """Return a deterministic JSON-compatible payload."""

        self.validate()
        return {
            "classification": self.classification.value,
            "description": self.description,
            "source": self.source,
            "value": self.value,
            "unavailable_reason": self.unavailable_reason,
        }


@dataclass(frozen=True)
class BacktestRunMetadata:
    """Immutable metadata for a future conservative backtest run."""

    run_id: str
    dataset_fingerprint: str
    symbol: str
    timeframe: str
    start_ts: str
    end_ts: str
    seed: int
    config_hash: str
    code_version: str
    created_at: str
    execution_assumptions: Mapping[ExecutionAssumption, ExecutionEvidence]

    def validate(self) -> None:
        """Fail closed if required reproducibility metadata is incomplete."""

        _require_non_empty("run_id", self.run_id)
        _require_sha256("dataset_fingerprint", self.dataset_fingerprint)
        _require_non_empty("symbol", self.symbol)
        _require_non_empty("timeframe", self.timeframe)
        _require_sha256("config_hash", self.config_hash)
        _require_non_empty("code_version", self.code_version)
        if self.seed < 0:
            raise BacktestFoundationError("seed must be non-negative")
        start = _parse_utc_timestamp("start_ts", self.start_ts)
        end = _parse_utc_timestamp("end_ts", self.end_ts)
        _parse_utc_timestamp("created_at", self.created_at)
        if start >= end:
            raise BacktestFoundationError("start_ts must be before end_ts")
        _validate_execution_assumption_keys(self.execution_assumptions)
        for evidence in self.execution_assumptions.values():
            evidence.validate()

    def payload(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible metadata payload."""

        self.validate()
        return {
            "run_id": self.run_id,
            "dataset_fingerprint": self.dataset_fingerprint,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "start_ts": self.start_ts,
            "end_ts": self.end_ts,
            "seed": self.seed,
            "config_hash": self.config_hash,
            "code_version": self.code_version,
            "created_at": self.created_at,
            "execution_assumptions": {
                assumption.value: self.execution_assumptions[assumption].payload()
                for assumption in REQUIRED_EXECUTION_ASSUMPTIONS
            },
        }


def unavailable_execution_assumptions(
    reason: str,
) -> dict[ExecutionAssumption, ExecutionEvidence]:
    """Build explicit unavailable evidence for all required execution inputs."""

    if not reason.strip():
        raise BacktestFoundationError("unavailable execution assumption reason required")
    return {
        assumption: ExecutionEvidence(
            classification=EvidenceClassification.UNAVAILABLE,
            description=f"{assumption.value} evidence is unavailable",
            unavailable_reason=reason,
        )
        for assumption in REQUIRED_EXECUTION_ASSUMPTIONS
    }


def backtest_metadata_json(metadata: BacktestRunMetadata) -> str:
    """Serialize metadata deterministically."""

    return dumps(metadata.payload(), sort_keys=True, separators=(",", ":"))


def assert_can_produce_performance_results(
    metadata: BacktestRunMetadata,
) -> None:
    """Fail closed while any required execution evidence is unavailable."""

    metadata.validate()
    unavailable = sorted(
        assumption.value
        for assumption, evidence in metadata.execution_assumptions.items()
        if evidence.classification is EvidenceClassification.UNAVAILABLE
    )
    if unavailable:
        joined = ", ".join(unavailable)
        raise BacktestExecutionEvidenceUnavailable(
            "cannot produce performance results with unavailable execution "
            f"evidence: {joined}"
        )


def _validate_execution_assumption_keys(
    evidence: Mapping[ExecutionAssumption, ExecutionEvidence],
) -> None:
    required = set(REQUIRED_EXECUTION_ASSUMPTIONS)
    received = set(evidence)
    if received != required:
        missing = sorted(assumption.value for assumption in required - received)
        extra = sorted(assumption.value for assumption in received - required)
        raise BacktestFoundationError(
            f"execution assumptions must match required set; missing={missing}; "
            f"extra={extra}"
        )


def _require_non_empty(name: str, value: str) -> None:
    if not value.strip():
        raise BacktestFoundationError(f"{name} is required")


def _require_sha256(name: str, value: str) -> None:
    if fullmatch(r"[0-9a-f]{64}", value) is None:
        raise BacktestFoundationError(f"{name} must be a lowercase sha256 hex digest")


def _parse_utc_timestamp(name: str, value: str) -> datetime:
    if not value.endswith("Z"):
        raise BacktestFoundationError(f"{name} must be UTC and end with 'Z'")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise BacktestFoundationError(f"{name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo != UTC:
        raise BacktestFoundationError(f"{name} must use UTC timezone")
    return parsed
