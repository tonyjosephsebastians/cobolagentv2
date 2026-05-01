# SDK Guide

`cobol_agent` is designed to be embedded in another Python program.

## Configuration

```python
from cobol_agent import CobolAgentConfig

config = CobolAgentConfig(
    openai_api_key="sk-...",
    model="gpt-4.1-mini",
    temperature=0.0,
    provider="openai",
    embedding_model="text-embedding-3-small",
    workspace_dir=".cobol-agent",
    max_context_files=20,
    cache_enabled=True,
)
```

Credential resolution order:

1. `CobolAgentConfig(openai_api_key="...")`
2. `OPENAI_API_KEY`
3. `ConfigurationError`

## Public API

```python
from cobol_agent import CobolAgent, CobolAgentConfig

agent = CobolAgent(CobolAgentConfig(openai_api_key="sk-..."))

index = agent.index_repo("./legacy-cobol")
summary = agent.summarize_repo("./legacy-cobol")
docs = agent.generate_docs("./legacy-cobol", "./docs/generated")
migration = agent.migrate_repo("./legacy-cobol", target="python", output_dir="./migrated")
answer = agent.chat("./legacy-cobol", "What files does CUSTOMER update?")
```

## Testing Without an API Key

Most workflows are deterministic and do not require an LLM. For tests, inject a provider:

```python
class FakeProvider:
    def complete(self, prompt: str) -> str:
        return "fake answer"

agent = CobolAgent(CobolAgentConfig(provider="offline"), provider=FakeProvider())
```

## Return Types

- `IndexResult`: repository path, parsed programs, copybook count, JCL count.
- `SummaryResult`: Markdown summary and index.
- `DocumentationResult`: generated documentation file paths and index.
- `MigrationResult`: generated migration files, report path, target, and index.
