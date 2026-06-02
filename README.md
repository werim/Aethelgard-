# Aethelgard

Aethelgard is a conservative crypto futures **research** and **PAPER-trading** foundation focused on Binance Futures market-structure research, execution realism, probabilistic modeling, auditability, and reproducibility.

## Safety posture

- Operating mode remains fixed to **PAPER_ONLY**.
- Operational readiness remains **RESEARCH_ONLY**.
- No strategy logic, exchange connectivity requiring secrets, optimizer, or performance claims are included.
- Simulated, estimated, measured, unknown, and unverified evidence must remain distinguishable.

## Implemented scope

Phase 1 established modular boundaries, validated configuration, fail-closed PAPER-only mode enforcement, deterministic seed metadata, structured JSON logging, and validation tooling.

Phase 2 added a supplied-row historical-data ingestion boundary with timestamp, continuity, OHLC, provenance, and deterministic fingerprint validation.

Phase 2B added only a read-only acquisition evidence boundary:

- credential-free GET acquisition from the public Binance Futures kline endpoint,
- validated fixed-interval request selectors and deterministic pagination,
- bounded retry and rate-limit diagnostics,
- immutable local raw artifact and checksummed metadata storage with persisted fetch diagnostics and verified readback,
- stale or future-dated acquisition-evidence rejection during artifact readback.

Gate 2A through Gate 2G established and closed the local persistence/audit research phase:

- append-only local JSON decision audit records and claim anchors,
- local SQLite audit-event persistence,
- controlled file/database append integration,
- reconciliation scans, reports, and persisted reconciliation artifacts,
- deterministic phase-closure ledger with explicit blocked capabilities.

Gate 3 adds only a pre-runtime stale tick data-quality guard:

- validates symbol, price bounds, receive age, exchange timestamp future skew, warmup drift, peer confirmation, peer-median drift, and duplicate sequence IDs,
- emits auditable pass/reject decisions with canonical reason codes and diagnostics,
- selects the first validated tick rather than blindly accepting the first arriving tick,
- keeps strategy generation, backtesting, execution simulation, fill modeling, risk allocation, PAPER runtime, LIVE trading, and profitability claims explicitly blocked.

Gate 4A adds only a conservative backtest metadata foundation:

- records immutable backtest run metadata for future research runs,
- records dataset fingerprint, symbol, timeframe, timestamp range, seed, config hash, code version, and creation timestamp,
- records execution-assumption evidence as `MEASURED`, `MODELED`, or `UNAVAILABLE`,
- keeps unknown fees, slippage, spreads, latency, funding, fill quality, and orderbook state explicitly unavailable,
- fails closed before performance output when any required execution evidence is unavailable,
- serializes metadata deterministically for auditability.

Increment 4B adds only a canonical effective RR evidence boundary:

- computes `effective_rr` from explicit entry, stop, and take-profit references,
- keeps raw expected RR separate from canonical effective RR,
- marks missing price references as `UNAVAILABLE`,
- marks invalid, non-finite, zero/negative distance, or raw/canonical mismatch states as `INVALID`,
- projects the same canonical result into decision-audit evidence and reporting rows.

It does **not** run backtests, issue signals, manage positions, authenticate exchange-origin claims beyond configured public data boundaries, establish market-data completeness, model fills or costs, repair persistence stores, or provide PAPER/LIVE readiness.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
python main.py
pytest -q
ruff check .
black --check .
mypy .
```

`main.py` performs a safe startup check and emits runtime metadata only. It does not fetch market data or generate trade decisions. Historical acquisition is an explicit research-data action through `src/data/acquisition.py`, not part of a trading runtime. Stale tick validation is an explicit research data-quality action through `src/data/stale_tick_guard.py`; it rejects questionable ticks before downstream research use but does not approve runtime use. Backtest foundation helpers in `src/backtest/foundation.py` record metadata and execution-evidence availability only; they do not replay candles or produce performance evidence. Effective RR helpers in `src/execution/effective_rr.py` validate caller-provided RR references only; they do not create signals, simulate fills, or approve execution. Persistence and reporting helpers remain research evidence boundaries only.

## Repository map

- `config/`: validated research configuration and declared symbol candidates.
- `data/`: local raw, processed, and cache data locations; substantive data is gitignored.
- `reports/`: generated report output location; documents at repository root track readiness.
- `src/data/`: supplied-row kline validation, read-only public acquisition, immutable raw-artifact evidence, and stale tick data-quality guards.
- `src/backtest/`: research-only metadata and execution-evidence availability foundation; no replay, strategy, or performance engine yet.
- `src/execution/`: research-only execution evidence helpers such as canonical effective RR validation; no order path.
- `src/persistence/`: research-only decision audit evidence, database audit-event persistence, narrow integration, reconciliation, reporting, and report-artifact boundaries.
- `src/reporting/`: research-only reporting and phase-closure ledgers.
- `src/`: separated engineering domains plus configuration/runtime/logging foundation.
- `tests/`: validation and safety boundary tests.

## License

MIT License. See `LICENSE`.
