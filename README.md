# COBOL Agent

COBOL Agent is a Python SDK and CLI for documenting, summarizing, analyzing, and
scaffolding migrations for COBOL repositories. It is designed as an embeddable
library first, so another Python application can import the SDK, pass provider
credentials such as an OpenAI API key, and run modernization tasks directly.


## What It Does

- Index COBOL repositories and discover `.cbl`, `.cob`, `.cpy`, and `.jcl` files.
- Extract common COBOL facts: divisions, sections, paragraphs, copybooks, calls,
  file declarations, and embedded SQL blocks.
- Generate repository summaries in Markdown.
- Generate documentation files for each COBOL program/copybook.
- Generate conservative Python migration scaffolds.
- Ask LLM-backed questions about a COBOL repository through a LangChain-compatible
  provider.
- Run deterministic local workflows without an API key for indexing, docs, and
  migration scaffolding.

## Project Status

This is an alpha SDK. The v1 parser is intentionally conservative and regex-based.
It is useful for source inventory, documentation, summarization, and migration
planning. It is not a full COBOL compiler or dialect-complete parser.

The parser, provider, and workflow layers are pluggable so stronger parsers,
additional LLM providers, and additional migration targets can be added without
breaking the public SDK surface.

## Requirements

- Python 3.11 or newer
- `pip`
- Optional: an OpenAI API key for `chat`

## Installation

For development from this repository:

```bash
pip install -e ".[dev]"
```

For OpenAI-backed chat support:

```bash
pip install -e ".[dev,openai]"
```

The local workflows below do not require an API key:

- `index_repo`
- `summarize_repo`
- `generate_docs`
- `migrate_repo`

The `chat` workflow requires a configured provider. OpenAI is the default provider.

## Quickstart: Use As A Python SDK

```python
from cobol_agent import CobolAgent, CobolAgentConfig

agent = CobolAgent(
    CobolAgentConfig(
        openai_api_key="sk-...",
        model="gpt-4.1-mini",
    )
)

summary = agent.summarize_repo("./legacy-cobol")
print(summary.content)

agent.generate_docs("./legacy-cobol", output_dir="./docs/generated")
agent.migrate_repo("./legacy-cobol", target="python", output_dir="./migrated")

answer = agent.chat("./legacy-cobol", "Which programs update customer data?")
print(answer)
```

## API Key Configuration

You can pass the API key directly:

```python
from cobol_agent import CobolAgent, CobolAgentConfig

agent = CobolAgent(
    CobolAgentConfig(
        openai_api_key="sk-...",
        model="gpt-4.1-mini",
        temperature=0.0,
    )
)
```

Or use the `OPENAI_API_KEY` environment variable:

```powershell
$env:OPENAI_API_KEY = "sk-..."
```

```bash
export OPENAI_API_KEY="sk-..."
```

Then create the agent without passing the key:

```python
from cobol_agent import CobolAgent, CobolAgentConfig

agent = CobolAgent(CobolAgentConfig(model="gpt-4.1-mini"))
```

Credential resolution order:

1. `CobolAgentConfig(openai_api_key="...")`
2. `OPENAI_API_KEY`
3. `ConfigurationError`

## SDK Reference

### `CobolAgentConfig`

```python
from cobol_agent import CobolAgentConfig

config = CobolAgentConfig(
    openai_api_key=None,
    model="gpt-4.1-mini",
    temperature=0.0,
    provider="openai",
    embedding_model="text-embedding-3-small",
    workspace_dir=".cobol-agent",
    max_context_files=20,
    cache_enabled=True,
)
```

Fields:

- `openai_api_key`: explicit OpenAI key. If omitted, the SDK checks
  `OPENAI_API_KEY`.
- `model`: chat model used by the LLM-backed workflow.
- `temperature`: provider sampling temperature.
- `provider`: provider name. `openai` and `offline` are available in v1.
- `embedding_model`: reserved for future retrieval/indexing expansion.
- `workspace_dir`: location for future caches and temporary workspace files.
- `max_context_files`: maximum number of source files included in chat context.
- `cache_enabled`: reserved for future cache-aware workflows.

### `CobolAgent`

```python
from cobol_agent import CobolAgent, CobolAgentConfig

agent = CobolAgent(CobolAgentConfig(provider="offline"))
```

#### `index_repo(repo_path)`

Indexes COBOL files and returns parsed repository facts.

```python
index = agent.index_repo("./legacy-cobol")

print(index.repo_path)
print(index.program_count)
print(index.copybook_count)
print(index.jcl_count)

for program in index.programs:
    print(program.name, program.copybooks, program.calls)
```

Returns `IndexResult`:

- `repo_path`
- `programs`
- `copybook_count`
- `jcl_count`
- `program_count`

#### `summarize_repo(repo_path, output_format="markdown")`

Creates a Markdown summary from parsed repository facts.

```python
summary = agent.summarize_repo("./legacy-cobol")
print(summary.content)
```

Returns `SummaryResult`:

- `repo_path`
- `content`
- `index`

#### `generate_docs(repo_path, output_dir)`

Writes Markdown documentation files to `output_dir`.

```python
docs = agent.generate_docs("./legacy-cobol", output_dir="./docs/generated")

for path in docs.files:
    print(path)
```

Generated docs include:

- `README.md` summary
- one Markdown file per detected COBOL source

Returns `DocumentationResult`:

- `repo_path`
- `output_dir`
- `files`
- `index`

#### `migrate_repo(repo_path, target="python", output_dir="migrated")`

