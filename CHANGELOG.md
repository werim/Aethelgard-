# Changelog

## [0.4.0] - 2026-05-30

### Added

- Research-only append audit persistence in `src/persistence/audit.py` for `REJECTED` and `NO_ACTION` decision outcomes.
- Explicit decision-evidence classification for `MEASURED`, `MODELED`, and `UNAVAILABLE` inputs.
- Checksum-addressed local audit filenames plus durable `decision_id.claim` anchors for conflict detection.
- Audit tests covering readback, idempotent append, conflicting decision identities, missing/orphaned claims, checksum tampering, unavailable evidence, missing measured evidence source references, non-UTC timestamps, and unsafe operating mode rejection.

### Changed

- Package version advanced to `0.4.0` and project phase metadata advanced to `PERSISTENCE_AUDIT`.
- README, VERSION, PLAN, and REPORT records now reflect that Gate 1.1 completed GitHub Actions run #14 successfully and that Gate 2A starts from merged `dev` commit `d09b7361a26f61d6cea7c0077d6d22a913548df0`.
- `src/persistence/__init__.py` now describes the research-only persistence boundary instead of remaining Phase-1-empty.

### Fixed

- Closed the documented absence of any generalized decision/rejection audit persistence boundary at the smallest local-file evidence layer.
- Prevented unavailable execution evidence from being persisted as a misleading zero value by requiring `UNAVAILABLE` evidence to carry a reason and no value/source reference.

### Removed

- None.

### Known limitations

- Gate 2A stores local JSON audit evidence and claim files only; it is not a database-backed event ledger or transactional runtime journal.
- Audit records do not generate decisions, issue signals, run backtests, model fills, estimate profitability, submit orders, or certify PAPER/LIVE readiness.
- Local checksum and claim files verify ordinary local stored-byte consistency and decision identity conflicts only. They are not external notarization or protection against an adversary able to replace the complete evidence set.
- Exact Gate 2A branch-head GitHub Actions validation remains `UNVERIFIED` until the PR workflow runs.

## [0.3.1] - 2026-05-29

### Added

- Transient pre-response transport-failure retry coverage and persisted transient-failure diagnostics in the public kline acquisition boundary.
- Restart-safe local artifact discovery using checksum-addressed metadata filenames.
- Tests for transient retry success/exhaustion, restart discovery, tampered or absent metadata anchors, diagnostics retention, and credential-free GET transport behavior.
- GitHub Actions Python 3.11/3.12 compile-and-test matrix and persisted JUnit test evidence artifacts.

### Changed

- Package version advanced to `0.3.1` while the research phase remains `DATA_ACQUISITION`.
- Ruff, Black, and Mypy run once on Python 3.11; code compilation and tests run on both supported CI interpreters.
- Documentation records that Gate 2 remains blocked until this Gate 1.1 integrity repair is reviewed and merged.
- Added narrowly scoped follow-up repairs after remote validation: Black-required test formatting and a Mypy-safe direct `urllib.request.Request` type reference in the public-transport test.

### Fixed

- Fixed the bounded retry gap where transport failures occurring before any HTTP response bypassed `max_retries`.
- Fixed the restart verification gap where metadata checksum identity existed only in an in-memory `PersistedArtifact` value.
- Corrected the merged Phase 2B documentation state to acknowledge successful repaired-head validation before merge and the two subsequently discovered integrity findings.
- Fixed CI findings without altering acquisition behavior: Black formatting in the checksum-anchor test and Mypy type resolution in the GET/no-credential test.

### Removed

- None.

### Known limitations

- Checksum-addressed local filenames verify ordinary stored-byte consistency and reject accidental/local tampering after restart; they are not cryptographic signatures against an adversary able to replace and rename all artifact files.
- Public HTTP acquisition plus local checksums do not prove Binance authenticity, external completeness beyond the requested fixed range, or data fitness for trading decisions.
- No generalized decision persistence, backtesting, execution-cost simulation, strategy, risk allocation, PAPER runtime, or reporting pipeline is implemented.
- GitHub Actions run #14 on the corrected PR #2 head completed successfully.

## [0.3.0] - 2026-05-27

### Added

- Read-only public Binance Futures historical kline acquisition using credential-free GET requests only.
- Fixed-interval request validation, deterministic pagination, bounded retry/rate-limit handling, immutable raw JSON and checksummed metadata evidence.

### Fixed

- Corrected the `tests/test_klines.py` import organization defect reported by the initial PR GitHub Actions workflow.

### Known limitations

- Review after merge identified incomplete pre-response transport retry handling and non-durable metadata checksum identity; these are addressed in `0.3.1`.

## [0.2.0] - 2026-05-25

- Added provenance-aware historical Binance Futures kline validation and deterministic dataset fingerprints.

## [0.1.0] - 2026-05-25

- Added the PAPER-only, RESEARCH_ONLY foundation, validation tooling, and CI definition.
