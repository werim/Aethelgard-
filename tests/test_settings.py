from pathlib import Path

import pytest

from src.settings import (
    ConfigurationError,
    OperatingMode,
    ReadinessClassification,
    load_settings,
)

CONFIG = Path("config/settings.yaml")


def test_defaults_remain_paper_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AETHELGARD_MODE", raising=False)
    monkeypatch.delenv("AETHELGARD_READINESS", raising=False)
    settings = load_settings(CONFIG, env_file=None)
    assert settings.mode is OperatingMode.PAPER_ONLY
    assert settings.readiness is ReadinessClassification.RESEARCH_ONLY
    assert settings.allow_exchange_orders is False


def test_live_mode_override_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AETHELGARD_MODE", "LIVE")
    with pytest.raises(ConfigurationError, match="PAPER_ONLY"):
        load_settings(CONFIG, env_file=None)


def test_non_research_readiness_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AETHELGARD_READINESS", "PAPER_RUNTIME_VALIDATED")
    with pytest.raises(ConfigurationError, match="RESEARCH_ONLY"):
        load_settings(CONFIG, env_file=None)


def test_unsafe_yaml_flags_fail_closed(tmp_path: Path) -> None:
    unsafe = tmp_path / "settings.yaml"
    unsafe.write_text(
        CONFIG.read_text().replace(
            "allow_live_trading: false", "allow_live_trading: true"
        )
    )
    with pytest.raises(ConfigurationError, match="LIVE trading"):
        load_settings(unsafe, env_file=None)
