# Aethelgard Version Ledger

## 0.22.3 - 2026-06-17

**Engineering milestone:** Gate 5B-2 main startup contract regression harness.

- Added `tests/test_main_startup_contract.py` to run `main.py` through the current Python executable in a controlled subprocess.
- Added `docs/gates/gate5b_main_startup_contract.md` to record the bounded startup-contract evidence limits.
- Package version advanced to `0.22.3`.

**Evidence classification:**

- `MEASURED_PAPER_DRY_RUN`: a passing local subprocess test may prove only bounded startup evidence for PAPER_ONLY / RESEARCH_ONLY metadata.
- `UNAVAILABLE`: open PR visibility, remote CI/workflow status, workflow artifacts, workflow job logs, exchange audit proof, exchange safety, market-data correctness, execution realism, strategy validity, profitability, and runtime proof beyond bounded startup remain unavailable.

**Safety boundary:** Gate 5B-2 remains PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY. It does not enable live trading, request/read/expose secrets, connect to exchanges, fetch market data, place or cancel orders, generate strategy alpha, run an optimizer, calculate or publish performance, claim profitability, approve readiness, or mutate exchange state. Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.



## 0.22.2 - 2026-06-17

**Engineering milestone:** Gate 5B-1 PAPER runtime dry-run evidence ledger.

- Added `src/reporting/paper_runtime_dry_run_evidence.py` for fail-closed dry-run evidence classification.
- Added focused tests in `tests/test_paper_runtime_dry_run_evidence.py` and public reporting exports.
- Added `docs/gates/gate5b_paper_runtime_dry_run_evidence.md` to record user-provided and Codex-measured dry-run evidence boundaries.
- Package version advanced to `0.22.2`.

**Evidence classification:**

- `MEASURED_PAPER_DRY_RUN`: Codex directly ran `python main.py` locally and observed bounded PAPER_ONLY / RESEARCH_ONLY startup metadata only.
- `USER_PROVIDED_RUNTIME_OUTPUT`: user provided `python main.py` output on macOS showing `foundation_runtime_initialized`, `PAPER_ONLY`, `RESEARCH_ONLY`, and initialized without execution capabilities; this does not prove production readiness, live readiness, exchange safety, data completeness, execution realism, or profitability.
- `UNAVAILABLE`: open PR visibility, remote CI/workflow status, workflow artifacts, workflow job logs, exchange audit proof, and live/production runtime proof remain unavailable.

**Safety boundary:** Gate 5B-1 remains PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY. It does not enable live trading, request/read/expose secrets, connect to exchanges, fetch market data, place or cancel orders, generate strategy alpha, run an optimizer, compute or publish performance, claim profitability, approve readiness, or mutate exchange state. Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.


## 0.22.1 - 2026-06-17

**Engineering milestone:** Gate 5B-0 PAPER runtime safe startup preflight evidence.

- Added `src/reporting/paper_runtime_preflight_evidence.py` for fail-closed `MEASURED_SAFE_STARTUP`, `USER_REPORTED_STARTUP_OK`, `UNAVAILABLE_STARTUP_RUN`, `UNAVAILABLE_RUNTIME_LOG`, `VIOLATION_LIVE_RUNTIME_ENABLED`, and `VIOLATION_SECRET_OR_EXCHANGE_ACCESS` classification.
- Added focused tests in `tests/test_paper_runtime_preflight_evidence.py` and public reporting exports for the bounded preflight evidence adapter.
- Added `docs/gates/gate5b_paper_runtime_preflight_evidence.md` to record the Gate 5B-0 startup/preflight boundary.
- Package version advanced to `0.22.1`.

**Evidence classification:**

- `MEASURED_LOCAL`: local branch `work`, starting commit `053052b4e35ecf2c2bc609e3c92fa9778cfeb3b1`, clean starting tree, source/docs/tests/config/workflow files, and safe startup behavior were inspected locally.
- `MEASURED_SAFE_STARTUP`: `python main.py` is required to be run locally for this gate and only proves bounded PAPER_ONLY startup metadata when observed.
- `USER_REPORTED`: the user requested Gate 5B-0; no user statement is promoted to measured runtime proof.
- `UNAVAILABLE`: open PR visibility, remote CI/workflow status, workflow artifacts, workflow job logs, exchange audit proof, and production/live readiness evidence remain unavailable.

**Safety boundary:** Gate 5B-0 remains PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY. It does not enable live trading, request or expose secrets, connect to exchanges, fetch market data, place or cancel orders, generate strategy alpha, run an optimizer, compute performance, claim profitability, approve readiness, or mutate exchange state. Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.


## 0.22.0 - 2026-06-17

