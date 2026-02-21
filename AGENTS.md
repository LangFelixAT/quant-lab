# AGENTS.md

## Purpose

This document defines the non-negotiable workflow for AI coding agents
operating in repositories created from this template.

It establishes governance rules, execution discipline, and quality
standards to ensure deterministic, traceable, and production-grade
development.

This file is intentionally project-agnostic and reusable across
projects.

------------------------------------------------------------------------

## Before You Start

Before touching any file, the agent must:

1. Read `AGENTS.md` (this file) in full.
2. Read `spec.md` if it exists — it defines the canonical data
   contracts, module boundaries, and design decisions for this project.
3. Read `brief.md` if it exists — it defines goals, constraints, and
   non-goals.
4. Understand the repository layout:

       find . -type f -not -path "./.git/*" | sort

5. Only then begin implementing the assigned issue.

If any of the above files are missing, flag it before proceeding.

------------------------------------------------------------------------

# Core Principles

1.  **One Issue = One Pull Request**
    -   Each PR must implement exactly one GitHub issue.
    -   No bundled features.
    -   No unrelated refactors.
2.  **Atomic Changes**
    -   Keep PRs small and focused.
    -   If scope expands, create a new issue.
3.  **Determinism**
    -   No hidden randomness.
    -   All computations must be reproducible.
    -   If randomness is required, the seed must be explicit.
    -   Avoid non-deterministic ordering assumptions.
4.  **CI is the Source of Truth**
    -   A PR must not be merged unless CI is green.
    -   All required checks must pass before completion.
5.  **Human-in-the-Loop**
    -   Agents must not merge PRs.
    -   Final approval is always performed by a human reviewer.

------------------------------------------------------------------------

# Non-Negotiables

1.  Never push directly to `main`.
2.  One issue per PR.
3.  No unrelated refactors in issue-focused PRs.
4.  Always run local checks before opening or updating a PR.
5.  Agents do not merge PRs.
6.  Do not introduce new third-party dependencies without explicit
    approval.

------------------------------------------------------------------------

# Standard Workflow

For every assigned issue:

1.  Read the issue fully (goal + acceptance criteria).

2.  Create a new branch:

        git checkout -b <type>/<issue-number>-<short-slug>

3.  Implement only what the issue specifies.

4.  Run local checks:

        make check

    If `make` is unavailable, run the equivalent commands directly.

5.  Commit changes using the required convention.

6.  Push branch:

        git push -u origin <branch-name>

7.  Open Pull Request:

        gh pr create --fill

------------------------------------------------------------------------

# Branch Naming Convention

Use issue-scoped branch names:

-   `feat/<issue-number>-<short-slug>`
-   `fix/<issue-number>-<short-slug>`
-   `chore/<issue-number>-<short-slug>`
-   `docs/<issue-number>-<short-slug>`
-   `refactor/<issue-number>-<short-slug>` (only when explicitly
    requested)

Examples:

-   `feat/123-add-auth-guard`
-   `fix/456-handle-null-profile`

------------------------------------------------------------------------

# Commit Naming Convention

Commits must remain scoped to the issue.

Pattern:

    <type>: <short description> (#<issue-number>)

Examples:

-   `feat: add session timeout middleware (#123)`
-   `fix: guard missing config in startup (#456)`

Keep commits small and focused.

------------------------------------------------------------------------

# PR Title Convention

    <type>: <short description> (#<issue-number>)

Allowed types:

-   `feat`
-   `fix`
-   `chore`
-   `docs`
-   `refactor` (only if explicitly required)

------------------------------------------------------------------------

# Required PR Body Content

Every PR must include:

1.  Issue link line: `Fixes #<issue-number>`
2.  Summary of what changed.
3.  How to verify, including exact commands executed.
4.  Confirmation that local checks were run.

------------------------------------------------------------------------

# Scope Discipline

-   Keep changes strictly limited to issue acceptance criteria.
-   If additional work is discovered, create or request a separate
    issue.
-   Do not silently expand scope.
-   Do not perform broad refactors unless explicitly required.
-   Do not mix planning-only and implementation-only changes in one PR
    unless explicitly required.

------------------------------------------------------------------------

# Architecture and Planning Guardrails

-   Do not modify `SPEC.md`, architecture documents, or planning
    artifacts unless the issue explicitly requires it.
-   Do not change architectural direction without an approved planning
    issue.
-   Planning freeze must be respected once a milestone begins
    implementation.

------------------------------------------------------------------------

# Coding Standards

-   Follow existing project structure.
-   Avoid global mutable state.
-   Prefer pure functions.
-   Keep modules cohesive.
-   Write tests for new functionality when applicable.
-   Do not modify unrelated files.

------------------------------------------------------------------------

# Forbidden Actions

Agents must NOT:

-   Push directly to `main`.
-   Merge their own PR.
-   Rewrite history of `main`.
-   Disable CI checks.
-   Introduce unapproved dependencies.
-   Make large refactors outside issue scope.

------------------------------------------------------------------------

# Definition of Done

An issue is complete when:

-   All acceptance criteria are met.
-   CI is green.
-   Code is formatted and linted.
-   Tests pass (if required).
-   PR is approved and merged by a human.

------------------------------------------------------------------------

# Environment Requirements

The agent execution environment must provide:

-   git
-   GitHub CLI (`gh`) authenticated
-   Python 3.11+ (if Python project)
-   Required dev tools (ruff, pytest, etc.)
-   Ability to run local commands

------------------------------------------------------------------------

# Philosophy

This repository follows disciplined, versioned, issue-driven
development.
Speed is secondary to correctness, traceability, determinism, and
reproducibility.
When in doubt, do less and ask — a small, correct PR
is always preferable to a large, speculative one.
