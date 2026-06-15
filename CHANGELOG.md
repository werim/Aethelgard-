# Changelog

## [0.22.0] - 2026-06-14

### Added

- Added Gate 5A-2 CI evidence adapter in `src/reporting/ci_evidence.py`.
- Added focused CI evidence coverage in `tests/test_ci_evidence.py`.
- Added Gate 5A-2 documentation in `docs/gates/gate5a_ci_evidence.md`.
- Added Gate 5A-3 audit/runtime evidence adapter in `src/reporting/audit_runtime_evidence.py`.
- Added focused audit/runtime evidence coverage in `tests/test_audit_runtime_evidence.py`.
- Added Gate 5A-3 documentation in `docs/gates/gate5a_audit_runtime_evidence.md`.
- Added Gate 5A-4 evidence ledger consistency audit in `tests/test_evidence_ledger_consistency.py`.
- Added Gate 5A-4 documentation in `docs/gates/gate5a_evidence_ledger.md`.

### Changed

- Package version advanced to `0.22.0` for Gate 5A-2 and kept stable for Gate 5A-3 and Gate 5A-4.
- CI validation can now be represented as a fail-closed Gate 5A `ci_validation` evidence item from caller-supplied workflow, job, and artifact evidence.
- Gate 5A-3 audit/runtime reconciliation evidence can now be represented as fail-closed Gate 5A evidence items from caller-supplied persistence reconciliation reports.
- Gate 5A-4 keeps user-reported green validation evidence separate from connector-visible CI evidence.

### Evidence ledger

- Gate 5A-3 source/test/doc counterparts are recorded as `src/reporting/audit_runtime_evidence.py`, `tests/test_audit_runtime_evidence.py`, and `docs/gates/gate5a_audit_runtime_evidence.md`.
- Gate 5A-3 has user-reported green validation evidence, while connector-visible CI remains UNAVAILABLE and is not connector-visible workflow evidence.
- Gate 5A-4 evidence ledger consistency audit preserves the evidence wording across `PROJECT_STATE.md`, `REPORT.md`, `VERSION.md`, `CHANGELOG.md`, and `docs/gates/gate5a_evidence_ledger.md`.

### Known limitations

- Gate 5A-2 does not call GitHub or fetch workflow artifacts automatically.
- Missing, malformed, duplicated, failed, or incomplete CI evidence remains `UNAVAILABLE`.
- Gate 5A-3 does not read local databases or run a PAPER runtime; it only classifies caller-supplied reconciliation reports.
- Gate 5A-4 does not run local validation or prove connector-visible CI.
- Local full-repository validation remains unavailable in this execution environment until CI or a mutable clone reports it.
- The Gate 5A-2 through Gate 5A-4 boundary does not compute performance, model costs, add optimizer behavior, add strategy logic, add PAPER runtime behavior, mutate exchange state, approve readiness, or enable live trading.

## [0.21.1] - 2026-06-13

### Fixed

- Hardened Gate 5A operational evidence input validation.
- Duplicate blocker evidence now fails closed instead of silently overwriting earlier evidence.
- Unsupported blocker IDs now fail closed instead of being ignored.
- Empty blocker IDs, non-canonical blocker IDs, empty summaries, and empty sources now fail closed.

### Changed

- Package version advanced to `0.21.1`.
- Gate 5A documentation now records the Gate 5A-1 input integrity boundary.

### Known limitations

- Gate 5A-1 does not collect CI, runtime, risk, audit, or execution-cost evidence automatically.
- Gate 5A-1 does not compute performance, model costs, add optimizer behavior, add strategy logic, add PAPER runtime behavior, mutate exchange state, approve readiness, or enable live trading.
- Local full-repository validation remains unavailable in this execution environment; only reconstructed focused Gate 5A tests were run locally.

## [0.21.0] - 2026-06-13

### Added

- Gate 5A operational evidence gate and deployment-blocker matrix in `src/reporting/operational_evidence.py`.
- Focused Gate 5A regression coverage in `tests/test_operational_evidence_gate.py`.
- Gate 5A documentation in `docs/gates/gate5a_operational_evidence_gate.md`.
- Public reporting exports for Gate 5A diagnostic helpers.

