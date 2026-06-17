"""Gate 5B-2 regression coverage for the safe main.py startup contract."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_OUTPUT_FRAGMENTS = (
    "LIVE",
    "LIVE_READY",
    "PRODUCTION_READY",
    "api_key",
    "secret",
    "place order",
    "placing order",
    "order placed",
    "cancel order",
    "market fetch success",
    "fetched market",
    "trade signal",
    "optimizer result",
    "pnl",
    "win rate",
    "sharpe",
    "drawdown",
)


def test_main_startup_contract_remains_paper_only_research_only_and_offline(
    tmp_path: Path,
) -> None:
    env = {
        "AETHELGARD_CONFIG_PATH": str(PROJECT_ROOT / "config" / "settings.yaml"),
        "HOME": str(tmp_path),
        "PATH": os.environ.get("PATH", ""),
        "PYTHONHASHSEED": "42",
        "PYTHONPATH": str(PROJECT_ROOT),
    }

    completed = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "main.py")],
        cwd=tmp_path,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
    assert "foundation_runtime_initialized" in completed.stdout
    assert "without execution capabilities" in completed.stdout

    payload = _extract_final_startup_payload(completed.stdout)
    settings = _mapping(payload["settings"])
    metadata = _mapping(payload["metadata"])

    assert settings["mode"] == "PAPER_ONLY"
    assert settings["readiness"] == "RESEARCH_ONLY"
    assert (
        metadata.get("requested_random_seed") == 42 or settings.get("random_seed") == 42
    )
    assert metadata["pythonhashseed_environment"] == "42"

    normalized_stdout = completed.stdout.lower()
    for forbidden in FORBIDDEN_OUTPUT_FRAGMENTS:
        assert forbidden.lower() not in normalized_stdout


def _extract_final_startup_payload(stdout: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    candidates: list[dict[str, Any]] = []
    for index, char in enumerate(stdout):
        if char != "{":
            continue
        try:
            value, _ = decoder.raw_decode(stdout[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and {"metadata", "settings"}.issubset(value):
            candidates.append(value)

    assert candidates, stdout
    return candidates[-1]


def _mapping(value: object) -> dict[str, Any]:
    assert isinstance(value, dict)
    return value
