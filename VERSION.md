# Version History

## 0.18.0 - 2026-06-05

**Engineering milestone:** Gate 4C conservative trade lifecycle simulation boundary.

- Reviewed Gate 4B first. Existing docs showed `0.17.0` Gate 4B deterministic candle replay and identified Gate 4C as the next safe recovery step.
- Added `src/backtest/lifecycle.py` with a deterministic, research-only lifecycle transition boundary over a valid `CandleReplay` plus caller-supplied observations.
- Added lifecycle event/state models, observation and transition records, simulation metadata, deterministic JSON helpers, and `build_trade_lifecycle_simulation(...)`.
- Validates trade ID presence, valid replay availability, UTC event timestamps, strictly increasing observation times, event alignment to replay candle open times, optional positive prices, supported event types, and conservative state transitions.
- Supports terminal evidence states only from caller observations: `POSITION_OBSERVED_CLOSED`, `ENTRY_REJECTED`, and `TIMED_OUT`.
- Fails closed on missing terminal state, terminal event before entry, duplicate/invalid entry observation, event after terminal state, non-replay event time, invalid replay, malformed timestamps, invalid prices, and unsupported event types.
- Added focused lifecycle tests covering valid entry/exit, rejected entry, timeout without entry, missing terminal state diagnostics, non-replay event time, unsorted events, invalid replay rejection, invalid optional price, and deterministic serialization.
- Exported lifecycle helpers from `src/backtest/__init__.py`.
- Retained the Gate 4C boundary: no strategy generation, no optimizer, no real exchange action, no order-management path, no cost accounting, no performance metric, no PAPER runtime behavior, and no readiness approval.

## Validation evidence

- `MEASURED`: local isolated Gate 4C focused tests passed with `9 passed in 0.21s`.
- `MEASURED`: local isolated compile check for the new Gate 4C module and tests passed with exit code `0`.
- `MEASURED`: local isolated line-length spot check found no lines above 88 characters in the new Gate 4C source/test files.
- `UNAVAILABLE`: direct mutable local clone evidence for the repository because GitHub writes were performed through the connector API.
- `UNAVAILABLE`: local Ruff, Black, and Mypy module execution in the scratch environment.
- `UNVERIFIED`: exact final branch-head full repository test suite and remote CI until GitHub Actions reports.

## 0.17.0 - 2026-06-04

**Engineering milestone:** Gate 4B deterministic candle replay recovery boundary.

- Started from verified `dev` head `f4b0b6ae6c9c20afd8d42c69a14bfdfcdaff9ba7`, which the connector showed was identical to `dev` before this recovery work.
- Startup recovery found the prompt's expected Gate 4A baseline was outdated: repository `dev` was already at `0.16.0 / Increment 4E`, while deterministic candle replay remained absent.
- Added `src/backtest/replay.py` with deterministic, research-only candle replay over caller-supplied rows.
- Added `CandleReplayRow`, `CandleReplayMetadata`, `CandleReplay`, `CandleReplayError`, `build_candle_replay(...)`, `candle_replay_metadata_json(...)`, and `candle_replay_rows_json(...)`.
- Validates UTC timestamps, strictly increasing open times, duplicate candles, missing candle intervals, malformed OHLC bounds, non-positive prices, invalid volume, symbol consistency, and timeframe consistency.
- Produces auditable replay metadata: dataset fingerprint, symbol, timeframe, start/end timestamp, row count, missing interval count, duplicate count, validation status, and deterministic hash.
- Fails closed on invalid replay data unless explicitly configured for read-only diagnostics, in which case invalid rows cannot be replayed.
- Added focused replay tests covering valid ordering/metadata, deterministic metadata JSON, duplicates, unsorted data, missing intervals, UTC enforcement, malformed OHLCV rows, non-positive price, negative volume, and symbol/timeframe mismatches.
- Exported replay helpers from `src/backtest/__init__.py` while preserving Gate 4A foundation exports.
- Retained the boundary: no strategy, signal generation, trade simulation, position state, PnL, win rate, Sharpe, expectancy, drawdown, optimizer, PAPER runtime, LIVE runtime, or readiness claim was added.

