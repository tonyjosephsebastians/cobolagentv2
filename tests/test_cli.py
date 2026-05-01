from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from cobol_agent.cli import app

FIXTURE = Path(__file__).parent / "fixtures" / "sample_cobol"


def test_cli_index() -> None:
    result = CliRunner().invoke(app, ["index", str(FIXTURE)])

    assert result.exit_code == 0
    assert "Indexed 2 source files" in result.output


def test_cli_docs(tmp_path: Path) -> None:
    result = CliRunner().invoke(app, ["docs", str(FIXTURE), "--out", str(tmp_path)])

    assert result.exit_code == 0
    assert (tmp_path / "README.md").exists()


def test_cli_migrate(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        ["migrate", str(FIXTURE), "--target", "python", "--out", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert (tmp_path / "customer.py").exists()
