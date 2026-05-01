"""SDK facade."""

from __future__ import annotations

from pathlib import Path

from cobol_agent.agents import AgentRuntime
from cobol_agent.commands import (
    ChatCommand,
    GenerateDocsCommand,
    IndexCommand,
    MigrateCommand,
    SummarizeCommand,
)
from cobol_agent.config import CobolAgentConfig
from cobol_agent.events import EventBus, EventObserver
from cobol_agent.models import DocumentationResult, IndexResult, MigrationResult, SummaryResult
from cobol_agent.providers import LlmProvider
from cobol_agent.workflows import (
    ChatWorkflow,
    DocumentationWorkflow,
    MigrationWorkflow,
    SummarizationWorkflow,
)
from cobol_agent.workspace import CobolWorkspace


class CobolAgent:
    """Facade API for COBOL repository tasks."""

    def __init__(
        self,
        config: CobolAgentConfig | None = None,
        *,
        provider: LlmProvider | None = None,
        observers: list[EventObserver] | None = None,
    ) -> None:
        self.config = config or CobolAgentConfig()
        self.events = EventBus(observers)
        self.workspace = CobolWorkspace()
        self.runtime = AgentRuntime(self.config, provider=provider)

        self._index = IndexCommand(self.workspace)
        self._summarize = SummarizeCommand(SummarizationWorkflow(self.workspace, self.events))
        self._docs = GenerateDocsCommand(DocumentationWorkflow(self.workspace, self.events))
        self._migrate = MigrateCommand(MigrationWorkflow(self.workspace, self.events))
        self._chat = ChatCommand(
            ChatWorkflow(
                self.workspace,
                self.runtime,
                self.events,
                max_context_files=self.config.max_context_files,
            )
        )

    def index_repo(self, repo_path: str | Path) -> IndexResult:
        """Index COBOL files and return parsed repository facts."""

        return self._index.execute(repo_path)

    def summarize_repo(
        self,
        repo_path: str | Path,
        output_format: str = "markdown",
    ) -> SummaryResult:
        """Return a Markdown repository summary."""

        return self._summarize.execute(repo_path, output_format)

    def generate_docs(self, repo_path: str | Path, output_dir: str | Path) -> DocumentationResult:
        """Generate Markdown documentation files."""

        return self._docs.execute(repo_path, output_dir)

    def migrate_repo(
        self,
        repo_path: str | Path,
        target: str = "python",
        output_dir: str | Path = "migrated",
    ) -> MigrationResult:
        """Generate conservative migration scaffolds."""

        return self._migrate.execute(repo_path, target, output_dir)

    def chat(self, repo_path: str | Path, question: str) -> str:
        """Ask an LLM-backed question about the repository."""

        return self._chat.execute(repo_path, question)
