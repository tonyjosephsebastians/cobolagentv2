"""Workflow pipeline implementations."""

from __future__ import annotations

from pathlib import Path

from cobol_agent.agents import AgentRuntime
from cobol_agent.errors import UnsupportedTargetError
from cobol_agent.events import EventBus
from cobol_agent.models import DocumentationResult, MigrationResult, SummaryResult
from cobol_agent.renderers import MarkdownRenderer, PythonMigrationRenderer
from cobol_agent.workspace import CobolWorkspace


class SummarizationWorkflow:
    """Generate repository summaries."""

    def __init__(self, workspace: CobolWorkspace, events: EventBus) -> None:
        self._workspace = workspace
        self._events = events
        self._renderer = MarkdownRenderer()

    def run(self, repo_path: str | Path, output_format: str = "markdown") -> SummaryResult:
        if output_format != "markdown":
            raise ValueError("Only markdown output is supported in v1.")
        self._events.emit("index.start", "Indexing COBOL repository", repo_path=str(repo_path))
        index = self._workspace.index(repo_path)
        self._events.emit("summary.render", "Rendering repository summary")
        return SummaryResult(
            repo_path=index.repo_path,
            content=self._renderer.render_summary(index),
            index=index,
        )


class DocumentationWorkflow:
    """Generate Markdown documentation for a COBOL repository."""

    def __init__(self, workspace: CobolWorkspace, events: EventBus) -> None:
        self._workspace = workspace
        self._events = events
        self._renderer = MarkdownRenderer()

    def run(self, repo_path: str | Path, output_dir: str | Path) -> DocumentationResult:
        index = self._workspace.index(repo_path)
        output = Path(output_dir).expanduser().resolve()
        output.mkdir(parents=True, exist_ok=True)
        files: list[Path] = []

        summary_path = output / "README.md"
        summary_path.write_text(self._renderer.render_summary(index), encoding="utf-8")
        files.append(summary_path)

        for program in index.programs:
            doc_name = f"{program.name.lower().replace('-', '_')}.md"
            doc_path = output / doc_name
            doc_path.write_text(
                self._renderer.render_program_doc(program, index.repo_path),
                encoding="utf-8",
            )
            files.append(doc_path)
            self._events.emit("docs.write", "Wrote program documentation", path=str(doc_path))

        return DocumentationResult(
            repo_path=index.repo_path,
            output_dir=output,
            files=files,
            index=index,
        )


class MigrationWorkflow:
    """Generate migration scaffolds."""

    def __init__(self, workspace: CobolWorkspace, events: EventBus) -> None:
        self._workspace = workspace
        self._events = events
        self._python_renderer = PythonMigrationRenderer()

    def run(
        self,
        repo_path: str | Path,
        target: str = "python",
        output_dir: str | Path = "migrated",
    ) -> MigrationResult:
        if target.lower() != "python":
            raise UnsupportedTargetError("Only target='python' is supported in v1.")
        index = self._workspace.index(repo_path)
        output = Path(output_dir).expanduser().resolve()
        output.mkdir(parents=True, exist_ok=True)
        generated: list[Path] = []

        for program in index.programs:
            if program.source_type == "jcl":
                continue
            module_path = output / self._python_renderer.module_filename(program)
            module_path.write_text(self._python_renderer.render_module(program), encoding="utf-8")
            generated.append(module_path)
            self._events.emit("migration.write", "Wrote migration scaffold", path=str(module_path))

        report_path = output / "MIGRATION_REPORT.md"
        report_path.write_text(
            self._python_renderer.render_report(index, generated),
            encoding="utf-8",
        )

        return MigrationResult(
            repo_path=index.repo_path,
            target="python",
            output_dir=output,
            files=generated,
            report_path=report_path,
            index=index,
        )


class ChatWorkflow:
    """Answer questions about a COBOL repository."""

    def __init__(
        self,
        workspace: CobolWorkspace,
        runtime: AgentRuntime,
        events: EventBus,
        max_context_files: int,
    ) -> None:
        self._workspace = workspace
        self._runtime = runtime
        self._events = events
        self._max_context_files = max_context_files
        self._renderer = MarkdownRenderer()

    def run(self, repo_path: str | Path, question: str) -> str:
        index = self._workspace.index(repo_path)
        context = self._renderer.render_summary(index)
        snippets = []
        for program in index.programs[: self._max_context_files]:
            source = self._workspace.read_source(program.path)
            snippets.append(f"File: {program.path.name}\n{source[:4000]}")
        prompt = (
            "You are a COBOL modernization assistant. Answer the user question using only "
            "the repository facts and source snippets below.\n\n"
            f"{context}\n\n"
            f"{chr(10).join(snippets)}\n\n"
            f"Question: {question}"
        )
        self._events.emit("chat.invoke", "Invoking agent runtime")
        return self._runtime.answer(prompt)
