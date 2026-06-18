# Changelog

## [0.22.4] - 2026-06-18

### Added

- Added Gate 5B-3 offline runtime artifact writer in `src/reporting/runtime_artifact_writer.py`.
- Added focused regression coverage in `tests/test_runtime_artifact_writer.py`.
- Added Gate 5B-3 documentation in `docs/gates/gate5b_runtime_artifact_writer.md`.
- Exported the Gate 5B-3 artifact writer through `src.reporting`.

### Safety

- Preserved PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY.
- Runtime artifacts are deterministic local JSON files under `reports/` only and contain bounded caller-supplied startup/runtime metadata.
- Unsafe paths, absolute paths, parent traversal, non-JSON files, secret-like fields, strategy alpha fields, optimizer/performance/profitability fields, and readiness-upgrade fields fail closed.
- No live trading, secret request/read/exposure, exchange connection, market fetch, order path, optimizer behavior, strategy alpha logic, performance calculation, profitability claim, or readiness approval was added.

### Evidence

- `MEASURED_PAPER_DRY_RUN`: admitted only for caller-supplied measured safe dry-run evidence.
- `USER_PROVIDED_RUNTIME_OUTPUT`: preserved as user-provided evidence only.
- `UNAVAILABLE`: open PR visibility, remote CI/workflow status, workflow artifacts, workflow job logs, exchange audit proof, market-data completeness, execution realism, profitability, live readiness, and production readiness remain unavailable.



## [0.22.3] - 2026-06-17

### Added

- Added Gate 5B-2 subprocess startup-contract regression coverage in `tests/test_main_startup_contract.py`.
- Added Gate 5B-2 documentation in `docs/gates/gate5b_main_startup_contract.md`.

### Safety

- Preserved PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY.
- The subprocess harness verifies bounded JSON startup metadata, `foundation_runtime_initialized`, deterministic seed evidence, and absence of unsafe live, secret, order, market-fetch, strategy, optimizer, performance, or readiness claims.
- No runtime behavior, live trading, secret request/read/exposure, exchange connection, market fetch, order path, optimizer behavior, strategy alpha logic, performance calculation, profitability claim, or readiness approval was added.

### Evidence

- `MEASURED_PAPER_DRY_RUN`: a passing local subprocess test may prove only bounded startup evidence.
- `UNAVAILABLE`: open PR visibility, remote CI/workflow status, workflow artifacts, workflow job logs, exchange audit proof, exchange safety, market-data correctness, execution realism, strategy validity, profitability, and runtime proof beyond bounded startup remain unavailable.



## [0.22.2] - 2026-06-17

### Added

- Added Gate 5B-1 PAPER runtime dry-run evidence classification in `src/reporting/paper_runtime_dry_run_evidence.py`.
- Added focused regression coverage in `tests/test_paper_runtime_dry_run_evidence.py`.
- Added Gate 5B-1 documentation in `docs/gates/gate5b_paper_runtime_dry_run_evidence.md`.
- Exported the Gate 5B-1 reporting adapter through `src.reporting`.

### Safety

- Preserved PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY.
- User-provided runtime output remains `USER_PROVIDED_RUNTIME_OUTPUT`, not measured local proof.
- User-reported dry-run success remains `USER_REPORTED_DRY_RUN_OK`, missing dry-run proof remains `UNAVAILABLE_DRY_RUN`, and missing logs remain `UNAVAILABLE_DRY_RUN_LOG`.
- LIVE mode, exchange connection, market fetch, order path, exchange mutation, secret access, or readiness claims classify as violations.
- No live trading, secret requests, exchange connections, market fetches, order paths, exchange mutation, optimizer behavior, strategy alpha logic, performance publication, profitability claim, or readiness approval was added.

### Evidence

- `MEASURED_PAPER_DRY_RUN`: Codex directly ran `python main.py` locally and observed bounded PAPER_ONLY / RESEARCH_ONLY startup metadata only.
- `USER_PROVIDED_RUNTIME_OUTPUT`: user provided `python main.py` output on macOS showing `foundation_runtime_initialized`, `PAPER_ONLY`, `RESEARCH_ONLY`, and initialized without execution capabilities; it does not prove production readiness, live readiness, exchange safety, data completeness, execution realism, or profitability.
- `UNAVAILABLE`: open PR visibility, remote CI/workflow status, workflow artifacts, workflow job logs, exchange audit proof, and live/production runtime proof remain unavailable.


## [0.22.1] - 2026-06-17

### Added

