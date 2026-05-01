# Architecture

COBOL Agent is SDK-first. The CLI calls the same command and workflow objects used by the
public Python API.

## Main Components

- `CobolAgent`: facade for application code.
- `CobolAgentConfig`: runtime and provider configuration.
- `CobolWorkspace`: repository abstraction for file discovery, reading, and indexing.
- `RegexCobolParser`: v1 parser strategy.
- Workflows: documentation, summarization, migration, and chat.
- Commands: reusable task objects shared by SDK and CLI.
- `AgentRuntime`: LangChain/OpenAI adapter boundary.

## Design Patterns

- Facade: `CobolAgent` exposes a small stable API.
- Strategy: parser, provider, and migration target implementations can be swapped.
- Adapter: LangChain/OpenAI details stay behind `AgentRuntime` and provider classes.
- Command: each task has an executable command object.
- Pipeline: workflows follow scan, parse, index, render, and write stages.
- Repository: `CobolWorkspace` isolates filesystem access.
- Factory: `ProviderFactory` creates provider strategies from config.
- Observer: `EventBus` sends progress events to CLI or application observers.

## Extending

To add another migration target, create a renderer/workflow strategy and register it in
`MigrationWorkflow`. To add another LLM provider, implement `LlmProvider` and update
`ProviderFactory`.
