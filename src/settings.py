"""Fail-closed configuration loading for Aethelgard Phase 1."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


class ConfigurationError(ValueError):
    """Raised when configuration violates a declared safety boundary."""


class OperatingMode(StrEnum):
    """Permitted operating modes in Phase 1."""

    PAPER_ONLY = "PAPER_ONLY"


class ReadinessClassification(StrEnum):
    """Readiness states admitted in the foundation release."""

    RESEARCH_ONLY = "RESEARCH_ONLY"


@dataclass(frozen=True)
class Settings:
    """Validated immutable settings used by the safe runtime bootstrap."""

    project_name: str
    phase: str
    mode: OperatingMode
    readiness: ReadinessClassification
    random_seed: int
    log_level: str
    timezone: str
    raw_data_path: Path
    processed_data_path: Path
    cache_data_path: Path
    reports_path: Path
    allow_live_trading: bool
    allow_exchange_orders: bool
    performance_claims_enabled: bool


def _mapping(value: object, section: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigurationError(
            f"Configuration section '{section}' must be a mapping."
        )
    return {str(k): v for k, v in value.items()}


def _bool(value: object, name: str) -> bool:
    if not isinstance(value, bool):
        raise ConfigurationError(f"Configuration value '{name}' must be boolean.")
    return value


def _env_or(source: dict[str, Any], key: str, env_key: str) -> Any:
    return os.environ.get(env_key, source.get(key))


def load_settings(
    config_path: Path | str = Path("config/settings.yaml"),
    env_file: Path | str | None = Path(".env"),
) -> Settings:
    """Load validated settings while refusing unsafe runtime requests."""

    if env_file is not None:
        load_dotenv(dotenv_path=env_file, override=False)
    path = Path(config_path)
    if not path.exists():
        raise ConfigurationError(f"Settings file not found: {path}")
    with path.open("r", encoding="utf-8") as stream:
        raw = yaml.safe_load(stream)
    root = _mapping(raw, "root")
    project = _mapping(root.get("project"), "project")
    runtime = _mapping(root.get("runtime"), "runtime")
    paths = _mapping(root.get("paths"), "paths")
    safety = _mapping(root.get("safety"), "safety")

    mode_value = str(_env_or(runtime, "mode", "AETHELGARD_MODE"))
    readiness_value = str(_env_or(runtime, "readiness", "AETHELGARD_READINESS"))
    try:
        mode = OperatingMode(mode_value)
    except ValueError as exc:
        raise ConfigurationError(
            "Only PAPER_ONLY operating mode is permitted."
        ) from exc
    try:
        readiness = ReadinessClassification(readiness_value)
    except ValueError as exc:
        raise ConfigurationError(
            "Phase 1 readiness must remain RESEARCH_ONLY."
        ) from exc

    try:
        seed = int(_env_or(runtime, "random_seed", "AETHELGARD_RANDOM_SEED"))
    except (TypeError, ValueError) as exc:
        raise ConfigurationError("Random seed must be an integer.") from exc
    if seed < 0:
        raise ConfigurationError("Random seed must be non-negative.")

    settings = Settings(
        project_name=str(project.get("name", "Aethelgard")),
        phase=str(project.get("phase", "FOUNDATION")),
        mode=mode,
        readiness=readiness,
        random_seed=seed,
        log_level=str(_env_or(runtime, "log_level", "AETHELGARD_LOG_LEVEL")).upper(),
        timezone=str(runtime.get("timezone", "UTC")),
        raw_data_path=Path(str(paths.get("raw_data", "data/raw"))),
        processed_data_path=Path(str(paths.get("processed_data", "data/processed"))),
        cache_data_path=Path(str(paths.get("cache_data", "data/cache"))),
        reports_path=Path(str(paths.get("reports", "reports"))),
        allow_live_trading=_bool(
            safety.get("allow_live_trading"), "allow_live_trading"
        ),
        allow_exchange_orders=_bool(
            safety.get("allow_exchange_orders"), "allow_exchange_orders"
        ),
        performance_claims_enabled=_bool(
            safety.get("performance_claims_enabled"), "performance_claims_enabled"
        ),
    )
    if settings.allow_live_trading or settings.allow_exchange_orders:
        raise ConfigurationError(
            "Exchange orders and LIVE trading are prohibited in Phase 1."
        )
    if settings.performance_claims_enabled:
        raise ConfigurationError("Performance claims are prohibited without evidence.")
    return settings
