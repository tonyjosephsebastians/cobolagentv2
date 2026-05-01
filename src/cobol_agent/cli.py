"""Command line interface for COBOL Agent."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from cobol_agent.config import CobolAgentConfig
from cobol_agent.events import AgentEvent
from cobol_agent.facade import CobolAgent

app = typer.Typer(help="COBOL Agent SDK command line tools.")
console = Console()


def _observer(event: AgentEvent) -> None:
    console.log(event.message)


def _agent(
    api_key: str | None = None,
    model: str = "gpt-4.1-mini",
    provider: str = "openai",
) -> CobolAgent:
    return CobolAgent(
        CobolAgentConfig(openai_api_key=api_key, model=model, provider=provider),
        observers=[_observer],
    )


@app.command("index")
def index_repo(repo: Path) -> None:
    """Index a COBOL repository."""

    result = _agent(provider="offline").index_repo(repo)
    console.print(f"Indexed {result.program_count} source files")
    console.print(f"Copybooks: {result.copybook_count}")
    console.print(f"JCL files: {result.jcl_count}")


@app.command("summarize")
def summarize_repo(repo: Path) -> None:
    """Print a Markdown summary."""

    result = _agent(provider="offline").summarize_repo(repo)
    console.print(result.content)


@app.command("docs")
def generate_docs(repo: Path, out: Annotated[Path, typer.Option("--out")]) -> None:
    """Generate Markdown documentation."""

    result = _agent(provider="offline").generate_docs(repo, out)
    console.print(f"Wrote {len(result.files)} documentation files to {result.output_dir}")


@app.command("migrate")
def migrate_repo(
    repo: Path,
    target: Annotated[str, typer.Option("--target")] = "python",
    out: Annotated[Path, typer.Option("--out")] = Path("migrated"),
) -> None:
    """Generate migration scaffolds."""

    result = _agent(provider="offline").migrate_repo(repo, target=target, output_dir=out)
    console.print(f"Wrote {len(result.files)} migration files to {result.output_dir}")
    console.print(f"Report: {result.report_path}")


@app.command("chat")
def chat_repo(
    repo: Path,
    question: str,
    api_key: Annotated[str | None, typer.Option("--api-key", help="OpenAI API key.")] = None,
    model: Annotated[str, typer.Option("--model")] = "gpt-4.1-mini",
) -> None:
    """Ask an LLM-backed question about a COBOL repository."""

    answer = _agent(api_key=api_key, model=model).chat(repo, question)
    console.print(answer)
