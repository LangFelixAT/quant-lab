# Project Factory Template

This repository is a factory template for new software projects.

It provides:
- Enforced PR workflow with CI gates.
- A stable developer and agent contract through `make check`.
- Agent SOP for branch naming, PR structure, and issue linking.
- Planning scaffolding from brief to issue JSON.
- Optional automation to create GitHub issues from planning JSON.

It is not a product repository and not an installable Python package.

## Create a New Project

1. In GitHub, click **Use this template**.
2. Clone your new repository.
3. Open it in VS Code.
4. Start planning from `planning/BRIEF.template.md`.

## Workflow

1. Create or select an issue.
2. Create a branch from the issue (see `AGENTS.md`).
3. Implement in a single PR linked to that issue.
4. Run `make check` locally.
5. Open PR with required template content.
6. CI runs `make check`.
7. Merge PR after review and green checks.

Detailed Lifecycle Guide:
- `planning/PROJECT_LIFECYCLE_GUIDE.md`
- Full step-by-step operations guide from template clone through version-to-version iteration.

## Contract

`make check` is the quality contract for local development, agents, and CI.

In this template it runs:
- `ruff format --check .`
- `ruff check .`
- `pytest -q`

The template includes a smoke test at `tests/test_smoke.py` so `pytest` is stable in fresh repos.

## Planning Scaffolding

Use:
- `planning/BRIEF.template.md`
- `planning/PLANNING_PROMPT.md`
- `planning/ISSUE_SCHEMA.md`
- `planning/examples/issues.v0.example.json`
- `planning/PROJECT_LIFECYCLE_GUIDE.md`

Recommended flow:
1. Copy `planning/BRIEF.template.md` to `planning/brief.md` and fill it.
2. Paste `planning/PLANNING_PROMPT.md` into Codex.
3. Generate project-specific docs and `planning/issues/v0.json`.
4. Commit planning baseline.

## Issue Automation

Script:
- `automation/create_issues.py`

CLI examples:
- `python automation/create_issues.py --input planning/issues/v0.json --mode dry-run --milestone v0`
- `python automation/create_issues.py --input planning/issues/v0.json --mode apply --milestone v0`

GitHub Actions workflow:
- `.github/workflows/create-issues.yml` (manual trigger only)

Behavior:
- `dry-run` is default and makes no API changes.
- `apply` creates/uses milestone and creates issues.

## Security and Permissions

- CI workflow requires read-only repository permissions.
- Create-issues workflow requires:
  - `contents: read`
  - `issues: write`

Use least privilege tokens. Start with manual issue creation workflow triggers for safe rollout.

## Recommended Labels

- `agent-ready`
- `blocked`
- `needs-spec`
- `priority:p0`, `priority:p1`, `priority:p2`
- `type:feature`, `type:bug`, `type:chore`

## How To Use With Codex

Example implementation prompt:

```text
Implement issue #123. Follow AGENTS.md. One PR. Run make check. Open PR with Fixes #123.
```

## Related Files

- Agent SOP: `AGENTS.md`
- CI gate: `.github/workflows/ci.yml`
- PR template: `.github/pull_request_template.md`
- Issue templates: `.github/ISSUE_TEMPLATE/`
