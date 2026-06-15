# Gate 5A-5 Risk Control Evidence Adapter

Gate: Gate 5A operational evidence gate
Increment: Gate 5A-5
Scope: risk-control enforcement evidence adapter
Operating mode: PAPER_ONLY / RESEARCH_ONLY
Live status: NOT_LIVE_READY

## Purpose

Gate 5A-5 adds a deterministic adapter that converts caller-supplied risk-control policy evidence into the Gate 5A `risk_control_enforcement` evidence item.

The adapter is fail-closed. Missing, malformed, duplicated, non-canonical, or unenforced policy evidence remains `UNAVAILABLE`.

## Required evidence

Risk-control enforcement evidence is classified as `MEASURED` only when all of the following are true:

- a non-empty evidence source is present;
- at least one required policy id is supplied;
- required policy ids are canonical and unique;
- observed policy evidence is supplied;
- observed policy ids are canonical and unique;
- every required policy id has observed evidence;
- every required policy is marked enforced.

## Gate 5A integration

When measured, the adapter returns a single `OperationalEvidenceItem` for:

- `risk_control_enforcement`

When unavailable, the same blocker id is returned with `UNAVAILABLE` classification and explicit diagnostics.

## Safety boundary

Gate 5A-5 is an evidence adapter only. It does not change runtime behavior, strategy logic, optimizer behavior, execution-cost modeling, performance calculation, PAPER runtime behavior, exchange mutation, exchange behavior, or readiness status.

Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.

## Validation commands

```bash
python -m compileall -q src tests main.py
pytest -q tests/test_risk_control_evidence.py
pytest -q tests/test_public_exports.py
pytest -q tests/test_evidence_ledger_consistency.py
pytest -q
ruff check .
black --check .
mypy .
```

Commands unavailable in an environment must be reported as UNAVAILABLE, not passed. Connector writes alone do not prove local or CI validation.
