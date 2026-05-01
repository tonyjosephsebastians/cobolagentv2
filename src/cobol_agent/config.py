"""Configuration for the COBOL Agent SDK."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from cobol_agent.errors import ConfigurationError


@dataclass(slots=True)
class CobolAgentConfig:
    """Runtime configuration for :class:`cobol_agent.CobolAgent`.

    Explicit constructor values always win over environment variables.
    """

    openai_api_key: str | None = None
    model: str = "gpt-4.1-mini"
    temperature: float = 0.0
    provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    workspace_dir: str | Path | None = None
    max_context_files: int = 20
    cache_enabled: bool = True

    def resolved_api_key(self) -> str | None:
        """Return the explicit API key or the matching environment fallback."""

        if self.openai_api_key:
            return self.openai_api_key
        if self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        return None

    def require_provider_credentials(self) -> str:
        """Return provider credentials or raise a user-facing configuration error."""

        api_key = self.resolved_api_key()
        if api_key:
            return api_key
        if self.provider == "openai":
            raise ConfigurationError(
                "OpenAI credentials are required. Pass "
                "CobolAgentConfig(openai_api_key='...') or set OPENAI_API_KEY."
            )
        raise ConfigurationError(
            f"No credential resolver is configured for provider '{self.provider}'."
        )

    @property
    def workspace_path(self) -> Path:
        """Return the workspace path used for caches and generated temporary files."""

        return Path(self.workspace_dir or ".cobol-agent").expanduser().resolve()
