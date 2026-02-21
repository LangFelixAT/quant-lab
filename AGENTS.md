# Agent Operating Procedure

This file defines the non-negotiable workflow for agents in repositories created from this template.

## Non-Negotiables

1. Never push directly to `main`.
2. One issue per PR.
3. No unrelated refactors in issue-focused PRs.
4. Always run `make check` before opening or updating a PR.
5. Agents do not merge PRs.

## Branch Naming

Use issue-scoped branch names:
- `feat/<issue-number>-<short-slug>`
- `fix/<issue-number>-<short-slug>`
- `chore/<issue-number>-<short-slug>`

Examples:
- `feat/123-add-auth-guard`
- `fix/456-handle-null-profile`

## Commit Naming

Keep commits small and scoped to the issue.

Recommended pattern:
- `<type>: <short description> (#<issue-number>)`

Examples:
- `feat: add session timeout middleware (#123)`
- `fix: guard missing config in startup (#456)`

## PR Title Convention

- `<type>: <short description> (#<issue-number>)`

Types:
- `feat`
- `fix`
- `chore`
- `docs`
- `refactor` (only when explicitly requested by the issue)

## Required PR Body Content

Every PR must include:
1. Issue link line: `Fixes #<issue-number>`
2. Summary of what changed.
3. How to verify, with exact commands run and key results.

## PR Scope Discipline

- Keep changes limited to issue acceptance criteria.
- If additional work is discovered, create or request a separate issue.
- Do not mix planning-only and implementation-only changes in one PR unless the issue explicitly requires both.

