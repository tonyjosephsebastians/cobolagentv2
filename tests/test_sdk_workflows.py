from __future__ import annotations

from pathlib import Path

from cobol_agent import CobolAgent, CobolAgentConfig

FIXTURE = Path(__file__).parent / "fixtures" / "sample_cobol"


class FakeProvider:
    def complete(self, prompt: str) -> str:
        assert "COBOL modernization assistant" in prompt
        return "CUSTOMER reads customer data."


def test_summarize_repo_returns_markdown() -> None:
    agent = CobolAgent(CobolAgentConfig(provider="offline"))

    result = agent.summarize_repo(FIXTURE)

    assert "# COBOL Repository Summary" in result.content
    assert "CUSTOMER" in result.content


def test_generate_docs_writes_markdown(tmp_path: Path) -> None:
    agent = CobolAgent(CobolAgentConfig(provider="offline"))

    result = agent.generate_docs(FIXTURE, tmp_path)

    assert (tmp_path / "README.md").exists()
    assert result.files


def test_migrate_repo_writes_python_scaffold(tmp_path: Path) -> None:
    agent = CobolAgent(CobolAgentConfig(provider="offline"))

    result = agent.migrate_repo(FIXTURE, target="python", output_dir=tmp_path)

    assert (tmp_path / "customer.py").exists()
    assert result.report_path.exists()
    assert "NotImplementedError" in (tmp_path / "customer.py").read_text()


def test_chat_uses_injected_provider() -> None:
    agent = CobolAgent(CobolAgentConfig(provider="offline"), provider=FakeProvider())

    assert agent.chat(FIXTURE, "What does CUSTOMER do?") == "CUSTOMER reads customer data."
