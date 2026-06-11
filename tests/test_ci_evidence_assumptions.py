from pathlib import Path

CI_WORKFLOW = Path(".github/workflows/ci.yml")


def _ci_workflow_text() -> str:
    assert CI_WORKFLOW.exists(), "CI workflow file is missing"
    return CI_WORKFLOW.read_text(encoding="utf-8")


def test_ci_workflow_preserves_dev_branch_validation_boundary() -> None:
    text = _ci_workflow_text()

    assert "push:" in text
    assert "pull_request:" in text
    assert text.count("branches: [dev]") == 2


def test_ci_workflow_records_junit_evidence_and_fails_closed() -> None:
    text = _ci_workflow_text()

    assert "pytest -q --junitxml=\"reports/junit-${{ matrix.python-version }}.xml\"" in text
    assert "uses: actions/upload-artifact@v4" in text
    assert "name: pytest-junit-${{ matrix.python-version }}" in text
    assert "path: reports/junit-${{ matrix.python-version }}.xml" in text
    assert "if-no-files-found: error" in text


def test_ci_workflow_keeps_validation_steps_explicit() -> None:
    text = _ci_workflow_text()

    required_steps = [
        "python -m compileall -q src tests main.py",
        "pytest -q --junitxml=\"reports/junit-${{ matrix.python-version }}.xml\"",
        "ruff check .",
        "black --check .",
        "mypy .",
    ]

    for step in required_steps:
        assert step in text
