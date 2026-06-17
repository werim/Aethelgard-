import re
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

LEDGER_PATHS = (
    "PROJECT_STATE.md",
    "REPORT.md",
    "VERSION.md",
    "CHANGELOG.md",
    "docs/gates/gate5a_evidence_ledger.md",
    "docs/gates/gate5a_workflow_artifact_evidence_ledger.md",
)

GATE5A3_IMPLEMENTED_FILES = (
    "src/reporting/audit_runtime_evidence.py",
    "tests/test_audit_runtime_evidence.py",
    "docs/gates/gate5a_audit_runtime_evidence.md",
)

GATE5A6_IMPLEMENTED_FILES = (
    "src/reporting/data_freshness_evidence.py",
    "tests/test_data_freshness_evidence.py",
    "docs/gates/gate5a_data_freshness_evidence.md",
)

SAFETY_PHRASES = (
    "PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY",
    "Unknown execution costs are not zero",
    "Missing evidence remains unavailable",
    "Backtest performance alone does not prove production readiness",
    "does not change runtime behavior",
    "strategy logic",
    "optimizer behavior",
    "execution-cost modeling",
    "performance calculation",
    "PAPER runtime behavior",
    "exchange mutation",
    "readiness status",
    "no optimizer",
    "place exchange orders",
    "production readiness",
)

GATE5A6_GREEN_HEAD = "3f5cb4ea89fa3c12661e020d802796439d3a064c"
GREEN_RUN_NUMBERS = ("309", "310", "311", "312", "313")


