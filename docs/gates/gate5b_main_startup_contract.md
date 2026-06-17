# Gate 5B-2 — Main Startup Contract Regression Harness

## Scope

Gate 5B-2 adds a subprocess regression test for the existing `main.py` startup contract. It runs the current Python executable against `main.py` in a controlled temporary working directory, passes only bounded environment values, avoids API keys and secrets, and verifies startup output remains PAPER_ONLY, RESEARCH_ONLY, JSON-parseable, bounded, and offline.

Changed implementation/test files:

- `tests/test_main_startup_contract.py`

Gate 5B-2 does not add runtime behavior, exchange access, market-data fetching, order paths, strategy logic, optimizer behavior, performance calculation, profitability claims, or readiness approval.

## Required startup contract

The harness verifies:

- `python main.py` exits with return code `0`.
- stdout includes `foundation_runtime_initialized` and the existing no-execution-capabilities message.
- stdout contains parseable JSON with `metadata` and `settings`.
- `settings.mode` remains `PAPER_ONLY`.
- `settings.readiness` remains `RESEARCH_ONLY`.
- `metadata.requested_random_seed` or `settings.random_seed` remains `42`.
- the controlled environment sets `PYTHONHASHSEED=42` and does not pass API keys or secrets.
- startup output does not contain unsafe live-readiness, production-readiness, secret, exchange-order, market-fetch success, trade-signal, optimizer-result, PnL, win-rate, Sharpe, or drawdown claims.

## Evidence classification

- A passing subprocess run may be classified as `MEASURED_PAPER_DRY_RUN` only for bounded startup evidence.
- It does not prove production readiness, live readiness, exchange safety, market-data correctness, data completeness, execution realism, strategy validity, or profitability.
- Open PR visibility, remote CI/workflow status, workflow artifacts, workflow job logs, exchange audit proof, and runtime proof beyond bounded startup remain `UNAVAILABLE` unless directly measured.

## Safety boundary

Gate 5B-2 remains PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY. It does not enable live trading, request/read/expose secrets, connect to Binance or any exchange, fetch market data, place or cancel orders, generate strategy alpha, run an optimizer, calculate or publish performance, claim profitability, approve readiness, mutate exchange state, or imply execution capabilities. Unknown execution costs are not zero. Missing evidence remains unavailable. Backtest performance alone does not prove production readiness.
