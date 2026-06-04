# Changelog

## [0.16.0] - 2026-06-04

### Added

- Increment 4E deterministic symbol-selection hardening in `src/data/symbol_selection.py`.
- `SymbolCandidate`, `ExchangeSymbolEvidence`, `SymbolMarketStats`, `SymbolSelectionPolicy`, `SymbolSelectionDecision`, and `SymbolSelectionReport` models.
- Explicit `SymbolSelectionStatus` states: `SELECTED`, `REJECTED`, and `UNAVAILABLE`.
- Canonical symbol-selection reason codes for invalid format, duplicate candidates, disabled research, market mismatch, quote-asset mismatch, unavailable exchange metadata, non-trading status, disallowed contract type, unavailable price/lot/notional filters, unavailable market stats, low volume, and max-symbol caps.
- Deterministic `symbol_selection_json(...)` report serialization.
- `assert_symbol_selection_has_candidates(...)` fail-closed guard.
- `src/data/__init__.py` exports for the new research-only symbol-selection helpers.
- Focused tests for deterministic valid selection, missing metadata, disabled candidates, duplicate candidates, non-trading status, missing filters, low volume, max-symbol caps, stable payloads, and invalid policy.

### Changed

- Package version advanced to `0.16.0`.
- README, VERSION, PLAN, and REPORT now describe Increment 4E as symbol-selection hardening only.
- Increment 4D status is recorded as green by user report at `dev` head `47d4ddc863c7e06aebb4a13e2d9a4ace9ba8b499`.

### Fixed

- Closed the absence of a deterministic, fail-closed research symbol-selection boundary before later paper/live parity work.
- Missing exchange metadata, missing filters, missing market stats, disabled candidates, duplicate candidates, and policy violations no longer flow into selected research symbols.

### Removed

- None.

### Known limitations

- Increment 4E does not fetch exchange data, rank alpha, optimize symbols, generate signals, run backtests, simulate fills, add PAPER runtime behavior, enable live execution, add exchange credentials, or certify readiness.
- Local Ruff, Black, and Mypy were unavailable in the scratch environment.
- Remote CI remains the source of truth for exact final branch-head full-suite validation.

## [0.15.0] - 2026-06-02

### Added

- Increment 4D read-only paper runtime DB audit pack in `src/reporting/paper_db_audit.py`.
- Deterministic JSON and Markdown paper DB audit reports.
- Diagnostics for missing schema, empty DBs, orphan lifecycle events, missing decision/lifecycle links, duplicate IDs, checksum issues, corrupted JSON, UNKNOWN rejection reasons, missing fields, lifecycle ordering issues, and inconsistent accepted/rejected transitions.

### Changed

- Package version advanced to `0.15.0`.
- README, VERSION, PLAN, and REPORT described Increment 4D as a read-only DB audit/reporting pack only.

### Fixed

- Closed the absence of a read-only paper runtime DB audit/reporting surface.

### Removed

- None.

### Known limitations

- Increment 4D does not repair databases, rewrite rows, create runtime events, simulate fills, add PAPER runtime behavior, enable live execution, add strategy logic, or certify readiness.

## [0.14.0] - 2026-06-02

### Added

- Increment 4C execution context snapshot boundary in `src/execution/context.py`.
- Explicit execution context and cost-assumption snapshots.
- Deterministic JSON serialization and decision-audit evidence projection.

### Changed

- Package version advanced to `0.14.0`.

### Fixed

- Missing execution-cost assumptions remain unavailable instead of silently becoming zero.
- Stale or unavailable critical market input fails closed.

### Removed

- None.

### Known limitations

- Increment 4C does not simulate fills, assume execution quality, add paper runtime behavior, enable live execution, add strategy logic, or certify readiness.

## [0.13.0] - 2026-06-02

### Added

- Increment 4B canonical effective RR boundary in `src/execution/effective_rr.py`.
- Single canonical effective RR calculation path and audit/report projections.

### Changed

- Package version advanced to `0.13.0`.

### Fixed

- Raw expected RR can no longer override canonical effective RR.
- Missing RR inputs remain unavailable rather than guessed or converted to zero.

### Removed

- None.

### Known limitations

- Increment 4B does not add strategy logic, signal generation, candle replay, trade simulation, fill modeling, risk allocation, PAPER runtime behavior, readiness certification, or profitability claims.

## [0.12.0] - 2026-06-02

### Added

- Gate 4A conservative backtest foundation skeleton in `src/backtest/foundation.py`.
- Immutable backtest run metadata and execution evidence records.
- Explicit measured, modeled, and unavailable evidence classifications.

### Changed

- Package version advanced to `0.12.0`.

### Fixed

- Performance results are blocked while required execution evidence is unavailable.

### Removed

- None.

### Known limitations

- Gate 4A does not replay candles, generate signals, simulate trades, calculate performance, model fills/costs, or certify readiness.

## [0.11.0] - 2026-06-01

### Added

- Gate 3 stale tick data-quality guard in `src/data/stale_tick_guard.py`.
- Auditable market tick and stale tick decision records.

### Changed

- Package version advanced to `0.11.0`.

### Fixed

- Closed the absence of reusable fail-closed pre-runtime stale tick validation.

### Removed

- None.

### Known limitations

- Gate 3 validates tick freshness and peer consistency only.

## [0.10.0] - 2026-06-01

- Added Gate 2G persistence/audit phase closure ledger.
- Package version advanced to `0.10.0`.

## [0.9.0] - 2026-05-31

- Added Gate 2F reconciliation report artifact persistence.
- Package version advanced to `0.9.0`.

## [0.8.0] - 2026-05-31

- Added Gate 2E reconciliation reporting helpers.
- Package version advanced to `0.8.0`.

## [0.7.0] - 2026-05-31

- Added Gate 2D persistence reconciliation scanner.
- Package version advanced to `0.7.0`.

## [0.6.0] - 2026-05-31

- Added Gate 2C persistence integration helper linking decision audit files to SQLite audit events.
- Package version advanced to `0.6.0`.

## [0.5.0] - 2026-05-30

- Added database-backed research audit-event persistence in `src/persistence/events.py`.
- Package version advanced to `0.5.0`.

## [0.4.0] - 2026-05-30

- Added research-only append audit persistence in `src/persistence/audit.py`.
- Package version advanced to `0.4.0`.

## [0.3.1] - 2026-05-29

- Repaired acquisition retry and restart readback evidence handling.
- Added Python 3.11/3.12 CI compile-and-test coverage.

## [0.3.0] - 2026-05-27

- Added read-only public Binance Futures historical kline acquisition and immutable raw-artifact evidence boundary.

## [0.2.0] - 2026-05-25

- Added provenance-aware historical Binance Futures kline validation and deterministic dataset fingerprints.

## [0.1.0] - 2026-05-25

- Added the PAPER-only, RESEARCH_ONLY foundation, validation tooling, and CI definition.
