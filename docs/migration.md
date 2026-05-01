# Migration Guide

`agent.migrate_repo(..., target="python")` generates conservative Python scaffolds from parsed
COBOL source facts.

The generated files are not a complete automatic rewrite. They provide:

- one Python module per COBOL program or copybook source,
- a context dataclass placeholder,
- an entrypoint function,
- comments for detected paragraphs, copybooks, calls, and SQL blocks,
- `MIGRATION_REPORT.md` with source inventory and generated files.

## Recommended Workflow

1. Run `cobol-agent summarize`.
2. Generate docs with `cobol-agent docs`.
3. Generate Python scaffolds with `cobol-agent migrate`.
4. Review file IO, SQL access, numeric precision, batch scheduling, and transaction behavior.
5. Add tests around migrated business rules before production use.

## Limitations

The v1 parser is regex-based. It is useful for inventory, documentation, and migration planning,
but it does not fully understand every COBOL dialect. The parser interface is pluggable so a
Tree-sitter or compiler-backed parser can replace it later.
