"""Data models returned by the SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class CobolProgram:
    """A parsed COBOL or JCL source file."""

    path: Path
    source_type: str
    program_id: str | None = None
    divisions: list[str] = field(default_factory=list)
    sections: list[str] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)
    copybooks: list[str] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)
    file_declarations: list[str] = field(default_factory=list)
    sql_blocks: list[str] = field(default_factory=list)
    lines: int = 0

    @property
    def name(self) -> str:
        return self.program_id or self.path.stem


@dataclass(slots=True)
class IndexResult:
    """Repository indexing result."""

    repo_path: Path
    programs: list[CobolProgram]
    copybook_count: int
    jcl_count: int

    @property
    def program_count(self) -> int:
        return len(self.programs)


@dataclass(slots=True)
class SummaryResult:
    """Summary text generated for a COBOL repository."""

    repo_path: Path
    content: str
    index: IndexResult


@dataclass(slots=True)
class DocumentationResult:
    """Documentation files generated for a COBOL repository."""

    repo_path: Path
    output_dir: Path
    files: list[Path]
    index: IndexResult


@dataclass(slots=True)
class MigrationResult:
    """Migration files generated for a COBOL repository."""

    repo_path: Path
    target: str
    output_dir: Path
    files: list[Path]
    report_path: Path
    index: IndexResult
