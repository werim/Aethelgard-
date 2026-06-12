# PROJECT_STATE.md

## Project Name
Aethelgard / AlphaForge

## Current Mode
BACKTEST / PAPER only

## Live Status
NOT READY

## Operational Classification
RESEARCH_ONLY

## Evidence Classification

### MEASURED / VERIFIED FROM PROVIDED PROJECT FILES
- Governance requires PAPER ONLY as default operating mode.
- Live trading, real exchange order placement, secret exposure, fabricated profitability, and production readiness approval are explicitly forbidden.
- Unknown execution costs must not be treated as zero.
- Missing data must remain explicitly unavailable.
- Backtest performance alone must not prove production readiness.
- Required modular structure is defined:
  - src/data
  - src/features
  - src/strategies
  - src/risk
  - src/execution
  - src/backtest
  - src/persistence
  - src/reporting
  - tests
  - config
  - reports
  - data
- Gate Tracker currently marks Gates 1 through 8 as Unknown.
- Current PROJECT_STATE says the last completed phase is not yet specified.

### MODELED / ASSUMED
- Based on the continuous implementation prompt, the latest audited baseline to verify is dev / version 0.2.0 / RESEARCH_ONLY.
- The next expected missing implementation after baseline reconciliation is Gate 1: data acquisition and immutable data-evidence boundary.
- The repository may already contain newer work, but that cannot be assumed without repo inspection.

### UNAVAILABLE / NOT VERIFIED
- Actual repository branch and HEAD.
- Existence and contents of REPORT.md, VERSION.md, CHANGELOG.md, PLAN.md in the live repo.
- Current source tree under src/, tests/, config/, reports/, data/.
- Current CI status.
- Current test/lint/type-check results.
- Whether any Gate 1 or later implementation has already been merged.
- Whether stale-data guard, provenance verification, selector consistency, immutable raw-data persistence, persistence/audit trail, execution realism, strategy, risk, backtest, reporting, or paper runtime are implemented.


## Branch Verification Policy
search_branches MUST NOT be treated as source-of-truth evidence for branch existence or branch contents. It is only a weak discovery signal.

Strong branch evidence must use one or more of the following, preferably in this order:
1. Direct ref lookup, for example `git rev-parse --verify origin/dev` or equivalent GitHub ref API lookup for `refs/heads/dev`.
2. Direct file fetch by explicit ref, for example fetching `VERSION.md`, `REPORT.md`, `CHANGELOG.md`, or `PLAN.md` from `dev` and recording the resolved commit/ref evidence.
3. `git ls-remote --heads origin dev` or equivalent remote ref listing.

If these stronger checks disagree with search discovery, the stronger checks win. If none of the stronger checks can be performed, branch status remains UNAVAILABLE rather than assumed.

## Current Verified Situation
This is a governance and audit-planning state, not an implementation-complete state. The project must remain PAPER ONLY and RESEARCH_ONLY until repository inspection, tests, documentation, and audit evidence prove a narrower PAPER-specific upgrade.

## Critical Gaps
1. Repository state is not verified.
2. Gate statuses are Unknown.
3. No verified dev branch HEAD is available.
4. No verified exact test, lint, type-check, or CI evidence is available.
5. No confirmed PLAN.md ledger state is available.
6. No confirmed stale-data rejection evidence is available.
7. No confirmed independent provenance verification is available.
8. No confirmed timeframe/interval selector consistency enforcement is available.
9. No confirmed immutable raw artifact persistence and checksum readback is available.
10. No confirmed execution-cost evidence gate is available.
11. No confirmed persistence/audit trail is available.
12. No confirmed risk system, circuit breaker, or bypass prevention is available.
13. No confirmed paper runtime lifecycle integrity or duplicate decision detection is available.

## Live-Blocking Risks
- Live order paths must remain disabled or absent.
- Any trading credentials or order endpoints must not be requested, stored, imported, invoked, or tested.
- Unknown fees, slippage, spread, funding, or latency cannot be treated as zero.
- Performance metrics must not be generated without cost evidence classification.
- Missing/stale/inconsistent data must fail closed.
- Backtest-only evidence must not be used as runtime or production readiness evidence.
- Risk controls and audit logging must not be bypassable.
- No readiness upgrade is allowed without repository and validation evidence.

## Selected Smallest Safe Next Phase
Gate 0 — Baseline Reconciliation and PLAN Ledger.

This is the safest next phase because the current codebase, dev HEAD, docs, tests, and CI are unavailable in this environment. Gate 1 must not begin until Gate 0 records the actual baseline and avoids duplicating or overwriting newer implementation.

## Gate 0 Scope
- Inspect current dev branch and HEAD.
- Read REPORT.md, VERSION.md, CHANGELOG.md, and PLAN.md if present.
- Inspect required folders and test layout.
- Identify implemented vs missing gates.
- Update or create PLAN.md as the living implementation ledger.
- Update REPORT.md only with verified evidence.
- Keep VERSION.md unchanged unless repository convention allows audit-only updates.
- Do not claim implementation completion.
- Do not upgrade readiness.

## Gate 0 Acceptance Criteria
- Branch and HEAD recorded.
- Relevant docs read and summarized.
- Source/test/config/report/data structure inspected.
- Current gate matrix updated with evidence status.
- Commands run and results recorded.
- Unavailable evidence explicitly listed.
- No live trading or order placement path enabled.
- Documentation-only atomic commit made if repo write access is available.

## Next Implementation Plan After Gate 0 Passes
Gate 1 — Data Acquisition and Immutable Data-Evidence Boundary.

Minimum implementation target:
- Public/read-only Binance Futures historical klines only.
- Initial selectors: BTCUSDT, ETHUSDT, 1h, at least two years where available.
- Deterministic pagination.
- Timeout, retry, and rate-limit handling.
- Source allowlisting.
- Selector consistency checks.
- Incomplete fetch failure behavior.
- UTC fetch metadata.
- Immutable or append-only raw artifact storage.
- Cryptographic checksum and deterministic readback verification.
- No secrets and no order endpoints.

## Required Gate 1 Tests
- Successful deterministic fixture acquisition.
- Pagination ordering.
- Duplicate candle detection.
- Missing candle detection.
- Stale timestamp failure.
- Unsupported source failure.
- Selector mismatch failure.
- Timeframe/interval mismatch failure.
- Timeout/retry/rate-limit behavior.
- Incomplete pagination failure.
- Raw artifact checksum/readback/tamper detection.
- Confirmation that no execution/order path is imported or invoked.

## Required Documentation Updates
- PLAN.md: baseline, phase ledger, acceptance gates, commands, outcomes, blockers, next phase.
- REPORT.md: implemented capability, measured evidence, modeled assumptions, unavailable evidence, failed checks, unresolved risks, operational classification.
- CHANGELOG.md: only after behavioral increment passes.
- VERSION.md: only after meaningful validated implementation, not for failed or unverified attempts unless repo convention says otherwise.

## Status
Blocked from implementation verification in this environment because live repository state, branch, HEAD, test results, lint/type checks, and CI evidence are unavailable.