## Validation evidence

- `MEASURED`: connector comparison showed starting `dev` was identical to `f4b0b6ae6c9c20afd8d42c69a14bfdfcdaff9ba7` before Gate 4B recovery began.
- `MEASURED`: local isolated Gate 4B focused tests passed with `10 passed in 0.55s`.
- `MEASURED`: local isolated compile check passed with exit code `0`.
- `MEASURED`: local isolated new-file line-length spot check found no lines above 88 characters in the new 4B source/test files.
- `UNAVAILABLE`: direct mutable local clone evidence because container network DNS could not resolve `github.com`.
- `UNAVAILABLE`: local Ruff, Black, and Mypy module execution in the scratch environment.
- `UNVERIFIED`: exact final branch-head full repository tests and remote CI until GitHub Actions reports.

## 0.16.0 - 2026-06-04

**Engineering milestone:** Increment 4E symbol selection hardening.

- Added deterministic research-only symbol-selection hardening in `src/data/symbol_selection.py`.
- Required caller-provided exchange metadata and market-liquidity evidence; missing evidence remains `UNAVAILABLE`.
- Retained the boundary: no exchange fetch, alpha ranking, optimizer, strategy logic, backtest replay, fill simulation, PAPER runtime behavior, readiness certification, or live order path was added.

## 0.15.0 - 2026-06-02

**Engineering milestone:** Increment 4D paper runtime DB audit pack.

- Added read-only SQLite paper runtime database integrity audit reporting.
- Retained the boundary: no DB repair, row deletion, historical rewrite, synthetic field invention, strategy logic, PAPER runtime behavior, readiness certification, or live order path was added.

## 0.14.0 - 2026-06-02

**Engineering milestone:** Increment 4C execution context population.

- Added explicit execution context snapshots and cost-assumption evidence.
- Missing execution-cost assumptions remain `UNAVAILABLE` and cannot carry zero values.

## 0.13.0 - 2026-06-02

**Engineering milestone:** Increment 4B canonical effective RR finalization.

- Added a single canonical effective RR calculation path.
- Preserved raw expected RR separately from canonical `effective_rr`.
- Retained the boundary: no optimizer, strategy logic, risk allocation, backtest replay, fill simulation, PAPER runtime, readiness certification, or live order path was added.

## 0.12.0 - 2026-06-02

**Engineering milestone:** Gate 4A conservative backtest foundation skeleton.

- Added immutable backtest run metadata and execution evidence records.
- Added fail-closed validation so performance results cannot be produced while any required execution evidence is unavailable.

## 0.11.0 - 2026-06-01

**Engineering milestone:** Gate 3 market tick data-quality guard.

- Added pre-runtime stale tick validation and first-valid tick selection.

## 0.10.0 - 2026-06-01

**Engineering milestone:** Gate 2G persistence/audit phase closure review.

- Added deterministic persistence/audit phase closure reporting.

## 0.9.0 - 2026-05-31

**Engineering milestone:** Gate 2F reconciliation report artifact persistence.

## 0.8.0 - 2026-05-31

**Engineering milestone:** Gate 2E reconciliation report surface.

## 0.7.0 - 2026-05-31

**Engineering milestone:** Gate 2D persistence reconciliation scan.

## 0.6.0 - 2026-05-31

**Engineering milestone:** Gate 2C persistence integration review.

## 0.5.0 - 2026-05-30

**Engineering milestone:** Gate 2B database-backed audit-event persistence boundary.

## 0.4.0 - 2026-05-30

**Engineering milestone:** Gate 2A append-only research decision audit-trail boundary.

## 0.3.1 - 2026-05-29

**Engineering milestone:** Phase 2B.1 acquisition-integrity repair and validation evidence hardening.

## 0.3.0 - 2026-05-27

**Engineering milestone:** Phase 2B read-only historical kline acquisition and immutable raw-artifact evidence boundary.

## 0.2.0 - 2026-05-25

**Engineering milestone:** Phase 2 validated historical kline ingestion boundary.

## 0.1.0 - 2026-05-25

**Engineering milestone:** Phase 1 foundation initialized.
