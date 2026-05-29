# Changelog

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

### Fixed

- Fixed the bounded retry gap where transport failures occurring before any HTTP response bypassed `max_retries`.
- Fixed the restart verification gap where metadata checksum identity existed only in an in-memory `PersistedArtifact` value.
- Corrected the merged Phase 2B documentation state to acknowledge successful repaired-head validation before merge and the two subsequently discovered integrity findings.

### Removed

- None.

### Known limitations

- Checksum-addressed local filenames verify ordinary stored-byte consistency and reject accidental/local tampering after restart; they are not cryptographic signatures against an adversary able to replace and rename all artifact files.
- Public HTTP acquisition plus local checksums do not prove Binance authenticity, external completeness beyond the requested fixed range, or data fitness for trading decisions.
- No generalized decision persistence, backtesting, execution-cost simulation, strategy, risk allocation, PAPER runtime, or reporting pipeline is implemented.
- Exact PR-commit full-suite and Python 3.12 evidence remain `UNVERIFIED` until the proposed workflow completes.

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