- Added Gate 5B-0 PAPER runtime safe startup preflight evidence classification in `src/reporting/paper_runtime_preflight_evidence.py`.
- Added focused regression coverage in `tests/test_paper_runtime_preflight_evidence.py`.
- Added Gate 5B-0 documentation in `docs/gates/gate5b_paper_runtime_preflight_evidence.md`.
- Exported the Gate 5B-0 reporting adapter through `src.reporting`.

### Safety

- Preserved PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY.
- `MEASURED_SAFE_STARTUP` only applies to directly observed bounded startup evidence showing PAPER_ONLY mode, no secret access, no exchange connection, no market fetch, no order path, no strategy alpha, no optimizer, and no readiness approval.
- User-reported startup success remains `USER_REPORTED_STARTUP_OK`, missing startup proof remains `UNAVAILABLE_STARTUP_RUN`, and missing runtime logs remain `UNAVAILABLE_RUNTIME_LOG`.
- LIVE mode, readiness approval, secret access, credential requirements, exchange connection, market fetch, order placement/cancellation, external mutation, strategy alpha execution, or optimizer execution classify as violations.
- No live trading, secret requests, exchange connections, order placement, exchange mutation, optimizer behavior, strategy alpha logic, performance calculation, profitability claim, or readiness approval was added.

### Evidence

- `MEASURED_LOCAL`: Gate 5B-0 source, tests, exports, docs, and local startup command are in scope for direct workspace validation.
- `UNAVAILABLE`: open PR visibility, remote CI/workflow status, workflow artifacts, workflow job logs, exchange audit proof, and live/production readiness evidence remain unavailable.


## [0.22.0] - 2026-06-17

### Gate 5A-13 user-reported green validation evidence reconciliation

- Recorded Gate 5A-12 as `GREEN_BY_USER_REPORTED_VALIDATION` from the user report that Gate 5A-12 was merged with green validation.
- Preserved that connector-visible CI remains `UNAVAILABLE`, workflow artifacts remain `UNAVAILABLE`, and workflow job logs remain `UNAVAILABLE` unless directly measured.
- Clarified that user-reported green validation is not connector-visible workflow evidence, is not direct workflow artifact proof, and does not prove production readiness.
- Added focused ledger consistency coverage to prevent drift from the Gate 5A-13 documentation/test-only reconciliation boundary.
- Retained PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY: no runtime behavior, strategy logic, optimizer behavior, execution-cost modeling, performance calculation, PAPER runtime behavior, exchange behavior, exchange mutation, secret handling, live trading, or readiness approval was added.


## [0.22.0] - 2026-06-17

### Changed

- Validated and repaired Gate 5A-12 secret material boundary evidence adapter formatting.
- Updated Gate 5A-12 ledger wording across project state, report, version, changelog, plan, and evidence ledger documentation.

### Safety

- Preserved PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY.
- Gate 5A-12 secret-material evidence never permits live-readiness or production-readiness claims.
- User-reported “secrets not shared” remains `USER_REPORTED_SECRETS_NOT_SHARED`, not measured proof.
- Missing secret audit evidence remains `UNAVAILABLE_SECRET_AUDIT`; missing runtime proof remains `UNAVAILABLE_RUNTIME_SECRET_PROOF`.
- Requested, committed, logged, or documented real secrets classify as `VIOLATION_SECRET_MATERIAL_EXPOSED`.
- No live trading, secret requests, exchange connections, order placement, exchange mutation, optimizer behavior, strategy alpha logic, performance calculation, or readiness approval was added.

### Evidence

- `MEASURED_LOCAL`: local Gate 5A-12 source, tests, exports, and docs were inspected and validation commands were executed in this workspace.
- `UNAVAILABLE`: open PR visibility, remote CI/workflow status, workflow artifacts, and merge evidence were unavailable.

## [0.22.0] - 2026-06-16

### Added

- Added Gate 5A-11 exchange mutation boundary evidence adapter for measured no-mutation paths, measured PAPER_ONLY guards, user-reported no-live-use, unavailable audit/runtime proof, and unguarded mutation violations.
- Added focused exchange mutation boundary tests and Gate 5A-11 evidence-ledger wording.

### Safety

- Gate 5A-11 is reporting-boundary/test/documentation work only; it does not add live trading, real exchange order placement, optimizer behavior, strategy alpha logic, performance calculation, or readiness approval.
- PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY remains unchanged. Unknown execution costs are not zero. Missing evidence remains unavailable.

### Evidence

