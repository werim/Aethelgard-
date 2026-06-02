# Changelog

## [0.14.0] - 2026-06-02

### Added

- Increment 4C execution context snapshot boundary in `src/execution/context.py`.
- `ExecutionContextInput`, `ExecutionContextSnapshot`, `ExecutionAssumptionSnapshot`, `ExecutionContextStatus`, `ExecutionContextAssumption`, and `ExecutionContextDecisionOutcome` models.
- Explicit required execution assumptions for spread, fee, slippage, latency, and funding.
- `build_execution_context_snapshot(...)` to classify context as `VALID`, `INVALID`, or `UNAVAILABLE`.
- `unavailable_execution_context_assumptions(...)`, `execution_context_json(...)`, `assert_execution_context_usable(...)`, and `execution_context_audit_evidence(...)`.
- Focused tests for fully populated context, missing spread, missing fee, missing slippage, missing latency/funding, missing timestamp, stale market input, unavailable market input, rejected-decision diagnostics, missing price references, zero-value unavailable assumptions, and audit evidence round-trip.

### Changed

- Package version advanced to `0.14.0`.
- README, VERSION, PLAN, and REPORT now describe Increment 4C as an execution-context evidence boundary only.
- `src/execution/__init__.py` now exports research-only execution context helpers.

### Fixed

- Closed the absence of explicit execution context snapshots before later paper-runtime audit work.
- Prevented missing execution-cost assumptions from silently becoming zero.
- Stale or unavailable critical market input now fails closed.

### Removed

- None.

### Known limitations

- Increment 4C does not simulate fills, assume execution quality, add paper runtime behavior, enable live execution, add strategy logic, or certify readiness.
- Remote CI remains the source of truth for branch-head full-suite checks.

## [0.13.0] - 2026-06-02

### Added

- Increment 4B canonical effective RR boundary in `src/execution/effective_rr.py`.
- `EffectiveRRInput`, `EffectiveRRResult`, `EffectiveRRStatus`, and `TradeSide` models.
- `canonical_effective_rr(...)` as the single canonical calculation path for caller-provided entry, stop, and take-profit references.
- `assert_effective_rr_valid(...)` fail-closed guard.
- `effective_rr_audit_evidence(...)` and `effective_rr_report_row(...)` projections derived only from the canonical result.
- Focused tests for valid LONG RR, valid SHORT RR, zero/negative/invalid distances, non-finite values, missing references, raw/canonical mismatch, source validation, and persistence/reporting consistency.

### Changed

- Package version advanced to `0.13.0`.
- README, VERSION, PLAN, and REPORT now describe Increment 4B as a canonical RR evidence boundary only.
- `src/execution/__init__.py` now exports research-only effective RR helpers.

### Fixed

- Closed the absence of a single canonical effective RR calculation path before later decision/context work.
- Prevented raw expected RR from silently overriding or replacing canonical effective RR.
- Missing RR inputs remain explicitly unavailable rather than being guessed or converted to zero.

### Removed

- None.

### Known limitations

- Increment 4B does not add strategy logic, signal generation, candle replay, trade simulation, fill modeling, execution-cost modeling, risk allocation, PAPER runtime behavior, readiness certification, or profitability claims.

## [0.12.0] - 2026-06-02

- Added Gate 4A conservative backtest foundation skeleton.

## [0.11.0] - 2026-06-01

- Added Gate 3 stale tick data-quality guard.

## [0.10.0] - 2026-06-01

- Added Gate 2G persistence/audit phase closure ledger.

## [0.9.0] - 2026-05-31

- Added Gate 2F reconciliation report artifact persistence.

## [0.8.0] - 2026-05-31

- Added Gate 2E reconciliation reporting helpers.

## [0.7.0] - 2026-05-31

- Added Gate 2D persistence reconciliation scanner.

## [0.6.0] - 2026-05-31

- Added Gate 2C persistence integration helper linking decision audit files to SQLite audit events.

## [0.5.0] - 2026-05-30

- Added database-backed research audit-event persistence.

## [0.4.0] - 2026-05-30

- Added research-only append audit persistence.

## [0.3.1] - 2026-05-29

- Repaired acquisition retry and restart readback evidence handling.

## [0.3.0] - 2026-05-27

- Added read-only public Binance Futures historical kline acquisition and immutable raw-artifact evidence boundary.

## [0.2.0] - 2026-05-25

- Added provenance-aware historical Binance Futures kline validation and deterministic dataset fingerprints.

## [0.1.0] - 2026-05-25

- Added the PAPER-only, RESEARCH_ONLY foundation, validation tooling, and CI definition.
