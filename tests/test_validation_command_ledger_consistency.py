EXPECTED_VALIDATION_COMMANDS = (
    "python -m compileall -q src tests main.py",
    "pytest -q tests/test_validation_command_ledger_consistency.py",
    "pytest -q tests/test_gate4_completion_evidence_matrix.py",
    "pytest -q tests/test_gate4_public_safety_exports.py",
    "pytest -q tests/test_cost_evidence.py",
    "pytest -q tests/test_public_exports.py",
    "pytest -q",
    "ruff check .",
    "black --check .",
    "mypy .",
)

VALIDATION_LEDGER_PATHS = (
    "REPORT.md",
    "PROJECT_STATE.md",
    "docs/gates/gate4_completion_evidence_matrix.md",
)

UNAVAILABLE_EVIDENCE_MARKERS = (
    "not directly run in this execution environment",
    "UNAVAILABLE",
)


def _read_project_file(path: str) -> str:
    with open(path, encoding="utf-8") as project_file:
        return project_file.read()


def test_validation_commands_stay_canonical_across_ledgers() -> None:
    for path in VALIDATION_LEDGER_PATHS:
        text = _read_project_file(path)

        for command in EXPECTED_VALIDATION_COMMANDS:
            assert command in text, f"{command!r} missing from {path}"


def test_validation_command_ledger_preserves_unavailable_evidence() -> None:
    combined_ledger = "\n".join(
        _read_project_file(path) for path in VALIDATION_LEDGER_PATHS
    )

    for marker in UNAVAILABLE_EVIDENCE_MARKERS:
        assert marker in combined_ledger
