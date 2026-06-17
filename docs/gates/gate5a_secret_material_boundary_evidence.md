# Gate 5A-12 Secret Material Boundary Evidence Adapter

Increment: Gate 5A-12 secret material boundary evidence adapter  
Scope: reporting-boundary adapter, focused regression coverage, and evidence-ledger documentation  
Operating mode: PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY

## Purpose

Gate 5A-12 hardens secret material boundary evidence classification so user statements, missing secret audits, placeholder-only references, runtime proof, and exposed credential violations cannot be conflated.

The adapter separates these classes:

- `MEASURED_NO_SECRET_MATERIAL`: source and test evidence show no secret material path.
- `MEASURED_SECRET_PLACEHOLDER_ONLY`: source, test, audit, and runtime evidence show only placeholders or environment references.
- `USER_REPORTED_SECRETS_NOT_SHARED`: user statements report that secrets were not shared; this is not measured proof.
- `UNAVAILABLE_SECRET_AUDIT`: secret material audit evidence is missing or incomplete.
- `UNAVAILABLE_RUNTIME_SECRET_PROOF`: runtime proof for placeholder/env-reference handling is missing or incomplete.
- `VIOLATION_SECRET_MATERIAL_EXPOSED`: secret material is requested, committed, or exposed through repository, documentation, or logs.

## Fail-closed rules

- Missing secret audit evidence remains `UNAVAILABLE_SECRET_AUDIT`.
- Missing runtime proof remains `UNAVAILABLE_RUNTIME_SECRET_PROOF`.
- User statements remain `USER_REPORTED_SECRETS_NOT_SHARED` and do not become measured proof.
- Placeholder-only or environment-reference secret handling is measured only when source, test, audit, and runtime proof are present.
- Any requested, committed, logged, or documented real secret material classifies as `VIOLATION_SECRET_MATERIAL_EXPOSED`.
- Secret-material evidence never permits live-readiness or production-readiness claims.

## Implemented surface

- `src/reporting/secret_material_boundary_evidence.py` defines the Gate 5A-12 secret material boundary classifications and deterministic classifier helper.
- `tests/test_secret_material_boundary_evidence.py` proves placeholder evidence does not imply live readiness, missing audit evidence stays unavailable, user reports stay user-reported, exposed or requested secret material is a violation, placeholder evidence requires runtime proof, and docs cannot claim secret safety without measured audit evidence.
- `docs/gates/gate5a_secret_material_boundary_evidence.md` records the evidence boundary and validation commands.

## Evidence classification

| Evidence | Classification | Note |
| --- | --- | --- |
| Local Gate 5A-12 source and tests | `MEASURED_LOCAL` | Source, tests, and docs were changed through the GitHub connector. |
| User statements about not sharing secrets | `USER_REPORTED_SECRETS_NOT_SHARED` | Recorded separately from measured source/test/audit/runtime proof. |
| Secret audit evidence | `UNAVAILABLE_SECRET_AUDIT` when missing | Missing audit evidence fails closed. |
| Runtime proof for placeholder/env references | `UNAVAILABLE_RUNTIME_SECRET_PROOF` when missing | Missing runtime proof fails closed. |
| Requested, committed, logged, or documented real secrets | `VIOLATION_SECRET_MATERIAL_EXPOSED` | Release-blocking if present. |
| Modeled evidence | `MODELED: none` | No modeled secret material boundary evidence is used. |

## Safety boundary

Gate 5A-12 does not change runtime behavior, strategy logic, optimizer behavior, execution-cost modeling, performance calculation, PAPER runtime behavior, exchange behavior, exchange mutation, or readiness status.

Gate 5A-12 does not fetch market data, connect to exchanges, request secrets, read environment variables, place exchange orders, cancel exchange orders, mutate exchange state, approve live trading, or approve production readiness.

Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.

## Validation commands

```bash
python -m compileall -q src tests main.py
pytest -q tests/test_secret_material_boundary_evidence.py
pytest -q tests/test_evidence_ledger_consistency.py
pytest -q
ruff check .
black --check .
mypy .
```

Commands unavailable in an environment must be reported as UNAVAILABLE, not passed. Connector writes alone do not prove local or CI validation.
