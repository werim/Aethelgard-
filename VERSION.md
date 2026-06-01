# Version History

## 0.11.0 - 2026-06-01

**Engineering milestone:** Gate 3 market tick data-quality guard.

- Started from `dev` merge commit `a5822ea66bfdbd403f18b7bd32599439a7580ce2` after Gate 2G merged.
- Added `src/data/stale_tick_guard.py`.
- Added auditable market tick, guard configuration, decision, and bounded tick buffer models.
- Added fail-closed checks for symbol validity, price bounds, local receive age, exchange timestamp skew, warmup drift, peer confirmation, peer-median drift, and duplicate sequence IDs.
- Added `select_first_valid_tick(...)` so research callers can skip rejected ticks and consume the first validated tick.
- Added focused tests for pass behavior, rejection paths, duplicate protection, first-valid selection, and unsafe configuration.
- Scope remains data quality only. This increment does not add strategy logic, backtesting, execution modeling, risk allocation, runtime loops, readiness certification, or performance claims.

## Validation evidence

- `MEASURED`: isolated stale tick guard tests passed with `14 passed in 0.13s`.
- `MEASURED`: isolated compile check returned exit code `0`.
- `UNVERIFIED`: exact branch-head full repository tests and static checks until the pull-request workflow runs.
- `UNAVAILABLE`: direct mutable local clone evidence in this execution environment.

## 0.10.0 - 2026-06-01

**Engineering milestone:** Gate 2G persistence/audit phase closure review.

- Added deterministic persistence/audit phase closure reporting in `src/reporting/phase_closure.py`.
- Recorded completed Gates 2A through 2F with evidence limits.
- Kept runtime, strategy, backtesting, execution modeling, and performance claims outside the implemented boundary.

## 0.9.0 - 2026-05-31

**Engineering milestone:** Gate 2F reconciliation report artifact persistence.

- Added local reconciliation report artifact persistence to `src/persistence/reconciliation.py`.
- Added JSON, Markdown, and metadata artifact write helpers with checksum readback checks.

## 0.8.0 - 2026-05-31

**Engineering milestone:** Gate 2E reconciliation report surface.

- Added deterministic reconciliation report payloads, JSON serialization, and Markdown summaries.

## 0.7.0 - 2026-05-31

**Engineering milestone:** Gate 2D persistence reconciliation scan.

- Added local file/database reconciliation checks and mismatch states.

## 0.6.0 - 2026-05-31

**Engineering milestone:** Gate 2C persistence integration review.

- Added controlled file audit to database event append helpers.

## 0.5.0 - 2026-05-30

**Engineering milestone:** Gate 2B database-backed audit-event persistence boundary.

- Added a local SQLite audit-event ledger and payload checksum validation.

## 0.4.0 - 2026-05-30

**Engineering milestone:** Gate 2A append-only research decision audit-trail boundary.

- Added local decision audit records and explicit evidence classification.

## 0.3.1 - 2026-05-29

**Engineering milestone:** Phase 2B.1 acquisition-integrity repair and validation evidence hardening.

- Repaired acquisition retry and restart readback evidence handling.

## 0.3.0 - 2026-05-27

**Engineering milestone:** Phase 2B read-only historical kline acquisition and immutable raw-artifact evidence boundary.

- Added public kline acquisition and immutable raw-artifact evidence handling.

## 0.2.0 - 2026-05-25

**Engineering milestone:** Phase 2 validated historical kline ingestion boundary.

- Added fixed-interval historical kline normalization and integrity checks.

## 0.1.0 - 2026-05-25

**Engineering milestone:** Phase 1 foundation initialized.

- Established the research foundation, validation tooling, deterministic metadata, and JSON logging.
