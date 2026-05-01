from __future__ import annotations

import pytest

from cobol_agent import CobolAgentConfig, ConfigurationError


def test_explicit_openai_key_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    config = CobolAgentConfig(openai_api_key="explicit-key")

    assert config.resolved_api_key() == "explicit-key"


def test_openai_key_falls_back_to_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")

    assert CobolAgentConfig().resolved_api_key() == "env-key"


def test_missing_openai_key_raises_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ConfigurationError, match="OpenAI credentials are required"):
        CobolAgentConfig().require_provider_credentials()
