# Gate 5A-3 Audit Runtime Evidence Adapter

Gate: Gate 5A operational evidence gate
Increment: Gate 5A-3
Scope: audit trail integrity and PAPER runtime reconciliation evidence adapter
Operating mode: PAPER_ONLY / RESEARCH_ONLY
Live status: NOT_LIVE_READY

## Purpose

Gate 5A-3 adds a deterministic adapter that converts caller-supplied persistence reconciliation reports into Gate 5A evidence items for:

- `audit_trail_integrity`
- `paper_runtime_reconciliation`

The adapter is intentionally offline. It does not read local databases, mutate audit artifacts, run a PAPER runtime, request secrets, compute performance, submit orders, add strategy logic, add optimizer behavior, expand PAPER runtime behavior, or approve readiness.

## Required evidence

Audit/runtime evidence is classified as `MEASURED` only when all of the following are true:

- a reconciliation report is present;
- the report has at least one matched decision audit;
- the report has no reconciliation issues;
- source evidence is present.

Any missing report, empty matched-decision set, reconciliation issue, or missing source is classified as `UNAVAILABLE`.

## Fail-closed behavior

The adapter returns Gate 5A `OperationalEvidenceItem` records for audit trail integrity and PAPER runtime reconciliation.

- Passing reconciliation evidence returns `classification=MEASURED` for both blocker rows.
- Any evidence gap returns `classification=UNAVAILABLE` for both blocker rows.
- Missing source text is rewritten to an explicit unavailable source string so downstream Gate 5A input validation does not silently accept empty evidence.

## Safety boundary

Gate 5A-3 is an evidence adapter only. It does not change runtime behavior, strategy logic, optimizer behavior, execution-cost modeling, performance calculation, PAPER runtime behavior, exchange mutation, exchange behavior, or readiness status.

Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.

## Validation commands

```bash
python -m compileall -q src tests main.py
pytest -q tests/test_validation_command_ledger_consistency.py
pytest -q tests/test_gate4_completion_evidence_matrix.py
pytest -q tests/test_gate4_public_safety_exports.py
pytest -q tests/test_cost_evidence.py
pytest -q tests/test_public_exports.py
pytest -q tests/test_audit_runtime_evidence.py
pytest -q
ruff check .
black --check .
mypy .
```

Commands unavailable in an environment must be reported as UNAVAILABLE, not passed. Connector writes alone do not prove local or CI validation.
