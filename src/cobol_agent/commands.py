"""Reusable command objects shared by SDK and CLI."""

from __future__ import annotations

from pathlib import Path

from cobol_agent.models import DocumentationResult, IndexResult, MigrationResult, SummaryResult
from cobol_agent.workflows import (
    ChatWorkflow,
    DocumentationWorkflow,
    MigrationWorkflow,
    SummarizationWorkflow,
)
from cobol_agent.workspace import CobolWorkspace


class IndexCommand:
    def __init__(self, workspace: CobolWorkspace) -> None:
        self._workspace = workspace

    def execute(self, repo_path: str | Path) -> IndexResult:
        return self._workspace.index(repo_path)


class SummarizeCommand:
    def __init__(self, workflow: SummarizationWorkflow) -> None:
        self._workflow = workflow

    def execute(self, repo_path: str | Path, output_format: str = "markdown") -> SummaryResult:
        return self._workflow.run(repo_path, output_format)


class GenerateDocsCommand:
    def __init__(self, workflow: DocumentationWorkflow) -> None:
        self._workflow = workflow

    def execute(self, repo_path: str | Path, output_dir: str | Path) -> DocumentationResult:
        return self._workflow.run(repo_path, output_dir)


class MigrateCommand:
    def __init__(self, workflow: MigrationWorkflow) -> None:
        self._workflow = workflow

    def execute(
        self,
        repo_path: str | Path,
        target: str = "python",
        output_dir: str | Path = "migrated",
    ) -> MigrationResult:
        return self._workflow.run(repo_path, target, output_dir)


class ChatCommand:
    def __init__(self, workflow: ChatWorkflow) -> None:
        self._workflow = workflow

    def execute(self, repo_path: str | Path, question: str) -> str:
        return self._workflow.run(repo_path, question)
