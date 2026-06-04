# Aethelgard Engineering Report

## Current classification

- Operational readiness: `RESEARCH_ONLY`
- Operating mode: `PAPER_ONLY`
- Active increment: Gate 4B deterministic candle replay recovery boundary.

## Baseline

- Repository: `werim/Aethelgard-`
- Base branch: `dev`
- Starting HEAD: `f4b0b6ae6c9c20afd8d42c69a14bfdfcdaff9ba7`, current `dev` before Gate 4B recovery began.
- Connector comparison showed `dev` was identical to `f4b0b6ae6c9c20afd8d42c69a14bfdfcdaff9ba7` before Gate 4B recovery began.
- Startup recovery found that the requested Gate 4A restart assumption was outdated: `dev` already contained `0.16.0 / Increment 4E`, but deterministic candle replay evidence was still absent.
- Direct mutable local clone status is unavailable in this execution environment because container DNS could not resolve `github.com`; GitHub API operations were used.

## Implemented Gate 4B boundary

Gate 4B implements only deterministic candle replay over caller-supplied candle rows.

| Area | Change | Evidence limit |
| --- | --- | --- |
| Replay row model | Added normalized `CandleReplayRow` records. | Uses caller-supplied rows only. |
| Validation | Validates UTC timestamps, monotonic open times, duplicates, gaps, OHLCV shape, prices, volume, symbol, and timeframe. | Does not fetch or prove exchange data authenticity. |
| Metadata | Emits dataset fingerprint, symbol, timeframe, start/end timestamp, row count, missing interval count, duplicate count, validation status, and deterministic hash. | Metadata is data-quality evidence, not profitability evidence. |
| Fail-closed behavior | Invalid replay data raises by default. | Read-only diagnostics may inspect invalid metadata, but invalid rows cannot be replayed. |
| Determinism | Serializes rows and metadata deterministically. | Determinism does not imply strategy edge. |
| Tests | Covers valid order, deterministic metadata, duplicate/unsorted/gapped data, UTC, OHLCV, price, volume, symbol, and timeframe failures. | Full repository CI pending. |

## Validation evidence

| Check | Result | Classification |
| --- | --- | --- |
| Starting `dev` comparison | `dev` identical to `f4b0b6ae6c9c20afd8d42c69a14bfdfcdaff9ba7` | `MEASURED` connector evidence |
| Local isolated Gate 4B focused tests | `10 passed in 0.55s` | `MEASURED` isolated evidence |
| Local isolated compile check | exit code `0` | `MEASURED` isolated evidence |
| New-file line-length spot check | no lines above 88 chars | `MEASURED` isolated evidence |
| Direct local clone | failed DNS resolution for `github.com` | `UNAVAILABLE` |
| Ruff, Black, Mypy | modules unavailable in scratch environment | `UNAVAILABLE` |
| Exact final branch-head full test suite | Pending CI | `UNVERIFIED` |
| Current-head workflow for this commit chain | Pending or unavailable until GitHub Actions runs | `UNVERIFIED` |

## Safety boundary and unresolved risks

- No account access, credentials, exchange fetch, strategy generation, signal generation, trade simulation, fill model, risk allocation, PAPER runtime behavior, real order path, DB repair, optimizer, performance metrics, or profitability analysis is introduced.
- Gate 4B replays only already supplied candle rows after validation.
- Missing candles, duplicates, unsorted timestamps, malformed OHLCV, invalid price/volume, and symbol/timeframe mismatches fail closed.
- Replay metadata does not prove execution realism, market-data completeness, exchange authenticity, fill quality, strategy expectancy, or readiness.
- API-backed writes created a sequence of small commits rather than one atomic local git commit because a mutable local clone was unavailable.

## Next step

After Gate 4B is validated, reviewed, and green, the next smallest safe recovery increment is Gate 4C: conservative trade lifecycle simulation boundary only. It must not add optimizer behavior, live execution, order placement, profitability claims, or readiness approval.
