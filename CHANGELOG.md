# Changelog

## [0.22.6] - 2026-06-19

### Added

- Added Gate 5B-5 optional local-only runtime artifact CLI in `src/reporting/runtime_artifact_cli.py`.
- Added focused CLI regression coverage in `tests/test_runtime_artifact_cli.py` for local path delegation, invalid local input failure, credential-free operation, and unchanged Gate 5B-2 startup behavior.

### Safety

- Preserved PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY.
- The CLI is optional and explicitly invoked; it reads only local JSON metadata and writes only local `reports/*.json` artifacts through the existing writer.
- No startup semantics, runtime boot behavior, exchange connection, network access, API-key requirement, market fetch, order path, background service, live trading behavior, performance claim, profitability claim, or readiness approval was added.

### Evidence

- Gate 5A-4 evidence ledger consistency audit preserved user-reported green evidence; connector-visible CI remains UNAVAILABLE; this is not connector-visible workflow evidence. Gate 5A-8 documentation evidence reconciliation remains documentation/test-only evidence reconciliation. Gate 5A-7 workflow artifact evidence ledger, Gate 4B-5, Gate 4B-5A, remote `origin`, open PR, and direct workflow artifact evidence remain UNAVAILABLE.
- `MEASURED`: local focused tests for the CLI, existing writer, and Gate 5B-2 startup contract were run.
- `UNAVAILABLE`: open PR visibility, remote CI/workflow status, workflow artifacts, workflow job logs, exchange audit proof, market-data completeness, execution realism, profitability, live readiness, and production readiness remain unavailable.


## [0.22.5-docs] - 2026-06-19

### Documentation

- Reconciled Gate 5B runtime artifact documentation with code evidence observed on `dev`.
- Added a code-evidence table to `docs/gates/gate5b_runtime_artifact_writer.md` for `src/reporting/runtime_artifact_writer.py`, `tests/test_runtime_artifact_writer.py`, `tests/test_runtime_artifact_schema_ledger_consistency.py`, `src/reporting/__init__.py`, and `pyproject.toml`.

### Safety

- Documentation-only reconciliation; no runtime behavior, CLI wrapper, `python main.py` behavior, strategy logic, optimizer behavior, performance calculation, exchange connection, market fetch, order path, secret handling, exchange mutation, live trading, or readiness approval was added.
- PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY remains unchanged.
- Missing evidence remains UNAVAILABLE, unknown execution costs are not zero, and backtest performance alone does not prove production readiness.

### Evidence

- `MEASURED`: direct GitHub connector reads of the listed source, tests, export surface, and packaging/version file on `dev`.
- `UNAVAILABLE`: local test execution in this environment, connector-visible CI/workflow status, workflow artifacts, workflow job logs, exchange audit proof, market-data completeness, execution realism, profitability, live readiness, and production readiness.


## [0.22.5] - 2026-06-18

### Added

- Added Gate 5B-4 runtime artifact schema ledger consistency coverage in `tests/test_runtime_artifact_schema_ledger_consistency.py`.
- Updated Gate 5B runtime artifact writer documentation with explicit required top-level, `safety_boundary`, and `unavailable_evidence` schema fields.

### Safety

- Preserved PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY.
- Gate 5B-4 is a ledger consistency check only.
- Local runtime artifacts are evidence artifacts, not production approval.
- Runtime artifact schema documentation must not imply live readiness.
- Missing evidence remains UNAVAILABLE, unknown execution costs are not zero, and backtest performance alone does not prove production readiness.
- No secrets, exchange connection, market fetch, order path, optimizer, strategy alpha, performance claim, or readiness approval was added.
- The optional CLI wrapper was intentionally deferred because the smallest safe step was ledger consistency only.

### Evidence

- `MEASURED`: local schema/test/docs consistency only.
- `UNAVAILABLE`: open PR visibility, remote CI/workflow status, workflow artifacts, workflow job logs, exchange audit proof, market-data completeness, execution realism, profitability, live readiness, and production readiness remain unavailable.



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
