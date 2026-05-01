"""LLM provider adapters."""

from __future__ import annotations

from typing import Protocol

from cobol_agent.config import CobolAgentConfig
from cobol_agent.errors import ConfigurationError


class LlmProvider(Protocol):
    """Provider strategy interface."""

    def complete(self, prompt: str) -> str:
        """Return a completion for a prompt."""


class LangChainOpenAIProvider:
    """Adapter for LangChain OpenAI chat models."""

    def __init__(self, config: CobolAgentConfig) -> None:
        api_key = config.require_provider_credentials()
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as exc:
            raise ConfigurationError(
                "Install the OpenAI extra before using the OpenAI provider: "
                "pip install 'cobol-agent[openai]'"
            ) from exc

        self._model = ChatOpenAI(
            api_key=api_key,
            model=config.model,
            temperature=config.temperature,
        )
        self._agent = None
        try:
            from langchain.agents import create_agent

            self._agent = create_agent(
                model=self._model,
                tools=[],
                system_prompt="You are a COBOL modernization assistant.",
            )
        except Exception:
            # Some environments have mismatched LangChain/LangGraph versions.
            # Keep the provider usable and let dependency checks catch this separately.
            self._agent = None

    def complete(self, prompt: str) -> str:
        if self._agent is not None:
            response = self._agent.invoke({"messages": [{"role": "user", "content": prompt}]})
            messages = response.get("messages", []) if isinstance(response, dict) else []
            if messages:
                content = getattr(messages[-1], "content", messages[-1])
                return str(content)
        response = self._model.invoke(prompt)
        content = getattr(response, "content", response)
        if isinstance(content, list):
            return "\n".join(str(item) for item in content)
        return str(content)


class OfflineProvider:
    """Deterministic provider useful for tests and local dry runs."""

    def complete(self, prompt: str) -> str:
        return prompt


class ProviderFactory:
    """Factory for provider strategies."""

    def create(self, config: CobolAgentConfig) -> LlmProvider:
        if config.provider == "openai":
            return LangChainOpenAIProvider(config)
        if config.provider == "offline":
            return OfflineProvider()
        raise ConfigurationError(f"Unsupported provider: {config.provider}")
