# Version History

## 0.22.0 - 2026-06-14

**Engineering milestone:** Gate 5A-2 CI evidence adapter with Gate 5A-3 audit/runtime evidence adapter and Gate 5A-4 evidence ledger consistency audit.

- Added `src/reporting/ci_evidence.py` as a deterministic, offline CI evidence adapter for the Gate 5A `ci_validation` blocker row.
- Added CI evidence payload models for workflow conclusion, required jobs, required artifacts, commit SHA, and source evidence.
- Added fail-closed classification: only complete successful CI payloads become `MEASURED`; missing, malformed, duplicated, failed, or incomplete evidence remains `UNAVAILABLE`.
- Added `tests/test_ci_evidence.py` covering measured CI evidence, failed jobs, missing artifacts, malformed required payloads, Gate 5A integration, and deterministic JSON without performance metrics.
- Added `docs/gates/gate5a_ci_evidence.md`.
- Added `src/reporting/audit_runtime_evidence.py` as a deterministic Gate 5A-3 adapter for audit trail integrity and PAPER runtime reconciliation evidence.
- Added `tests/test_audit_runtime_evidence.py` for measured reconciliation, missing report, reconciliation issues, empty matched decisions, missing source, Gate 5A integration, and deterministic JSON safety.
- Added `docs/gates/gate5a_audit_runtime_evidence.md`.
- Added Gate 5A-4 evidence ledger consistency audit in `tests/test_evidence_ledger_consistency.py` and `docs/gates/gate5a_evidence_ledger.md`.
- Gate 5A-3 source/test/doc counterparts are recorded as `src/reporting/audit_runtime_evidence.py`, `tests/test_audit_runtime_evidence.py`, and `docs/gates/gate5a_audit_runtime_evidence.md`.
- Gate 5A-3 retains user-reported green validation evidence, while connector-visible CI remains UNAVAILABLE and is not connector-visible workflow evidence.
- Gate 5A-4 evidence ledger consistency audit preserves package-version, implementation-counterpart, unavailable-evidence, and safety-boundary wording across `PROJECT_STATE.md`, `REPORT.md`, `VERSION.md`, `CHANGELOG.md`, and `docs/gates/gate5a_evidence_ledger.md`.
- Advanced package version to `0.22.0` for Gate 5A-2 and kept it stable for Gate 5A-3 and Gate 5A-4.
- Retained the safety boundary: no runtime behavior, no strategy logic, no optimizer, no execution-cost modeling, no performance calculation, no PAPER runtime expansion, no exchange mutation, no LIVE readiness, and no production-readiness approval.

## Validation evidence

- `MEASURED`: connector comparison resolved `dev` HEAD `c8b5b1852f297863940f45b7e927a35bf983cd88` before Gate 5A-4.
- `MEASURED`: `PROJECT_STATE.md`, `REPORT.md`, `VERSION.md`, `CHANGELOG.md`, Gate 5A-3 documentation, and package metadata were read from `dev` before this increment.
- `MEASURED`: connector writes added Gate 5A-4 focused test, documentation, and ledger updates on `dev`.
- `MEASURED`: Gate 5A-3 user-reported green validation evidence remains recorded as measured user evidence.
- `UNAVAILABLE`: connector-visible CI remains UNAVAILABLE and user-reported green validation evidence is not connector-visible workflow evidence.
- `UNAVAILABLE`: direct mutable local clone evidence because repository operations were performed through the GitHub connector.
- `UNAVAILABLE`: exact branch-head full-repository local validation, Ruff, Black, and Mypy in this execution environment.
- `MODELED`: none.

## 0.21.1 - 2026-06-13

**Engineering milestone:** Gate 5A-1 operational evidence input integrity hardening.

- Hardened Gate 5A evidence item validation so duplicate blocker IDs, unsupported blocker IDs, empty blocker IDs, non-canonical blocker IDs, empty summaries, and empty sources fail closed.
- Preserved the Gate 5A deployment-blocker matrix behavior: only `MEASURED` evidence clears required PAPER operational diagnostic blocker rows.
- Added focused tests covering duplicate evidence, unsupported evidence, empty and non-canonical blocker IDs, empty summaries, and empty sources.
- Advanced package version to `0.21.1`.
- Retained the safety boundary: no runtime behavior, no strategy logic, no optimizer, no execution-cost modeling, no performance calculation, no PAPER runtime expansion, no exchange mutation, no LIVE readiness, and no production-readiness approval.

