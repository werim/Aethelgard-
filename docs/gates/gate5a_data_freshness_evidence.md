# Gate 5A-6 Data-Freshness Evidence Adapter

## Classification

- Operating mode: `PAPER_ONLY / RESEARCH_ONLY`
- Readiness: `NOT_LIVE_READY`
- Evidence class target: Gate 5A `data_freshness`

## Purpose

Gate 5A-6 adds a deterministic adapter for caller-supplied data freshness and selector-consistency evidence. The adapter converts a validated evidence bundle into a Gate 5A `data_freshness` evidence item.

It does not fetch market data, connect to Binance, place exchange orders, mutate exchange state, compute performance, model costs, expand PAPER runtime behavior, change strategy logic, or approve readiness.

## Required caller-supplied evidence

Measured data-freshness evidence requires all of the following:

- source evidence text
- canonical dataset id
- canonical expected selector id
- canonical observed selector id
- expected selector id matching observed selector id
- canonical latest closed bar timestamp text
- non-negative observed age seconds
- positive max age seconds
- observed age seconds less than or equal to max age seconds

Missing, stale, malformed, or selector-mismatched evidence remains `UNAVAILABLE`.

## Gate 5A integration

The adapter emits an `OperationalEvidenceItem` with blocker id `data_freshness`.

- `MEASURED` evidence can clear only the `data_freshness` blocker row.
- `UNAVAILABLE` evidence keeps the `data_freshness` blocker row blocked.
- All other Gate 5A blocker rows still require their own measured evidence.

## Validation commands

```bash
python -m compileall -q src tests main.py
pytest -q tests/test_data_freshness_evidence.py
pytest -q tests/test_public_exports.py
pytest -q tests/test_evidence_ledger_consistency.py
pytest -q tests/test_validation_command_ledger_consistency.py
pytest -q
ruff check .
black --check .
mypy .
```

Commands not directly run in this execution environment remain `UNAVAILABLE` here. Connector writes alone do not prove local or CI validation.

## Safety boundary

Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.

Gate 5A-6 is an evidence adapter only. It does not change runtime behavior, strategy logic, optimizer behavior, execution-cost modeling, performance calculation, PAPER runtime behavior, exchange mutation, exchange behavior, or readiness status.
