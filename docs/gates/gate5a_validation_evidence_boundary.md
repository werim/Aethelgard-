# Gate 5A-9 CI/Validation Evidence Boundary Adapter

Increment: Gate 5A-9 CI/validation evidence boundary adapter
Scope: reporting-boundary adapter, focused regression coverage, and evidence-ledger documentation
Operating mode: PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY

## Purpose

Gate 5A-9 hardens the validation evidence boundary so CI, local validation, and user-reported validation evidence cannot be conflated.

The adapter separates four provenance classes:

- `MEASURED_LOCAL`: validation command evidence directly observed in the local workspace.
- `USER_REPORTED`: user statements or screenshots. This remains separate from measured local evidence and connector-visible CI.
- `CONNECTOR_VISIBLE_CI`: workflow/status evidence directly visible through a connector and tied to the requested commit.
- `UNAVAILABLE`: missing, empty, contradictory, malformed, or unverifiable validation evidence.

## Fail-closed rules

- No workflow runs means `UNAVAILABLE`.
- Empty combined status means `UNAVAILABLE`.
- Empty status contexts mean `UNAVAILABLE`.
- User screenshots or user statements remain `USER_REPORTED` and do not clear the Gate 5A `ci_validation` blocker as measured evidence.
- Unavailable connector-visible CI is never promoted to measured validation.
- Local validation evidence can be `MEASURED_LOCAL` only when a concrete command, zero exit code, output excerpt, and source are supplied.

## Implemented surface

- `src/reporting/ci_evidence.py` defines the Gate 5A-9 boundary classifications and deterministic classifier helpers.
- `tests/test_validation_evidence_boundary.py` proves missing workflow runs, empty combined statuses, and user-reported validation evidence fail closed instead of becoming green CI evidence.
- `tests/test_evidence_ledger_consistency.py` guards that docs and reports cannot claim connector-visible CI evidence while connector-visible CI remains unavailable.

## Evidence classification

| Evidence | Classification | Note |
| --- | --- | --- |
| Local Gate 5A-9 source and tests | `MEASURED_LOCAL` | Source and tests were edited and run in this workspace. |
| User screenshots or statements | `USER_REPORTED` | Recorded separately from measured local evidence and connector-visible CI. |
| Connector-visible CI for this workspace commit | `UNAVAILABLE` | No connector-visible workflow run or combined-status evidence was available in this environment. |
| Modeled validation evidence | `MODELED: none` | No modeled validation outcome is used. |

## Safety boundary

Gate 5A-9 does not change runtime behavior, strategy logic, optimizer behavior, execution-cost modeling, performance calculation, PAPER runtime behavior, exchange mutation, exchange behavior, or readiness status.

Gate 5A-9 does not fetch market data, connect to exchanges, request secrets, mutate workflows, download private artifacts, or place exchange orders.

Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.

## Validation commands

```bash
python -m compileall -q src tests main.py
pytest -q tests/test_validation_evidence_boundary.py
pytest -q tests/test_ci_evidence.py
pytest -q tests/test_evidence_ledger_consistency.py
pytest -q
ruff check .
black --check .
mypy .
```

Commands unavailable in an environment must be reported as UNAVAILABLE, not passed. Connector writes alone do not prove local or CI validation.
