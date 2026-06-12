from pathlib import Path


MATRIX = Path("docs/gates/gate4_completion_evidence_matrix.md")
ROOT_DOCS = (
    Path("PLAN.md"),
    Path("REPORT.md"),
    Path("PROJECT_STATE.md"),
)

REQUIRED_BOUNDARIES = (
    "Fee modeling boundary",
    "Slippage modeling boundary",
    "Spread modeling boundary",
    "Funding or carry cost boundary",
    "Latency or fill realism boundary",
    "Unknown costs are not zero",
    "Missing cost evidence remains unavailable",
    "Backtest metrics do not prove readiness",
    "PAPER-only safety text exists",
    "No unsafe public exports",
    "No secret handling exposed publicly",
)

REQUIRED_SAFETY_PHRASES = (
    "PAPER_ONLY",
    "RESEARCH_ONLY",
    "NOT_LIVE_READY",
    "Unknown execution costs are not zero",
    "Missing cost evidence remains explicitly UNAVAILABLE",
    "Backtest performance alone does not prove production readiness",
    "does not approve live trading",
)

REQUIRED_EVIDENCE_PATHS = (
    "src/backtest/cost_evidence.py",
    "src/backtest/lifecycle.py",
    "src/backtest/__init__.py",
    "src/execution/__init__.py",
    "tests/test_cost_evidence.py",
    "tests/test_backtest_lifecycle.py",
    "tests/test_public_exports.py",
    "tests/test_gate4_public_safety_exports.py",
)


def test_gate4_completion_matrix_exists_with_required_boundaries() -> None:
    text = MATRIX.read_text(encoding="utf-8")

    for boundary in REQUIRED_BOUNDARIES:
        assert boundary in text

    assert "| Boundary | Source evidence | Test evidence |" in text
    assert "| Public export check | Status | Notes |" in text
    assert "UNAVAILABLE" in text
    assert "PROVEN" in text


def test_gate4_completion_matrix_records_safety_language() -> None:
    matrix_text = MATRIX.read_text(encoding="utf-8")
    ledger_text = "\n".join(
        path.read_text(encoding="utf-8") for path in ROOT_DOCS
    )
    combined_text = f"{matrix_text}\n{ledger_text}"

    for phrase in REQUIRED_SAFETY_PHRASES:
        assert phrase in combined_text


def test_gate4_completion_matrix_links_source_and_test_evidence() -> None:
    text = MATRIX.read_text(encoding="utf-8")

    for evidence_path in REQUIRED_EVIDENCE_PATHS:
        assert evidence_path in text
