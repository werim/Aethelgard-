import tomllib
from pathlib import Path

import src


def test_package_version_matches_project_metadata() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert src.__version__ == pyproject["project"]["version"]