**Engineering milestone:** Gate 5A-13 user-reported green validation evidence reconciliation.

- Recorded Gate 5A-12 as `GREEN_BY_USER_REPORTED_VALIDATION` based on the user report that Gate 5A-12 was merged with green validation.
- Preserved that connector-visible CI remains `UNAVAILABLE`, workflow artifacts remain `UNAVAILABLE`, and workflow job logs remain `UNAVAILABLE` unless directly measured.
- Clarified that user-reported green validation is not connector-visible workflow evidence, is not direct workflow artifact proof, and does not prove production readiness.
- Package version remains `0.22.0`; this is a documentation/test-only reconciliation and does not publish a runtime package increment.

**Evidence classification:**

- `MEASURED_LOCAL`: local documentation and focused ledger tests were updated in this workspace.
- `USER_REPORTED_GREEN_VALIDATION`: Gate 5A-12 was reported by the user as merged with green validation.
- `UNAVAILABLE`: connector-visible CI, workflow artifacts, workflow job logs, open PR visibility, and direct remote validation evidence remain unavailable in this workspace.

**Safety boundary:** Gate 5A-13 does not change runtime behavior, strategy logic, optimizer behavior, execution-cost modeling, performance calculation, PAPER runtime behavior, exchange behavior, exchange mutation, secret handling, or readiness status. No live trading, secret request, secret exposure, exchange connection, order placement, exchange mutation, strategy alpha logic, performance calculation, or readiness approval is added. Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.

## 0.22.0 - 2026-06-17

**Engineering milestone:** Gate 5A-12 secret material boundary evidence adapter validation and repair.

- Validated and repaired the Gate 5A-12 secret material boundary evidence adapter formatting and ledger recency.
- Confirmed public reporting exports include the Gate 5A-12 classification, evidence, assessment, classifier, and documentation-claim helpers.
- Package version remains `0.22.0`; this is a reporting-boundary/test/documentation repair and does not publish a runtime package increment.

**Evidence classification:**

- `MEASURED_LOCAL`: Gate 5A-12 source, focused tests, public exports, and documentation were inspected locally.
- `UNAVAILABLE_SECRET_AUDIT`: missing secret audit evidence remains unavailable.
- `UNAVAILABLE_RUNTIME_SECRET_PROOF`: missing runtime proof remains unavailable.
- `UNAVAILABLE`: open PR, remote CI, workflow artifacts, and remote merge evidence were not visible in this workspace.

**Safety boundary:** Gate 5A-12 does not read environment variables, request credentials, expose secrets, connect to exchanges, place exchange orders, mutate exchange state, approve live trading, approve live readiness, or approve production readiness. Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.

# Version History

## 0.22.0 - 2026-06-16

**Engineering milestone:** Gate 5A-11 exchange mutation boundary evidence adapter.

- Added a fail-closed exchange mutation boundary evidence adapter for `MEASURED_NO_MUTATION_PATH`, `MEASURED_PAPER_ONLY_GUARD`, `USER_REPORTED_NO_LIVE_USE`, `UNAVAILABLE_EXCHANGE_AUDIT`, `UNAVAILABLE_RUNTIME_PROOF`, and `VIOLATION_EXCHANGE_MUTATION_ALLOWED`.
- Hardened evidence classification so PAPER_ONLY evidence does not imply live readiness, user statements stay user-reported, missing audit/runtime proof stays unavailable, and unguarded mutation surfaces classify as violations.
- Added focused tests and a Gate 5A-11 ledger document.
- Package version remains `0.22.0`; this is a reporting-boundary/test/documentation increment and does not publish a runtime package increment.
- Retained the safety boundary: no runtime behavior, no strategy logic, no optimizer, no execution-cost modeling, no performance calculation, no PAPER runtime expansion, no exchange mutation capability, no readiness approval.

## Validation evidence

- `MEASURED_LOCAL`: Gate 5A-11 source, tests, and documentation were changed in this workspace.
- `USER_REPORTED`: user-reported no-live-use statements remain separate from measured source/test/runtime proof.
- `UNAVAILABLE`: remote `origin`, open PR visibility, connector-visible CI, direct workflow artifacts, missing exchange audit evidence, and missing runtime proof remain unavailable unless directly measured.
- `VIOLATION`: unguarded exchange mutation capability is classified as `VIOLATION_EXCHANGE_MUTATION_ALLOWED`.
- `MODELED`: none.


## 0.22.0 - 2026-06-16

**Engineering milestone:** Gate 5A-10 PR / Branch-head provenance evidence adapter.

