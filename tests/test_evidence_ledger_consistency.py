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
)

GATE5A3_IMPLEMENTED_FILES = (
    "src/reporting/audit_runtime_evidence.py",
    "tests/test_audit_runtime_evidence.py",
    "docs/gates/gate5a_audit_runtime_evidence.md",
)

SAFETY_PHRASES = (
    "PAPER_ONLY / RESEARCH_ONLY / NOT_LIVE_READY",
    "Unknown execution costs are not zero",
    "Missing evidence remains unavailable",
    "Backtest performance alone does not prove production readiness",
    "does not change runtime behavior",
    "no optimizer",
    "place exchange orders",
    "production readiness",
)


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
