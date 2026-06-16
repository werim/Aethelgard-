# Gate 5A-10 PR / Branch-Head Provenance Evidence Adapter

Increment: Gate 5A-10 PR / Branch-head provenance evidence adapter
Scope: reporting-boundary adapter, focused regression coverage, and evidence-ledger documentation
Operating mode: PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY

## Purpose

Gate 5A-10 hardens repository provenance evidence classification so branch-head, PR visibility, merge, commit ancestry, and unavailable remote evidence cannot be conflated.

The adapter separates these repository provenance classes:

- `USER_REPORTED_PR`: a user statement or screenshot about a PR; not connector-visible PR evidence.
- `USER_REPORTED_COMMIT`: a user statement about a commit; not branch containment or merge evidence.
- `MEASURED_PR_VISIBLE`: a directly measured PR lookup for the target branch.
- `MEASURED_BRANCH_HEAD`: a directly measured refreshed branch-head observation.
- `MEASURED_BRANCH_CONTAINS`: measured compare/ancestry evidence that a branch contains a commit, without measured merge evidence.
- `MEASURED_MERGED_TO_BRANCH`: measured branch containment and measured merge evidence.
- `UNAVAILABLE_PR_VISIBILITY`: missing or failed PR lookup evidence.
- `UNAVAILABLE_BRANCH_REFRESH`: missing or stale branch-head refresh evidence.
- `UNAVAILABLE_MERGE_EVIDENCE`: missing compare, ancestry, containment, or merge evidence.

## Fail-closed rules

- User-reported PR creation remains `USER_REPORTED_PR`; it is not `MEASURED_PR_VISIBLE`.
- User-reported commit evidence remains `USER_REPORTED_COMMIT`; it does not prove the commit is on `dev`.
- A visible commit SHA alone is not merge evidence.
- `dev` branch containment requires measured branch/compare evidence.
- Missing PR lookup remains `UNAVAILABLE_PR_VISIBILITY`.
- Missing branch refresh remains `UNAVAILABLE_BRANCH_REFRESH`.
- Missing compare/ancestry evidence remains `UNAVAILABLE_MERGE_EVIDENCE`.
- Documentation may claim merged-to-`dev` only when `MEASURED_MERGED_TO_BRANCH` evidence is present.

## Implemented surface

- `src/reporting/repository_provenance_evidence.py` defines the Gate 5A-10 repository provenance classifications and deterministic classifier helpers.
- `tests/test_repository_provenance_evidence.py` proves user-reported PRs, missing PR lookup, commit-SHA-only evidence, missing branch refresh, and missing merge evidence fail closed.
- `tests/test_evidence_ledger_consistency.py` guards the Gate 5A-10 ledger wording so unavailable provenance evidence is not promoted to measured evidence.

## Evidence classification

| Evidence | Classification | Note |
| --- | --- | --- |
| Local Gate 5A-10 source and tests | `MEASURED_LOCAL` | Source, tests, and docs were changed in this workspace. |
| User-reported PR/commit statements | `USER_REPORTED_PR` / `USER_REPORTED_COMMIT` | Recorded separately from measured PR visibility, branch containment, or merge evidence. |
| Remote `origin` refresh for this workspace | `UNAVAILABLE_BRANCH_REFRESH` | No `origin` remote was visible in this workspace. |
| Open PR lookup for `dev` | `UNAVAILABLE_PR_VISIBILITY` | No connector-visible PR lookup was available in this workspace. |
| Compare/ancestry evidence for this workspace commit on `dev` | `UNAVAILABLE_MERGE_EVIDENCE` | No measured branch compare or merge evidence was available in this workspace. |
| Modeled repository provenance | `MODELED: none` | No modeled repository provenance is used. |

## Safety boundary

Gate 5A-10 does not change runtime behavior, strategy logic, optimizer behavior, execution-cost modeling, performance calculation, PAPER runtime behavior, exchange mutation, exchange behavior, or readiness status.

Gate 5A-10 does not fetch market data, connect to exchanges, request secrets, mutate workflows, download private artifacts, place exchange orders, or enable live trading.

Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.

## Validation commands

```bash
python -m compileall -q src tests main.py
pytest -q tests/test_repository_provenance_evidence.py
pytest -q tests/test_evidence_ledger_consistency.py
pytest -q
ruff check .
black --check .
mypy .
```

Commands unavailable in an environment must be reported as UNAVAILABLE, not passed. Connector writes alone do not prove local or CI validation.
