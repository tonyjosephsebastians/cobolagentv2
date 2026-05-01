"""Pluggable COBOL parsing strategies."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Protocol

from cobol_agent.models import CobolProgram


class CobolParser(Protocol):
    """Parser strategy interface."""

    def parse(self, path: Path, source: str) -> CobolProgram:
        """Parse one COBOL source file."""


class RegexCobolParser:
    """Conservative regex parser for common COBOL and JCL facts."""

    _program_id = re.compile(r"\bPROGRAM-ID\.\s*([A-Z0-9_-]+)", re.IGNORECASE)
    _division = re.compile(r"^\s*([A-Z0-9 -]+)\s+DIVISION\.", re.IGNORECASE | re.MULTILINE)
    _section = re.compile(r"^\s*([A-Z0-9 -]+)\s+SECTION\.", re.IGNORECASE | re.MULTILINE)
    _copy = re.compile(r"\bCOPY\s+([A-Z0-9_.-]+)", re.IGNORECASE)
    _call = re.compile(r"\bCALL\s+['\"]?([A-Z0-9_.-]+)['\"]?", re.IGNORECASE)
    _select = re.compile(
        r"^\s*SELECT\s+([A-Z0-9_-]+)\s+ASSIGN",
        re.IGNORECASE | re.MULTILINE,
    )
    _fd = re.compile(r"^\s*FD\s+([A-Z0-9_-]+)", re.IGNORECASE | re.MULTILINE)
    _sql = re.compile(r"EXEC\s+SQL(.*?)END-EXEC", re.IGNORECASE | re.DOTALL)
    _paragraph = re.compile(r"^\s{0,7}([A-Z0-9][A-Z0-9_-]*)\.\s*$", re.IGNORECASE | re.MULTILINE)

    def parse(self, path: Path, source: str) -> CobolProgram:
        source_type = self._source_type(path)
        program_match = self._program_id.search(source)
        divisions = self._dedupe(self._division.findall(source))
        sections = self._dedupe(self._section.findall(source))
        copybooks = self._dedupe(self._copy.findall(source))
        calls = self._dedupe(self._call.findall(source))
        file_declarations = self._dedupe(
            [*self._select.findall(source), *self._fd.findall(source)]
        )
        sql_blocks = [self._normalize(block) for block in self._sql.findall(source)]
        paragraphs = [
            item
            for item in self._dedupe(self._paragraph.findall(source))
            if item.upper() not in {"END-IF", "END-EVALUATE", "END-PERFORM"}
        ]

        return CobolProgram(
            path=path,
            source_type=source_type,
            program_id=program_match.group(1) if program_match else None,
            divisions=divisions,
            sections=sections,
            paragraphs=paragraphs,
            copybooks=copybooks,
            calls=calls,
            file_declarations=file_declarations,
            sql_blocks=sql_blocks,
            lines=len(source.splitlines()),
        )

    def _source_type(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".cpy":
            return "copybook"
        if suffix == ".jcl":
            return "jcl"
        return "program"

    def _dedupe(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            normalized = self._normalize(value).upper()
            if normalized and normalized not in seen:
                seen.add(normalized)
                result.append(normalized)
        return result

    def _normalize(self, value: str) -> str:
        return " ".join(value.strip().strip(".;,").split())
