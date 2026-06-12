VERSION_PATH = "VERSION.md"
PROJECT_STATE_PATH = "PROJECT_STATE.md"
CHANGELOG_PATH = "CHANGELOG.md"
REPORT_PATH = "REPORT.md"


def read_repo_file(path: str) -> str:
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[1]
    return (project_root / path).read_text(encoding="utf-8")


def test_version_records_gate_4b5_current_ledger_increment() -> None:
    version_text = read_repo_file(VERSION_PATH)

    assert "Gate 4B-5" in version_text
    assert "project-state ledger reconciliation" in version_text
    assert "documentation/test-only increment" in version_text


def test_gate_4b5_is_recorded_across_current_ledgers() -> None:
    ledger_texts = {
        "VERSION.md": read_repo_file(VERSION_PATH),
        "CHANGELOG.md": read_repo_file(CHANGELOG_PATH),
        "REPORT.md": read_repo_file(REPORT_PATH),
        "PROJECT_STATE.md": read_repo_file(PROJECT_STATE_PATH),
    }

    for path, text in ledger_texts.items():
        assert "Gate 4B-5" in text, path


def test_version_preserves_gate_4b5_safety_boundary() -> None:
    version_text = read_repo_file(VERSION_PATH)

    required_phrases = {
        "no runtime behavior",
        "no strategy logic",
        "no optimizer",
        "no execution-cost modeling",
        "no performance calculation",
        "no PAPER runtime expansion",
        "no exchange mutation",
        "no readiness approval",
    }

    for phrase in required_phrases:
        assert phrase in version_text
