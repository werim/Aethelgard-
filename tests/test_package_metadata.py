import re
import tomllib
from pathlib import Path

import src

_VERSION_HEADING_RE = re.compile(
    r"^## \[?(?P<version>\d+\.\d+\.\d+)\]?\b",
    re.MULTILINE,
)


def _project_version() -> str:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    return str(pyproject["project"]["version"])


def _latest_version_heading(path: str) -> str:
    content = Path(path).read_text(encoding="utf-8")
    match = _VERSION_HEADING_RE.search(content)

    assert match is not None, f"missing version heading in {path}"
    return match.group("version")


def test_package_version_matches_project_metadata() -> None:
    assert src.__version__ == _project_version()


def test_version_history_matches_project_metadata() -> None:
    assert _latest_version_heading("VERSION.md") == _project_version()


def test_changelog_matches_project_metadata() -> None:
    assert _latest_version_heading("CHANGELOG.md") == _project_version()
