# CLI Guide

The CLI is a thin wrapper around the SDK.

## Commands

```bash
cobol-agent index <repo>
cobol-agent summarize <repo>
cobol-agent docs <repo> --out docs/generated
cobol-agent migrate <repo> --target python --out migrated
cobol-agent chat <repo> "question"
```

## Notes

- `index`, `summarize`, `docs`, and `migrate` run locally without an API key.
- `chat` uses the configured LLM provider and requires an OpenAI key unless a custom provider is added.
- Generated documentation and migration files are written outside the source repository unless you choose an output path inside it.
