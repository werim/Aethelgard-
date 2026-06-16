# Gate 5A-11 Exchange Mutation Boundary Evidence Adapter

Increment: Gate 5A-11 exchange mutation boundary evidence adapter  
Scope: reporting-boundary adapter, focused regression coverage, and evidence-ledger documentation  
Operating mode: PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY

## Purpose

Gate 5A-11 hardens exchange mutation boundary evidence classification so PAPER-only source/test evidence, user statements, missing audit evidence, missing runtime proof, and violation findings cannot be conflated.

The adapter separates these classes:

- `MEASURED_NO_MUTATION_PATH`: source and test evidence show no exchange mutation path.
- `MEASURED_PAPER_ONLY_GUARD`: source, test, exchange-audit, and runtime evidence show a hard PAPER_ONLY guard around a mutation surface.
- `USER_REPORTED_NO_LIVE_USE`: user statements or screenshots report no live use; this is not measured proof.
- `UNAVAILABLE_EXCHANGE_AUDIT`: exchange audit evidence is missing or incomplete.
- `UNAVAILABLE_RUNTIME_PROOF`: runtime proof is missing or incomplete.
- `VIOLATION_EXCHANGE_MUTATION_ALLOWED`: real order placement or exchange mutation capability exists without a hard guard, or docs claim production/live readiness.

## Fail-closed rules

- Missing exchange audit evidence remains `UNAVAILABLE_EXCHANGE_AUDIT`.
- Missing runtime proof remains `UNAVAILABLE_RUNTIME_PROOF`.
- User statements remain `USER_REPORTED_NO_LIVE_USE` and do not become measured proof.
- PAPER_ONLY mode is not promoted to live safety or production readiness.
- Any real order placement or exchange mutation capability without a hard PAPER_ONLY guard classifies as `VIOLATION_EXCHANGE_MUTATION_ALLOWED`.
- Guarded PAPER-only execution is measured boundary evidence only when source, test, exchange-audit, and runtime proof evidence are present.
- Docs cannot claim production readiness from this adapter.

## Implemented surface

- `src/reporting/exchange_mutation_boundary_evidence.py` defines the Gate 5A-11 exchange mutation boundary classifications and deterministic classifier helper.
- `tests/test_exchange_mutation_boundary_evidence.py` proves PAPER_ONLY evidence does not imply live readiness, missing evidence stays unavailable, user reports stay user-reported, unguarded mutation surfaces are violations, guarded PAPER-only evidence requires source/test proof, and docs cannot claim production readiness.
- `tests/test_evidence_ledger_consistency.py` guards the Gate 5A-11 ledger wording.

## Evidence classification

| Evidence | Classification | Note |
| --- | --- | --- |
| Local Gate 5A-11 source and tests | `MEASURED_LOCAL` | Source, tests, and docs were changed in this workspace. |
| User statements about no live use | `USER_REPORTED_NO_LIVE_USE` | Recorded separately from measured source/test/runtime proof. |
| Exchange audit evidence | `UNAVAILABLE_EXCHANGE_AUDIT` when missing | Missing audit evidence fails closed. |
| Runtime proof | `UNAVAILABLE_RUNTIME_PROOF` when missing | Missing runtime proof fails closed. |
| Unguarded exchange mutation capability | `VIOLATION_EXCHANGE_MUTATION_ALLOWED` | Release-blocking if present. |
| Modeled evidence | `MODELED: none` | No modeled exchange mutation boundary evidence is used. |

## Safety boundary

Gate 5A-11 does not change runtime behavior, strategy logic, optimizer behavior, execution-cost modeling, performance calculation, PAPER runtime behavior, exchange behavior, or readiness status.

Gate 5A-11 does not fetch market data, connect to exchanges, request secrets, place exchange orders, cancel exchange orders, mutate exchange state, approve live trading, or approve production readiness.

Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.

## Validation commands

```bash
python -m compileall -q src tests main.py
pytest -q tests/test_exchange_mutation_boundary_evidence.py
pytest -q tests/test_evidence_ledger_consistency.py
pytest -q
ruff check .
black --check .
mypy .
```

Commands unavailable in an environment must be reported as UNAVAILABLE, not passed. Connector writes alone do not prove local or CI validation.