- `MEASURED_LOCAL`: Gate 5A-11 source/tests/docs changed locally.
- `USER_REPORTED`: user statements remain user-reported no-live-use only.
- `UNAVAILABLE`: missing exchange audit evidence and runtime proof remain unavailable.
- `VIOLATION`: unguarded exchange mutation capability classifies as `VIOLATION_EXCHANGE_MUTATION_ALLOWED`.
- `MODELED`: none.


## [0.22.0] - 2026-06-16

### Changed

- Added Gate 5A-10 PR / Branch-head provenance evidence adapter for PR visibility, branch head, commit ancestry, merge, and unavailable remote evidence classification.
- Kept user-reported PR and commit evidence separate from measured PR visibility, measured branch containment, and measured merge evidence.
- Added focused repository provenance tests and Gate 5A-10 evidence-ledger wording.

### Safety

- Gate 5A-10 is reporting-boundary/test/documentation work only; it does not change runtime behavior, strategy logic, optimizer behavior, execution-cost modeling, performance calculation, PAPER runtime behavior, exchange mutation, or readiness status.
- Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.

### Evidence classification

- `MEASURED_LOCAL`: Gate 5A-10 source/tests/docs changed locally and validation commands run in this workspace.
- `USER_REPORTED`: user-reported PR/commit statements remain user-reported and are not measured branch or merge evidence.
- `UNAVAILABLE`: remote `origin`, open PRs for `dev`, branch refresh evidence, compare/ancestry evidence, connector-visible CI, direct workflow artifacts, and workflow job logs.
- `MODELED`: none.


## [0.22.0] - 2026-06-16

### Changed

- Added Gate 5A-9 CI/validation evidence boundary adapter for `MEASURED_LOCAL`, `USER_REPORTED`, `CONNECTOR_VISIBLE_CI`, and `UNAVAILABLE` provenance.
- Hardened validation evidence classification so missing workflow runs and empty combined statuses remain `UNAVAILABLE`, and user screenshots/statements remain `USER_REPORTED`.
- Reconciled documentation evidence claims with the current local repository state.
- Corrected stale connector-only local-validation wording from Gate 5A-7 where this workspace now has measured local branch, commit, working-tree status, and validation-command evidence.
- Kept connector-visible CI, direct workflow artifacts, workflow logs, remote PR visibility, and `origin` refresh evidence classified as `UNAVAILABLE`.
- Preserved Gate 4B-5, Gate 4B-5A, Gate 5A-4, Gate 5A-6, and Gate 5A-7 regression anchors.

### Safety

- Gate 5A-9 is reporting-boundary/test/documentation work only; it does not change runtime behavior, strategy logic, optimizer behavior, execution-cost modeling, performance calculation, PAPER runtime behavior, exchange mutation, or readiness status.
- Documentation/test-only reconciliation; does not change runtime behavior, strategy logic, optimizer behavior, execution-cost modeling, performance calculation, PAPER runtime behavior, exchange mutation, or readiness status.
- Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.

### Evidence classification

- `MEASURED_LOCAL`: Gate 5A-9 source/tests/docs changed locally and focused validation evidence boundary tests run in this workspace.
- `MEASURED`: local branch `work`, starting commit `0e01736c2f17ed47cd0b9ec4f2bd5cf155699872`, clean starting working tree, required file inspection, and local validation command outputs for this workspace.
- `USER_REPORTED`: Gate 5A-6 screenshot-backed green validation remains user-reported and is not connector-visible workflow evidence.
- `UNAVAILABLE`: remote `origin`, open PRs for `dev`, connector-visible CI, direct workflow artifacts, and workflow job logs.

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
- Added Gate 5A-5 risk-control enforcement evidence adapter in `src/reporting/risk_control_evidence.py`.
- Added focused Gate 5A-5 risk-control evidence coverage in `tests/test_risk_control_evidence.py`.
- Added Gate 5A-5 documentation in `docs/gates/gate5a_risk_control_evidence.md`.
- Added Gate 5A-6 data-freshness evidence adapter in `src/reporting/data_freshness_evidence.py`.
- Added focused Gate 5A-6 data-freshness evidence coverage in `tests/test_data_freshness_evidence.py`.
- Added Gate 5A-6 documentation in `docs/gates/gate5a_data_freshness_evidence.md`.
- Added Gate 5A-7 workflow artifact evidence ledger in `docs/gates/gate5a_workflow_artifact_evidence_ledger.md`.
- Extended `tests/test_evidence_ledger_consistency.py` so Gate 5A-6 and Gate 5A-7 evidence wording stays explicit.

