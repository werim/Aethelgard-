"""Aethelgard Phase 1 safe startup entrypoint."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from src.logging_config import configure_logging
from src.runtime import initialize_runtime


def main() -> int:
    """Validate PAPER-only startup and emit non-trading runtime audit metadata."""

    config_path = Path(os.environ.get("AETHELGARD_CONFIG_PATH", "config/settings.yaml"))
    context = initialize_runtime(config_path=config_path)
    configure_logging(context.settings.log_level)
    logger = logging.getLogger("aethelgard.bootstrap")
    logger.info(
        "Foundation runtime initialized without execution capabilities.",
        extra={
            "event": "foundation_runtime_initialized",
            "mode": context.settings.mode.value,
            "readiness": context.settings.readiness.value,
            "random_seed": context.settings.random_seed,
        },
    )
    print(json.dumps(context.audit_record(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
