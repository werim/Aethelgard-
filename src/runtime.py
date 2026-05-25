"""Safe Phase 1 runtime bootstrap and reproducibility metadata."""

from __future__ import annotations

import os
import platform
import random
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.settings import Settings, load_settings


@dataclass(frozen=True)
class RuntimeMetadata:
    """Audit metadata emitted at bootstrap, not a trading or performance record."""

    startup_timestamp_utc: str
    python_version: str
    platform: str
    requested_random_seed: int
    pythonhashseed_environment: str
    determinism_scope: str = "PYTHON_RANDOM_SEED_DECLARATION_ONLY"


@dataclass(frozen=True)
class RuntimeContext:
    """The validated Phase 1 configuration and associated startup evidence."""

    settings: Settings
    metadata: RuntimeMetadata

    def audit_record(self) -> dict[str, Any]:
        return {
            "settings": {
                "project_name": self.settings.project_name,
                "phase": self.settings.phase,
                "mode": self.settings.mode.value,
                "readiness": self.settings.readiness.value,
                "random_seed": self.settings.random_seed,
            },
            "metadata": asdict(self.metadata),
        }


def configure_determinism(seed: int) -> RuntimeMetadata:
    """Declare and apply Phase 1 deterministic settings without overclaiming scope."""

    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    return RuntimeMetadata(
        startup_timestamp_utc=datetime.now(UTC).isoformat(),
        python_version=sys.version.split()[0],
        platform=platform.platform(),
        requested_random_seed=seed,
        pythonhashseed_environment=str(seed),
    )


def initialize_runtime(
    config_path: Path | str = Path("config/settings.yaml"),
) -> RuntimeContext:
    """Load safe configuration and return a non-trading foundation context."""

    settings = load_settings(config_path=config_path)
    return RuntimeContext(
        settings=settings, metadata=configure_determinism(settings.random_seed)
    )