Generates Python migration scaffolds and a migration report.

```python
migration = agent.migrate_repo(
    "./legacy-cobol",
    target="python",
    output_dir="./migrated",
)

print(migration.report_path)
print(migration.files)
```

Generated Python files are intentionally conservative. They include:

- module docstrings with review warnings
- a context dataclass placeholder
- an entrypoint function
- comments for detected paragraphs, calls, copybooks, and SQL blocks
- `NotImplementedError` so incomplete migrations fail loudly

Returns `MigrationResult`:

- `repo_path`
- `target`
- `output_dir`
- `files`
- `report_path`
- `index`

#### `chat(repo_path, question)`

Asks an LLM-backed question about a COBOL repository.

```python
agent = CobolAgent(
    CobolAgentConfig(
        openai_api_key="sk-...",
        model="gpt-4.1-mini",
    )
)

answer = agent.chat(
    "./legacy-cobol",
    "Summarize the customer update flow.",
)
print(answer)
```

The chat workflow indexes the repo, builds a bounded source context, and calls the
configured provider through the SDK's provider abstraction.

## Use Without An API Key

Use the `offline` provider for local deterministic tasks and tests:

```python
from cobol_agent import CobolAgent, CobolAgentConfig

agent = CobolAgent(CobolAgentConfig(provider="offline"))

index = agent.index_repo("./legacy-cobol")
summary = agent.summarize_repo("./legacy-cobol")
docs = agent.generate_docs("./legacy-cobol", "./docs/generated")
migration = agent.migrate_repo("./legacy-cobol", output_dir="./migrated")
```

## Inject A Custom Provider

Applications can inject a provider for tests or custom LLM backends:

```python
from cobol_agent import CobolAgent, CobolAgentConfig


class MyProvider:
    def complete(self, prompt: str) -> str:
        return "custom answer"


agent = CobolAgent(
    CobolAgentConfig(provider="offline"),
    provider=MyProvider(),
)

print(agent.chat("./legacy-cobol", "What does this repo do?"))
```

Custom providers only need a `complete(prompt: str) -> str` method.

## CLI Usage

After installation, use:

```bash
cobol-agent index ./legacy-cobol
cobol-agent summarize ./legacy-cobol
cobol-agent docs ./legacy-cobol --out ./docs/generated
cobol-agent migrate ./legacy-cobol --target python --out ./migrated
cobol-agent chat ./legacy-cobol "Summarize the batch flow"
```

CLI notes:

- `index`, `summarize`, `docs`, and `migrate` use deterministic local workflows.
- `chat` uses the configured LLM provider and requires credentials for OpenAI.

## Example Project

This repository includes a small COBOL sample:

```text
examples/sample_cobol/
  CUSTOMER.cbl
  CUSTREC.cpy
```

Run the example:

```bash
python examples/sdk_usage.py
```

Or from Python:

```python
from cobol_agent import CobolAgent, CobolAgentConfig

agent = CobolAgent(CobolAgentConfig(provider="offline"))
agent.generate_docs("examples/sample_cobol", "build/generated-docs")
agent.migrate_repo("examples/sample_cobol", output_dir="build/migrated")
```

## Architecture

COBOL Agent uses several design patterns to keep the SDK extensible:

- Facade: `CobolAgent` exposes the stable public SDK.
- Strategy: parser, provider, and migration target implementations are swappable.
- Adapter: LangChain/OpenAI details stay behind provider/runtime classes.
- Command: SDK and CLI share reusable task commands.
- Pipeline: workflows follow scan, parse, index, render, and write stages.
- Repository: `CobolWorkspace` isolates filesystem access.
- Factory: `ProviderFactory` creates provider strategies from config.
- Observer: `EventBus` emits progress events for CLI output and host apps.

High-level flow:

```text
Python app or CLI
        |
        v
CobolAgent facade
        |
        v
Command object
        |
        v
Workflow pipeline
        |
        v
CobolWorkspace -> Parser -> IndexResult -> Renderer or LLM provider
```

## Generated Migration Output

The Python migration generator is a scaffold generator, not a full automatic COBOL
transpiler. Generated files require human review, especially for:

- packed decimals and numeric precision
- file IO and record layouts
- database access and embedded SQL
- transaction boundaries
- batch scheduling and JCL semantics
- external program calls
- copybook expansion and shared state

## Development

Install development dependencies:

```bash
pip install -e ".[dev,openai]"
```

Run tests:

```bash
python -m pytest
```

Run lint checks:

```bash
python -m ruff check src tests
```

Package install dry-run:

```bash
python -m pip install -e . --dry-run
```

## Repository Layout

```text
src/cobol_agent/
  agents.py       LangChain/provider runtime boundary
  cli.py          Typer CLI
  commands.py     Reusable SDK/CLI commands
  config.py       SDK configuration and credential resolution
  events.py       Observer/event hooks
  facade.py       CobolAgent public facade
  models.py       SDK result models
  parser.py       COBOL parser strategy
  providers.py    LLM provider strategies
  renderers.py    Markdown and Python migration renderers
  workspace.py    Repository discovery and indexing
  workflows.py    Task workflows

docs/              Detailed guides
examples/          Sample COBOL repo and SDK usage
tests/             Unit and CLI tests
```

## Documentation

- [SDK Guide](docs/sdk.md)
- [CLI Guide](docs/cli.md)
- [Architecture](docs/architecture.md)
- [Migration Guide](docs/migration.md)

## License

MIT
