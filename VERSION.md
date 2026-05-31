# Version History

## 0.9.0 - 2026-05-31

**Engineering milestone:** Gate 2F reconciliation report artifact persistence.

- Reconciled Gate 2E status after PR #7 merged into `dev` at merge commit `80545452e5caa9197f7ac42b9aa9cae30e1d9ae3`.
- Recorded PR #7 head `d05c6230be42c3301a43ca5cf9ec7bbbe8ac195e` GitHub Actions `validation` run #60 as successful remote evidence before Gate 2F began.
- Added local reconciliation report artifact persistence to `src/persistence/reconciliation.py`.
- Added JSON, Markdown, and metadata artifact write helpers with checksum-anchored filenames.
- Added readback verification for checksums, filename anchors, metadata schema, artifact type, mode, readiness, and status consistency.
- Added focused artifact tests for round-trip, idempotency, unavailable reports, tampered JSON, tampered Markdown, tampered metadata, and conflicting files.
- Retained the boundary: no strategy, backtest, runtime signal generation, execution model, risk allocation, PAPER runtime, performance analysis, persistence repair, or LIVE trading capability was added.

## Validation evidence

- `MEASURED`: PR #7 Gate 2E final head `d05c6230be42c3301a43ca5cf9ec7bbbe8ac195e` completed GitHub Actions `validation` run #60 successfully before Gate 2F began.
- `UNVERIFIED`: Gate 2F exact branch-head compilation, tests, Ruff, Black, and Mypy until the PR workflow runs.
- `UNAVAILABLE`: direct mutable local clone evidence in this execution environment because direct local git operations were unavailable.
- Gate 2F persists local report artifacts only. It does not provide external notarization, runtime evidence, or PAPER/LIVE approval.

## 0.8.0 - 2026-05-31

**Engineering milestone:** Gate 2E reconciliation report surface.

- Reconciled Gate 2D status after PR #6 merged into `dev` at merge commit `d05f013f0a38f8abe82bedc06a7e83adaecd67f4`.
- Recorded PR #6 head `68e6a89f788a2aa6fa5081e5116c8aa556478bd6` GitHub Actions `validation` run #56 as successful remote evidence before Gate 2E began.
- Added deterministic reconciliation reporting helpers to `src/persistence/reconciliation.py`.
- Added explicit report status values: `CONSISTENT`, `INCONSISTENT`, and `UNAVAILABLE`.
- Added deterministic JSON-compatible payloads, compact JSON serialization, and Markdown summaries for reconciliation reports.
- Added issue counts by reconciliation mismatch type and sorted issue details.
- Added focused reporting tests for consistent, inconsistent, unavailable, JSON, and Markdown report paths.
- Retained the boundary: no strategy, backtest, runtime signal generation, position management, execution model, risk allocation, PAPER runtime, performance analysis, persistence repair, or LIVE trading capability was added.

## Validation evidence

- `MEASURED`: PR #6 Gate 2D final head `68e6a89f788a2aa6fa5081e5116c8aa556478bd6` completed GitHub Actions `validation` run #56 successfully before Gate 2E began.
- Gate 2E reports local reconciliation evidence only. It does not repair files or database rows, provide runtime evidence, or approve PAPER/LIVE operation.

## 0.7.0 - 2026-05-31

**Engineering milestone:** Gate 2D persistence reconciliation scan.

- Added `src/persistence/reconciliation.py` to scan verified decision audit files and verified SQLite audit events for local evidence alignment.
- Added explicit mismatch states for missing database events, missing file audit records, and database event identity or payload mismatches.
- Added a fail-closed assertion helper that raises when local persistence evidence is not fully reconciled.
- Added focused reconciliation tests for consistent evidence and mismatch behavior.

## 0.6.0 - 2026-05-31

**Engineering milestone:** Gate 2C persistence integration review.

- Added `src/persistence/integration.py` to append a validated decision audit file record and a matching SQLite audit event in one narrow research-only helper.
- Added deterministic event identity and provenance payload for local persistence integration.

## 0.5.0 - 2026-05-30

**Engineering milestone:** Gate 2B database-backed audit-event persistence boundary.

- Added a local SQLite `audit_events` ledger for research-only persistence events in `src/persistence/events.py`.
- Added canonical JSON payload storage with SHA-256 readback verification.

## 0.4.0 - 2026-05-30

**Engineering milestone:** Gate 2A append-only research decision audit-trail boundary.

- Added research-only decision audit records for `REJECTED` and `NO_ACTION` outcomes.
- Added explicit evidence classification for `MEASURED`, `MODELED`, and `UNAVAILABLE` decision inputs.

## 0.3.1 - 2026-05-29

**Engineering milestone:** Phase 2B.1 acquisition-integrity repair and validation evidence hardening.

- Repaired bounded retry handling and restart readback evidence.
- Hardened GitHub Actions validation with Python 3.11/3.12 compile-and-test coverage.

## 0.3.0 - 2026-05-27

**Engineering milestone:** Phase 2B read-only historical kline acquisition and immutable raw-artifact evidence boundary.

- Added credential-free public Binance Futures kline GET acquisition with validated fixed-interval selectors, deterministic pagination, and bounded retry/rate-limit behavior.

## 0.2.0 - 2026-05-25

**Engineering milestone:** Phase 2 validated historical kline ingestion boundary.

- Added fixed-interval Binance Futures historical kline normalization and integrity checks.

## 0.1.0 - 2026-05-25

**Engineering milestone:** Phase 1 foundation initialized.

- Established a PAPER-only, RESEARCH_ONLY project foundation.
- Added validated configuration, deterministic runtime metadata, JSON logging, and validation tooling.
