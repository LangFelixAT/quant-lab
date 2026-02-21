# Planning Prompt for Codex

Use this prompt in a new project repo created from this template.

```text
You are generating a planning baseline for this repository.

Input context:
- planning/brief.md (filled from planning/BRIEF.template.md)
- AGENTS.md
- planning/ISSUE_SCHEMA.md
- planning/examples/issues.v0.example.json

Produce and update these files:
1) README.md (project-specific; not template-level)
2) SPEC.md
3) ARCHITECTURE.md
4) AGENTS.md additions for project-specific commands, structure, and constraints
5) planning/issues/v0.json conforming strictly to planning/ISSUE_SCHEMA.md

Requirements:
- Keep one issue per PR workflow compatible with AGENTS.md.
- Make issues implementation-ready for an agent.
- Include explicit acceptance criteria and how-to-verify steps per issue.
- Include dependencies where needed using issue IDs from the same JSON file.
- Use labels suitable for prioritization and routing.
- Ensure output is internally consistent and executable.

When done:
- Summarize assumptions.
- Provide a recommended implementation order.
```

