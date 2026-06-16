# Gate 5A-4 Evidence Ledger Consistency Audit

Increment: Gate 5A-4 evidence ledger consistency audit
Scope: documentation, version, and evidence-language consistency guard
Operating mode: PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY

## Purpose

Gate 5A-4 adds a fail-closed ledger consistency guard for the evidence language used across `PROJECT_STATE.md`, `REPORT.md`, `VERSION.md`, `CHANGELOG.md`, and this Gate document.

The goal is to prevent documentation drift where user-reported green validation evidence is restated as connector-visible CI evidence or readiness evidence.

Gate 5A-7 extends the same guard to `docs/gates/gate5a_workflow_artifact_evidence_ledger.md` so screenshot-backed green validation evidence is not restated as direct workflow artifact proof. Gate 5A-8 preserves those anchors while correcting stale documentation evidence classes against the current local repo state.

## Evidence boundary

Gate 5A-4 records that Gate 5A-3 has source, test, and documentation counterparts:

- `src/reporting/audit_runtime_evidence.py`
- `tests/test_audit_runtime_evidence.py`
- `docs/gates/gate5a_audit_runtime_evidence.md`

Gate 5A-6 records that the data-freshness evidence adapter has source, test, and documentation counterparts:

- `src/reporting/data_freshness_evidence.py`
- `tests/test_data_freshness_evidence.py`
- `docs/gates/gate5a_data_freshness_evidence.md`

Gate 5A-4 does not prove those tests passed in this execution environment. It preserves the distinction that Gate 5A-3 and Gate 5A-6 have user-reported green validation evidence, while connector-visible CI remains UNAVAILABLE and is not connector-visible workflow evidence.

Gate 5A-7 records that user-provided screenshot evidence shows green validation runs 309 through 313 for `dev`, but direct workflow artifacts, job logs, and connector-visible workflow runs remain unavailable through the connector in this environment.

## Consistency checks

The focused guard in `tests/test_evidence_ledger_consistency.py` checks:

- package version alignment across `pyproject.toml`, `src.__version__`, `VERSION.md`, and `CHANGELOG.md`;
- Gate 5A-4 ledger text across the current documentation surfaces;
- Gate 5A-3 source, test, and documentation counterparts;
- Gate 5A-6 source, test, and documentation counterparts;
- Gate 5A-7 workflow evidence boundary wording;
- Gate 5A-8 documentation evidence reconciliation wording;
- user-reported green evidence language;
- connector-visible CI remains UNAVAILABLE and not connector-visible workflow evidence;
- screenshot evidence is not restated as direct workflow artifact proof;
- safety phrases for PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY.

## Safety boundary

Gate 5A-4, Gate 5A-7, and Gate 5A-8 are ledger consistency guards only. They do not change runtime behavior, strategy logic, optimizer behavior, execution-cost modeling, performance calculation, PAPER runtime behavior, exchange mutation, exchange behavior, or readiness status.

Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.

## Validation commands

```bash
python -m compileall -q src tests main.py
pytest -q tests/test_evidence_ledger_consistency.py
pytest -q tests/test_validation_command_ledger_consistency.py
pytest -q tests/test_gate4_completion_evidence_matrix.py
pytest -q tests/test_gate4_public_safety_exports.py
pytest -q tests/test_cost_evidence.py
pytest -q tests/test_public_exports.py
pytest -q tests/test_audit_runtime_evidence.py
pytest -q tests/test_risk_control_evidence.py
pytest -q tests/test_data_freshness_evidence.py
pytest -q
ruff check .
black --check .
mypy .
```

Commands unavailable in an environment must be reported as UNAVAILABLE, not passed. Connector writes alone do not prove local or CI validation.
## Gate 5A-10 repository provenance evidence note

Gate 5A-10 adds `src/reporting/repository_provenance_evidence.py`, `tests/test_repository_provenance_evidence.py`, and `docs/gates/gate5a_pr_branch_provenance_evidence.md` as the PR / Branch-head provenance evidence adapter.

Gate 5A-10 preserves these fail-closed evidence boundaries:

- user-reported PR creation remains `USER_REPORTED_PR`, not `MEASURED_PR_VISIBLE`;
- user-reported commit evidence remains `USER_REPORTED_COMMIT`, not branch containment or merge evidence;
- commit SHA visibility alone is not merge evidence;
- `dev` branch containment requires measured branch/compare evidence;
- missing PR lookup remains `UNAVAILABLE_PR_VISIBILITY`;
- missing branch refresh remains `UNAVAILABLE_BRANCH_REFRESH`;
- missing compare/ancestry evidence remains `UNAVAILABLE_MERGE_EVIDENCE`;
- docs cannot claim merged-to-`dev` unless `MEASURED_MERGED_TO_BRANCH` evidence is present.

Gate 5A-10 is a reporting-boundary/test/documentation increment only. It does not change runtime behavior, strategy logic, optimizer behavior, execution-cost modeling, performance calculation, PAPER runtime behavior, exchange mutation, exchange behavior, or readiness status.
