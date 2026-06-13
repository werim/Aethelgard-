# Gate 5A Operational Evidence Gate / Deployment Blocker Matrix

Gate: Gate 5A operational evidence and deployment-blocker diagnostics
Scope: reporting-boundary and focused regression coverage
Runtime behavior changed: no exchange mutation, no order path, no strategy logic
Operating mode: PAPER_ONLY / RESEARCH_ONLY
Readiness classification: NOT_LIVE_READY

## Purpose

Gate 5A adds a deterministic deployment-blocker matrix for PAPER operational
evidence. The matrix records whether required blocker categories have measured
evidence before a PAPER operational deployment claim can be considered.

This gate does not approve production readiness. It does not approve LIVE
readiness. It does not compute performance metrics, model missing costs,
generate alpha, run strategies, submit orders, mutate exchange state, or infer
that backtest results are operationally safe.

## Required blocker categories

| Blocker | Required evidence | Clearing rule |
| --- | --- | --- |
| `audit_trail_integrity` | append-only audit trail integrity evidence | `MEASURED` only |
| `ci_validation` | exact branch-head CI or local validation evidence | `MEASURED` only |
| `data_freshness` | freshness and selector-consistency evidence | `MEASURED` only |
| `execution_cost_evidence` | fees, spread, slippage, funding, and latency evidence | `MEASURED` only |
| `paper_runtime_reconciliation` | PAPER runtime lifecycle reconciliation evidence | `MEASURED` only |
| `risk_control_enforcement` | risk controls and circuit-breaker enforcement evidence | `MEASURED` only |

Any missing, `MODELED`, or `UNAVAILABLE` evidence leaves the blocker in
`BLOCKED` status. Unknown execution costs are not zero. Missing evidence remains
unavailable.

## Implemented surface

- `src/reporting/operational_evidence.py`
- `tests/test_operational_evidence_gate.py`
- `src.reporting` public exports for Gate 5A diagnostic helpers

## Validation commands

```bash
python -m compileall -q src tests main.py
pytest -q tests/test_operational_evidence_gate.py
pytest -q tests/test_public_exports.py
pytest -q tests/test_gate4_public_safety_exports.py
pytest -q
ruff check .
black --check .
mypy .
```

Commands not directly run in an environment must be reported as `UNAVAILABLE`,
not passed. Connector writes alone do not prove local or CI validation.

## Safety conclusion

Gate 5A is a fail-closed operational evidence reporting boundary. It can report
that PAPER deployment diagnostics are blocked or not blocked by the supplied
measured evidence matrix, but it does not certify live trading, production
readiness, profitability, execution realism, strategy performance, or risk
survivability.
