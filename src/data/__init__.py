"""Validated, provenance-aware historical market-data boundary."""

from src.data.symbol_selection import (
    ExchangeSymbolEvidence,
    SymbolCandidate,
    SymbolMarketStats,
    SymbolSelectionDecision,
    SymbolSelectionError,
    SymbolSelectionPolicy,
    SymbolSelectionReason,
    SymbolSelectionReport,
    SymbolSelectionStatus,
    assert_symbol_selection_has_candidates,
    harden_symbol_selection,
    symbol_selection_json,
)

__all__ = [
    "ExchangeSymbolEvidence",
    "SymbolCandidate",
    "SymbolMarketStats",
    "SymbolSelectionDecision",
    "SymbolSelectionError",
    "SymbolSelectionPolicy",
    "SymbolSelectionReason",
    "SymbolSelectionReport",
    "SymbolSelectionStatus",
    "assert_symbol_selection_has_candidates",
    "harden_symbol_selection",
    "symbol_selection_json",
]