### Changed

- Package version advanced to `0.21.0`.
- `src.reporting.__all__` now exposes the Gate 5A operational evidence diagnostic boundary.

### Fixed

- PAPER deployment diagnostics now fail closed when operational evidence for audit trail integrity, CI validation, data freshness, execution-cost evidence, PAPER runtime reconciliation, or risk-control enforcement is missing, modeled, or unavailable.

### Known limitations

- Gate 5A does not compute performance, model costs, add optimizer behavior, add strategy logic, add PAPER runtime behavior, mutate exchange state, approve readiness, or enable live trading.
- Local full-repository validation remains unavailable in this execution environment; only reconstructed focused Gate 5A tests were run locally.
- Connector writes were performed as separate commits because the available GitHub contents API actions write one file per commit in this environment.

## [0.20.0] - 2026-06-07

### Added

- Gate 4B-0 metric-publication eligibility boundary in `src/reporting/performance_boundary.py`.
- Gate 4B replay hardening coverage for metric-like and execution-like field leakage.
- Gate 4B-1 guarded report-publication helpers over an existing Gate 4B-0 eligibility result.
- Gate 4B-2 reporting-boundary completeness and forged-eligibility regression coverage.
- Gate 4B-3 reporting export-boundary evidence reconciliation for `src.reporting.__all__`.
- Version-ledger consistency tests for `src.__version__`, `pyproject.toml`, `VERSION.md`, and `CHANGELOG.md`.
- Public package export-boundary consistency tests for `src.backtest`, `src.data`, `src.execution`, and `src.reporting`.
- Gate 4B-5 project-state ledger reconciliation and focused stale-claim regression coverage.
- Gate 4B-5A VERSION ledger reconciliation coverage so Gate 4B-5 is recorded across `VERSION.md`, `CHANGELOG.md`, `REPORT.md`, and `PROJECT_STATE.md`.
- Gate 4CLOSE-1 completion evidence matrix in `docs/gates/gate4_completion_evidence_matrix.md`.
- Gate 4CLOSE-1A focused matrix wording reconciliation and regression coverage in `tests/test_gate4_completion_evidence_matrix.py`.
- Gate 4CLOSE-1B validation-command ledger consistency regression coverage in `tests/test_validation_command_ledger_consistency.py`.
- Gate 4CLOSE-1C validation-command canonicalization coverage across `REPORT.md`, `PROJECT_STATE.md`, and the Gate 4 completion matrix.

### Changed

- Package version advanced to `0.20.0`.
- `src/reporting/__init__.py` exports Gate 4B-0 and Gate 4B-1 reporting helpers.
- Gate 4B-2 records a reporting-boundary completeness audit of report, Markdown, JSON, payload, and serialization paths.
- Gate 4B-3 records user-reported green validation for the reporting export-boundary test.
- Version-ledger evidence reconciliation records user-reported green validation for the version consistency test.
- Public export-boundary evidence reconciliation records user-reported green validation for the package export consistency test after Ruff import-block repair.
- The guarded publication helper now requires eligibility produced by the Gate 4B evaluator before caller payload publication.
- `PROJECT_STATE.md` now reflects the current `dev` ledger state instead of the stale Gate 0 planning state.
- `VERSION.md` now records Gate 4B-5 as part of the current 0.20.0 ledger bundle.
- Gate 4CLOSE-1A narrows the completion evidence matrix so public-export evidence is limited to checked live/order/runtime names on public package surfaces.
- `REPORT.md` and `PROJECT_STATE.md` now share a guarded validation command surface for Gate 4CLOSE-1B.
- Gate 4CLOSE-1C canonicalizes the validation command surface across `REPORT.md`, `PROJECT_STATE.md`, and the Gate 4 completion matrix.

### Fixed

- Guarded reporting publication refuses malformed eligibility objects.

### Known limitations

- Retained the Gate 4B-0 through Gate 4CLOSE-1C boundary: no runtime behavior, no strategy logic, no optimizer, no execution-cost modeling, no performance calculation, no PAPER runtime expansion, no exchange mutation, and no readiness approval.
