# Version History

## 0.22.0 - 2026-06-14

**Engineering milestone:** Gate 5A-2 CI evidence adapter with Gate 5A-3 audit/runtime evidence adapter, Gate 5A-4 evidence ledger consistency audit, Gate 5A-5 risk-control enforcement evidence adapter, Gate 5A-6 data-freshness evidence adapter, and Gate 5A-7 workflow artifact evidence ledger.

- Added `src/reporting/ci_evidence.py` as a deterministic, offline CI evidence adapter for the Gate 5A `ci_validation` blocker row.
- Added `src/reporting/audit_runtime_evidence.py` as a deterministic Gate 5A-3 adapter for audit trail integrity and PAPER runtime reconciliation evidence.
- Added Gate 5A-4 evidence ledger consistency audit in `tests/test_evidence_ledger_consistency.py` and `docs/gates/gate5a_evidence_ledger.md`.
- Added Gate 5A-5 risk-control enforcement evidence adapter in `src/reporting/risk_control_evidence.py`.
- Added Gate 5A-6 data-freshness evidence adapter in `src/reporting/data_freshness_evidence.py`.
- Added focused Gate 5A-6 data-freshness evidence tests in `tests/test_data_freshness_evidence.py`.
- Added Gate 5A-6 documentation in `docs/gates/gate5a_data_freshness_evidence.md`.
- Added Gate 5A-7 workflow artifact evidence ledger in `docs/gates/gate5a_workflow_artifact_evidence_ledger.md`.
- Extended `tests/test_evidence_ledger_consistency.py` to keep Gate 5A-6 source/test/doc counterparts and Gate 5A-7 evidence wording guarded.
- Exported Gate 5A-5 risk-control evidence helpers and Gate 5A-6 data-freshness evidence helpers from `src.reporting`.
- Gate 5A-3 source/test/doc counterparts are recorded as `src/reporting/audit_runtime_evidence.py`, `tests/test_audit_runtime_evidence.py`, and `docs/gates/gate5a_audit_runtime_evidence.md`.
- Gate 5A-3 retains user-reported green validation evidence, while connector-visible CI remains UNAVAILABLE and is not connector-visible workflow evidence.
- Gate 5A-4 evidence ledger consistency audit preserves package-version, implementation-counterpart, unavailable-evidence, and safety-boundary wording across the current ledgers.
- Gate 4B-5 project-state ledger reconciliation and Gate 4B-5A VERSION ledger reconciliation remain recorded as current regression anchors for the version ledger.
- Gate 5A-4 green is recorded as user-reported green validation evidence for `e6b4f28285da0a488e40f84ff47395b89059ff11` after the Gate 4B-5 VERSION anchor repair.
- Gate 5A-5 green is recorded as user-reported green validation evidence for `07becd0c773cde6a50c40c5d9c4fe5da4c29ad49` after the Ruff import-block repair.
- Gate 5A-6 green is recorded as user-reported green validation evidence for `3f5cb4ea89fa3c12661e020d802796439d3a064c` after the Ruff and Black formatting repairs.
- Gate 5A-7 records that validation runs 309, 310, 311, 312, and 313 are green by user-provided screenshot evidence, while direct workflow artifacts remain unavailable through the connector.
- Package version remains `0.22.0` for Gate 5A-2 through Gate 5A-7.
- Retained the safety boundary: no runtime behavior, no strategy logic, no optimizer, no execution-cost modeling, no performance calculation, no PAPER runtime expansion, no readiness approval.

## Validation evidence

- `MEASURED`: connector comparison resolved `dev` HEAD `15fc057c0b9625936b2c0f7e9670a235d6c4f589` before Gate 5A-6.
- `MEASURED`: connector writes added Gate 5A-6 source, focused tests, documentation, export, and ledger updates on `dev`.
- `MEASURED`: connector fetched commit metadata for `3f5cb4ea89fa3c12661e020d802796439d3a064c`.
- `MEASURED`: Gate 5A-6 user-reported green validation evidence is recorded for `3f5cb4ea89fa3c12661e020d802796439d3a064c` after Ruff and Black formatting repairs.
- `MEASURED`: user-provided screenshot shows validation runs 309, 310, 311, 312, and 313 green on `dev`.
- `MEASURED`: Gate 5A-5 user-reported green validation evidence remains recorded for `07becd0c773cde6a50c40c5d9c4fe5da4c29ad49` after Ruff import-block repair.
- `MEASURED`: Gate 5A-4 user-reported green validation evidence remains recorded as measured user evidence.
- `UNAVAILABLE`: Gate 5A-7 connector-visible CI remains UNAVAILABLE and user-reported green validation evidence is not connector-visible workflow evidence.
- `UNAVAILABLE`: workflow artifacts and job logs for Gate 5A-6 are unavailable through the connector in this increment.
- `UNAVAILABLE`: direct mutable local clone evidence because repository operations were performed through the GitHub connector.
- `UNAVAILABLE`: exact branch-head full-repository local validation, Ruff, Black, and Mypy in this execution environment.
- `MODELED`: none.

