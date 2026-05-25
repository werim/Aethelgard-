# Aethelgard

Aethelgard is a conservative crypto futures **research** and **PAPER-trading** foundation focused on Binance Futures market-structure research, execution realism, probabilistic modeling, auditability, and reproducibility.

## Safety posture

- Operating mode is fixed to **PAPER_ONLY** in Phase 1.
- Operational readiness is **RESEARCH_ONLY**.
- No strategy logic, exchange execution, credentials, live infrastructure, optimizer, or performance claims are included.
- Simulated, estimated, measured, unknown, and unverified evidence must remain distinguishable in future phases.

## Phase 1 scope

This initial foundation provides:

- modular repository boundaries,
- validated YAML and environment-backed settings,
- fail-closed rejection of any non-paper operating mode,
- deterministic seed configuration and runtime metadata,
- structured JSON logging,
- automated tests and CI configuration,
- linting, formatting, and static typing setup.

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

`main.py` performs a safe startup check and emits runtime metadata only. It does not fetch market data or generate or execute trades.

## Repository map

- `config/`: validated research configuration and declared symbol candidates.
- `data/`: local raw, processed, and cache data locations; substantive data is gitignored.
- `reports/`: generated report output location; documents at repository root track readiness.
- `src/`: separated engineering domains plus Phase 1 configuration/runtime/logging foundation.
- `tests/`: validation and safety boundary tests.

## License

MIT License. See `LICENSE`.
