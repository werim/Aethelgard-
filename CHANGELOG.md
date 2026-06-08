# Changelog

## [0.20.0] - 2026-06-07

### Added

- Gate 4B-0 minimal performance metric publication boundary in `src/reporting/performance_boundary.py`.
- `MetricPublicationStatus`, immutable eligibility diagnostics, and deterministic JSON serialization for metric-publication eligibility/refusal payloads.
- Focused tests for unavailable evidence blocking, measured/modeled evidence eligibility, unavailable-not-zero behavior, deterministic JSON, malformed metadata fail-closed behavior, and absence of performance metric fields.
- Gate 4B replay hardening tests confirming deterministic replay metadata and row payloads expose no performance metric or execution fields and do not import `src.execution` or order-related modules.

### Changed

- Package version advanced to `0.20.0`.
- `src/reporting/__init__.py` now exports Gate 4B-0 metric-publication eligibility helpers.
- Reporting can now publish only eligibility/refusal diagnostics before any performance metric surface is allowed.
- Documentation now records the PR #13 merge evidence for Gate 4B replay hardening without advancing the version.

### Fixed

- Unavailable Gate 4A execution evidence now blocks metric-publication eligibility through a reporting boundary before any performance field is emitted.
- Unsafe or malformed backtest metadata fails closed as `METRICS_BLOCKED`.
- Unknown execution evidence remains unavailable and is not converted to zero.
- Deterministic replay boundary tests now guard against accidental performance-field publication or execution/order imports.

### Removed

- None.

### Known limitations

- Gate 4B-0 does not replay candles, simulate trades, compute performance, model costs, integrate an optimizer, add PAPER runtime behavior, place orders, enable LIVE trading, or approve readiness.
- Gate 4B replay hardening is test coverage only and does not change runtime behavior.
- The boundary only reports metric eligibility/refusal diagnostics.
- Local Ruff, Black, and Mypy were unavailable in the scratch environment.
- Exact final branch-head full-suite validation and remote CI are unverified until GitHub Actions reports.
- API-backed writes created several small commits rather than one atomic local commit because direct mutable local clone access was unavailable.

## [0.19.0] - 2026-06-05

### Added

- Gate 4D execution-cost evidence boundary in `src/backtest/cost_evidence.py`.
- Cost evidence records for fees, slippage, spread, funding, and latency.
- Cost evidence gate before net metrics, expectancy, strategy ranking, optimizer input, and readiness statements.
- Deterministic JSON and Markdown diagnostics for cost-evidence gate results.
- Focused tests for missing fees, slippage, spread, funding, latency, unavailable-not-zero behavior, modeled assumptions, measured pass behavior, reporting visibility, and readiness blocking.

### Changed

- Package version advanced to `0.19.0`.
- `src/backtest/__init__.py` now exports Gate 4D cost-evidence helpers.
- Metric publication now fails closed when required execution-cost evidence is unavailable.

### Fixed

- Unknown execution costs can no longer be implicitly treated as zero inside the Gate 4D boundary.
- `UNAVAILABLE` cost evidence cannot carry value or unit fields.
- MODELED cost evidence requires explicit assumptions and emits modeled-cost metric labeling.

### Removed

- None.

### Known limitations

- Measured cost coverage may still be incomplete and remains caller-supplied evidence.
- Gate 4D does not integrate an optimizer, tune models, generate alpha, change runtime execution, or approve readiness.
- Operational readiness remains PAPER ONLY / NOT LIVE READY.
- Local Ruff, Black, and Mypy were unavailable in the scratch environment.
- Exact final branch-head full-suite validation and remote CI are unverified until GitHub Actions reports.
- API-backed writes created several small commits rather than one atomic local commit because direct mutable local clone access was unavailable.

## [0.18.0] - 2026-06-05

### Added

- Gate 4C conservative trade lifecycle simulation boundary in `src/backtest/lifecycle.py`.
- Lifecycle event/state models, caller observation records, transition records, simulation metadata, and deterministic JSON helpers.
- `build_trade_lifecycle_simulation(...)` for fail-closed validation over valid candle replay plus caller-supplied observations.
- Focused lifecycle tests for valid entry/exit, rejected entry, timeout without entry, missing terminal-state diagnostics, non-replay event time, unsorted events, invalid replay rejection, invalid optional price, and deterministic serialization.

