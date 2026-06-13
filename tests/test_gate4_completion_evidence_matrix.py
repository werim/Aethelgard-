from pathlib import Path


MATRIX = Path("docs/gates/gate4_completion_evidence_matrix.md")


def test_gate4_completion_matrix_current_target() -> None:
    text = MATRIX.read_text(encoding="utf-8")

    assert "Gate 4CLOSE-1A" in text
    assert "PAPER_ONLY" in text
    assert "RESEARCH_ONLY" in text
    assert "NOT_LIVE_READY" in text


def test_gate4_completion_matrix_core_boundaries() -> None:
    text = MATRIX.read_text(encoding="utf-8")

    for phrase in (
        "Fee modeling boundary",
        "Slippage modeling boundary",
        "Spread modeling boundary",
        "Funding or carry cost boundary",
        "Latency or fill realism boundary",
        "Unknown costs are not zero",
        "Missing cost evidence remains unavailable",
        "Backtest metrics do not prove readiness",
        "PAPER-only safety text exists",
    ):
        assert phrase in text


def test_gate4_completion_matrix_links_evidence_files() -> None:
    text = MATRIX.read_text(encoding="utf-8")

    for evidence_path in (
        "src/backtest/cost_evidence.py",
        "src/backtest/lifecycle.py",
        "tests/test_cost_evidence.py",
        "tests/test_public_exports.py",
    ):
        assert evidence_path in text
