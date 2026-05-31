# Version History

## 0.7.0 - 2026-05-31

**Engineering milestone:** Gate 2D persistence reconciliation scan.

- Reconciled Gate 2C status after PR #5 merged into `dev` at merge commit `f085b1412d8670058b2e45a02b4590aa40145069`.
- Recorded PR #5 head `16dfe24c624742729fbab2303b8defbd7eb3a780` GitHub Actions `validation` run #51 as successful remote evidence before Gate 2D began.
- Added `src/persistence/reconciliation.py` to scan verified decision audit files and verified SQLite audit events for local evidence alignment.
- Added explicit mismatch states for missing database events, missing file audit records, and database event identity or payload mismatches.
- Added a fail-closed assertion helper that raises when local persistence evidence is not fully reconciled.
- Exposed deterministic decision-audit event identity and payload helpers from `src/persistence/integration.py` so reconciliation uses the same canonical event contract as append.
- Added focused reconciliation tests for consistent evidence, missing database events, missing file audits, database-event mismatch, and fail-closed assertion behavior.
- Retained the boundary: no strategy, backtest, runtime signal generation, order path, execution model, risk allocation, PAPER runtime, performance analysis, persistence repair, or LIVE trading capability was added.

## Validation evidence

- `MEASURED`: PR #5 Gate 2C final head `16dfe24c624742729fbab2303b8defbd7eb3a780` completed GitHub Actions `validation` run #51 successfully before Gate 2D began.
- `UNVERIFIED`: Gate 2D exact branch-head compilation, tests, Ruff, Black, and Mypy until the PR workflow runs.
- `UNAVAILABLE`: direct mutable local clone evidence in this execution environment because direct local git operations were unavailable.
- Gate 2D reports local mismatch states only. It does not repair files or database rows, provide cross-store transaction semantics, certify runtime evidence, or approve PAPER/LIVE operation.

## 0.6.0 - 2026-05-31

**Engineering milestone:** Gate 2C persistence integration review.

- Reconciled Gate 2B status after PR #4 merged into `dev` at merge commit `e37268fe21f5fa46c6e804f059df6a05c38f999f`.
- Recorded PR #4 head `8746bac98aaa08691c4a26b97f084b5bb9cd6359` GitHub Actions `validation` run #48 as successful remote evidence before Gate 2C began.
- Added `src/persistence/integration.py` to append a validated decision audit file record and a matching SQLite audit event in one narrow research-only helper.
- Added deterministic event identity derived from decision identity and decision audit checksum.
- Added event payload provenance linking decision audit checksum, audit filename, claim filename, dataset checksum, artifact checksum, outcome, reason codes, and evidence classifications.
- Added preflight conflict detection so an existing database event for the same decision/type but different expected identity fails closed before appending another audit file record.
- Added focused integration tests for matched file/database persistence, idempotency, non-PAPER rejection, and preflight conflict behavior.
- Retained the boundary: no strategy, backtest, runtime signal generation, order path, execution model, risk allocation, PAPER runtime, performance analysis, or LIVE trading capability was added.

## Validation evidence

- `MEASURED`: PR #4 Gate 2B final head `8746bac98aaa08691c4a26b97f084b5bb9cd6359` completed GitHub Actions `validation` run #48 successfully before Gate 2C began.
- `UNVERIFIED`: Gate 2C exact branch-head compilation, tests, Ruff, Black, and Mypy until the PR workflow runs.
- `UNAVAILABLE`: direct mutable local clone evidence in this execution environment because direct local git operations were unavailable.
- Gate 2C links two local persistence evidence boundaries only. It is not a cross-store transaction manager, external notarization layer, runtime event bus, strategy runtime, execution ledger, or readiness certificate.

## 0.5.0 - 2026-05-30

**Engineering milestone:** Gate 2B database-backed audit-event persistence boundary.

- Reconciled Gate 2A status after PR #3 merged into `dev` at merge commit `5ce82c134656e206ce90c2b93585bb80222ebf71`.
- Recorded PR #3 head `ed1641191d7d495ddab325e0ef54877fe64cf8d2` GitHub Actions `validation` run #28 as successful remote evidence before Gate 2B began.
- Added a local SQLite `audit_events` ledger for research-only persistence events in `src/persistence/events.py`.
- Added immutable audit-event identity, idempotent identical append behavior, and fail-closed conflict detection for changed event identities or repeated decision/type pairs.
- Added canonical JSON payload storage with SHA-256 readback verification so database payload tampering is detected.
- Added UTC timestamp, `PAPER_ONLY`, `RESEARCH_ONLY`, schema-version, and deterministic JSON payload validation.
- Added focused database event tests for schema initialization, readback, idempotency, conflict rejection, checksum tampering, UTC/mode safety, and JSON determinism.
- Retained the boundary: no strategy, backtest, runtime signal generation, order path, execution model, risk allocation, PAPER runtime, performance analysis, or LIVE trading capability was added.

## Validation evidence

- `MEASURED`: PR #3 Gate 2A final head `ed1641191d7d495ddab325e0ef54877fe64cf8d2` completed GitHub Actions `validation` run #28 successfully before Gate 2B began.
- `UNVERIFIED`: Gate 2B exact branch-head compilation, tests, Ruff, Black, and Mypy until the PR workflow runs.
- `UNAVAILABLE`: direct mutable local clone evidence in this execution environment because direct local git operations were unavailable.
- SQLite audit events provide local database-row checksum verification only. They are not an external notarization layer, multi-writer distributed log, strategy runtime, execution ledger, or readiness certificate.

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
- `MEASURED`: PR #3 follow-up head `1a8237635db1c9ee0c3d48db8e6f63aaeffbf939` reached Black on Python 3.11 after Ruff passed, then failed because `src/persistence/audit.py` required formatting.
- `MEASURED`: PR #3 follow-up head `433dbe6bd8276764e540b6b39c28fa6450d82035` reached Black on Python 3.11 and again failed because `src/persistence/audit.py` still required exact Black line collapsing.
- `CHANGED`: follow-up head `efc128f8dfb98ccf189b0c896537185a78a44f36` chained the `AuditIntegrityError` from the caught `FileExistsError`; functional audit behavior was unchanged.
- `CHANGED`: follow-up head `e2ef8ee76995d3261a37a3da23bc0bd47d0ed140` applied partial Black formatting to `src/persistence/audit.py`; functional audit behavior was unchanged.
- `CHANGED`: follow-up head `818d17bfc255a52b9ed32392d2a48c257640a545` applied the exact local Black 24.10.0 diff to `src/persistence/audit.py`; functional audit behavior was unchanged.
- `MEASURED`: PR #3 final head `ed1641191d7d495ddab325e0ef54877fe64cf8d2` completed GitHub Actions `validation` run #28 successfully before merge.
- `UNAVAILABLE`: direct mutable local clone evidence in this execution environment because direct local git operations were unavailable.
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
