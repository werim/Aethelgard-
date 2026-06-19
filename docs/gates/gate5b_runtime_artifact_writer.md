# Gate 5B-3 — Offline Runtime Output Artifact Writer

## Scope

Gate 5B-3 adds a local, offline runtime evidence artifact writer. It accepts caller-supplied startup/runtime metadata and writes deterministic JSON under `reports/` only. Generated runtime evidence artifacts are local audit evidence, not production approval.

Changed implementation/test files:

- `src/reporting/runtime_artifact_writer.py`
- `tests/test_runtime_artifact_writer.py`
- `src/reporting/__init__.py`

## Artifact boundary

The writer:

- writes sorted-key JSON with a newline at EOF;
- creates local parent directories under `reports/` when needed;
- rejects absolute paths, parent traversal, non-JSON paths, and paths outside `reports/`;
- records `PAPER_ONLY`, `RESEARCH_ONLY`, deterministic seed metadata, safety-boundary flags, evidence classification, and unavailable-evidence fields;
- rejects secret-like, alpha, optimizer, PnL, win-rate, Sharpe, drawdown, returns, profitability, live-readiness, and production-readiness inputs.

## Evidence classifications admitted

- `MEASURED_PAPER_DRY_RUN` only when the caller supplies measured local evidence from a safe dry run.
- `USER_PROVIDED_RUNTIME_OUTPUT` when runtime evidence came from pasted/user-provided output.
- `UNAVAILABLE_DRY_RUN` when dry-run evidence is missing.
- `UNAVAILABLE_DRY_RUN_LOG` when dry-run log evidence is missing.

## Explicitly unavailable evidence

Artifacts record CI workflow artifacts, exchange audit, market-data completeness, execution realism, profitability, live readiness, and production readiness as `UNAVAILABLE`. Missing evidence remains unavailable. Unknown execution costs are not zero. Backtest performance alone does not prove production readiness.

## Safety boundary

Gate 5B-3 is a local offline artifact-writing boundary only. It does not add runtime trading behavior, fetch market data, connect to exchanges, read or write secrets, place or cancel orders, simulate real exchange orders, add strategy alpha, run optimizers, calculate or publish performance, validate strategy, validate profitability, validate data completeness, validate execution realism, prove exchange safety, approve runtime readiness, approve live readiness, or approve production readiness. Aethelgard remains PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY.

## Gate 5B-4 schema ledger consistency

Gate 5B-4 is a ledger consistency check only. It keeps generated local runtime-artifact schema documentation aligned with `src/reporting/runtime_artifact_writer.py` and `tests/test_runtime_artifact_writer.py`; it does not add a CLI wrapper or change `python main.py` behavior. The optional CLI wrapper is intentionally deferred because the smallest safe step was ledger consistency only.

### Documented runtime artifact schema

Top-level required fields:

- `schema_version`
- `source`
- `mode`
- `readiness`
- `project_name`
- `random_seed`
- `determinism_scope`
- `safety_boundary`
- `evidence_classification`
- `unavailable_evidence`

Required `safety_boundary` fields:

- `paper_only`
- `research_only`
- `live_trading_enabled`
- `secrets_requested`
- `secrets_exposed`
- `exchange_connection`
- `market_fetch`
- `order_path`
- `strategy_alpha`
- `optimizer`
- `performance_claim`
- `readiness_approval`

Required `unavailable_evidence` fields:

- `ci_workflow_artifacts`
- `exchange_audit`
- `market_data_completeness`
- `execution_realism`
- `profitability`
- `live_readiness`
- `production_readiness`

Local runtime artifacts are evidence artifacts, not production approval. Runtime artifact schema documentation must not imply live readiness. Missing evidence remains UNAVAILABLE. Unknown execution costs are not zero. Backtest performance alone does not prove production readiness. No secrets, exchange connection, market fetch, order path, optimizer, strategy alpha, performance claim, or readiness approval is added.
