"""LangChain/LangGraph adapter boundary."""

from __future__ import annotations

from cobol_agent.config import CobolAgentConfig
from cobol_agent.providers import LlmProvider, ProviderFactory


class AgentRuntime:
    """Adapter that hides direct LangChain/LangGraph usage from workflows.

    The current workflows are deterministic for documentation and scaffold generation.
    This runtime is used by chat and is the extension point for richer agent workflows.
    """

    def __init__(self, config: CobolAgentConfig, provider: LlmProvider | None = None) -> None:
        self._config = config
        self._provider = provider

    @property
    def provider(self) -> LlmProvider:
        if self._provider is None:
            self._provider = ProviderFactory().create(self._config)
        return self._provider

    def answer(self, prompt: str) -> str:
        return self.provider.complete(prompt)
