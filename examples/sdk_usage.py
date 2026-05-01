from cobol_agent import CobolAgent, CobolAgentConfig


agent = CobolAgent(CobolAgentConfig(provider="offline"))

summary = agent.summarize_repo("examples/sample_cobol")
print(summary.content)

agent.generate_docs("examples/sample_cobol", output_dir="build/generated-docs")
agent.migrate_repo("examples/sample_cobol", target="python", output_dir="build/migrated")
