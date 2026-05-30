# Version History

## 0.4.0 - 2026-05-30

**Engineering milestone:** Gate 2A append-only research decision audit-trail boundary.

- Added research-only decision audit records for `REJECTED` and `NO_ACTION` outcomes.
- Added explicit evidence classification for `MEASURED`, `MODELED`, and `UNAVAILABLE` decision inputs so missing execution-cost evidence cannot be represented as zero.
- Added checksum-addressed audit filenames and durable `decision_id.claim` anchors to reject conflicting immutable records for the same decision identity.
- Added fail-closed readback for altered audit bytes, missing or orphaned claims, non-UTC timestamps, unsafe operating mode, and incomplete evidence provenance.
- Advanced project phase metadata to `PERSISTENCE_AUDIT` while retaining `PAPER_ONLY` and `RESEARCH_ONLY` controls.
- Retained the boundary: no strategy, backtest, runtime signal generation, order path, execution model, database event log, or LIVE trading capability was added.

## Validation evidence

- `MEASURED` before branch publication in a reconstructed targeted workspace: `python -m compileall -q src tests` passed and `python -m pytest -q tests/test_audit.py` passed for the initial audit tests (`7 passed`).
- `MEASURED`: Gate 1.1 corrected PR head `e8caecc2aa545ea0bacdab79f28220ba21c14343` completed GitHub Actions `validation` run #14 successfully before Gate 2A began.
- `MEASURED`: PR #3 initial head `a3621feb5f68c2eee8b1273321fe5aa2cfdbc6b2` reached Ruff on Python 3.11 after earlier validation steps, then failed with `B904` in `src/persistence/audit.py` because the audit-claim conflict raise lacked exception chaining.
- `CHANGED`: follow-up head `efc128f8dfb98ccf189b0c896537185a78a44f36` chains the `AuditIntegrityError` from the caught `FileExistsError`; functional audit behavior is unchanged.
- `UNVERIFIED`: exact Gate 2A follow-up head GitHub Actions evidence until the workflow reruns.
- `UNAVAILABLE`: direct mutable local clone evidence in this execution environment because `git clone` failed with DNS resolution for `github.com`.
- Local JSON audit records plus claim files provide local stored-byte and identity consistency only. They are not a database transaction log, external notarization, or protection against an attacker able to replace the complete local evidence set.

## 0.3.1 - 2026-05-29

**Engineering milestone:** Phase 2B.1 acquisition-integrity repair and validation evidence hardening.

- Repaired bounded retry handling so transient public-transport failures before an HTTP response are retried within policy and recorded in diagnostics.
- Repaired restart readback evidence by encoding metadata SHA-256 identity in the immutable metadata filename and adding checksum-aware artifact discovery.
- Added fail-closed tests for transient transport retry/exhaustion, restart discovery, tampered or missing metadata checksum anchors, retry diagnostics, and GET-only public transport behavior.
- Hardened GitHub Actions validation with Python 3.11/3.12 compile-and-test coverage plus JUnit artifacts; Ruff, Black, and Mypy remain Python 3.11 gates.
- Retained `PAPER_ONLY` and `RESEARCH_ONLY`; no backtest, strategy, risk, execution, order, or LIVE trading path was added.

## Validation evidence

- `MEASURED` before PR creation in a reconstructed targeted workspace: `python -m compileall -q src tests` passed and `python -m pytest -q tests/test_acquisition.py` passed (`17 passed`).
- GitHub Actions `validation` run #12 on initial PR #2 head `90160d31036e5d95ef3bd188404835484c7f9441`: Python 3.12 compilation, tests, and JUnit upload passed; Python 3.11 compilation, tests, JUnit upload, and Ruff passed, then Black failed on formatting in `tests/test_acquisition.py`; Mypy was skipped.
- GitHub Actions `validation` run #13 on formatting follow-up head `14200bfcf32d037735c9dc1ac08c6b3eff380de3`: Python 3.12 compilation, tests, and JUnit upload passed; Python 3.11 compilation, tests, JUnit upload, Ruff, and Black passed, then Mypy failed in the new transport-boundary test's `Request` type reference.
- GitHub Actions `validation` run #14 on corrected PR #2 head `e8caecc2aa545ea0bacdab79f28220ba21c14343`: completed successfully.
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
