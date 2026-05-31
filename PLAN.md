# Aethelgard Implementation Ledger

## Readiness boundary

- Operating mode: `PAPER_ONLY`.
- Operational classification: `RESEARCH_ONLY`.
- LIVE trading and real exchange orders remain prohibited.
- No alpha, profitability, execution realism, or operational-readiness claim is made.

## Gate 0 — Baseline reconciliation and ledger establishment

**Status:** `COMPLETE` for repository reconciliation only.

## Gate 1 — Read-only acquisition and immutable raw-data evidence boundary

**Merged baseline:** PR #1 merged into `dev` at merge commit `c6c163a0d21960ee08b0162bd9e41cf06ac9396b`.

**Measured merge-path evidence:** Corrected PR head `cd7c1e642525da7fc4d47c614b03c9f5e541501d` completed GitHub Actions `validation` run #10 successfully before merge.

**Post-merge findings:** Review identified two integrity gaps that required repair before Gate 2:

1. pre-response transient network failures bypassed the declared bounded retry policy;
2. metadata checksum identity could not be independently recovered after process restart.

## Gate 1.1 — Acquisition integrity repair and CI evidence hardening

**Status:** `MERGED_TO_DEV`.

**Merged baseline:** PR #2 merged into `dev` at merge commit `d09b7361a26f61d6cea7c0077d6d22a913548df0`.

### Scope

- Admit transient pre-response transport errors to the bounded retry policy and persist their diagnostics.
- Anchor metadata checksum identity in immutable checksum-addressed naming and provide restart discovery/readback validation.
- Add fail-closed tests for the two review findings and GET-only, credential-free transport behavior.
- Expand CI to Python 3.11/3.12 compile-and-test validation with JUnit artifacts; keep lint/format/type gates on Python 3.11.

### Evidence classification

- `MEASURED`: reconstructed targeted candidate execution of compilation and acquisition tests (`17 passed`).
- `MEASURED`: GitHub Actions `validation` run #14 on corrected PR #2 head `e8caecc2aa545ea0bacdab79f28220ba21c14343` completed successfully before Gate 2A began.
- `UNAVAILABLE`: direct mutable local clone/working-tree evidence in the Gate 2A execution environment because direct local git operations were unavailable.

### Boundary limit

Checksum-addressed local metadata discovery verifies ordinary persisted-byte consistency. It is not an external signature against an attacker able to replace and rename the full local artifact set.

## Gate 2A — Append-only research decision audit trail

**Status:** `MERGED_TO_DEV`.

**Starting baseline:** `dev` merge commit `d09b7361a26f61d6cea7c0077d6d22a913548df0` after Gate 1.1 merge.

**Merged baseline:** PR #3 merged into `dev` at merge commit `5ce82c134656e206ce90c2b93585bb80222ebf71`.

### Scope

- Add local append-only JSON audit records for research-only `REJECTED` and `NO_ACTION` outcomes.
- Require every evidence item to be classified as `MEASURED`, `MODELED`, or `UNAVAILABLE`.
- Require unavailable evidence to carry a reason and no value/source reference, preserving the rule that unknown execution costs are not zero.
- Persist checksum-addressed audit filenames plus durable `decision_id.claim` anchors so conflicting records for the same decision identity fail closed.
- Verify audit readback against payload checksum, filename checksum, claim checksum, UTC timestamp, PAPER-only mode, and evidence provenance.

### Evidence classification

- `MEASURED`: targeted reconstructed local validation before branch publication passed `python -m compileall -q src tests` and `python -m pytest -q tests/test_audit.py` for the initial audit test set (`7 passed`).
- `MEASURED`: PR #3 final head `ed1641191d7d495ddab325e0ef54877fe64cf8d2` completed GitHub Actions `validation` run #28 successfully before merge.
- `UNAVAILABLE`: direct local clean working-tree evidence in this execution environment.

### Boundary limit

Gate 2A is a local file evidence boundary only. It is not a database transaction log, runtime event pipeline, strategy, backtest, risk system, execution-cost model, paper runtime, or readiness certification.

## Gate 2B — Database-backed persistence and audit events

**Status:** `MERGED_TO_DEV`.

**Starting baseline:** `dev` merge commit `5ce82c134656e206ce90c2b93585bb80222ebf71` after Gate 2A merge.

**Merged baseline:** PR #4 merged into `dev` at merge commit `e37268fe21f5fa46c6e804f059df6a05c38f999f`.

