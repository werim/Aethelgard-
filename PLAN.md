# Aethelgard Implementation Ledger

## Readiness boundary

- Operating mode: `PAPER_ONLY`.
- Operational classification: `RESEARCH_ONLY`.
- LIVE trading and real exchange orders remain prohibited.
- No alpha, profitability, execution realism, or operational-readiness claim is made.

## Gate 0 — Baseline reconciliation and ledger establishment

**Status:** `COMPLETE` for repository reconciliation only.

## Gate 1 — Read-only acquisition and immutable raw-data evidence boundary

**Status:** `MERGED_TO_DEV`.

**Merged baseline:** PR #1 merged into `dev` at merge commit `c6c163a0d21960ee08b0162bd9e41cf06ac9396b`.

## Gate 1.1 — Acquisition integrity repair and CI evidence hardening

**Status:** `MERGED_TO_DEV`.

**Merged baseline:** PR #2 merged into `dev` at merge commit `d09b7361a26f61d6cea7c0077d6d22a913548df0`.

### Scope

- Admit transient pre-response transport errors to the bounded retry policy and persist their diagnostics.
- Anchor metadata checksum identity in immutable checksum-addressed naming and provide restart discovery/readback validation.
- Add fail-closed tests for the two review findings and credential-free public transport behavior.

### Evidence classification

- `MEASURED`: GitHub Actions `validation` run #14 on corrected PR #2 head `e8caecc2aa545ea0bacdab79f28220ba21c14343` completed successfully before Gate 2A began.
- `UNAVAILABLE`: direct mutable local clone/working-tree evidence in this execution environment.

## Gate 2A — Append-only research decision audit trail

**Status:** `MERGED_TO_DEV`.

**Merged baseline:** PR #3 merged into `dev` at merge commit `5ce82c134656e206ce90c2b93585bb80222ebf71`.

### Scope

- Add local append-only JSON audit records for research-only `REJECTED` and `NO_ACTION` outcomes.
- Require every evidence item to be classified as `MEASURED`, `MODELED`, or `UNAVAILABLE`.
- Require unavailable evidence to carry a reason and no value/source reference.
- Persist checksum-addressed audit filenames plus durable `decision_id.claim` anchors.

### Evidence classification

- `MEASURED`: PR #3 final head `ed1641191d7d495ddab325e0ef54877fe64cf8d2` completed GitHub Actions `validation` run #28 successfully before merge.
- `UNAVAILABLE`: direct local clean working-tree evidence in this execution environment.

## Gate 2B — Database-backed persistence and audit events

**Status:** `MERGED_TO_DEV`.

**Merged baseline:** PR #4 merged into `dev` at merge commit `e37268fe21f5fa46c6e804f059df6a05c38f999f`.

### Scope

- Add the smallest local SQLite audit-event ledger for research-only persistence events.
- Persist canonical JSON payloads and SHA-256 payload checksums.
- Validate event identity, decision identity, UTC timestamps, `PAPER_ONLY`, `RESEARCH_ONLY`, and deterministic JSON payloads.
- Make identical append idempotent while rejecting conflicting event IDs and repeated decision/type pairs.

### Evidence classification

- `MEASURED`: PR #4 final head `8746bac98aaa08691c4a26b97f084b5bb9cd6359` completed GitHub Actions `validation` run #48 successfully before merge.
- `UNAVAILABLE`: direct local clean working-tree evidence in this execution environment.

## Gate 2C — Persistence integration review

**Status:** `MERGED_TO_DEV`.

**Merged baseline:** PR #5 merged into `dev` at merge commit `f085b1412d8670058b2e45a02b4590aa40145069`.

### Scope

- Add the smallest helper that appends a validated local decision audit file and a matching database audit event.
- Derive deterministic event identity from the decision identity and audit checksum.
- Record local provenance linking audit checksum, filenames, dataset checksum, artifact checksum, reason codes, outcome, and evidence classifications.
- Preflight existing database events before file append so conflicting decision/type events fail closed without writing another audit file.

### Evidence classification

- `MEASURED`: PR #5 final head `16dfe24c624742729fbab2303b8defbd7eb3a780` completed GitHub Actions `validation` run #51 successfully before merge.
- `UNAVAILABLE`: direct local clean working-tree evidence in this execution environment.

## Gate 2D — Persistence reconciliation scan

**Status:** `MERGED_TO_DEV`.

**Starting baseline:** `dev` merge commit `f085b1412d8670058b2e45a02b4590aa40145069` after Gate 2C merge.

**Merged baseline:** PR #6 merged into `dev` at merge commit `d05f013f0a38f8abe82bedc06a7e83adaecd67f4`.

### Scope

- Add the smallest read-only scanner that compares verified local decision audit files against verified SQLite audit events.
- Report missing database events, missing file audit records, and database event identity or payload mismatches.
- Add a fail-closed assertion helper for callers that require fully reconciled local persistence evidence.
- Do not repair, delete, rewrite, or promote evidence.

### Evidence classification

- `MEASURED`: PR #6 final head `68e6a89f788a2aa6fa5081e5116c8aa556478bd6` completed GitHub Actions `validation` run #56 successfully before merge.
- `UNAVAILABLE`: direct local clean working-tree evidence in this execution environment.

### Boundary limit

Gate 2D is a local reconciliation scan boundary only. It is not a repair tool, transaction manager, runtime event bus, strategy runtime, execution ledger, fill model, cost model, risk allocator, paper runtime, live path, or readiness certification.

## Gate 2E — Reconciliation report surface

**Status:** `IMPLEMENTED_IN_FOCUSED_BRANCH_PENDING_PR_VALIDATION`.

**Starting baseline:** `dev` merge commit `d05f013f0a38f8abe82bedc06a7e83adaecd67f4` after Gate 2D merge.

### Scope

- Add deterministic report helpers for reconciliation results.
- Export JSON-compatible payloads, compact JSON strings, and Markdown summaries.
- Report `CONSISTENT`, `INCONSISTENT`, and `UNAVAILABLE` explicitly.
- Include issue counts by mismatch type and sorted issue details.
- Do not repair evidence, add runtime behavior, add strategy behavior, or make readiness claims.

### Evidence classification

- `MEASURED`: PR #6 final head GitHub Actions `validation` run #56 passed before Gate 2E began.
- `UNVERIFIED`: exact Gate 2E branch-head GitHub Actions validation until the PR workflow runs.
- `UNAVAILABLE`: direct local compilation, full-suite tests, Ruff, Black, Mypy, and clean working-tree evidence in this execution environment.

### Boundary limit

Gate 2E is a local reporting surface only. It is not a report-file persistence layer, repair workflow, transaction manager, runtime event bus, strategy runtime, execution ledger, fill model, cost model, risk allocator, paper runtime, live path, or readiness certification.

## Gate 2F — Reconciliation report artifact persistence

**Status:** `BLOCKED_PENDING_GATE_2E_VALIDATION_REVIEW_AND_MERGE`.

Only after Gate 2E is validated, reviewed, and merged may the next run start from the then-current `dev` and add the smallest checksum/readback persistence layer for reconciliation report artifacts. Backtesting, strategies, risk, execution simulation, PAPER runtime, and any performance analysis remain blocked.
