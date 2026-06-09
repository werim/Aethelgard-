# Changelog

## [0.20.0] - 2026-06-07

### Added

- Gate 4B-0 metric-publication eligibility boundary in `src/reporting/performance_boundary.py`.
- Gate 4B replay hardening coverage for metric-like and execution-like field leakage.
- Gate 4B-1 guarded report-publication helpers over an existing Gate 4B-0 eligibility result.
- Gate 4B-2 forged-eligibility regression coverage.

### Changed

- Package version advanced to `0.20.0`.
- `src/reporting/__init__.py` exports Gate 4B-0 and Gate 4B-1 reporting helpers.
- Gate 4B-2 records a reporting-boundary completeness audit of report, Markdown, JSON, payload, and serialization paths.
- The guarded publication helper now requires eligibility produced by the Gate 4B evaluator before caller payload publication.

### Fixed

- Unavailable Gate 4A execution evidence blocks metric-publication eligibility.
- Unsafe or malformed backtest metadata fails closed as `METRICS_BLOCKED`.
- Unknown execution evidence remains unavailable and is not converted to zero.
- Gate 4B-2 rejects manually constructed publishable `MetricPublicationEligibility` objects before guarded payload publication.

### Known limitations

- Gate 4B-0, Gate 4B-1, and Gate 4B-2 do not compute performance, model costs, add optimizer behavior, add PAPER runtime behavior, mutate market state, or approve readiness.
- Exact final branch-head full-suite validation remains unavailable locally; focused reconstructed validation passed for Gate 4B-2.
- API-backed writes created several small commits rather than one atomic local commit because direct mutable local clone access was unavailable.

## [0.19.0] - 2026-06-05

- Added Gate 4D execution-cost evidence boundary in `src/backtest/cost_evidence.py`.
- Added explicit measured, modeled, and unavailable cost-evidence diagnostics.
- Unknown execution costs remain unavailable rather than silently becoming zero.
- Package version advanced to `0.19.0`.

## [0.18.0] - 2026-06-05

- Added Gate 4C conservative lifecycle boundary in `src/backtest/lifecycle.py`.
- Added caller-observation records, transition records, metadata, deterministic JSON helpers, and focused fail-closed tests.
- Package version advanced to `0.18.0`.

## [0.17.0] - 2026-06-04

- Added Gate 4B deterministic candle replay recovery boundary in `src/backtest/replay.py`.
- Added replay row, replay metadata, deterministic JSON helpers, and focused data-validation tests.
- Package version advanced to `0.17.0`.

## [0.16.0] - 2026-06-04

- Added Increment 4E deterministic symbol-selection hardening in `src/data/symbol_selection.py`.
- Package version advanced to `0.16.0`.

## [0.15.0] - 2026-06-02

- Added Increment 4D read-only paper runtime DB audit pack in `src/reporting/paper_db_audit.py`.
- Added deterministic JSON and Markdown audit reports.
- Package version advanced to `0.15.0`.

## [0.14.0] - 2026-06-02

- Added Increment 4C execution context snapshot boundary in `src/execution/context.py`.
- Missing execution-cost assumptions remain unavailable instead of silently becoming zero.
- Package version advanced to `0.14.0`.

## [0.13.0] - 2026-06-02

- Added Increment 4B canonical effective RR boundary in `src/execution/effective_rr.py`.
- Missing RR inputs remain unavailable rather than guessed or converted to zero.
- Package version advanced to `0.13.0`.

## [0.12.0] - 2026-06-02

- Added Gate 4A conservative backtest foundation skeleton in `src/backtest/foundation.py`.
- Performance results are blocked while required execution evidence is unavailable.
- Package version advanced to `0.12.0`.

## [0.11.0] - 2026-06-01

- Added Gate 3 stale tick data-quality guard in `src/data/stale_tick_guard.py`.
- Package version advanced to `0.11.0`.

## [0.10.0] - 2026-06-01

- Added Gate 2G persistence/audit phase closure ledger.
- Package version advanced to `0.10.0`.

## [0.9.0] - 2026-05-31

- Added Gate 2F reconciliation report artifact persistence.
- Package version advanced to `0.9.0`.
