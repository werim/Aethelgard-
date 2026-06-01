# Changelog

## [0.12.0] - 2026-06-02

### Added

- Gate 4A conservative backtest foundation skeleton in `src/backtest/foundation.py`.
- Immutable `BacktestRunMetadata` for run ID, dataset fingerprint, symbol, timeframe, timestamp range, seed, config hash, code version, creation timestamp, and execution assumptions.
- Explicit `EvidenceClassification` values: `MEASURED`, `MODELED`, and `UNAVAILABLE`.
- Required execution assumption keys for fees, slippage, spreads, latency, funding, fill quality, and orderbook state.
- `unavailable_execution_assumptions(...)` helper that preserves unknown execution evidence as unavailable.
- Fail-closed performance-result guard that raises while any required execution evidence remains unavailable.
- Deterministic metadata JSON serialization.
- Focused tests for metadata determinism, unavailable-evidence blocking, required assumption coverage, UTC timestamps, hashes, and unavailable evidence integrity.

### Changed

- Package version advanced to `0.12.0`.
- README, VERSION, PLAN, and REPORT now describe Gate 4A as a metadata/evidence foundation only.
- Reconciled Gate 3 status by recording PR #10 merge into `dev` at commit `f546959764281a92942e63ca0587be83d67c6057` and PR-head validation run #70 success.

### Fixed

- Closed the absence of a minimal reproducible backtest-run metadata boundary before any replay or performance work.
- Prevented unavailable execution assumptions from being treated as zero-cost evidence.

### Removed

- None.

### Known limitations

- Gate 4A does not replay candles, generate signals, simulate trades, calculate PnL, win rate, Sharpe, expectancy, drawdown, or alpha.
- Gate 4A does not model fills, fees, slippage, spreads, latency, funding, fill quality, or orderbook state.
- Exact Gate 4A branch-head full-suite tests, Ruff, Black, and Mypy remain `UNVERIFIED` until the PR workflow runs.

## [0.11.0] - 2026-06-01

### Added

- Gate 3 stale tick data-quality guard in `src/data/stale_tick_guard.py`.
- Auditable `MarketTick`, `StaleTickDecision`, `StaleTickGuardConfig`, and `TickBuffer` models.
- Canonical reject reasons for invalid symbols, price bounds, stale local receive age, exchange timestamp future skew, missing warmup evidence, warmup drift, insufficient peer confirmation, peer-median drift, and duplicate tick sequence IDs.
- `select_first_valid_tick(...)` helper that returns the first validated tick rather than blindly accepting the first arriving tick.
- Focused tests covering pass, fail-closed rejection modes, duplicate protection, first-valid selection, and unsafe configuration handling.

### Changed

- Package version advanced to `0.11.0`.
- README, VERSION, PLAN, and REPORT now describe Gate 3 as a narrow data-quality guard, not a strategy, runtime, execution, or profitability milestone.
- Reconciled Gate 2G status by recording PR #9 merge into `dev` at commit `a5822ea66bfdbd403f18b7bd32599439a7580ce2`.

### Fixed

- Closed the absence of a reusable fail-closed pre-runtime stale tick validation boundary for research data streams.

### Removed

- None.

### Known limitations

- Gate 3 validates tick freshness and peer consistency only.
- It does not prove exchange authenticity, market-data completeness, execution realism, fill quality, latency edge, strategy expectancy, PAPER readiness, LIVE readiness, or profitability.
- Exact Gate 3 branch-head full-suite tests, Ruff, Black, and Mypy remain `UNVERIFIED` until the PR workflow runs.

## [0.10.0] - 2026-06-01

### Added

- Gate 2G persistence/audit phase closure ledger in `src/reporting/phase_closure.py`.
- Deterministic completed-gate evidence rows for Gates 2A through 2F.
- Explicit blocked-capability list for strategy generation, backtesting, execution simulation, fill modeling, risk allocation, PAPER runtime, LIVE trading, and profitability claims.
- Deterministic JSON and Markdown renderers for the phase closure ledger.
- Focused closure tests for safe status, blocked runtime capabilities, JSON determinism, Markdown limits, unsafe mode rejection, and blocked status rejection.

### Changed

- Package version advanced to `0.10.0`.
- README, VERSION, PLAN, and REPORT now describe Gate 2G as a persistence/audit phase closure review, not a trading-runtime milestone.
- Reconciled Gate 2F status by recording PR #8 merge and GitHub Actions `validation` run #63 success before Gate 2G began.
- Updated the reporting package description from Phase-1-empty to research-only evidence ledgers.

### Fixed

- Closed the documented Gate 2G gap by adding a deterministic closure ledger that keeps backtesting, strategies, execution simulation, and PAPER runtime explicitly blocked.

