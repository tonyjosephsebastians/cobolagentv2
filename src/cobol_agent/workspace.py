"""Repository access and indexing."""

from __future__ import annotations

from pathlib import Path

from cobol_agent.models import CobolProgram, IndexResult
from cobol_agent.parser import CobolParser, RegexCobolParser


class CobolWorkspace:
    """Repository pattern around COBOL source discovery and indexing."""

    COBOL_EXTENSIONS = {".cbl", ".cob", ".cpy", ".jcl"}

    def __init__(self, parser: CobolParser | None = None) -> None:
        self._parser = parser or RegexCobolParser()

    def discover_files(self, repo_path: str | Path) -> list[Path]:
        root = Path(repo_path).expanduser().resolve()
        if not root.exists():
            raise FileNotFoundError(f"Repository path does not exist: {root}")
        if root.is_file():
            return [root] if root.suffix.lower() in self.COBOL_EXTENSIONS else []
        return sorted(
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in self.COBOL_EXTENSIONS
        )

    def index(self, repo_path: str | Path) -> IndexResult:
        root = Path(repo_path).expanduser().resolve()
        programs: list[CobolProgram] = []
        for path in self.discover_files(root):
            source = path.read_text(encoding="utf-8", errors="ignore")
            programs.append(self._parser.parse(path, source))

        return IndexResult(
            repo_path=root,
            programs=programs,
            copybook_count=sum(1 for item in programs if item.source_type == "copybook"),
            jcl_count=sum(1 for item in programs if item.source_type == "jcl"),
        )

    def read_source(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="ignore")
