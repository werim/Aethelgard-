# Aethelgard

Aethelgard is a conservative crypto futures **research** and **PAPER-trading** foundation focused on Binance Futures market-structure research, execution realism, probabilistic modeling, auditability, and reproducibility.

## Safety posture

- Operating mode remains fixed to **PAPER_ONLY**.
- Operational readiness remains **RESEARCH_ONLY**.
- No strategy logic, exchange connectivity requiring secrets, optimizer, or performance claims are included.
- Simulated, estimated, measured, unknown, and unverified evidence must remain distinguishable.

## Implemented scope

Phase 1 established modular boundaries, validated configuration, fail-closed PAPER-only mode enforcement, deterministic seed metadata, structured JSON logging, and validation tooling.

Phase 2 added supplied-row historical-data validation and read-only public kline acquisition evidence.

Gate 2A through Gate 2G established and closed the local persistence/audit research phase with append-only local JSON decision audits, SQLite audit events, file/database integration, reconciliation scans, reports, persisted reconciliation artifacts, and a deterministic phase-closure ledger.

Gate 3 adds only a pre-runtime stale tick data-quality guard.

Gate 4A adds only a conservative backtest metadata foundation.

Increment 4B adds only a canonical effective RR evidence boundary.

Increment 4C adds only explicit execution-context snapshots for accepted or rejected research decisions.

Increment 4D adds only a read-only paper runtime DB audit pack.

Increment 4E adds only deterministic research symbol-selection hardening:

- validates configured research symbol candidates only,
- requires caller-provided exchange metadata and market-liquidity evidence,
- checks market, quote asset, contract type, exchange status, filters, notional, 24h quote volume, duplicates, disabled candidates, symbol format, and max-symbol caps,
- emits deterministic `SELECTED`, `REJECTED`, or `UNAVAILABLE` decisions with canonical reason codes,
- serializes reports deterministically,
- never fetches exchange data, ranks alpha, optimizes symbols, creates signals, or approves runtime use.

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

`main.py` performs a safe startup check and emits runtime metadata only. It does not fetch market data or generate trade decisions. Historical acquisition is an explicit research-data action through `src/data/acquisition.py`, not part of a trading runtime. Stale tick validation is an explicit research data-quality action through `src/data/stale_tick_guard.py`; it rejects questionable ticks before downstream research use but does not approve runtime use. Symbol selection helpers in `src/data/symbol_selection.py` harden configured research candidates only; they do not fetch exchange data, rank alpha, or approve execution. Backtest foundation helpers in `src/backtest/foundation.py` record metadata and execution-evidence availability only; they do not replay candles or produce performance evidence. Effective RR helpers in `src/execution/effective_rr.py` validate caller-provided RR references only; they do not create signals, simulate fills, or approve execution. Execution context helpers in `src/execution/context.py` record explicit context evidence only; they do not assume execution quality or submit orders. Paper DB audit helpers in `src/reporting/paper_db_audit.py` inspect and report local evidence only; they do not repair, rewrite, or certify runtime readiness.

## Repository map

- `config/`: validated research configuration and declared symbol candidates.
- `data/`: local raw, processed, and cache data locations; substantive data is gitignored.
- `reports/`: generated report output location; documents at repository root track readiness.
- `src/data/`: supplied-row kline validation, read-only public acquisition, immutable raw-artifact evidence, stale tick data-quality guards, and research-only symbol-selection hardening.
- `src/backtest/`: research-only metadata and execution-evidence availability foundation; no replay, strategy, or performance engine yet.
- `src/execution/`: research-only execution evidence helpers such as canonical effective RR and execution-context snapshots; no order path.
- `src/persistence/`: research-only decision audit evidence, database audit-event persistence, narrow integration, reconciliation, reporting, and report-artifact boundaries.
- `src/reporting/`: research-only reporting, phase-closure ledgers, and read-only paper DB audit reports.
- `src/`: separated engineering domains plus configuration/runtime/logging foundation.
- `tests/`: validation and safety boundary tests.

## License

MIT License. See `LICENSE`.