### Changed

- Package version advanced to `0.22.0` for Gate 5A-2 and kept stable for Gate 5A-3 through Gate 5A-7.
- CI validation can now be represented as a fail-closed Gate 5A `ci_validation` evidence item from caller-supplied workflow, job, and artifact evidence.
- Gate 5A-3 audit/runtime reconciliation evidence can now be represented as fail-closed Gate 5A evidence items from caller-supplied persistence reconciliation reports.
- Gate 5A-4 keeps user-reported green validation evidence separate from connector-visible CI evidence.
- Gate 5A-5 risk-control enforcement evidence can now be represented as a fail-closed Gate 5A `risk_control_enforcement` evidence item from caller-supplied policy evidence.
- Gate 5A-6 data-freshness evidence can now be represented as a fail-closed Gate 5A `data_freshness` evidence item from caller-supplied freshness and selector-consistency evidence.
- Gate 5A-7 records user-provided green validation screenshot evidence without converting it into connector-visible workflow artifact evidence.
- `src.reporting.__all__` now exposes Gate 5A-5 risk-control and Gate 5A-6 data-freshness evidence helpers.

### Evidence ledger

- Gate 5A-3 source/test/doc counterparts are recorded as `src/reporting/audit_runtime_evidence.py`, `tests/test_audit_runtime_evidence.py`, and `docs/gates/gate5a_audit_runtime_evidence.md`.
- Gate 5A-3 has user-reported green validation evidence, while connector-visible CI remains UNAVAILABLE and is not connector-visible workflow evidence.
- Gate 5A-4 evidence ledger consistency audit preserves the evidence wording across `PROJECT_STATE.md`, `REPORT.md`, `VERSION.md`, `CHANGELOG.md`, and Gate 5A evidence docs.
- Gate 5A-4 green is recorded as user-reported green validation evidence for `e6b4f28285da0a488e40f84ff47395b89059ff11` after the Gate 4B-5 VERSION anchor repair.
- Gate 5A-5 green is recorded as user-reported green validation evidence for `07becd0c773cde6a50c40c5d9c4fe5da4c29ad49` after Ruff import-block repair.
- Gate 5A-5 connector-visible CI remains UNAVAILABLE and user-reported green validation evidence is not connector-visible workflow evidence.
- Gate 5A-6 green is recorded as user-reported green validation evidence for `3f5cb4ea89fa3c12661e020d802796439d3a064c` after Ruff and Black formatting repairs.
- Gate 5A-6 connector-visible CI remains UNAVAILABLE and user-reported green validation evidence is not connector-visible workflow evidence.
- Gate 5A-7 records that user-provided screenshot evidence shows validation runs 309, 310, 311, 312, and 313 green on `dev`, while connector-visible workflow artifacts remain `UNAVAILABLE`.

### Known limitations

- Gate 5A-2 does not call GitHub or fetch workflow artifacts automatically.
- Missing, malformed, duplicated, failed, or incomplete CI evidence remains `UNAVAILABLE`.
- Gate 5A-3 does not read local databases or run a PAPER runtime; it only classifies caller-supplied reconciliation reports.
- Gate 5A-4 does not run local validation or prove connector-visible CI.
- Gate 5A-5 does not execute risk controls; it only classifies caller-supplied risk-control policy evidence.
- Gate 5A-6 does not fetch market data; it only classifies caller-supplied freshness and selector-consistency evidence.
- Gate 5A-7 does not prove direct workflow artifact evidence because connector workflow lookup returned no runs for the Gate 5A-6 green-by-user-report head.
- Local full-repository validation remains unavailable in this execution environment until CI or a mutable clone reports it.
- The Gate 5A-2 through Gate 5A-7 boundary does not compute performance, model costs, add optimizer behavior, add strategy logic, add PAPER runtime behavior, approve readiness, or enable live trading.

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
- Gate 4CLOSE-1C canonicalization coverage across `REPORT.md`, `PROJECT_STATE.md`, and the Gate 4 completion matrix.

### Changed

- Package version advanced to `0.20.0`.
- `src/reporting/__init__.py` exports Gate 4B-0 and Gate 4B-1 reporting helpers.
- Gate 4B-2 records a reporting-boundary completeness audit of report, Markdown, JSON, payload, and serialization paths.
- Gate 4B-3 records user-reported green validation for the reporting export-boundary test.
- Version-ledger evidence reconciliation records user-reported green validation for the version consistency test after Ruff import-block repair.
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
