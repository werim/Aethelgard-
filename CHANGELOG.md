# Changelog

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
- Exact Gate 2F branch-head compilation, tests, Ruff, Black, and Mypy remain `UNVERIFIED` until the PR workflow runs.

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
