# Version History

## 0.15.0 - 2026-06-02

**Engineering milestone:** Increment 4D paper runtime DB audit pack.

- Started from green Increment 4C `dev` head `743dbfa7fafb47c22630908275e67a235c22aa0a` after validation #80 passed by user screenshot/report.
- Added `src/reporting/paper_db_audit.py` with a read-only SQLite paper runtime database integrity audit pack.
- Added deterministic `PaperDbAuditReport` and `PaperDbAuditIssue` payloads plus JSON and Markdown renderers.
- Added diagnostics for empty DBs, missing schema, orphan lifecycle events, decisions without lifecycle entries, lifecycle entries without decisions, duplicate event IDs, duplicate conflicting decision IDs, missing checksums, checksum mismatches, missing symbol/side/reason fields, UNKNOWN rejection reasons, corrupted JSON payloads, audit events without decisions, lifecycle ordering issues, and inconsistent accepted/rejected transitions.
- Added optional local audit artifact checksum/link diagnostics without repair or rewrite behavior.
- Added focused tests covering clean DB, empty DB, missing schema, orphan lifecycle event, missing decision event, duplicate event ID, duplicate conflicting decision ID, checksum mismatch, unknown reject reason, corrupted JSON payload, and report output stability.
- Retained the boundary: no DB repair, row deletion, historical rewrite, synthetic field invention, strategy logic, PAPER runtime behavior, readiness certification, or live order path was added.

## Validation evidence

- `MEASURED`: local isolated Increment 4D focused tests passed with `11 passed in 0.28s`.
- `MEASURED`: local isolated Increment 4D Ruff check passed with `All checks passed!`.
- `MEASURED`: local isolated Increment 4D Black check passed with `2 files would be left unchanged`.
- `UNAVAILABLE`: Mypy module was not installed in this execution environment.
- `UNVERIFIED`: remote CI for this commit until GitHub Actions reports.

## 0.14.0 - 2026-06-02

**Engineering milestone:** Increment 4C execution context population.

- Started from green Increment 4B `dev` head `74c1ebb73ecae2ef9a7cff5afcb585e945b34a57` after the Ruff repair commit passed CI by user report.
- Added `src/execution/context.py` with explicit execution context snapshot records.
- Added required execution context fields for decision ID, outcome, symbol, side, timestamp, price source, entry reference, stop reference, take-profit reference, market-input state, and execution-cost assumptions.
- Added explicit spread, fee, slippage, latency, and funding assumption snapshots.
- Missing execution-cost assumptions remain `UNAVAILABLE` and cannot carry zero values.
- Missing timestamp, missing critical price references, unavailable market input, and stale market input fail closed as `INVALID`.
- Added deterministic JSON serialization and decision-audit evidence projection from the same snapshot.
- Added focused tests covering fully populated context, missing spread, missing fee, missing slippage, missing latency/funding, missing timestamp, stale market input, unavailable market input, rejected-decision diagnostics, missing price references, unavailable zero-value rejection, and audit evidence round-trip.
- Retained the boundary: no fill simulation, execution-quality assumptions, strategy logic, backtest replay, risk allocation, PAPER runtime, readiness certification, or live order path was added.

## Validation evidence

- `MEASURED`: local isolated Increment 4C focused tests passed with `15 passed in 0.30s`.
- `MEASURED`: local isolated Increment 4C compile check passed with exit code `0`.
- `MEASURED`: local isolated Increment 4C Ruff check passed with `All checks passed!`.
- `UNAVAILABLE`: Black and Mypy executables were not available in this execution environment.
- `UNAVAILABLE`: exact branch-head full repository tests before commit because direct mutable checkout/network clone is unavailable here.
- `UNVERIFIED`: remote CI for this commit until GitHub Actions reports.

## 0.13.0 - 2026-06-02

**Engineering milestone:** Increment 4B canonical effective RR finalization.

- Reconciled Gate 4A status after PR #11 merged into `dev` at merge commit `25ebe9e9f0a51baa05c9af9f36ad4792bbccde84`.
- Recorded PR #11 head `605159418e9a7551754812675358728449f5743f` GitHub Actions `validation` run #73 as successful remote evidence before 4B began.
- Added `src/execution/effective_rr.py` with a single canonical effective RR calculation path.
- Preserved raw expected RR separately from canonical `effective_rr`.
- Added explicit `VALID`, `INVALID`, and `UNAVAILABLE` RR states.
- Added fail-closed validation for missing entry, stop, and take-profit references, non-finite values, zero or negative distances, invalid raw expected RR, and raw/canonical mismatch.
- Added audit-evidence and report-row projection helpers that derive from the canonical result only.
- Added focused tests covering valid LONG, valid SHORT, invalid stop/reward distance, non-finite prices, missing references, raw RR mismatch, raw source validation, and persistence/reporting consistency.
- Retained the boundary: no optimizer, strategy logic, risk allocation, backtest replay, fill simulation, PAPER runtime, readiness certification, or live order path was added.

## 0.12.0 - 2026-06-02

**Engineering milestone:** Gate 4A conservative backtest foundation skeleton.

- Added immutable backtest run metadata and execution evidence records.
- Added fail-closed validation so performance results cannot be produced while any required execution evidence is unavailable.

## 0.11.0 - 2026-06-01

**Engineering milestone:** Gate 3 market tick data-quality guard.

- Added pre-runtime stale tick validation and first-valid tick selection.

## 0.10.0 - 2026-06-01

**Engineering milestone:** Gate 2G persistence/audit phase closure review.

- Added deterministic persistence/audit phase closure reporting.

## 0.9.0 - 2026-05-31

**Engineering milestone:** Gate 2F reconciliation report artifact persistence.

## 0.8.0 - 2026-05-31

**Engineering milestone:** Gate 2E reconciliation report surface.

## 0.7.0 - 2026-05-31

**Engineering milestone:** Gate 2D persistence reconciliation scan.

## 0.6.0 - 2026-05-31

**Engineering milestone:** Gate 2C persistence integration review.

## 0.5.0 - 2026-05-30

**Engineering milestone:** Gate 2B database-backed audit-event persistence boundary.

## 0.4.0 - 2026-05-30

**Engineering milestone:** Gate 2A append-only research decision audit-trail boundary.

## 0.3.1 - 2026-05-29

**Engineering milestone:** Phase 2B.1 acquisition-integrity repair and validation evidence hardening.

## 0.3.0 - 2026-05-27

**Engineering milestone:** Phase 2B read-only historical kline acquisition and immutable raw-artifact evidence boundary.

## 0.2.0 - 2026-05-25

**Engineering milestone:** Phase 2 validated historical kline ingestion boundary.

## 0.1.0 - 2026-05-25

**Engineering milestone:** Phase 1 foundation initialized.
