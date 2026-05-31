# Aethelgard

Aethelgard is a conservative crypto futures **research** and **PAPER-trading** foundation focused on Binance Futures market-structure research, execution realism, probabilistic modeling, auditability, and reproducibility.

## Safety posture

- Operating mode remains fixed to **PAPER_ONLY**.
- Operational readiness remains **RESEARCH_ONLY**.
- No strategy logic, exchange connectivity requiring secrets, optimizer, or performance claims are included.
- Simulated, estimated, measured, unknown, and unverified evidence must remain distinguishable.

## Implemented scope

Phase 1 established modular boundaries, validated configuration, fail-closed PAPER-only mode enforcement, deterministic seed metadata, structured JSON logging, and validation tooling.

Phase 2 added a supplied-row historical-data ingestion boundary with timestamp, continuity, OHLC, provenance, and deterministic fingerprint validation.

Phase 2B added only a read-only acquisition evidence boundary:

- credential-free GET acquisition from the public Binance Futures kline endpoint,
- validated fixed-interval request selectors and deterministic pagination,
- bounded retry and rate-limit diagnostics,
- immutable local raw artifact and checksummed metadata storage with persisted fetch diagnostics and verified readback,
- stale or future-dated acquisition-evidence rejection during artifact readback.

Gate 2A adds only a research decision audit-trail boundary:

- append-only local JSON audit records for `REJECTED` and `NO_ACTION` outcomes,
- explicit `MEASURED`, `MODELED`, and `UNAVAILABLE` evidence classification,
- checksum-addressed audit filenames plus `decision_id.claim` conflict anchors,
- fail-closed readback when record bytes, claims, UTC timestamps, PAPER-only mode, or evidence provenance are invalid.

Gate 2B adds only the smallest database-backed audit-event boundary:

- a local SQLite `audit_events` ledger for research audit events,
- append-only event identity with idempotent identical appends and fail-closed conflicts,
- canonical JSON payload storage with SHA-256 readback verification,
- UTC timestamp, `PAPER_ONLY`, and `RESEARCH_ONLY` validation,
- focused tests for schema initialization, idempotency, conflicts, checksum tampering, UTC mode safety, and deterministic JSON payload requirements.

Gate 2C adds only a narrow persistence-integration helper:

- appends a validated decision audit record and a matching SQLite audit event,
- derives deterministic event identity from the decision identity and audit checksum,
- records measured local evidence linking the audit filename, claim filename, dataset checksum, artifact checksum, reason codes, and evidence classifications,
- preflights existing database events before writing a new file audit record so conflicting decision/type events fail closed without partial file writes.

Gate 2D adds only a local persistence-reconciliation scan:

- discovers verified decision audit files and verified SQLite audit events,
- reports missing database events, missing file audit records, and mismatched database event identity or payload,
- exposes a fail-closed assertion helper for callers that require a fully consistent local evidence set,
- leaves repair, deletion, runtime promotion, and decision generation out of scope.

Gate 2E adds only a reconciliation reporting surface:

- renders reconciliation reports as deterministic JSON-compatible payloads, deterministic JSON strings, and deterministic Markdown summaries,
- reports `CONSISTENT`, `INCONSISTENT`, or `UNAVAILABLE` status explicitly,
- includes mismatch counts by issue type and sorted issue details,
- preserves unavailable reconciliation evidence as unavailable instead of treating missing reports as clean.

Gate 2F adds only local reconciliation report artifact persistence:

- writes reconciliation report JSON, Markdown, and metadata artifacts,
- anchors artifact filenames with checksums,
- validates readback checksums, mode, readiness, schema, and status consistency,
- detects local tampering and conflicting idempotent writes fail closed.

It does **not** run backtests, issue signals, manage positions, authenticate exchange-origin claims beyond the configured public endpoint, establish long-horizon exchange completeness, model fills or costs, repair persistence stores, or provide PAPER/LIVE readiness.

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

`main.py` performs a safe startup check and emits runtime metadata only. It does not fetch market data or generate trade decisions. Historical acquisition is an explicit research-data action through `src/data/acquisition.py`, not part of a trading runtime. Decision audit persistence is an explicit research evidence action through `src/persistence/audit.py`; database audit events are explicit persistence evidence through `src/persistence/events.py`; integration helpers in `src/persistence/integration.py` link those persistence evidence boundaries; reconciliation helpers in `src/persistence/reconciliation.py` scan, report, and persist local reconciliation report artifacts. None of these paths approves runtime use.

## Repository map

- `config/`: validated research configuration and declared symbol candidates.
- `data/`: local raw, processed, and cache data locations; substantive data is gitignored.
- `reports/`: generated report output location; documents at repository root track readiness.
- `src/data/`: supplied-row kline validation plus read-only public acquisition and immutable raw-artifact evidence boundary.
- `src/persistence/`: research-only decision audit evidence, database audit-event persistence, narrow integration, reconciliation, reporting, and report-artifact boundaries.
- `src/`: separated engineering domains plus configuration/runtime/logging foundation.
- `tests/`: validation and safety boundary tests.

## License

MIT License. See `LICENSE`.
