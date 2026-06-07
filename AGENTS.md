# AGENTS.md — Project Aethelgard Engineering Constitution

## Mission

Aethelgard is a modular Binance Futures market-structure research and PAPER-trading engine.
Build it incrementally as a truthfulness-first research platform focused on robustness,
auditability, reproducibility, execution realism, and capital preservation.

This repository is not a profit promise and not a live trading system.

## Non-negotiable safety boundary

- Default and permitted operational mode is `PAPER_ONLY` / `RESEARCH_ONLY` unless a future, separately reviewed governance change states otherwise.
- Never enable LIVE trading.
- Never create code paths that submit real exchange orders.
- Never store or expose credentials, tokens, API secrets, or private data.
- Never fabricate alpha, profitability, fills, readiness, validation, costs, or market evidence.
- Unknown execution costs are not zero; record them as unavailable or modeled assumptions.
- Missing, stale, corrupt, contradictory, or unverifiable critical evidence must fail closed.

## Branch and task discipline

- Start every implementation task from the current remote `dev` branch.
- Refresh repository state before any edit.
- Inspect active pull requests affecting `dev` and avoid duplicate work.
- Do not assume the repository is still at a prior milestone. Establish the actual baseline first.
- Implement exactly one smallest coherent next increment per task.
- Do not broaden scope, begin later subsystems early, or refactor unrelated stable code.
- Use a feature branch for each increment and target `dev` with one focused PR.
- Never merge automatically unless the human repository owner explicitly enables that policy after reviewing the safety implications.

## Required starting inspection for every run

Before modifying code, read and reconcile:

1. `REPORT.md`
2. `VERSION.md`
3. `CHANGELOG.md`
4. `PLAN.md`, if present
5. the master governance document, if present
6. `README.md`
7. root project/tooling configuration
8. workflows/CI definitions
9. the relevant `src/`, `tests/`, `config/`, `reports/`, and `data/` boundaries
10. open PRs, branch/head status, and visible CI status for the starting `dev` commit

Record in the task summary:

- repository URL
- starting branch
- starting commit SHA
- working tree status
- open PRs relevant to `dev`
- visible CI/workflow status
- authoritative milestone discovered from repository documentation
- the single chosen next increment and why it is the smallest safe step

If repository access, branch access, required-file access, write access, or test execution is unavailable, stop implementation and report the blocker truthfully.

## Architecture boundaries

Maintain separated responsibilities:

- `src/data`
- `src/features`
- `src/strategies`
- `src/risk`
- `src/execution`
- `src/backtest`
- `src/persistence`
- `src/reporting`
- `tests`
- `config`
- `reports`
- `data`

Do not collapse unrelated responsibilities into one file or create speculative abstractions.

## Ordered delivery roadmap

Use the repository's current state as source of truth. Subject to already-completed work, progress only in this order:

1. Foundation and safe configuration
2. Logging and CI
3. Validated historical data ingestion boundary
4. Read-only historical acquisition, provenance, freshness rejection, and immutable artifact storage
5. Persistence and audit trail
6. Backtesting framework
7. Execution realism model
8. Conservative baseline strategy
9. Risk systems and circuit breaker
10. Reporting and diagnostics
11. Sentiment/risk filter only after the preceding evidence chain is working

Later stages must not be implemented merely because they are interesting. A later-stage dependency may only be scaffolded when narrowly required for the current coherent increment, with no readiness claims.

## Data rules

Historical market-data work must validate and test as applicable:

- timestamp format, ordering, interval alignment, duplicates, and gaps
- malformed/non-finite/negative numeric fields and OHLC consistency
- request selectors and timeframe/interval consistency
- provenance and fetch metadata
- deterministic hashes and immutable local artifact readback
- stale-data rejection
- pagination boundaries, retry behavior, rate-limit handling, and deterministic acquisition behavior
- explicit treatment of unsupported intervals, unavailable external completeness, and exchange/API uncertainty

Never claim exchange authenticity or completeness unless evidence directly establishes it.

## Backtest and execution realism rules

When those phases are reached, simulated results must explicitly model or mark unavailable:

- fees
- spread
- slippage
- latency assumptions
- funding costs where available
- rejection/non-fill behavior and lifecycle evidence

No cost field may silently default to zero when evidence is missing.

## Strategy and validation rules

Initial strategies must be conservative and explainable.

Do not introduce deep learning, aggressive optimization, broad hyperparameter sweeps, validation/test leakage, or metrics presented as trading readiness.

Require, when the strategy stage is reached:

- train/validation/test separation
- walk-forward validation
- deterministic seeds and run metadata
- probabilistic output with uncertainty awareness
- truthful performance diagnostics after modeled execution costs

## Risk rules

When risk implementation is the next justified phase, implement and test:

- capped fractional Kelly sizing
- volatility targeting
- exposure caps
- concentration limits
- drawdown controls
- regime handling
- circuit breakers

Required daily drawdown circuit breaker:

- if daily drawdown exceeds 3%, close PAPER positions and halt new PAPER entries for 24 hours
- preserve reconstructable evidence of trigger, actions, and halt period

## Required validation after each meaningful increment

Run all relevant checks already configured by the repository. At minimum, attempt:

```bash
python -m compileall -q src tests main.py
pytest -q
ruff check .
black --check .
mypy .
```

Do not claim a check passed unless its output was observed for the changed commit or workspace.
If a check cannot run, classify it as `UNVERIFIED` and explain why.
If a required test or safety check fails, fix within current scope or stop with the failure clearly reported.

## Required documentation after each implemented increment

Update in the same PR:

- `VERSION.md`
- `CHANGELOG.md`
- `REPORT.md`

Documentation must distinguish:

- measured evidence
- modeled/simulated estimates
- unavailable or unverified evidence
- remaining blockers
- what cannot yet be proven

No readiness level may be upgraded without supporting evidence.

## Commit and pull request rules

Each implementation task should produce one coherent branch and focused PR to `dev`.

PR description must include:

- starting baseline and chosen increment
- changed files and architectural boundary
- validation commands actually executed and exact results
- evidence classification
- safety boundary confirmation: PAPER-only and no real orders
- remaining risks and blocked claims
- next recommended smallest increment

Do not mix unrelated fixes or future roadmap implementation into the same PR.

## Review guidelines

Treat the following as release-blocking findings:

- any path capable of live order submission
- weakened PAPER-only protection
- silent zero-cost assumptions
- missing stale-data/reproducibility controls in implemented data boundaries
- claims unsupported by executed tests or persisted evidence
- validation leakage or test/validation optimization
- undocumented changes to risk or readiness classification
- secrets or credential exposure

## Current known baseline note

As of the repository documentation inspected on 2026-05-27, `dev` documented version `0.2.0`,
with Phase 2 validated supplied historical-kline ingestion and the next recommended bounded
increment described as read-only Binance Futures historical kline acquisition with deterministic
pagination, retry/rate-limit handling, stale-data checks, validated request/provenance consistency,
and immutable local artifact plus metadata/checksum persistence.

This note is context only. Every Codex task must re-read the repository and may not assume it is still current.
