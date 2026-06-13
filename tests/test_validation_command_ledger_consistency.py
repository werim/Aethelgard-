EXPECTED_VALIDATION_COMMANDS = (
    "pytest -q tests/test_gate4_completion_evidence_matrix.py",
    "pytest -q tests/test_gate4_public_safety_exports.py",
    "pytest -q",
    "ruff check .",
    "black --check .",
    "mypy .",
)


UNAVAILABLE_EVIDENCE_MARKERS = (
    "not directly run in this execution environment",
    "UNAVAILABLE",
)


def _read_project_file(path: str) -> str:
    with open(path, encoding="utf-8") as project_file:
        return project_file.read()


def test_report_and_project_state_validation_commands_stay_in_sync() -> None:
    report = _read_project_file("REPORT.md")
    project_state = _read_project_file("PROJECT_STATE.md")

    for command in EXPECTED_VALIDATION_COMMANDS:
        assert command in report
        assert command in project_state


def test_validation_command_ledger_preserves_unavailable_evidence() -> None:
    combined_ledger = "\n".join(
        (
            _read_project_file("REPORT.md"),
            _read_project_file("PROJECT_STATE.md"),
        )
    )

    for marker in UNAVAILABLE_EVIDENCE_MARKERS:
        assert marker in combined_ledger
