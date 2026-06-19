"""Optional local-only CLI wrapper for runtime evidence artifacts.

This module is intentionally offline and user-invoked. It reads caller-supplied
local JSON metadata and delegates artifact creation to
``src.reporting.runtime_artifact_writer.write_runtime_artifact``. Importing this
module has no runtime startup side effects and does not read secrets,
environment variables, network resources, exchange state, market data, orders,
strategy logic, optimizer results, performance, or readiness approvals.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from src.reporting.runtime_artifact_writer import (
    RuntimeArtifactWriterError,
    write_runtime_artifact,
)

Writer = Callable[[Path, dict[str, object]], Path]


def main(
    argv: Sequence[str] | None = None, *, writer: Writer = write_runtime_artifact
) -> int:
    """Write a local runtime artifact from a local metadata JSON file."""

    parser = _parser()
    args = parser.parse_args(argv)

    try:
        metadata = _read_metadata(args.metadata)
        artifact_path = writer(args.output, metadata)
    except (
        OSError,
        json.JSONDecodeError,
        RuntimeArtifactWriterError,
        TypeError,
    ) as exc:
        print(f"runtime artifact CLI failed: {exc}", file=sys.stderr)
        return 1

    print(f"runtime artifact written: {artifact_path.as_posix()}")
    print("status: LOCAL_ONLY_OFFLINE_ARTIFACT")
    print("mode: PAPER_ONLY")
    print("readiness: RESEARCH_ONLY")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="runtime-artifact-cli",
        description=(
            "Write a local-only PAPER runtime evidence artifact "
            "from local JSON metadata."
        ),
    )
    parser.add_argument(
        "--metadata",
        required=True,
        type=Path,
        help="Local JSON metadata file supplied by the user.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Repo-relative reports/*.json artifact path.",
    )
    return parser


def _read_metadata(path: Path) -> dict[str, object]:
    if path.is_absolute() or any(part == ".." for part in path.parts):
        raise RuntimeArtifactWriterError(
            "metadata path must be local and repo-relative"
        )
    if path.suffix != ".json":
        raise RuntimeArtifactWriterError("metadata path must be a JSON file")
    if not path.is_file():
        raise RuntimeArtifactWriterError("metadata file is missing")

    value: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeArtifactWriterError("metadata JSON must be an object")
    return dict(value)


if __name__ == "__main__":
    raise SystemExit(main())
