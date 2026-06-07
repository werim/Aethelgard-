"""Deterministic research-only symbol selection hardening.

This module validates caller-provided research candidate symbols against explicit
exchange metadata and market-liquidity evidence. It does not discover alpha,
rank profitability, fetch exchange data, create orders, or approve PAPER/LIVE use.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from json import dumps
from re import fullmatch


class SymbolSelectionError(ValueError):
    """Raised when symbol selection evidence is missing or unsafe."""


class SymbolSelectionStatus(StrEnum):
    """Final availability state for a research symbol candidate."""

    SELECTED = "SELECTED"
    REJECTED = "REJECTED"
    UNAVAILABLE = "UNAVAILABLE"


class SymbolSelectionReason(StrEnum):
    """Canonical symbol-selection diagnostics."""

    SYMBOL_SELECTED = "SYMBOL_SELECTED"
    SYMBOL_FORMAT_INVALID = "SYMBOL_FORMAT_INVALID"
    DUPLICATE_CANDIDATE = "DUPLICATE_CANDIDATE"
    RESEARCH_DISABLED = "RESEARCH_DISABLED"
    MARKET_MISMATCH = "MARKET_MISMATCH"
    QUOTE_ASSET_NOT_ALLOWED = "QUOTE_ASSET_NOT_ALLOWED"
    EXCHANGE_METADATA_UNAVAILABLE = "EXCHANGE_METADATA_UNAVAILABLE"
    EXCHANGE_STATUS_NOT_TRADING = "EXCHANGE_STATUS_NOT_TRADING"
    CONTRACT_TYPE_NOT_ALLOWED = "CONTRACT_TYPE_NOT_ALLOWED"
    PRICE_FILTER_UNAVAILABLE = "PRICE_FILTER_UNAVAILABLE"
    LOT_SIZE_FILTER_UNAVAILABLE = "LOT_SIZE_FILTER_UNAVAILABLE"
    MIN_NOTIONAL_UNAVAILABLE = "MIN_NOTIONAL_UNAVAILABLE"
    MARKET_STATS_UNAVAILABLE = "MARKET_STATS_UNAVAILABLE"
    VOLUME_BELOW_MINIMUM = "VOLUME_BELOW_MINIMUM"
    MAX_SYMBOLS_REACHED = "MAX_SYMBOLS_REACHED"


@dataclass(frozen=True)
class SymbolCandidate:
    """Configured research symbol candidate."""

    symbol: str
    market: str
    enabled_for_research: bool


@dataclass(frozen=True)
class ExchangeSymbolEvidence:
    """Caller-provided exchange metadata evidence for one symbol."""

    symbol: str
    market: str
    status: str
    contract_type: str
    quote_asset: str
    price_tick_size: float | None
    lot_step_size: float | None
    min_notional: float | None
    source: str


@dataclass(frozen=True)
class SymbolMarketStats:
    """Caller-provided market-liquidity evidence for one symbol."""

    symbol: str
    quote_volume_24h: float | None
    source: str


@dataclass(frozen=True)
class SymbolSelectionPolicy:
    """Fail-closed symbol-selection policy for research candidates."""

    allowed_market: str = "BINANCE_FUTURES"
    allowed_quote_assets: tuple[str, ...] = ("USDT",)
    allowed_contract_types: tuple[str, ...] = ("PERPETUAL",)
    min_quote_volume_24h: float = 50_000_000.0
    max_symbols: int = 20
    symbol_pattern: str = r"^[A-Z0-9]{2,20}USDT$"

    def validate(self) -> None:
        """Validate policy before it can select symbols."""

        if not self.allowed_market.strip():
            raise SymbolSelectionError("allowed_market is required")
        if not self.allowed_quote_assets:
            raise SymbolSelectionError("at least one quote asset is required")
        if not self.allowed_contract_types:
            raise SymbolSelectionError("at least one contract type is required")
        if self.max_symbols <= 0:
            raise SymbolSelectionError("max_symbols must be positive")
        if (
            not math.isfinite(self.min_quote_volume_24h)
            or self.min_quote_volume_24h < 0
        ):
            raise SymbolSelectionError(
                "min_quote_volume_24h must be finite and non-negative"
            )
        try:
            fullmatch(self.symbol_pattern, "BTCUSDT")
        except Exception as exc:  # pragma: no cover - defensive regex validation
            raise SymbolSelectionError("symbol_pattern must be a valid regex") from exc


@dataclass(frozen=True)
class SymbolSelectionDecision:
    """Deterministic decision for one configured candidate."""

    symbol: str
    status: SymbolSelectionStatus
    reason_codes: tuple[SymbolSelectionReason, ...]
    market: str | None
    quote_asset: str | None
    quote_volume_24h: float | None
    evidence_sources: tuple[str, ...]

    def payload(self) -> dict[str, object]:
        """Return deterministic JSON-compatible decision payload."""

        return {
            "symbol": self.symbol,
            "status": self.status.value,
            "reason_codes": [reason.value for reason in self.reason_codes],
            "market": self.market,
            "quote_asset": self.quote_asset,
            "quote_volume_24h": self.quote_volume_24h,
            "evidence_sources": list(self.evidence_sources),
        }


@dataclass(frozen=True)
class SymbolSelectionReport:
    """Research-only symbol-selection report."""

    policy: SymbolSelectionPolicy
    decisions: tuple[SymbolSelectionDecision, ...]

    def payload(self) -> dict[str, object]:
        selected = [
            decision.symbol
            for decision in self.decisions
            if decision.status is SymbolSelectionStatus.SELECTED
        ]
        return {
            "policy": {
                "allowed_market": self.policy.allowed_market,
                "allowed_quote_assets": list(self.policy.allowed_quote_assets),
                "allowed_contract_types": list(self.policy.allowed_contract_types),
                "min_quote_volume_24h": self.policy.min_quote_volume_24h,
                "max_symbols": self.policy.max_symbols,
                "symbol_pattern": self.policy.symbol_pattern,
            },
            "selected_symbols": selected,
            "decisions": [decision.payload() for decision in self.decisions],
        }


def harden_symbol_selection(
    candidates: tuple[SymbolCandidate, ...],
    exchange_evidence: tuple[ExchangeSymbolEvidence, ...],
    market_stats: tuple[SymbolMarketStats, ...],
    policy: SymbolSelectionPolicy | None = None,
) -> SymbolSelectionReport:
    """Validate configured symbols without inventing exchange or liquidity evidence."""

    active_policy = policy or SymbolSelectionPolicy()
    active_policy.validate()
    exchange_by_symbol = _unique_exchange_evidence(exchange_evidence)
    stats_by_symbol = _unique_market_stats(market_stats)
    seen: set[str] = set()
    selected_count = 0
    decisions: list[SymbolSelectionDecision] = []
    for candidate in candidates:
        decision, selected_count = _decide_candidate(
            candidate=candidate,
            policy=active_policy,
            exchange_by_symbol=exchange_by_symbol,
            stats_by_symbol=stats_by_symbol,
            seen=seen,
            selected_count=selected_count,
        )
        decisions.append(decision)
    return SymbolSelectionReport(policy=active_policy, decisions=tuple(decisions))


def symbol_selection_json(report: SymbolSelectionReport) -> str:
    """Serialize the selection report deterministically."""

    return dumps(report.payload(), sort_keys=True, separators=(",", ":"))


def assert_symbol_selection_has_candidates(report: SymbolSelectionReport) -> None:
    """Fail closed if no research symbols survived hardening."""

    if not any(
        decision.status is SymbolSelectionStatus.SELECTED
        for decision in report.decisions
    ):
        raise SymbolSelectionError("no symbols selected for research after hardening")


def _decide_candidate(
    candidate: SymbolCandidate,
    policy: SymbolSelectionPolicy,
    exchange_by_symbol: dict[str, ExchangeSymbolEvidence | None],
    stats_by_symbol: dict[str, SymbolMarketStats | None],
    seen: set[str],
    selected_count: int,
) -> tuple[SymbolSelectionDecision, int]:
    symbol = candidate.symbol.strip().upper()
    reasons: list[SymbolSelectionReason] = []
    if symbol in seen:
        reasons.append(SymbolSelectionReason.DUPLICATE_CANDIDATE)
    seen.add(symbol)
    if fullmatch(policy.symbol_pattern, symbol) is None:
        reasons.append(SymbolSelectionReason.SYMBOL_FORMAT_INVALID)
    if not candidate.enabled_for_research:
        reasons.append(SymbolSelectionReason.RESEARCH_DISABLED)
    if candidate.market != policy.allowed_market:
        reasons.append(SymbolSelectionReason.MARKET_MISMATCH)

    exchange = exchange_by_symbol.get(symbol)
    stats = stats_by_symbol.get(symbol)
    quote_asset: str | None = None
    quote_volume_24h: float | None = None
    sources: list[str] = []

    if exchange is None:
        reasons.append(SymbolSelectionReason.EXCHANGE_METADATA_UNAVAILABLE)
    else:
        quote_asset = exchange.quote_asset
        if exchange.source:
            sources.append(exchange.source)
        if exchange.market != policy.allowed_market:
            reasons.append(SymbolSelectionReason.MARKET_MISMATCH)
        if exchange.status != "TRADING":
            reasons.append(SymbolSelectionReason.EXCHANGE_STATUS_NOT_TRADING)
        if exchange.contract_type not in policy.allowed_contract_types:
            reasons.append(SymbolSelectionReason.CONTRACT_TYPE_NOT_ALLOWED)
        if exchange.quote_asset not in policy.allowed_quote_assets:
            reasons.append(SymbolSelectionReason.QUOTE_ASSET_NOT_ALLOWED)
        if exchange.price_tick_size is None or exchange.price_tick_size <= 0:
            reasons.append(SymbolSelectionReason.PRICE_FILTER_UNAVAILABLE)
        if exchange.lot_step_size is None or exchange.lot_step_size <= 0:
            reasons.append(SymbolSelectionReason.LOT_SIZE_FILTER_UNAVAILABLE)
        if exchange.min_notional is None or exchange.min_notional <= 0:
            reasons.append(SymbolSelectionReason.MIN_NOTIONAL_UNAVAILABLE)

    if stats is None:
        reasons.append(SymbolSelectionReason.MARKET_STATS_UNAVAILABLE)
    else:
        quote_volume_24h = stats.quote_volume_24h
        if stats.source:
            sources.append(stats.source)
        if quote_volume_24h is None or not math.isfinite(quote_volume_24h):
            reasons.append(SymbolSelectionReason.MARKET_STATS_UNAVAILABLE)
        elif quote_volume_24h < policy.min_quote_volume_24h:
            reasons.append(SymbolSelectionReason.VOLUME_BELOW_MINIMUM)

    if not reasons and selected_count >= policy.max_symbols:
        reasons.append(SymbolSelectionReason.MAX_SYMBOLS_REACHED)

    if reasons:
        status = (
            SymbolSelectionStatus.UNAVAILABLE
            if _has_unavailable_reason(tuple(reasons))
            else SymbolSelectionStatus.REJECTED
        )
        return (
            SymbolSelectionDecision(
                symbol=symbol,
                status=status,
                reason_codes=tuple(reasons),
                market=candidate.market,
                quote_asset=quote_asset,
                quote_volume_24h=quote_volume_24h,
                evidence_sources=tuple(sorted(set(sources))),
            ),
            selected_count,
        )

    return (
        SymbolSelectionDecision(
            symbol=symbol,
            status=SymbolSelectionStatus.SELECTED,
            reason_codes=(SymbolSelectionReason.SYMBOL_SELECTED,),
            market=candidate.market,
            quote_asset=quote_asset,
            quote_volume_24h=quote_volume_24h,
            evidence_sources=tuple(sorted(set(sources))),
        ),
        selected_count + 1,
    )


def _unique_exchange_evidence(
    evidence_rows: tuple[ExchangeSymbolEvidence, ...],
) -> dict[str, ExchangeSymbolEvidence | None]:
    by_symbol: dict[str, ExchangeSymbolEvidence | None] = {}
    for row in evidence_rows:
        symbol = row.symbol.strip().upper()
        if symbol in by_symbol:
            by_symbol[symbol] = None
        else:
            by_symbol[symbol] = row
    return by_symbol


def _unique_market_stats(
    stats_rows: tuple[SymbolMarketStats, ...],
) -> dict[str, SymbolMarketStats | None]:
    by_symbol: dict[str, SymbolMarketStats | None] = {}
    for row in stats_rows:
        symbol = row.symbol.strip().upper()
        if symbol in by_symbol:
            by_symbol[symbol] = None
        else:
            by_symbol[symbol] = row
    return by_symbol


def _has_unavailable_reason(reasons: tuple[SymbolSelectionReason, ...]) -> bool:
    unavailable_reasons = {
        SymbolSelectionReason.EXCHANGE_METADATA_UNAVAILABLE,
        SymbolSelectionReason.PRICE_FILTER_UNAVAILABLE,
        SymbolSelectionReason.LOT_SIZE_FILTER_UNAVAILABLE,
        SymbolSelectionReason.MIN_NOTIONAL_UNAVAILABLE,
        SymbolSelectionReason.MARKET_STATS_UNAVAILABLE,
    }
    return any(reason in unavailable_reasons for reason in reasons)
