# Aethelgard

Aethelgard is a conservative crypto futures **research** and **PAPER-trading** foundation focused on Binance Futures market-structure research, execution realism, probabilistic modeling, auditability, and reproducibility.

## Safety posture

- Operating mode remains fixed to **PAPER_ONLY**.
- Operational readiness remains **RESEARCH_ONLY**.
- No strategy logic, exchange execution, credentials, live infrastructure, optimizer, or performance claims are included.
- Simulated, estimated, measured, unknown, and unverified evidence must remain distinguishable.

## Implemented scope

Phase 1 established modular boundaries, validated configuration, fail-closed PAPER-only mode enforcement, deterministic seed metadata, structured JSON logging, and validation tooling.

Phase 2 added a supplied-row historical-data ingestion boundary with timestamp, continuity, OHLC, provenance, and deterministic fingerprint validation.

Phase 2B adds only a read-only acquisition evidence boundary:

- credential-free GET acquisition from the public Binance Futures kline endpoint,
- validated fixed-interval request selectors and deterministic pagination,
- bounded retry and rate-limit diagnostics,
- immutable local raw artifact and checksummed metadata storage with persisted fetch diagnostics and verified readback,
- stale or future-dated acquisition-evidence rejection during artifact readback.

It does **not** run backtests, issue signals, execute orders, authenticate exchange-origin claims beyond the configured public endpoint, or establish long-horizon exchange completeness.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
python main.py
pytest -q
ruff check .
black --check .
mypy .
```

`main.py` performs a safe startup check and emits runtime metadata only. It does not fetch market data or generate or execute trades. Historical acquisition is an explicit research-data action through `src/data/acquisition.py`, not part of a trading runtime.

## Repository map

- `config/`: validated research configuration and declared symbol candidates.
- `data/`: local raw, processed, and cache data locations; substantive data is gitignored.
- `reports/`: generated report output location; documents at repository root track readiness.
- `src/data/`: supplied-row kline validation plus read-only public acquisition and immutable raw-artifact evidence boundary.
- `src/`: separated engineering domains plus configuration/runtime/logging foundation.
- `tests/`: validation and safety boundary tests.

## License

MIT License. See `LICENSE`.