### Removed

- None.

### Known limitations

- Gate 2G closes only the local persistence/audit research phase.
- It does not prove execution realism, strategy expectancy, market-data completeness, PAPER runtime readiness, LIVE readiness, or profitability.
- Exact Gate 2G branch-head compilation, tests, Ruff, Black, and Mypy remain `UNVERIFIED` until the PR workflow runs.

## [0.9.0] - 2026-05-31

### Added

- Gate 2F reconciliation report artifact persistence in `src/persistence/reconciliation.py`.
- `PersistedReconciliationReportArtifact` for verified local artifact paths and checksums.
- Local persistence helper for reconciliation report JSON, Markdown, and metadata files.
- Checksum-anchored report artifact filenames and metadata filenames.
- Readback verification for metadata schema, artifact type, mode, readiness, checksums, filename anchors, and status consistency.
- Focused artifact tests for round-trip verification, idempotency, unavailable report persistence, JSON tampering, Markdown tampering, metadata tampering, and conflicting local files.

### Changed

- Package version advanced to `0.9.0`.
- README, VERSION, PLAN, and REPORT now describe Gate 2F as a narrow local reconciliation report artifact persistence boundary.
- Reconciled Gate 2E status by recording PR #7 merge and GitHub Actions `validation` run #60 success before Gate 2F began.

### Fixed

- Closed the documented absence of checksum/readback persistence for reconciliation report artifacts.
- Conflicting existing local report artifacts now fail closed instead of being overwritten.

### Removed

- None.

### Known limitations

- Gate 2F persists local report artifacts only.
- Artifact checksums detect local stored-byte changes but are not external notarization or protection against full evidence-set replacement.

## [0.8.0] - 2026-05-31

### Added

- Gate 2E reconciliation reporting helpers in `src/persistence/reconciliation.py`.
- Explicit `CONSISTENT`, `INCONSISTENT`, and `UNAVAILABLE` report states.
- Deterministic JSON-compatible payloads, compact JSON serialization, and Markdown summaries.
- Focused reporting tests for consistent, inconsistent, unavailable, JSON, and Markdown report paths.

### Changed

- Package version advanced to `0.8.0`.
- README, VERSION, PLAN, and REPORT now describe Gate 2E as a narrow reconciliation reporting surface.
- Reconciled Gate 2D status by recording PR #6 merge and GitHub Actions `validation` run #56 success before Gate 2E began.

### Fixed

- Missing reconciliation scans are now represented as `UNAVAILABLE` rather than treated as clean evidence.

### Known limitations

- Gate 2E reports local reconciliation results only.

## [0.7.0] - 2026-05-31

### Added

- Gate 2D persistence reconciliation scanner in `src/persistence/reconciliation.py`.
- Explicit reconciliation issue states for missing database events, missing file audit records, and mismatched database-event identity or payload.
- Fail-closed reconciliation assertion helper.
- Focused reconciliation tests for consistent file/database evidence and mismatch cases.

### Changed

- Package version advanced to `0.7.0`.
- Reconciled Gate 2C status by recording PR #5 merge and GitHub Actions `validation` run #51 success before Gate 2D began.

### Fixed

- Closed the documented absence of a read-only file/database reconciliation scan after Gate 2C.

### Known limitations

- Gate 2D reports mismatch states only and does not repair evidence.

## [0.6.0] - 2026-05-31

- Added Gate 2C persistence integration helper linking decision audit files to SQLite audit events.
- Package version advanced to `0.6.0`.
- Reconciled Gate 2B status by recording PR #4 merge and GitHub Actions `validation` run #48 success before Gate 2C began.

## [0.5.0] - 2026-05-30

- Added database-backed research audit-event persistence in `src/persistence/events.py`.
- Package version advanced to `0.5.0`.
- Added focused audit-event tests and local payload checksum validation.

## [0.4.0] - 2026-05-30

- Added research-only append audit persistence in `src/persistence/audit.py`.
- Package version advanced to `0.4.0`.
- Added focused audit tests and explicit evidence classification.

## [0.3.1] - 2026-05-29

- Repaired acquisition retry and restart readback evidence handling.
- Added Python 3.11/3.12 CI compile-and-test coverage.

## [0.3.0] - 2026-05-27

- Added read-only public Binance Futures historical kline acquisition and immutable raw-artifact evidence boundary.

## [0.2.0] - 2026-05-25

- Added provenance-aware historical Binance Futures kline validation and deterministic dataset fingerprints.

## [0.1.0] - 2026-05-25

- Added the PAPER-only, RESEARCH_ONLY foundation, validation tooling, and CI definition.
