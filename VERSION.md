# Version History

## 0.20.1 - 2026-06-11

**Engineering milestone:** CI evidence assumption hardening test.

- Added `tests/test_ci_evidence_assumptions.py` to lock down the existing CI evidence contract without changing runtime, reporting, export, optimizer, or execution behavior.
- Verified the workflow remains scoped to `dev` push and pull-request validation.
- Added tests that JUnit evidence is produced under `reports/junit-${{ matrix.python-version }}.xml`, uploaded as a per-version artifact, and fails closed when the evidence file is missing.
- Added tests that compile, pytest, Ruff, Black, and Mypy validation steps remain explicit in `.github/workflows/ci.yml`.
- Advanced package version to `0.20.1`.
- Preserved PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY and the existing Gate 4B-0 public metric boundary.

## Validation evidence

- `MEASURED`: GitHub connector inspection found `.github/workflows/ci.yml` exists and already runs compile, pytest with JUnit XML evidence, artifact upload, Ruff, Black, and Mypy.
- `MEASURED`: GitHub connector inspection found no equivalent CI evidence-assumption test before adding `tests/test_ci_evidence_assumptions.py`.
- `MEASURED`: GitHub connector writes completed for the focused test and documentation/version updates.
- `UNAVAILABLE`: direct mutable local clone execution in this environment; GitHub connector writes were used.
- `UNAVAILABLE`: local full-suite pytest, Ruff, Black, and Mypy execution against the final repository state.
- `UNVERIFIED`: exact final branch-head remote CI until GitHub Actions reports.

## 0.20.0 - 2026-06-07

**Engineering milestone:** Gate 4B-0 minimal performance metric publication boundary.

- Added `src/reporting/performance_boundary.py` as a reporting-only eligibility boundary over Gate 4A `BacktestRunMetadata`.
- Added `MetricPublicationStatus` values `METRICS_BLOCKED` and `METRICS_PUBLISHABLE` plus an immutable eligibility result object.
- Reused `assert_can_produce_performance_results(...)` so unavailable Gate 4A execution evidence blocks metric publication.
- Preserved exact unavailable execution assumption names in refusal diagnostics.
- Added deterministic JSON serialization for metric-publication eligibility/refusal payloads.
- Added focused tests covering unavailable evidence blocking, measured/modeled evidence eligibility, unavailable-not-zero behavior, deterministic JSON, malformed metadata fail-closed behavior, and absence of performance metric fields.
- Exported the new reporting boundary from `src/reporting/__init__.py` and advanced package version to `0.20.0`.
- Retained the Gate 4B-0 boundary: no candle replay, no trade simulation, no cost modeling, no PnL, no returns, no win rate, no drawdown, no Sharpe, no expectancy, no optimizer, no PAPER runtime, no live trading, no order placement, no profitability claim, and no readiness approval.

## Validation evidence

- `MEASURED`: local isolated Gate 4B-0 focused tests passed with `6 passed in 0.15s`.
- `MEASURED`: local isolated compile check for the new Gate 4B-0 module and focused tests passed with exit code `0`.
- `UNAVAILABLE`: direct mutable local clone evidence for the repository because container DNS could not resolve `github.com`; GitHub connector writes were used.
- `UNAVAILABLE`: local Ruff, Black, and Mypy module execution in the scratch environment because those modules were not installed.
- `UNVERIFIED`: exact final branch-head full repository test suite and remote CI until GitHub Actions reports.

## 0.19.0 - 2026-06-05

**Engineering milestone:** Gate 4D execution-cost evidence boundary.

- Added `src/backtest/cost_evidence.py` with explicit execution-cost evidence records for fees, slippage, spread, funding, and latency.
- Added `CostEvidenceClassification` values `MEASURED`, `MODELED`, and `UNAVAILABLE` plus deterministic gate/report serialization helpers.
- Added `evaluate_cost_evidence_gate(...)` and `assert_can_publish_net_metrics(...)` so net PnL, expectancy, profitability ranking, optimizer input, and readiness approval remain blocked while required costs are unavailable.
- Enforced that `UNAVAILABLE` execution-cost evidence cannot carry a value or unit, so unknown costs cannot become zero.
- Allowed modeled-cost metrics only when assumptions are present and the result is labeled `NET_MODELED_COST_METRICS`.
- Added markdown reporting for cost evidence diagnostics and focused tests covering missing fees, slippage, spread, funding, latency, unavailable-not-zero behavior, modeled assumptions, measured pass behavior, report visibility, and readiness blocking.
- Exported Gate 4D helpers from `src/backtest/__init__.py` and advanced package version to `0.19.0`.
- Retained the Gate 4D boundary: no optimizer, no strategy tuning, no alpha generation, no live trading, no exchange order placement, no PAPER runtime behavior, no profitability claim, and no readiness approval.

## Validation evidence

- `MEASURED`: local isolated Gate 4D focused tests passed with `12 passed in 0.14s` after the final line-length adjustment.
- `MEASURED`: local isolated compile check for the new Gate 4D module and tests passed with exit code `0`.
- `MEASURED`: local isolated line-length spot check found no lines above 88 characters in the new Gate 4D source/test files.
- `UNAVAILABLE`: direct mutable local clone evidence for the repository because container DNS could not resolve `github.com`; GitHub connector writes were used.
- `UNAVAILABLE`: local Ruff, Black, and Mypy module execution in the scratch environment because those modules were not installed.
- `UNVERIFIED`: exact final branch-head full repository test suite and remote CI until GitHub Actions reports.

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
- `UNVERIFIED`: exact final branch-head full repository tests and remote CI until GitHub Actions reports.

## 0.17.0 - 2026-06-04

**Engineering milestone:** Gate 4B deterministic candle replay recovery boundary.

- Started from verified `dev` head `f4b0b6ae6c9c20afd8d42c69a14bfdfcdaff9ba7`, which the connector showed was identical to `dev` before this recovery work.
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
- `UNVERIFIED`: exact final branch-head full repository tests until CI runs.

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
