# Version History

## 0.3.0 - 2026-05-27

**Engineering milestone:** Phase 2B read-only historical kline acquisition and immutable raw-artifact evidence boundary.

- Added credential-free public Binance Futures kline GET acquisition with validated fixed-interval selectors, deterministic pagination, and bounded retry/rate-limit behavior.
- Added immutable local JSON artifact and checksummed metadata persistence with retained fetch diagnostics, checksum/readback verification, and stale/future-dated acquisition-evidence rejection.
- Added fail-closed tests for incomplete pagination, unsupported or misaligned requests, retry exhaustion, stale/future-dated or tampered artifacts, and conflicting immutable writes.
- Retained `PAPER_ONLY` and `RESEARCH_ONLY`; no signal, backtest, execution, order, credential, or LIVE trading path was added.

## Validation evidence

- `MEASURED` on the reconstructed candidate workspace containing the proposed Phase 2B contents: `python -m compileall -q src tests main.py` passed; `pytest -q` passed (`22 passed`); `ruff check .` passed; `black --check .` passed; `mypy .` passed.
- Exact pushed-commit and GitHub Actions validation remain `UNVERIFIED` until CI runs on the pull-request commit.
- Public exchange authenticity, external completeness, and runtime trading behavior remain `UNVERIFIED` or `UNKNOWN`; no such claim is made.

## 0.2.0 - 2026-05-25

**Engineering milestone:** Phase 2 validated historical kline ingestion boundary.

- Added fixed-interval Binance Futures historical kline normalization and integrity checks.
- Added required source, symbol, timeframe, fetch timestamp, request-parameter, and schema-version provenance metadata.
- Added deterministic SHA-256 hashing of validated content and acquisition selectors.
- Retained PAPER_ONLY and RESEARCH_ONLY safety boundaries; no fetcher, persistence, strategy, backtest, or execution system was added.

## Validation evidence

- Local candidate-workspace validation passed: `python -m compileall -q src tests main.py` and `pytest -q` (`13 passed`).
- Ruff, Black, and Mypy are specified in project tooling but no successful execution evidence is available in this workspace; their result remains `UNVERIFIED` pending CI.
- Remote GitHub Actions evidence remains `UNVERIFIED` until a workflow run completes on this commit.

## 0.1.0 - 2026-05-25

**Engineering milestone:** Phase 1 foundation initialized.

- Established a PAPER-only, RESEARCH_ONLY project foundation.
- Added validated configuration, deterministic runtime metadata, and JSON logging.
- Added testing, linting, formatting, typing, and CI definitions.

No market data processing, strategy, backtest, risk engine, or execution capability existed in this version.

## Validation evidence

- Clean-publication validation exposed and corrected missing pytest project-root import resolution before repository publication; tests, linting, formatting check, compilation, and static typing then passed.
- Remote CI evidence remained unavailable until GitHub Actions completed a workflow run on `dev`.