- Added a fail-closed repository provenance evidence adapter for `USER_REPORTED_PR`, `USER_REPORTED_COMMIT`, `MEASURED_PR_VISIBLE`, `MEASURED_BRANCH_HEAD`, `MEASURED_BRANCH_CONTAINS`, `MEASURED_MERGED_TO_BRANCH`, `UNAVAILABLE_PR_VISIBILITY`, `UNAVAILABLE_BRANCH_REFRESH`, and `UNAVAILABLE_MERGE_EVIDENCE`.
- Hardened PR, branch-head, commit ancestry, and merge evidence classification so user-reported PRs/commits and commit SHA visibility cannot be promoted to measured PR visibility, branch containment, or merge evidence.
- Added focused tests and a Gate 5A-10 ledger document.
- Package version remains `0.22.0`; this is a reporting-boundary/test/documentation increment and does not publish a runtime package increment.
- Retained the safety boundary: no runtime behavior, no strategy logic, no optimizer, no execution-cost modeling, no performance calculation, no PAPER runtime expansion, no exchange mutation, no readiness approval.

## Validation evidence

- `MEASURED_LOCAL`: Gate 5A-10 source, tests, and documentation were changed in this workspace and validation commands were run locally.
- `USER_REPORTED`: user-reported PR/commit statements remain separate from measured repository provenance.
- `UNAVAILABLE`: remote `origin`, open PR visibility, branch refresh evidence, connector-visible CI, direct workflow artifacts, and compare/ancestry evidence for this workspace commit on `dev` remain unavailable.
- `MODELED`: none.


## 0.22.0 - 2026-06-16

**Engineering milestone:** Gate 5A-9 CI/validation evidence boundary adapter.

- Added a fail-closed validation evidence boundary adapter for `MEASURED_LOCAL`, `USER_REPORTED`, `CONNECTOR_VISIBLE_CI`, and `UNAVAILABLE` validation provenance.
- Hardened CI evidence classification so missing workflow runs and empty combined statuses remain `UNAVAILABLE`.
- Preserved user screenshots and user statements as `USER_REPORTED`, not measured local validation or connector-visible CI.
- Added focused regression coverage and a Gate 5A-9 ledger document.
- Package version remains `0.22.0`; this is a reporting-boundary/test/documentation increment and does not publish a runtime package increment.
- Retained the safety boundary: no runtime behavior, no strategy logic, no optimizer, no execution-cost modeling, no performance calculation, no PAPER runtime expansion, no exchange mutation, no readiness approval.

## Validation evidence

- `MEASURED_LOCAL`: Gate 5A-9 source, tests, and documentation were changed in this workspace and focused tests were run locally.
- `USER_REPORTED`: prior Gate 5A-6 green validation screenshot evidence remains user-reported and separate from measured evidence.
- `UNAVAILABLE`: remote `origin`, open PR visibility, connector-visible CI, direct workflow artifacts, workflow job logs, and connector-visible combined status for this workspace commit remain unavailable.
- `MODELED`: none.

## 0.22.0 - 2026-06-16

**Engineering milestone:** Gate 5A-8 documentation evidence reconciliation.

- Reconciled current documentation claims against local repository code, tests, and evidence ledgers.
- Corrected stale Gate 5A-7 connector-only local-execution wording where this workspace now provides measured local branch, commit, status, and validation-command evidence.
- Preserved Gate 4B-5, Gate 4B-5A, Gate 5A-4, Gate 5A-6, and Gate 5A-7 regression anchors.
- Preserved that Gate 5A-6 green validation remains user-reported screenshot evidence and not connector-visible workflow evidence or direct workflow artifact proof.
- Package version remains `0.22.0`; this is documentation/test-only evidence reconciliation and does not publish a runtime package increment.
- Retained the safety boundary: no runtime behavior, no strategy logic, no optimizer, no execution-cost modeling, no performance calculation, no PAPER runtime expansion, no exchange mutation, no readiness approval.

## Validation evidence

- `MEASURED`: local workspace inspection observed branch `work`, starting commit `0e01736c2f17ed47cd0b9ec4f2bd5cf155699872`, and clean starting status.
- `MEASURED`: local files under `src/`, `tests/`, `docs/gates/`, and root project ledgers were read before documentation edits.
- `MEASURED`: Gate 5A-8 changes are limited to documentation and evidence-ledger guard tests.
- `USER_REPORTED`: Gate 5A-6 green validation remains screenshot/user-reported evidence for runs 309, 310, 311, 312, and 313 on `dev`.
- `UNAVAILABLE`: remote `origin` fetch/checkout/pull, open PR visibility, connector-visible CI, direct workflow artifacts, and workflow job logs remain unavailable in this workspace.
- `MODELED`: none.

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