## Validation evidence

- `MEASURED`: connector comparison resolved `dev` HEAD `4d641dcb023e0c5e9303c7d0fba32b1d27f2d9e4` before this increment.
- `MEASURED`: `PROJECT_STATE.md`, `PLAN.md`, `REPORT.md`, `CHANGELOG.md`, and `VERSION.md` were read from `dev` before this increment.
- `MEASURED`: reconstructed focused Gate 5A-1 validation passed `PYTHONPATH=. python -m compileall -q src tests` and `PYTHONPATH=. pytest -q tests/test_operational_evidence_gate.py` with `10 passed` in the scratch workspace.
- `UNAVAILABLE`: direct mutable local clone evidence because repository operations were performed through the GitHub connector.
- `UNAVAILABLE`: exact branch-head full-repository local validation, Ruff, Black, and Mypy in this execution environment.
- `UNVERIFIED`: exact final branch-head remote CI until GitHub Actions reports.

## 0.21.0 - 2026-06-13

**Engineering milestone:** Gate 5A operational evidence gate and deployment-blocker matrix.

- Added `src/reporting/operational_evidence.py` as a deterministic PAPER-only operational evidence diagnostic boundary.
- Added Gate 5A evidence classifications `MEASURED`, `MODELED`, and `UNAVAILABLE` plus fail-closed blocker statuses `BLOCKED` and `CLEARED`.
- Added required blocker categories for audit trail integrity, CI validation, data freshness, execution-cost evidence, PAPER runtime reconciliation, and risk-control enforcement.
- Added `evaluate_operational_evidence_gate(...)`, `assert_operational_deployment_not_blocked(...)`, deterministic JSON serialization, and Markdown matrix rendering.
- Added focused tests proving missing evidence blocks, modeled cost evidence blocks, all-measured evidence clears the diagnostic matrix, JSON remains deterministic, and safety text remains visible.
- Exported the Gate 5A reporting helpers from `src.reporting` and advanced package version to `0.21.0`.
- Retained the safety boundary: no runtime behavior, no strategy logic, no optimizer, no execution-cost modeling, no performance calculation, no PAPER runtime expansion, no exchange mutation, no LIVE readiness, and no production-readiness approval.

## Validation evidence

- `MEASURED`: connector comparison resolved `dev` HEAD `8fca2c83ea11fd1f1d6279c48b168305df55015e` before this increment.
- `MEASURED`: `PROJECT_STATE.md`, `PLAN.md`, `REPORT.md`, `CHANGELOG.md`, and `VERSION.md` were read from `dev` before this increment.
- `MEASURED`: reconstructed focused Gate 5A validation passed `python -m compileall -q src tests` and `pytest -q tests/test_operational_evidence_gate.py` with `5 passed` in the scratch workspace.
- `UNAVAILABLE`: direct mutable local clone evidence because container DNS could not resolve `github.com`.
- `UNAVAILABLE`: exact final branch-head full-repository local validation, Ruff, Black, and Mypy in this execution environment.
- `UNVERIFIED`: exact final branch-head remote CI until GitHub Actions reports.

## 0.20.0 - 2026-06-07

**Engineering milestone:** Gate 4B reporting-boundary and ledger-reconciliation bundle.

- Added `src/reporting/performance_boundary.py` as a reporting-only eligibility boundary over Gate 4A `BacktestRunMetadata`.
- Added deterministic reporting and publication guards for metric eligibility.
- Added Gate 4B through Gate 4CLOSE ledger reconciliation, completion evidence matrix, validation-command consistency, and public-export consistency guards.
- Retained the Gate 4B-0 through Gate 4CLOSE-1C boundary: no runtime behavior, no strategy logic, no optimizer, no execution-cost modeling, no performance calculation, no PAPER runtime expansion, no exchange mutation, and no readiness approval.
