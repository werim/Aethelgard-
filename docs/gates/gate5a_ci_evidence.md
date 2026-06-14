# Gate 5A-2 CI Evidence Adapter

Gate: Gate 5A operational evidence gate
Increment: Gate 5A-2
Scope: CI/status artifact evidence adapter for the `ci_validation` blocker row
Operating mode: PAPER_ONLY / RESEARCH_ONLY
Live status: NOT_LIVE_READY

## Purpose

Gate 5A-2 adds a deterministic adapter that converts caller-supplied CI evidence into a Gate 5A `ci_validation` evidence item.

The adapter is intentionally offline. It does not call GitHub, mutate workflow state, request secrets, compute performance, submit orders, add strategy logic, add optimizer behavior, expand PAPER runtime behavior, or approve readiness.

## Required evidence

A CI payload is classified as `MEASURED` only when all of the following are true:

- `commit_sha` is present.
- `workflow_name` is present.
- workflow conclusion is exactly `success`.
- CI evidence source is present.
- required job names are non-empty, canonical, unique, present, and successful.
- required artifact names are non-empty, canonical, unique, and present.

Any missing, malformed, duplicated, non-canonical, failed, or incomplete evidence is classified as `UNAVAILABLE`.

## Fail-closed behavior

The adapter returns a Gate 5A `OperationalEvidenceItem` for `ci_validation`.

- Passing CI evidence returns `classification=MEASURED`.
- Any evidence gap returns `classification=UNAVAILABLE`.
- Missing source text is rewritten to an explicit unavailable source string so the downstream Gate 5A input-integrity guard does not silently accept empty evidence.

## Safety boundary

Gate 5A-2 is an evidence adapter only. It does not change runtime behavior, strategy logic, optimizer behavior, execution-cost modeling, performance calculation, PAPER runtime behavior, exchange mutation, exchange behavior, or readiness status.

Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.

## Validation commands

```bash
python -m compileall -q src tests main.py
pytest -q tests/test_validation_command_ledger_consistency.py
pytest -q tests/test_gate4_completion_evidence_matrix.py
pytest -q tests/test_gate4_public_safety_exports.py
pytest -q tests/test_cost_evidence.py
pytest -q tests/test_public_exports.py
pytest -q tests/test_ci_evidence.py
pytest -q
ruff check .
black --check .
mypy .
```

Commands unavailable in an environment must be reported as UNAVAILABLE, not passed. Connector writes alone do not prove local or CI validation.
