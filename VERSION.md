# Version History

## 0.3.1 - 2026-05-29

**Engineering milestone:** Phase 2B.1 acquisition-integrity repair and validation evidence hardening.

- Repaired bounded retry handling so transient public-transport failures before an HTTP response are retried within policy and recorded in diagnostics.
- Repaired restart readback evidence by encoding metadata SHA-256 identity in the immutable metadata filename and adding checksum-aware artifact discovery.
- Added fail-closed tests for transient transport retry/exhaustion, restart discovery, tampered or missing metadata checksum anchors, retry diagnostics, and GET-only public transport behavior.
- Hardened GitHub Actions validation with Python 3.11/3.12 compile-and-test coverage plus JUnit artifacts; Ruff, Black, and Mypy remain Python 3.11 gates.
- Retained `PAPER_ONLY` and `RESEARCH_ONLY`; no backtest, strategy, risk, execution, order, or LIVE trading path was added.

## Validation evidence

- `MEASURED` before PR creation in a reconstructed targeted workspace: `python -m compileall -q src tests` passed and `python -m pytest -q tests/test_acquisition.py` passed (`17 passed`).
- Ruff, Black, Mypy, the full repository suite, and Python 3.12 validation are `UNVERIFIED` locally because the directly cloned repository/tool environment was unavailable; the proposed workflow is the required remote validation gate.
- The merged Phase 2B PR repair head `cd7c1e642525da7fc4d47c614b03c9f5e541501d` had a successful GitHub Actions `validation` run #10 before merge.
- Local checksum-addressed metadata discovery is not an external signature or protection against an adversary able to replace and rename the complete artifact set.

## 0.3.0 - 2026-05-27

**Engineering milestone:** Phase 2B read-only historical kline acquisition and immutable raw-artifact evidence boundary.

- Added credential-free public Binance Futures kline GET acquisition with validated fixed-interval selectors, deterministic pagination, and bounded retry/rate-limit behavior.
- Added immutable local JSON artifact and checksummed metadata persistence with retained fetch diagnostics, checksum/readback verification, and stale/future-dated acquisition-evidence rejection.
- Retained `PAPER_ONLY` and `RESEARCH_ONLY`; no signal, backtest, execution, order, or LIVE trading path was added.

## 0.2.0 - 2026-05-25

**Engineering milestone:** Phase 2 validated historical kline ingestion boundary.

- Added fixed-interval Binance Futures historical kline normalization and integrity checks.
- Added provenance metadata and deterministic SHA-256 hashing of validated content and acquisition selectors.

## 0.1.0 - 2026-05-25

**Engineering milestone:** Phase 1 foundation initialized.

- Established a PAPER-only, RESEARCH_ONLY project foundation.
- Added validated configuration, deterministic runtime metadata, JSON logging, and validation tooling.