### Scope

- Add the smallest local SQLite audit-event ledger for research-only persistence events.
- Persist canonical JSON payloads and SHA-256 payload checksums.
- Validate event identity, decision identity, UTC timestamps, `PAPER_ONLY`, `RESEARCH_ONLY`, and deterministic JSON payloads.
- Make identical append idempotent while rejecting conflicting event IDs and repeated decision/type pairs.
- Add fail-closed tests for schema initialization, readback, idempotency, conflict rejection, checksum tampering, UTC/mode safety, and JSON determinism.

### Evidence classification

- `MEASURED`: PR #3 final head GitHub Actions `validation` run #28 passed before Gate 2B began.
- `MEASURED`: PR #4 final head `8746bac98aaa08691c4a26b97f084b5bb9cd6359` completed GitHub Actions `validation` run #48 successfully before merge.
- `UNAVAILABLE`: direct local clean working-tree evidence in this execution environment.

### Boundary limit

Gate 2B is a local database persistence boundary only. It is not a strategy runtime, execution ledger, fill model, cost model, risk allocator, reporting system, paper runtime, live path, or readiness certification.

## Gate 2C — Persistence integration review

**Status:** `MERGED_TO_DEV`.

**Starting baseline:** `dev` merge commit `e37268fe21f5fa46c6e804f059df6a05c38f999f` after Gate 2B merge.

**Merged baseline:** PR #5 merged into `dev` at merge commit `f085b1412d8670058b2e45a02b4590aa40145069`.

### Scope

- Add the smallest helper that appends a validated local decision audit file and a matching database audit event.
- Derive deterministic event identity from the decision identity and audit checksum.
- Record local provenance linking audit checksum, filenames, dataset checksum, artifact checksum, reason codes, outcome, and evidence classifications.
- Preflight existing database events before file append so conflicting decision/type events fail closed without writing another audit file.
- Add fail-closed tests for matched persistence, idempotency, non-PAPER rejection, and database conflict preflight behavior.

### Evidence classification

- `MEASURED`: PR #4 final head GitHub Actions `validation` run #48 passed before Gate 2C began.
- `MEASURED`: PR #5 final head `16dfe24c624742729fbab2303b8defbd7eb3a780` completed GitHub Actions `validation` run #51 successfully before merge.
- `UNAVAILABLE`: direct local clean working-tree evidence in this execution environment.

### Boundary limit

Gate 2C links local file and SQLite evidence boundaries only. It is not a cross-store transaction manager, runtime event bus, strategy runtime, execution ledger, fill model, cost model, risk allocator, reporting system, paper runtime, live path, or readiness certification.

## Gate 2D — Persistence reconciliation scan

**Status:** `IMPLEMENTED_IN_FOCUSED_BRANCH_PENDING_PR_VALIDATION`.

**Starting baseline:** `dev` merge commit `f085b1412d8670058b2e45a02b4590aa40145069` after Gate 2C merge.

### Scope

- Add the smallest read-only scanner that compares verified local decision audit files against verified SQLite audit events.
- Report missing database events, missing file audit records, and database event identity or payload mismatches.
- Add a fail-closed assertion helper for callers that require fully reconciled local persistence evidence.
- Add focused tests for consistent evidence and all admitted mismatch states.
- Do not repair, delete, rewrite, or promote evidence. Do not add runtime, strategy, backtest, risk, or execution behavior.

### Evidence classification

- `MEASURED`: PR #5 final head GitHub Actions `validation` run #51 passed before Gate 2D began.
- `UNVERIFIED`: exact Gate 2D branch-head GitHub Actions validation until the PR workflow runs.
- `UNAVAILABLE`: direct local compilation, full-suite tests, Ruff, Black, Mypy, and clean working-tree evidence in this execution environment.

### Boundary limit

Gate 2D is a local reconciliation report boundary only. It is not a repair tool, transaction manager, runtime event bus, strategy runtime, execution ledger, fill model, cost model, risk allocator, reporting system, paper runtime, live path, or readiness certification.

## Gate 2E — Reconciliation report surface

**Status:** `BLOCKED_PENDING_GATE_2D_VALIDATION_REVIEW_AND_MERGE`.

Only after Gate 2D is validated, reviewed, and merged may the next run start from the then-current `dev` and expose the reconciliation result in the smallest safe reporting surface. Backtesting, strategies, risk, execution simulation, PAPER runtime, and any performance analysis remain blocked.