### Changed

- Package version advanced to `0.18.0`.
- `src/backtest/__init__.py` now exports Gate 4C lifecycle helpers.
- VERSION and REPORT now describe the Gate 4C lifecycle simulation boundary and evidence limits.

### Fixed

- Closed the absence of a deterministic lifecycle transition boundary after Gate 4B candle replay.
- Invalid lifecycle observations now fail closed instead of becoming assumed trade outcomes.

### Removed

- None.

### Known limitations

- Gate 4C consumes caller-supplied lifecycle observations only.
- Gate 4C does not generate strategies, optimize parameters, access real exchanges, manage orders, compute performance metrics, add PAPER runtime behavior, or approve readiness.
- Local Ruff, Black, and Mypy were unavailable in the scratch environment.
- Exact final branch-head full-suite validation and remote CI are unverified until GitHub Actions reports.
- API-backed writes created several small commits rather than one atomic local commit because direct mutable local clone access was unavailable.

## [0.17.0] - 2026-06-04

### Added

- Gate 4B deterministic candle replay recovery boundary in `src/backtest/replay.py`.
- `CandleReplayRow`, `CandleReplayMetadata`, `CandleReplay`, and `CandleReplayError` models.
- `build_candle_replay(...)` for fail-closed validation and deterministic replay packaging over caller-supplied candle rows.
- Deterministic replay metadata and row JSON serialization helpers.
- Focused tests for valid ordering/metadata, deterministic metadata JSON, duplicate candles, unsorted candles, missing intervals, UTC timestamp enforcement, malformed OHLCV rows, non-positive price, negative volume, and symbol/timeframe consistency.

### Changed

- Package version advanced to `0.17.0`.
- `src/backtest/__init__.py` now exports replay helpers while preserving Gate 4A foundation exports.
- README, VERSION, PLAN, and REPORT now describe the Gate 4B replay recovery boundary.

### Fixed

- Closed the absence of a deterministic candle replay boundary in the recovered Gate 4B-4F sequence.
- Corrupted, duplicate, unsorted, incomplete, malformed, or inconsistent candle rows now fail closed before replay unless explicitly requested as read-only diagnostics.

### Removed

- None.

### Known limitations

- Gate 4B replay does not generate strategy signals, simulate trades, model fills, calculate PnL, compute win rate, Sharpe, expectancy, or drawdown, run optimizers, add PAPER runtime behavior, enable live execution, or certify readiness.
- Local Ruff, Black, and Mypy were unavailable in the scratch environment.
- Exact final branch-head full-suite validation and remote CI are unverified until GitHub Actions reports.
- API-backed writes created several small commits rather than one atomic local commit because direct mutable local clone access was unavailable.

## [0.16.0] - 2026-06-04

### Added

- Increment 4E deterministic symbol-selection hardening in `src/data/symbol_selection.py`.
- Explicit symbol-selection states and canonical reason codes.
- Deterministic symbol-selection report serialization.

### Changed

- Package version advanced to `0.16.0`.

### Fixed

- Missing exchange metadata, filters, market stats, disabled candidates, duplicate candidates, and policy violations no longer flow into selected research symbols.

### Removed

- None.

### Known limitations

- Increment 4E does not fetch exchange data, rank alpha, optimize symbols, generate signals, run backtests, simulate fills, add PAPER runtime behavior, enable live execution, add exchange credentials, or certify readiness.

## [0.15.0] - 2026-06-02

### Added

- Increment 4D read-only paper runtime DB audit pack in `src/reporting/paper_db_audit.py`.
- Deterministic JSON and Markdown paper DB audit reports.
- Diagnostics for missing schema, empty DBs, orphan lifecycle events, missing decision/lifecycle links, duplicate IDs, checksum issues, corrupted JSON, UNKNOWN rejection reasons, missing fields, lifecycle ordering issues, and inconsistent accepted/rejected transitions.

### Changed

- Package version advanced to `0.15.0`.

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
