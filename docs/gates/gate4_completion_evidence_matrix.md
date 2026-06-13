# Gate 4 Completion Evidence Matrix

Gate: Gate 4 execution realism and reporting safety
Target: Gate 4CLOSE-1 / Gate 4CLOSE-1A / Gate 4CLOSE-1C
Scope: test/documentation-only evidence closure
Runtime behavior changed: no
Operating mode: PAPER_ONLY / RESEARCH_ONLY
Live status: NOT_LIVE_READY

## Safety position

This matrix does not approve operational readiness. Unknown execution costs
are not zero. Missing cost evidence remains explicitly UNAVAILABLE. Backtest
performance alone does not prove production readiness. Gate 4CLOSE-1A narrows
the public-export claim to the evidence actually covered by the safe public
export tests: unsafe live/order/runtime names are rejected from checked public
package surfaces. Broader export classes are not claimed by this matrix unless
a focused safe test exists for them. Gate 4CLOSE-1C canonicalizes the
validation command ledger across this matrix, `REPORT.md`, and
`PROJECT_STATE.md`.

## Evidence matrix

| Boundary | Source evidence | Test evidence | Safety text | Public export check | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Fee modeling boundary | `src/backtest/cost_evidence.py` defines `CostEvidenceCategory.FEES` and validates evidence records. | `tests/test_cost_evidence.py` covers missing required fees and measured/modelled evidence. | This document and `REPORT.md`. | No direct live/order/readiness export required. | PROVEN | Evidence classification only; no fee model is computed here. |
| Slippage modeling boundary | `src/backtest/cost_evidence.py` defines `CostEvidenceCategory.SLIPPAGE`. | `tests/test_cost_evidence.py` blocks net metrics when slippage is unavailable. | This document and `REPORT.md`. | No direct live/order/readiness export required. | PROVEN | Evidence classification only; no slippage model is computed here. |
| Spread modeling boundary | `src/backtest/cost_evidence.py` defines `CostEvidenceCategory.SPREAD`. | `tests/test_cost_evidence.py` checks unavailable spread reporting. | This document and `REPORT.md`. | No direct live/order/readiness export required. | PROVEN | Evidence classification only; no spread model is computed here. |
| Funding or carry cost boundary | `src/backtest/cost_evidence.py` defines `CostEvidenceCategory.FUNDING`. | `tests/test_cost_evidence.py` blocks when funding evidence is required and missing. | This document and `REPORT.md`. | No direct live/order/readiness export required. | PROVEN | Funding remains evidence-gated, not assumed away. |
| Latency or fill realism boundary | `src/backtest/cost_evidence.py` defines `CostEvidenceCategory.LATENCY`; `src/backtest/lifecycle.py` defines conservative lifecycle observations. | `tests/test_cost_evidence.py` blocks latency gaps; `tests/test_backtest_lifecycle.py` checks fail-closed lifecycle transitions. | This document and `REPORT.md`. | No direct live/order/readiness export required. | PROVEN | Lifecycle is caller-observation based, not an order-management path. |
| Unknown costs are not zero | `CostEvidenceRecord.validate()` rejects UNAVAILABLE records with values or units. | `tests/test_cost_evidence.py::test_unavailable_evidence_is_not_treated_as_zero`. | This document, `PLAN.md`, `REPORT.md`, and `PROJECT_STATE.md`. | No zero-cost helper is exported as a public readiness path. | PROVEN | Unknown costs remain unavailable. |
| Missing cost evidence remains unavailable | `evaluate_cost_evidence_gate()` records missing categories as UNAVAILABLE and blocking. | `tests/test_cost_evidence.py::test_no_cost_evidence_fails_closed`. | This document, `PLAN.md`, `REPORT.md`, and `PROJECT_STATE.md`. | No default-cost public export is approved. | PROVEN | Missing evidence must be reported, not guessed. |
| Backtest metrics do not prove readiness | `CostEvidenceGateResult.readiness_allowed` is always false in the cost gate. | `tests/test_cost_evidence.py::test_readiness_approval_remains_blocked_with_unavailable_costs`. | This document and `REPORT.md`. | `tests/test_public_exports.py` rejects direct readiness exports. | PROVEN | Backtest evidence remains research-only. |
| PAPER-only safety text exists | `PLAN.md`, `REPORT.md`, and `PROJECT_STATE.md` state PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY. | `tests/test_gate4_completion_evidence_matrix.py` guards the required safety wording. | This document and current ledgers. | Public export checks remain documentation/test-only. | PROVEN | No runtime code is changed by Gate 4CLOSE-1. |
| No unsafe public exports | `src/backtest/__init__.py`, `src/execution/__init__.py`, `src/data/__init__.py`, and `src/reporting/__init__.py` are the checked public surfaces. | `tests/test_public_exports.py` and `tests/test_gate4_public_safety_exports.py`. | This document and `REPORT.md`. | Unsafe live/order/runtime names are rejected. | PROVEN | Export safety is proven only for checked public package surfaces and listed unsafe live/order/runtime names. |

## Validation commands

```bash
python -m compileall -q src tests main.py
pytest -q tests/test_validation_command_ledger_consistency.py
pytest -q tests/test_gate4_completion_evidence_matrix.py
pytest -q tests/test_gate4_public_safety_exports.py
pytest -q tests/test_cost_evidence.py
pytest -q tests/test_public_exports.py
pytest -q
ruff check .
black --check .
mypy .
```

Commands unavailable in an environment must be reported as UNAVAILABLE, not
passed. Connector writes alone do not prove local or CI validation.

## Gate 4CLOSE-1C conclusion

Gate 4CLOSE-1C is documentation and focused regression coverage only. It keeps
the validation command surface canonical across this matrix, `REPORT.md`, and
`PROJECT_STATE.md`. It does not compute performance, model new costs, add
strategy logic, add optimizer behavior, expand PAPER runtime behavior, or
approve readiness.
