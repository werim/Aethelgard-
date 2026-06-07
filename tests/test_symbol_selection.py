import json

import pytest

from src.data.symbol_selection import (
    ExchangeSymbolEvidence,
    SymbolCandidate,
    SymbolMarketStats,
    SymbolSelectionError,
    SymbolSelectionPolicy,
    SymbolSelectionReason,
    SymbolSelectionStatus,
    assert_symbol_selection_has_candidates,
    harden_symbol_selection,
    symbol_selection_json,
)


def candidate(
    symbol: str,
    *,
    enabled: bool = True,
    market: str = "BINANCE_FUTURES",
) -> SymbolCandidate:
    return SymbolCandidate(symbol=symbol, market=market, enabled_for_research=enabled)


def exchange(symbol: str, **overrides: object) -> ExchangeSymbolEvidence:
    values = {
        "symbol": symbol,
        "market": "BINANCE_FUTURES",
        "status": "TRADING",
        "contract_type": "PERPETUAL",
        "quote_asset": "USDT",
        "price_tick_size": 0.1,
        "lot_step_size": 0.001,
        "min_notional": 5.0,
        "source": "exchangeInfo-snapshot",
    }
    values.update(overrides)
    return ExchangeSymbolEvidence(**values)  # type: ignore[arg-type]


def stats(symbol: str, volume: float | None = 100_000_000.0) -> SymbolMarketStats:
    return SymbolMarketStats(
        symbol=symbol,
        quote_volume_24h=volume,
        source="ticker24h-snapshot",
    )


def test_selects_valid_configured_symbols_deterministically() -> None:
    report = harden_symbol_selection(
        candidates=(candidate("BTCUSDT"), candidate("ETHUSDT")),
        exchange_evidence=(exchange("ETHUSDT"), exchange("BTCUSDT")),
        market_stats=(stats("ETHUSDT"), stats("BTCUSDT")),
        policy=SymbolSelectionPolicy(max_symbols=5),
    )
    payload = report.payload()
    assert payload["selected_symbols"] == ["BTCUSDT", "ETHUSDT"]
    assert symbol_selection_json(report) == symbol_selection_json(report)
    assert all(
        decision.status is SymbolSelectionStatus.SELECTED
        for decision in report.decisions
    )


def test_missing_exchange_metadata_is_unavailable_not_selected() -> None:
    report = harden_symbol_selection(
        candidates=(candidate("BTCUSDT"),),
        exchange_evidence=(),
        market_stats=(stats("BTCUSDT"),),
    )
    decision = report.decisions[0]
    assert decision.status is SymbolSelectionStatus.UNAVAILABLE
    assert SymbolSelectionReason.EXCHANGE_METADATA_UNAVAILABLE in decision.reason_codes
    with pytest.raises(SymbolSelectionError, match="no symbols selected"):
        assert_symbol_selection_has_candidates(report)


def test_disabled_candidate_is_rejected() -> None:
    report = harden_symbol_selection(
        candidates=(candidate("BTCUSDT", enabled=False),),
        exchange_evidence=(exchange("BTCUSDT"),),
        market_stats=(stats("BTCUSDT"),),
    )
    decision = report.decisions[0]
    assert decision.status is SymbolSelectionStatus.REJECTED
    assert decision.reason_codes == (SymbolSelectionReason.RESEARCH_DISABLED,)


def test_duplicate_candidate_does_not_double_select() -> None:
    report = harden_symbol_selection(
        candidates=(candidate("BTCUSDT"), candidate("BTCUSDT")),
        exchange_evidence=(exchange("BTCUSDT"),),
        market_stats=(stats("BTCUSDT"),),
    )
    assert report.decisions[0].status is SymbolSelectionStatus.SELECTED
    assert report.decisions[1].status is SymbolSelectionStatus.REJECTED
    assert SymbolSelectionReason.DUPLICATE_CANDIDATE in report.decisions[1].reason_codes
    assert report.payload()["selected_symbols"] == ["BTCUSDT"]


def test_non_trading_exchange_status_rejected() -> None:
    report = harden_symbol_selection(
        candidates=(candidate("BTCUSDT"),),
        exchange_evidence=(exchange("BTCUSDT", status="BREAK"),),
        market_stats=(stats("BTCUSDT"),),
    )
    decision = report.decisions[0]
    assert decision.status is SymbolSelectionStatus.REJECTED
    assert SymbolSelectionReason.EXCHANGE_STATUS_NOT_TRADING in decision.reason_codes


def test_missing_filters_are_unavailable() -> None:
    report = harden_symbol_selection(
        candidates=(candidate("BTCUSDT"),),
        exchange_evidence=(exchange("BTCUSDT", price_tick_size=None),),
        market_stats=(stats("BTCUSDT"),),
    )
    decision = report.decisions[0]
    assert decision.status is SymbolSelectionStatus.UNAVAILABLE
    assert SymbolSelectionReason.PRICE_FILTER_UNAVAILABLE in decision.reason_codes


def test_low_volume_rejected_without_alpha_ranking() -> None:
    report = harden_symbol_selection(
        candidates=(candidate("BTCUSDT"),),
        exchange_evidence=(exchange("BTCUSDT"),),
        market_stats=(stats("BTCUSDT", volume=10_000.0),),
    )
    decision = report.decisions[0]
    assert decision.status is SymbolSelectionStatus.REJECTED
    assert SymbolSelectionReason.VOLUME_BELOW_MINIMUM in decision.reason_codes


def test_max_symbols_rejects_after_cap_in_input_order() -> None:
    report = harden_symbol_selection(
        candidates=(candidate("BTCUSDT"), candidate("ETHUSDT")),
        exchange_evidence=(exchange("BTCUSDT"), exchange("ETHUSDT")),
        market_stats=(stats("BTCUSDT"), stats("ETHUSDT")),
        policy=SymbolSelectionPolicy(max_symbols=1),
    )
    assert report.decisions[0].status is SymbolSelectionStatus.SELECTED
    assert report.decisions[1].status is SymbolSelectionStatus.REJECTED
    assert SymbolSelectionReason.MAX_SYMBOLS_REACHED in report.decisions[1].reason_codes


def test_payload_keeps_sources_and_reason_codes_stable() -> None:
    report = harden_symbol_selection(
        candidates=(candidate("BTCUSDT"),),
        exchange_evidence=(exchange("BTCUSDT"),),
        market_stats=(stats("BTCUSDT"),),
    )
    payload = json.loads(symbol_selection_json(report))
    decision = payload["decisions"][0]
    assert decision["reason_codes"] == ["SYMBOL_SELECTED"]
    assert decision["evidence_sources"] == [
        "exchangeInfo-snapshot",
        "ticker24h-snapshot",
    ]


def test_invalid_policy_fails_closed() -> None:
    with pytest.raises(SymbolSelectionError, match="max_symbols"):
        SymbolSelectionPolicy(max_symbols=0).validate()