def _read(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_package_version_contract_stays_aligned() -> None:
    pyproject = tomllib.loads(_read("pyproject.toml"))
    src_init = _read("src/__init__.py")
    version_match = re.search(r'__version__ = "([^"]+)"', src_init)

    assert version_match is not None
    package_version = pyproject["project"]["version"]

    assert package_version == version_match.group(1)
    assert f"## {package_version}" in _read("VERSION.md")
    assert f"## [{package_version}]" in _read("CHANGELOG.md")


def test_gate5a4_is_recorded_across_ledgers() -> None:
    for path in LEDGER_PATHS:
        text = _read(path)

        assert "Gate 5A-4 evidence ledger consistency audit" in text
        assert "user-reported green" in text
        assert "connector-visible CI remains UNAVAILABLE" in text


def test_gate5a3_implemented_claim_has_source_test_and_doc_counterparts() -> None:
    combined_ledger = "\n".join(_read(path) for path in LEDGER_PATHS)

    for path in GATE5A3_IMPLEMENTED_FILES:
        assert (PROJECT_ROOT / path).exists(), f"{path} is missing"
        assert path in combined_ledger, f"{path} missing from ledger text"


def test_gate5a6_implemented_claim_has_source_test_and_doc_counterparts() -> None:
    combined_ledger = "\n".join(_read(path) for path in LEDGER_PATHS)

    for path in GATE5A6_IMPLEMENTED_FILES:
        assert (PROJECT_ROOT / path).exists(), f"{path} is missing"
        assert path in combined_ledger, f"{path} missing from ledger text"


def test_gate5a7_keeps_workflow_artifact_evidence_unavailable() -> None:
    combined_ledger = "\n".join(_read(path) for path in LEDGER_PATHS)

    assert "Gate 5A-7 workflow artifact evidence ledger" in combined_ledger
    assert GATE5A6_GREEN_HEAD in combined_ledger
    assert "Commit title: `Gate 5A-6: apply black formatting" in combined_ledger
    assert "connector-visible workflow evidence remains unavailable" in (
        combined_ledger.lower()
    )
    assert "not connector-visible workflow evidence" in combined_ledger.lower()
    assert "direct workflow artifact proof" in combined_ledger

    for run_number in GREEN_RUN_NUMBERS:
        assert run_number in combined_ledger


def test_green_evidence_language_cannot_become_connector_ci_claim() -> None:
    for path in LEDGER_PATHS:
        text = _read(path)
        lower_text = text.lower()

        assert "user-reported green" in lower_text
        assert "connector-visible ci remains unavailable" in lower_text
        assert "not connector-visible workflow evidence" in lower_text


def test_safety_boundary_phrases_remain_visible() -> None:
    combined_ledger = "\n".join(_read(path) for path in LEDGER_PATHS)

    for phrase in SAFETY_PHRASES:
        assert phrase in combined_ledger


def test_gate5a8_records_documentation_reconciliation_without_runtime_claims() -> None:
    combined_ledger = "\n".join(_read(path) for path in LEDGER_PATHS)

    assert "gate 5a-8 documentation evidence reconciliation" in combined_ledger.lower()
    assert "documentation/test-only evidence reconciliation" in combined_ledger
    assert "Gate 4B-5" in combined_ledger
    assert "Gate 4B-5A" in combined_ledger
    assert "Gate 5A-7" in combined_ledger
    assert "remote `origin`" in combined_ledger
    assert "open PR" in combined_ledger
    assert "direct workflow artifact" in combined_ledger
    assert "UNAVAILABLE" in combined_ledger


def test_gate5a9_validation_boundary_keeps_unavailable_ci_unavailable() -> None:
    gate5a9_paths = (*LEDGER_PATHS, "docs/gates/gate5a_validation_evidence_boundary.md")
    combined_ledger = "\n".join(_read(path) for path in gate5a9_paths)

    assert "Gate 5A-9 CI/validation evidence boundary adapter" in combined_ledger
    assert "MEASURED_LOCAL" in combined_ledger
    assert "USER_REPORTED" in combined_ledger
    assert "CONNECTOR_VISIBLE_CI" in combined_ledger
    assert "No workflow runs means `UNAVAILABLE`" in combined_ledger
    assert "Empty combined status means `UNAVAILABLE`" in combined_ledger
    assert "Unavailable connector-visible CI is never promoted" in combined_ledger
    assert "connector-visible ci remains unavailable" in combined_ledger.lower()


def test_gate5a10_repository_provenance_boundary_fails_closed() -> None:
    paths = (*LEDGER_PATHS, "docs/gates/gate5a_pr_branch_provenance_evidence.md")
    combined_ledger = "\n".join(_read(path) for path in paths)

    assert "Gate 5A-10 PR / Branch-head provenance evidence adapter" in combined_ledger
    assert "src/reporting/repository_provenance_evidence.py" in combined_ledger
    assert "tests/test_repository_provenance_evidence.py" in combined_ledger
    assert "USER_REPORTED_PR" in combined_ledger
    assert "MEASURED_PR_VISIBLE" in combined_ledger
    assert "UNAVAILABLE_PR_VISIBILITY" in combined_ledger
    assert "UNAVAILABLE_BRANCH_REFRESH" in combined_ledger
    assert "UNAVAILABLE_MERGE_EVIDENCE" in combined_ledger
    assert "MEASURED_MERGED_TO_BRANCH" in combined_ledger
    assert "commit SHA visibility alone is not merge evidence" in combined_ledger
    assert "docs cannot claim merged-to-`dev` unless" in combined_ledger


def test_gate5a11_exchange_mutation_boundary_fails_closed() -> None:
    paths = (*LEDGER_PATHS, "docs/gates/gate5a_exchange_mutation_boundary_evidence.md")
    combined_ledger = "\n".join(_read(path) for path in paths)

    assert "Gate 5A-11 exchange mutation boundary evidence adapter" in combined_ledger
    assert "src/reporting/exchange_mutation_boundary_evidence.py" in combined_ledger
    assert "tests/test_exchange_mutation_boundary_evidence.py" in combined_ledger
    assert "MEASURED_NO_MUTATION_PATH" in combined_ledger
    assert "MEASURED_PAPER_ONLY_GUARD" in combined_ledger
    assert "USER_REPORTED_NO_LIVE_USE" in combined_ledger
    assert "UNAVAILABLE_EXCHANGE_AUDIT" in combined_ledger
    assert "UNAVAILABLE_RUNTIME_PROOF" in combined_ledger
    assert "VIOLATION_EXCHANGE_MUTATION_ALLOWED" in combined_ledger
    assert "PAPER_ONLY evidence does not imply live readiness" in combined_ledger
    assert "Docs cannot claim production readiness" in combined_ledger


def test_gate5a12_secret_material_boundary_fails_closed() -> None:
    paths = (*LEDGER_PATHS, "docs/gates/gate5a_secret_material_boundary_evidence.md")
    combined_ledger = "\n".join(_read(path) for path in paths)

    assert "Gate 5A-12 secret material boundary evidence adapter" in combined_ledger
    assert "src/reporting/secret_material_boundary_evidence.py" in combined_ledger
    assert "tests/test_secret_material_boundary_evidence.py" in combined_ledger
    assert "MEASURED_NO_SECRET_MATERIAL" in combined_ledger
    assert "MEASURED_SECRET_PLACEHOLDER_ONLY" in combined_ledger
    assert "USER_REPORTED_SECRETS_NOT_SHARED" in combined_ledger
    assert "UNAVAILABLE_SECRET_AUDIT" in combined_ledger
    assert "UNAVAILABLE_RUNTIME_SECRET_PROOF" in combined_ledger
    assert "VIOLATION_SECRET_MATERIAL_EXPOSED" in combined_ledger
    assert "Secret-material evidence never permits live-readiness" in combined_ledger


def test_gate5a13_user_reported_green_validation_reconciliation() -> None:
    paths = (
        *LEDGER_PATHS,
        "PLAN.md",
        "docs/gates/gate5a_secret_material_boundary_evidence.md",
    )
    combined_ledger = "\n".join(_read(path) for path in paths)
    lower_ledger = combined_ledger.lower()

    assert (
        "Gate 5A-13 user-reported green validation evidence reconciliation"
        in combined_ledger
    )
    assert "GREEN_BY_USER_REPORTED_VALIDATION" in combined_ledger
    assert "USER_REPORTED_GREEN_VALIDATION" in combined_ledger
    assert (
        "Gate 5A-12 remains secret-material boundary evidence only" in combined_ledger
    )
    assert "connector-visible CI remains `UNAVAILABLE`" in combined_ledger
    assert "workflow artifacts remain `UNAVAILABLE`" in combined_ledger
    assert "workflow job logs remain `UNAVAILABLE`" in combined_ledger
    assert (
        "user-reported green validation is not connector-visible workflow evidence"
        in lower_ledger
    )
    assert (
        "user-reported green validation is not direct workflow artifact proof"
        in lower_ledger
    )
    assert (
        "user-reported green validation does not prove production readiness"
        in lower_ledger
    )
    assert "documentation/test-only reconciliation" in combined_ledger
    assert "does not change runtime behavior" in combined_ledger
    assert "secret handling" in combined_ledger
    assert "No live trading" in combined_ledger
    assert "No live trading, secret request" in combined_ledger
