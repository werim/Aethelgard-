"""Gate 5B-5 tests for the optional offline runtime artifact CLI."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from src.reporting import runtime_artifact_cli

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _metadata() -> dict[str, object]:
    return {
        "determinism_scope": "caller-supplied local metadata only",
        "evidence_classification": "MEASURED_PAPER_DRY_RUN",
        "generated_at_utc": "2026-06-19T00:00:00Z",
        "mode": "PAPER_ONLY",
        "project_name": "Aethelgard",
        "random_seed": 42,
        "readiness": "RESEARCH_ONLY",
        "source": "tests/test_runtime_artifact_cli.py",
    }


def test_cli_invokes_existing_writer_with_local_paths_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    metadata_path = Path("local_metadata.json")
    metadata_path.write_text(json.dumps(_metadata(), sort_keys=True), encoding="utf-8")
    calls: list[tuple[Path, dict[str, object]]] = []

    def writer(path: Path, metadata: dict[str, object]) -> Path:
        calls.append((path, metadata))
        assert path == Path("reports/runtime_cli.json")
        assert metadata == _metadata()
        return path

    result = runtime_artifact_cli.main(
        ["--metadata", "local_metadata.json", "--output", "reports/runtime_cli.json"],
        writer=writer,
    )

    assert result == 0
    assert calls == [(Path("reports/runtime_cli.json"), _metadata())]
    out = capsys.readouterr()
    assert "runtime artifact written: reports/runtime_cli.json" in out.out
    assert "LOCAL_ONLY_OFFLINE_ARTIFACT" in out.out
    assert out.err == ""


@pytest.mark.parametrize(
    "metadata_path",
    [
        "missing.json",
        "metadata.txt",
        "../metadata.json",
        str(Path.cwd() / "metadata.json"),
    ],
)
def test_cli_invalid_or_missing_local_input_exits_nonzero(
    metadata_path: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runtime_artifact_cli.main(
        ["--metadata", metadata_path, "--output", "reports/runtime_cli.json"]
    )

    assert result == 1
    out = capsys.readouterr()
    assert out.out == ""
    assert "runtime artifact CLI failed:" in out.err


def test_cli_does_not_require_exchange_credentials(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("BINANCE_API_KEY", raising=False)
    monkeypatch.delenv("BINANCE_API_SECRET", raising=False)
    metadata_path = Path("local_metadata.json")
    metadata_path.write_text(json.dumps(_metadata(), sort_keys=True), encoding="utf-8")

    result = runtime_artifact_cli.main(
        ["--metadata", "local_metadata.json", "--output", "reports/runtime_cli.json"]
    )

    assert result == 0
    assert Path("reports/runtime_cli.json").is_file()
    out = capsys.readouterr()
    assert "PAPER_ONLY" in out.out
    assert "RESEARCH_ONLY" in out.out
    assert "credential" not in out.out.lower()
    assert os.environ.get("BINANCE_API_KEY") is None
    assert os.environ.get("BINANCE_API_SECRET") is None


def test_cli_module_does_not_alter_gate5b2_startup_contract(tmp_path: Path) -> None:
    assert callable(runtime_artifact_cli.main)
    completed = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "main.py")],
        cwd=tmp_path,
        env={
            "AETHELGARD_CONFIG_PATH": str(PROJECT_ROOT / "config" / "settings.yaml"),
            "HOME": str(tmp_path),
            "PATH": os.environ.get("PATH", ""),
            "PYTHONHASHSEED": "42",
            "PYTHONPATH": str(PROJECT_ROOT),
        },
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
    assert "foundation_runtime_initialized" in completed.stdout
    assert "without execution capabilities" in completed.stdout
    assert "PAPER_ONLY" in completed.stdout
    assert "RESEARCH_ONLY" in completed.stdout
