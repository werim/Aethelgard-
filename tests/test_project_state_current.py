PROJECT_STATE_PATH = "PROJECT_STATE.md"


def project_state_text() -> str:
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[1]
    return (project_root / PROJECT_STATE_PATH).read_text(encoding="utf-8")


def test_project_state_no_longer_claims_repository_state_unknown() -> None:
    text = project_state_text()

    stale_claims = {
        "Actual repository branch and HEAD.",
        "No verified dev branch HEAD is available.",
        "No confirmed PLAN.md ledger state is available.",
        "Gate statuses are Unknown.",
        "Gate 0 — Baseline Reconciliation and PLAN Ledger.",
    }

    for stale_claim in stale_claims:
        assert stale_claim not in text


def test_project_state_records_current_dev_evidence_without_readiness_upgrade() -> None:
    text = project_state_text()

    assert "Repository: `werim/Aethelgard-`" in text
    assert "Target branch: `dev`" in text
    assert "Gate 4B-5 — Project state ledger reconciliation." in text
    assert "PAPER ONLY" in text
    assert "RESEARCH ONLY" in text
    assert "NOT READY" in text


def test_project_state_preserves_safety_boundary() -> None:
    text = project_state_text()

    required_phrases = {
        "does not compute performance",
        "model execution costs",
        "add optimizer behavior",
        "add non-paper runtime behavior",
        "approve operational readiness",
        "Unknown execution costs are not zero",
        "Missing evidence remains unavailable",
    }

    for phrase in required_phrases:
        assert phrase in text
