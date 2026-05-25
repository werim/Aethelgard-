# Changelog

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
- Remote GitHub Actions CI evidence remains unavailable until a workflow run completes on the published `dev` branch.
