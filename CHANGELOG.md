# Changelog

## [0.3.0] - 2026-05-27

### Added

- Read-only public Binance Futures historical kline acquisition in `src/data/acquisition.py` using credential-free GET requests only.
- Fixed-interval request validation, deterministic cursor pagination, bounded retry/rate-limit handling, and persisted request diagnostics.
- Immutable raw JSON artifact plus checksummed metadata storage, checksum/readback verification, and stale/future-dated acquisition-evidence rejection.
- Acquisition-boundary tests covering pagination, bounded retry and retry exhaustion, incomplete data, unsupported/misaligned selectors, stale/future-dated or tampered evidence, and immutable-write conflict rejection.

### Changed

- Project phase metadata advanced from `DATA_INGESTION` to `DATA_ACQUISITION` while retaining `PAPER_ONLY` and `RESEARCH_ONLY` controls.
- Package version advanced to `0.3.0`.
- Documentation records the Phase 2B measured candidate-validation boundary and remaining evidence limits.

### Fixed

- Closed the documented absence of read-only acquisition, acquisition-evidence freshness rejection, and immutable artifact checksum/readback storage within the bounded data layer.

### Removed

- None.

### Known limitations

- Public HTTP acquisition plus local checksums do not prove Binance authenticity, external completeness beyond the requested fixed range, or data fitness for trading decisions.
- Only listed fixed-duration intervals are admitted; calendar-month intervals are intentionally unsupported.
- No persistence for runtime decisions, backtesting, execution-cost simulation, strategy, risk allocation, paper runtime, or reporting pipeline is implemented.
- Exact PR-commit CI validation remains `UNVERIFIED` until GitHub Actions runs on the pushed branch.

## [0.2.0] - 2026-05-25

### Added

- Provenance-aware historical Binance Futures kline validation in `src/data/klines.py`.
- Fail-closed checks for missing metadata, non-UTC fetch timestamps, malformed row shapes, invalid OHLC ranges, negative volume/trade values, timestamp alignment, duplicate timestamps, and missing candle gaps.
- Deterministic dataset SHA-256 fingerprints for validated supplied rows and acquisition selectors.
- Automated ingestion-boundary validation tests.

### Changed

- Project phase metadata advanced from `FOUNDATION` to `DATA_INGESTION` while retaining `PAPER_ONLY` and `RESEARCH_ONLY` controls.
- Package version advanced to `0.2.0`.

### Fixed

- None.

### Removed

- None.

### Known limitations

- No exchange fetcher or persisted immutable raw-data artifact is implemented; provenance is validated metadata supplied at the ingestion boundary, not independently authenticated evidence.
- Dataset hashing verifies deterministic supplied content, not external completeness or Binance authenticity.
- No persistence, backtesting, execution-cost simulation, strategy, risk allocation, paper runtime, or reporting pipeline is implemented.
- Ruff, Black, Mypy, and remote GitHub Actions results for this change remain `UNVERIFIED` until executed in an environment with those tools.

## [0.1.0] - 2026-05-25

### Added

- Public-repository-ready Phase 1 project structure and MIT license.
- YAML plus environment-backed configuration loading with strict PAPER-only safety validation.
- Deterministic seed setup and auditable runtime metadata snapshot.
- Structured JSON logging configuration.
- Pytest tests and Ruff, Black, Mypy, and GitHub Actions CI configuration.
- Initial governance-aligned documentation and safety posture.

### Changed

- None. Initial foundation release.

### Fixed

- Corrected initial Ruff formatting and `StrEnum` findings detected during pre-commit validation.
- Corrected clean-extraction pytest import resolution so the project test suite collects reliably before publication.

### Removed

- None. Initial foundation release.

### Known limitations

- No market-data ingestion, persistence, backtesting, strategy, risk allocation, execution simulator, paper runtime, or reporting pipeline is implemented.
- Runtime determinism is limited to Phase 1 Python seed declaration; it does not yet prove dataset or simulation reproducibility.
- Remote GitHub Actions CI evidence remains unavailable until GitHub Actions completes a workflow run on the published `dev` branch.
