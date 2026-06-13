# Version History

## 0.21.0 - 2026-06-13

**Engineering milestone:** Gate 5A operational evidence gate and deployment-blocker matrix.

- Added `src/reporting/operational_evidence.py` as a deterministic PAPER-only operational evidence diagnostic boundary.
- Added Gate 5A evidence classifications `MEASURED`, `MODELED`, and `UNAVAILABLE` plus fail-closed blocker statuses `BLOCKED` and `CLEARED`.
- Added required blocker categories for audit trail integrity, CI validation, data freshness, execution-cost evidence, PAPER runtime reconciliation, and risk-control enforcement.
- Added `evaluate_operational_evidence_gate(...)`, `assert_operational_deployment_not_blocked(...)`, deterministic JSON serialization, and Markdown matrix rendering.
- Added focused tests proving missing evidence blocks, modeled cost evidence blocks, all-measured evidence clears the diagnostic matrix, JSON remains deterministic, and safety text remains visible.
- Exported the Gate 5A reporting helpers from `src.reporting` and advanced package version to `0.21.0`.
- Retained the safety boundary: no runtime behavior, no strategy logic, no optimizer, no execution-cost modeling, no performance calculation, no PAPER runtime expansion, no exchange mutation, no LIVE readiness, and no production-readiness approval.

## Validation evidence

- `MEASURED`: connector comparison resolved `dev` HEAD `8fca2c83ea11fd1f1d6279c48b168305df55015e` before this increment.
- `MEASURED`: `PROJECT_STATE.md`, `PLAN.md`, `REPORT.md`, `CHANGELOG.md`, and `VERSION.md` were read from `dev` before this increment.
- `MEASURED`: reconstructed focused Gate 5A validation passed `python -m compileall -q src tests` and `pytest -q tests/test_operational_evidence_gate.py` with `5 passed` in the scratch workspace.
- `UNAVAILABLE`: direct mutable local clone evidence because container DNS could not resolve `github.com`.
- `UNAVAILABLE`: exact branch-head full-repository local validation, Ruff, Black, and Mypy in this execution environment.
- `UNVERIFIED`: exact final branch-head remote CI until GitHub Actions reports.

## 0.20.0 - 2026-06-07

**Engineering milestone:** Gate 4B reporting-boundary and ledger-reconciliation bundle, including Gate 4CLOSE-1A evidence-matrix reconciliation, Gate 4CLOSE-1B validation-command ledger consistency, and Gate 4CLOSE-1C validation-command canonicalization.

- Added `src/reporting/performance_boundary.py` as a reporting-only eligibility boundary over Gate 4A `BacktestRunMetadata`.
- Added `MetricPublicationStatus` values `METRICS_BLOCKED` and `METRICS_PUBLISHABLE` plus an immutable eligibility result object.
- Reused `assert_can_produce_performance_results(...)` so unavailable Gate 4A execution evidence blocks metric publication.
- Preserved exact unavailable execution assumption names in refusal diagnostics.
- Added deterministic JSON serialization for metric-publication eligibility/refusal payloads.
- Added focused tests covering unavailable evidence blocking, measured/modeled evidence eligibility, unavailable-not-zero behavior, deterministic JSON, malformed metadata fail-closed behavior, and absence of performance metric fields.
- Exported the new reporting boundary from `src/reporting/__init__.py` and advanced package version to `0.20.0`.
- Recorded Gate 4B-5 project-state ledger reconciliation so `VERSION.md`, `CHANGELOG.md`, `REPORT.md`, and `PROJECT_STATE.md` identify the same current documentation/test-only increment.
- Added Gate 4CLOSE-1 completion evidence matrix for Gate 4 source, test, safety-text, and public-export evidence.
- Completed Gate 4CLOSE-1A matrix wording reconciliation so the public-export evidence claim is limited to checked live/order/runtime names on public package surfaces.
- Added Gate 4CLOSE-1B validation-command ledger consistency coverage so `REPORT.md` and `PROJECT_STATE.md` keep the same validation command surface and preserve explicit `UNAVAILABLE` local-execution wording.
- Added Gate 4CLOSE-1C validation-command canonicalization so `REPORT.md`, `PROJECT_STATE.md`, and the Gate 4 completion matrix keep the same validation command surface.
- Retained the Gate 4B-0 through Gate 4CLOSE-1C boundary: no runtime behavior, no strategy logic, no optimizer, no execution-cost modeling, no performance calculation, no PAPER runtime expansion, no exchange mutation, and no readiness approval.

## Validation evidence

- `MEASURED`: local isolated Gate 4B-0 focused tests passed with `6 passed in 0.15s`.
- `MEASURED`: local isolated compile check for the new Gate 4B-0 module and focused tests passed with exit code `0`.
- `MEASURED`: Gate 4B-5A review evidence identified and repaired `VERSION.md` ledger drift for Gate 4B-5.
- `MEASURED`: Gate 4CLOSE-1A connector evidence updated the matrix and focused matrix test on `dev` through commit `334bb0d909bdc1e8538ebeee5336c3b71bf7a77a`.
- `MEASURED`: user-provided CI screenshot shows validation run `#196` succeeded for commit `334bb0d` on `dev`, including Python 3.11 and 3.12 jobs.
- `MEASURED`: Gate 4CLOSE-1B connector evidence added validation-command ledger consistency coverage on PR branch `gate4close-1b-validation-ledger`.
- `MEASURED`: Gate 4CLOSE-1C connector evidence expanded validation-command ledger canonicalization coverage on PR branch `gate4close-1c-validation-ledger`.
- `UNAVAILABLE`: direct mutable local clone evidence for the repository because GitHub connector writes were used.
- `UNAVAILABLE`: local command execution for Gate 4CLOSE-1C in this execution environment until run in a mutable clone or CI.
- `UNVERIFIED`: connector-visible workflow/status APIs may remain empty even when user-provided CI evidence is available.

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
- `UNVERIFIED`: exact final branch-head full repository tests and remote CI until GitHub Actions reports.

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
- Added replay row, replay metadata, deterministic JSON helpers, and focused data-validation tests.
- Exported replay helpers from `src/backtest/__init__.py` while preserving Gate 4A foundation exports.
- Retained the boundary: no strategy, signal generation, trade simulation, position state, PnL, win rate, Sharpe, expectancy, drawdown, optimizer, PAPER runtime, LIVE runtime, or readiness claim was added.

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
