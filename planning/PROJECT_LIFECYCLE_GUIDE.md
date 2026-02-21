# Project Lifecycle Guide (Windows-first)

## 1. Purpose and Audience

This guide is for repository owners and Codex users who want a repeatable way to build projects from this template.

It covers the full lifecycle:
- Create a repo from template
- Plan `v0` and generate atomic tasks
- Execute issue-by-issue with Codex + PR workflow
- Close `v0` and transition into `v1`

## 2. Prerequisites

Required tools:
- Git
- Python 3.12+
- `ruff`
- `pytest`

Optional tools:
- `make` (recommended; otherwise use direct check commands)
- GitHub CLI `gh` (for CLI PR creation fallback)

Auth prerequisites:
- Access to the target GitHub repository
- `GITHUB_TOKEN` with issue write permission when running issue creation in apply mode

Quick validation commands (PowerShell):

```powershell
python --version
ruff --version
pytest --version
gh --version
```

If `gh` is not installed, skip it and use GitHub UI for PR creation.

## 3. Day 0: Create Project From Template

1. Open this template on GitHub and click **Use this template**.
2. Enter repository name/visibility and create repository.
3. Clone locally:

```powershell
git clone <repo-url>
cd <repo-name>
```

4. Open the repository in VS Code.
5. Run quality gate:
   Preferred:

```powershell
make check
```

Fallback when `make` is unavailable:

```powershell
ruff format --check .
ruff check .
pytest -q
```

## 4. Planning Phase (Generate v0)

1. Create working brief:

```powershell
Copy-Item planning/BRIEF.template.md planning/brief.md
```

2. Fill `planning/brief.md` with concrete scope and constraints.
3. Copy/paste `planning/PLANNING_PROMPT.md` into Codex.
4. Ask Codex to generate:
   - Project `README.md`
   - `SPEC.md`
   - `ARCHITECTURE.md`
   - Project-specific additions in `AGENTS.md`
   - `planning/issues/v0.json` conforming to `planning/ISSUE_SCHEMA.md`
5. Validate generated issue file shape against `planning/ISSUE_SCHEMA.md`.
6. Commit planning baseline (`v0` docs + issue file).

## 5. Create GitHub Issues for v0

1. Run dry-run first:

```powershell
python automation/create_issues.py --input planning/issues/v0.json --mode dry-run --milestone v0
```

2. If dry-run output is correct, apply:

```powershell
python automation/create_issues.py --input planning/issues/v0.json --mode apply --milestone v0
```

3. Confirm on GitHub:
   - Milestone `v0` exists
   - Issues were created
   - Labels (especially `agent-ready`) look correct

## 6. Execution Loop for Each Atomic v0 Issue

For each issue labeled `agent-ready`:

1. Select one issue only.
2. Prompt Codex with strict scope:
   - implement only that issue
   - create issue-scoped branch
   - run `make check`
   - prepare PR with `Fixes #<issue>`
3. Ensure scope discipline from `AGENTS.md` (no unrelated refactors).
4. Ensure CI passes on PR.
5. Human reviews and merges.
6. Repeat for next issue.

Reusable prompt:

```text
Implement issue #X. Follow AGENTS.md. One issue, one PR. Create branch <type>/<id>-<slug>. Run make check. Open PR with Fixes #X, summary, and verification steps.
```

## 7. PR Creation Paths (Preferred + Fallback)

Preferred (Codex-assisted):
1. Codex creates branch, changes, commits, and PR-ready description.
2. Push branch and open PR.

Fallback A (GitHub UI):
1. Push branch.
2. Open repository in GitHub.
3. Click compare/open PR.
4. Fill `.github/pull_request_template.md` fields.

Fallback B (`gh` CLI):

```powershell
gh pr create --fill --title "feat: short summary (#X)" --body-file .github/pull_request_template.md
```

If needed, create a custom body file that includes `Fixes #X`, summary, and verify steps.

## 8. Definition of Done for v0

`v0` is complete when all are true:
- All milestone `v0` issues are closed
- No open PRs targeting `v0`
- CI is green on `main`
- `README.md`, `SPEC.md`, and `ARCHITECTURE.md` reflect shipped behavior
- Carryover work is explicitly documented for next version

## 9. Transition v0 -> v1

1. Create next brief:

```powershell
Copy-Item planning/BRIEF.template.md planning/brief.v1.md
```

2. Document learnings from `v0`:
   - shipped items
   - slipped items
   - defects/incidents
   - constraint changes
3. Update `SPEC.md` and `ARCHITECTURE.md` for `v1` deltas.
4. Use Codex to generate `planning/issues/v1.json` (same schema).
5. Dry-run/apply issue creation for milestone `v1`:

```powershell
python automation/create_issues.py --input planning/issues/v1.json --mode dry-run --milestone v1
python automation/create_issues.py --input planning/issues/v1.json --mode apply --milestone v1
```

6. Start the same issue-by-issue implementation loop for `v1`.
7. Keep all versioned planning artifacts in repo history.

## 10. Modeling Rules for Versioned Backlogs

- Never overwrite previous version issue files (`v0.json`, `v1.json`, `v2.json`).
- Carryovers must be explicit:
  - either create new IDs for re-scoped work, or
  - include clear carryover mapping notes in issue content.
- Dependencies in a version file must reference IDs in that same file.
- Use one milestone per version (`v0`, `v1`, `v2`, ...).

## 11. Troubleshooting

`make` not found on Windows:
- Use direct commands (`ruff format --check .`, `ruff check .`, `pytest -q`) or run in WSL.

`AUTH_ERROR: GITHUB_TOKEN is required`:
- Set token in environment before apply mode:

```powershell
$env:GITHUB_TOKEN = "<token>"
```

Schema validation errors:
- Check all required fields in `planning/ISSUE_SCHEMA.md`.
- Confirm dependency IDs exist in same issue file.

CI failures (format/lint/test):
- Run the same checks locally.
- Fix formatting/lint/test failures before updating PR.

## 12. Copy/Paste Checklists

### New Project Kickoff Checklist

- [ ] Create repo from template
- [ ] Clone locally and open in VS Code
- [ ] Run `make check` (or fallback commands)
- [ ] Create and fill `planning/brief.md`
- [ ] Run planning prompt via Codex
- [ ] Review generated docs and `planning/issues/v0.json`
- [ ] Commit planning baseline
- [ ] Dry-run then apply issue creation for milestone `v0`
- [ ] Start implementation with one `agent-ready` issue

### v0 -> v1 Kickoff Checklist

- [ ] Confirm all `v0` issues closed and CI green on `main`
- [ ] Create `planning/brief.v1.md`
- [ ] Record v0 learnings and update specs/architecture
- [ ] Generate `planning/issues/v1.json` with Codex
- [ ] Dry-run and apply issue creation for `v1`
- [ ] Start v1 issue execution loop (one issue per PR)

