# Aethelgard Implementation Ledger

## Readiness boundary

- Operating mode: `PAPER_ONLY`.
- Operational classification: `RESEARCH_ONLY`.
- Live order placement remains prohibited.
- No alpha, profitability, execution realism, or operational-readiness claim is made.
- Unknown execution evidence remains `UNAVAILABLE`; it is never converted to zero.

## Gate 0 — Baseline reconciliation and ledger establishment

**Status:** `COMPLETE` for repository reconciliation only.

## Gate 1 — Read-only acquisition and immutable raw-data evidence boundary

**Status:** `MERGED_TO_DEV`.

## Gate 1.1 — Acquisition integrity repair and CI evidence hardening

**Status:** `MERGED_TO_DEV`.

## Gate 2A — Append-only research decision audit trail

**Status:** `MERGED_TO_DEV`.

## Gate 2B — Database-backed persistence and audit events

**Status:** `MERGED_TO_DEV`.

## Gate 2C — Persistence integration review

**Status:** `MERGED_TO_DEV`.

## Gate 2D — Persistence reconciliation scan

**Status:** `MERGED_TO_DEV`.

## Gate 2E — Reconciliation report surface

**Status:** `MERGED_TO_DEV`.

## Gate 2F — Reconciliation report artifact persistence

**Status:** `MERGED_TO_DEV`.

## Gate 2G — Persistence and audit phase closure review

**Status:** `MERGED_TO_DEV`.

## Gate 3 — Market tick data-quality guard

**Status:** `MERGED_TO_DEV`.

## Gate 4A — Conservative backtest foundation skeleton

**Status:** `MERGED_TO_DEV`.

## Prior Increment 4B — Canonical effective RR finalization

**Status:** `MERGED_TO_DEV_AND_GREEN_BY_USER_REPORT`.

This was not the missing deterministic candle replay boundary requested by the recovery sequence.

## Prior Increment 4C — Execution context population

**Status:** `MERGED_TO_DEV_AND_GREEN_BY_USER_REPORT`.

## Prior Increment 4D — Paper runtime DB audit pack

**Status:** `MERGED_TO_DEV_AND_GREEN_BY_USER_REPORT`.

**Green head:** `47d4ddc863c7e06aebb4a13e2d9a4ace9ba8b499`.

## Prior Increment 4E — Symbol selection hardening

**Status:** `MERGED_TO_DEV_PENDING_REMOTE_VALIDATION_EVIDENCE`.

## Recovery Gate 4B — Deterministic candle replay boundary

**Status:** `IMPLEMENTED_PENDING_REMOTE_VALIDATION`.

### Scope

- Add deterministic replay over caller-supplied candle rows.
- Preserve replay row order only after UTC timestamps are strictly increasing.
- Validate UTC timestamps, duplicate candles, missing intervals, malformed OHLCV rows, non-positive prices, invalid volume, symbol consistency, and timeframe consistency.
- Produce dataset fingerprint, symbol, timeframe, start/end timestamp, row count, missing interval count, duplicate count, validation status, and deterministic hash.
- Fail closed on corrupted, duplicate, unsorted, or incomplete data unless explicitly configured for read-only diagnostics.
- Do not add strategy, signal generation, trade simulation, position state, PnL, win rate, Sharpe, expectancy, drawdown, optimizer, PAPER runtime, LIVE runtime, or readiness claims.

### Evidence classification

- `MEASURED`: starting `dev` was identical to `f4b0b6ae6c9c20afd8d42c69a14bfdfcdaff9ba7` through connector comparison.
- `MEASURED`: local isolated Gate 4B focused tests passed with `10 passed in 0.55s`.
- `MEASURED`: local isolated compile check passed.
- `MEASURED`: local isolated new-file line-length spot check passed.
- `UNAVAILABLE`: Ruff, Black, and Mypy modules were unavailable in the scratch environment.
- `UNAVAILABLE`: direct mutable local clone evidence because container DNS could not resolve `github.com`.
- `UNVERIFIED`: exact final branch-head full repository tests until CI runs.

### Boundary limit

Recovery Gate 4B validates and packages candle replay data only. It is not a strategy runtime, execution ledger, fill model, cost model, risk allocator, paper runtime, order path, performance report, or readiness certification.

## Recovery Gate 4C — Conservative trade lifecycle simulation boundary

**Status:** `IMPLEMENTED_PENDING_REMOTE_VALIDATION`.

## Gate 4D — Execution-cost evidence boundary

**Status:** `IMPLEMENTED_PENDING_REMOTE_VALIDATION`.

Gate 4D classifies execution-cost evidence as `MEASURED`, `MODELED`, or `UNAVAILABLE`, blocks net metrics while required cost evidence is unavailable, and keeps unknown costs from becoming zero. It does not compute strategy performance, optimize, place orders, or approve readiness.

## Gate 4B-0 — Minimal performance metric publication boundary

**Status:** `IMPLEMENTED_PENDING_REMOTE_VALIDATION`.

### Scope

- Consume Gate 4A `BacktestRunMetadata`.
- Reuse `assert_can_produce_performance_results(...)`.
- Emit only `METRICS_BLOCKED` or `METRICS_PUBLISHABLE` eligibility/refusal diagnostics.
- Preserve exact unavailable execution assumption names.
- Serialize eligibility/refusal payloads deterministically.
- Fail closed on malformed metadata.
- Do not replay candles, simulate trades, model costs, compute performance, optimize, add PAPER runtime behavior, place orders, or approve readiness.

### Evidence classification

- `MEASURED`: local isolated Gate 4B-0 focused tests passed with `6 passed in 0.15s`.
- `MEASURED`: local isolated compile check passed.
- `UNAVAILABLE`: Ruff, Black, and Mypy modules were unavailable in the scratch environment.
- `UNAVAILABLE`: direct mutable local clone evidence because container DNS could not resolve `github.com`.
- `UNVERIFIED`: exact final branch-head full repository tests and remote CI until GitHub Actions reports.

### Boundary limit

Gate 4B-0 is a reporting/publication guard only. It publishes no PnL, returns, win rate, drawdown, Sharpe, expectancy, alpha, profitability metric, or readiness approval.

## Gate 4B-1 — Reporting integration safety pass

**Status:** `DEFERRED_UNTIL_CONCRETE_NEW_PUBLIC_EXPORT_GAP`.

Do not continue public export work unless a concrete new reporting/export gap is found.

## Gate 4B-0A — CI evidence assumption hardening test

**Status:** `IMPLEMENTED_PENDING_REMOTE_VALIDATION`.

### Scope

- Add a focused repository test for existing `.github/workflows/ci.yml` assumptions.
- Preserve dev push and pull-request validation boundaries.
- Assert pytest JUnit evidence is generated under `reports/` and uploaded as a per-Python-version artifact.
- Assert artifact upload fails closed when JUnit evidence is missing.
- Assert compile, pytest, Ruff, Black, and Mypy validation steps remain explicit.
- Do not alter runtime, strategy, optimizer, reporting export, paper execution, live execution, order placement, or readiness status.

### Evidence classification

- `MEASURED`: connector inspection found `.github/workflows/ci.yml` exists.
- `MEASURED`: connector inspection found no equivalent CI evidence-assumption test before this increment.
- `MEASURED`: connector writes added the focused test and updated version/documentation ledgers.
- `UNAVAILABLE`: direct mutable local clone and local validation execution.
- `UNVERIFIED`: exact final branch-head full repository tests and remote CI until GitHub Actions reports.

### Boundary limit

This gate only prevents silent drift in CI evidence assumptions. It does not produce CI evidence, prove tests passed, compute any performance metric, or certify operational readiness.
