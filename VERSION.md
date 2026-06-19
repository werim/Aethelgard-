# Aethelgard Version Ledger

## 0.22.5-docs - 2026-06-19

**Engineering milestone:** Gate 5B runtime artifact code evidence documentation reconciliation.

- Updated `docs/gates/gate5b_runtime_artifact_writer.md` with a code-evidence reconciliation table based on direct `dev` branch reads.
- Recorded observed code surfaces: `src/reporting/runtime_artifact_writer.py`, `tests/test_runtime_artifact_writer.py`, `tests/test_runtime_artifact_schema_ledger_consistency.py`, `src/reporting/__init__.py`, and `pyproject.toml`.
- No package version bump was made; `pyproject.toml` remains `0.22.5` because this is documentation-only reconciliation of already-present code evidence.

**Evidence classification:**

- `MEASURED`: direct GitHub connector reads of the listed source, test, export, and packaging/version files on `dev`.
- `UNAVAILABLE`: local test execution in this environment, connector-visible CI/workflow status, workflow artifacts, workflow job logs, exchange audit proof, market-data completeness, execution realism, profitability, live readiness, and production readiness remain unavailable unless directly measured.

**Safety boundary:** This reconciliation is documentation-only. It does not add runtime behavior, a CLI wrapper, `python main.py` behavior, live trading, secret request/read/exposure, exchange connection, market fetch, order path, strategy alpha, optimizer, performance calculation, profitability claim, readiness approval, or exchange mutation. PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY remains unchanged. Missing evidence remains UNAVAILABLE. Unknown execution costs are not zero. Backtest performance alone does not prove production readiness.


## 0.22.5 - 2026-06-18

**Engineering milestone:** Gate 5B-4 runtime artifact schema ledger consistency check.

- Added `tests/test_runtime_artifact_schema_ledger_consistency.py` to verify documented runtime artifact schema fields and safety phrases stay aligned with the runtime artifact writer.
- Updated `docs/gates/gate5b_runtime_artifact_writer.md` with the Gate 5B-4 schema ledger consistency section.
- Documented that the optional CLI wrapper was intentionally deferred because the smallest safe step was ledger consistency only.
- Package version advanced to `0.22.5`.

**Evidence classification:**

- `MEASURED`: local schema/test/docs consistency evidence only.
- `UNAVAILABLE`: open PR visibility, remote CI/workflow status, workflow artifacts, workflow job logs, exchange audit proof, market-data completeness, execution realism, profitability, live readiness, and production readiness remain unavailable unless directly measured.

**Safety boundary:** Gate 5B-4 remains PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY. It is a ledger consistency check only, does not change `python main.py`, does not weaken the Gate 5B-2 startup contract, and adds no live trading, secret request/read/exposure, exchange connection, market fetch, order path, strategy alpha, optimizer, performance claim, or readiness approval. Missing evidence remains UNAVAILABLE. Unknown execution costs are not zero. Backtest performance alone does not prove production readiness.



# Aethelgard Version Ledger

## 0.22.4 - 2026-06-18

**Engineering milestone:** Gate 5B-3 offline runtime output artifact writer.

- Added `src/reporting/runtime_artifact_writer.py` for deterministic local JSON runtime evidence artifacts under `reports/` only.
- Added `tests/test_runtime_artifact_writer.py` to verify deterministic JSON, bounded safety metadata, explicit unavailable evidence, forbidden secret/performance fields, no readiness implication, and fail-closed path policy.
- Added `docs/gates/gate5b_runtime_artifact_writer.md` to document the local offline artifact boundary.
- Package version advanced to `0.22.4`.

**Evidence classification:**

- `MEASURED_PAPER_DRY_RUN`: admitted only when the caller supplies measured local safe dry-run evidence.
- `USER_PROVIDED_RUNTIME_OUTPUT`: admitted only as user-provided runtime output, not measured local proof.
- `UNAVAILABLE_DRY_RUN` / `UNAVAILABLE_DRY_RUN_LOG`: missing evidence remains unavailable.
- `UNAVAILABLE`: open PR visibility, remote CI/workflow status, workflow artifacts, workflow job logs, exchange audit proof, market-data completeness, execution realism, profitability, live readiness, and production readiness remain unavailable unless directly measured.

**Safety boundary:** Gate 5B-3 remains PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY. It does not enable live trading, request/read/expose secrets, connect to exchanges, fetch market data, place or cancel orders, generate strategy alpha, run an optimizer, calculate or publish performance, claim profitability, approve readiness, or mutate exchange state. Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.



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
