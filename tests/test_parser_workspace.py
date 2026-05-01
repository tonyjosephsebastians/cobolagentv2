from __future__ import annotations

from pathlib import Path

from cobol_agent.parser import RegexCobolParser
from cobol_agent.workspace import CobolWorkspace

FIXTURE = Path(__file__).parent / "fixtures" / "sample_cobol"


def test_parser_extracts_common_cobol_facts() -> None:
    path = FIXTURE / "CUSTOMER.cbl"
    program = RegexCobolParser().parse(path, path.read_text())

    assert program.program_id == "CUSTOMER"
    assert "IDENTIFICATION" in program.divisions
    assert "INPUT-OUTPUT" in program.sections
    assert "CUSTREC" in program.copybooks
    assert "VALIDATE-CUSTOMER" in program.calls
    assert "CUSTOMER-FILE" in program.file_declarations
    assert len(program.sql_blocks) == 1


def test_workspace_indexes_cobol_repo() -> None:
    index = CobolWorkspace().index(FIXTURE)

    assert index.program_count == 2
    assert index.copybook_count == 1
    assert index.jcl_count == 0