## 0.21.1 - 2026-06-13

**Engineering milestone:** Gate 5A-1 operational evidence input integrity hardening.

- Hardened Gate 5A evidence item validation so duplicate blocker IDs, unsupported blocker IDs, empty blocker IDs, non-canonical blocker IDs, empty summaries, and empty sources fail closed.
- Preserved the Gate 5A deployment-blocker matrix behavior: only `MEASURED` evidence clears required PAPER operational diagnostic blocker rows.
- Added focused tests covering duplicate evidence, unsupported evidence, empty and non-canonical blocker IDs, empty summaries, and empty sources.
- Advanced package version to `0.21.1`.
- Retained the safety boundary: no runtime behavior, no strategy logic, no optimizer, no execution-cost modeling, no performance calculation, no PAPER runtime expansion, no readiness approval.

## Validation evidence

- `MEASURED`: connector comparison resolved `dev` HEAD `4d641dcb023e0c5e9303c7d0fba32b1d27f2d9e4` before this increment.
- `MEASURED`: `PROJECT_STATE.md`, `PLAN.md`, `REPORT.md`, `CHANGELOG.md`, and `VERSION.md` were read from `dev` before this increment.
- `UNAVAILABLE`: direct mutable local clone evidence because repository operations were performed through the GitHub connector.
- `UNAVAILABLE`: exact branch-head full-repository local validation, Ruff, Black, and Mypy in this execution environment.

## 0.21.0 - 2026-06-13

**Engineering milestone:** Gate 5A operational evidence gate and deployment-blocker matrix.

- Added `src/reporting/operational_evidence.py` as a deterministic PAPER-only operational evidence diagnostic boundary.
- Added Gate 5A evidence classifications `MEASURED`, `MODELED`, and `UNAVAILABLE` plus fail-closed blocker statuses `BLOCKED` and `CLEARED`.
- Added required blocker categories for audit trail integrity, CI validation, data freshness, execution-cost evidence, PAPER runtime reconciliation, and risk-control enforcement.
- Exported the Gate 5A reporting helpers from `src.reporting` and advanced package version to `0.21.0`.
- Retained the safety boundary: no runtime behavior, no strategy logic, no optimizer, no execution-cost modeling, no performance calculation, no PAPER runtime expansion, no readiness approval.

## Validation evidence

- `MEASURED`: connector comparison resolved `dev` HEAD `8fca2c83ea11fd1f1d6279c48b168305df55015e` before this increment.
- `MEASURED`: `PROJECT_STATE.md`, `PLAN.md`, `REPORT.md`, `CHANGELOG.md`, and `VERSION.md` were read from `dev` before this increment.
- `UNAVAILABLE`: exact final branch-head full-repository local validation, Ruff, Black, and Mypy in this execution environment.

## 0.20.0 - 2026-06-07

**Engineering milestone:** Gate 4B reporting-boundary and ledger-reconciliation bundle, including Gate 4B-5 project-state ledger reconciliation and Gate 4B-5A VERSION ledger reconciliation.

- Added `src/reporting/performance_boundary.py` as a reporting-only eligibility boundary over Gate 4A `BacktestRunMetadata`.
- Added Gate 4B through Gate 4CLOSE ledger reconciliation, completion evidence matrix, validation-command consistency, and public-export consistency guards.
- Gate 4B-5 project-state ledger reconciliation keeps `VERSION.md`, `CHANGELOG.md`, `REPORT.md`, and `PROJECT_STATE.md` aligned on the current documentation/test-only increment.
- Gate 4B-5A VERSION ledger reconciliation records the Gate 4B-5 anchor in this version ledger.
- Retained the Gate 4B-0 through Gate 4CLOSE-1C boundary: no runtime behavior, no strategy logic, no optimizer, no execution-cost modeling, no performance calculation, no PAPER runtime expansion, no exchange mutation, and no readiness approval.