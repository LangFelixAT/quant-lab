# Issue JSON Schema Contract

This file defines the required shape for planning issue files (for example `planning/issues/v0.json`).

## Top-Level Shape

```json
{
  "version": "v0",
  "milestone": "v0",
  "issues": []
}
```

Required top-level fields:
- `version` (string)
- `milestone` (string)
- `issues` (array of issue objects)

## Required Issue Fields

Each item in `issues` must include all fields below:

- `id` (string, unique within file)
- `title` (string)
- `type` (string: `feature` | `bug` | `chore`)
- `summary` (string)
- `problem` (string)
- `scope` (array of strings)
- `out_of_scope` (array of strings)
- `acceptance_criteria` (array of strings, at least 1)
- `how_to_verify` (array of strings, at least 1)
- `labels` (array of strings)
- `dependencies` (array of issue IDs from this same file)
- `estimate` (string, for example `S`, `M`, `L`, or team format)

No required field may be null or empty.

## Semantics

- `id`: stable planning identifier, example `PF-001`.
- `dependencies`: must reference existing `id` values in the same JSON.
- `acceptance_criteria`: objective done conditions.
- `how_to_verify`: exact commands or manual checks.
- `labels`: include routing and priority labels; include `agent-ready` when ready for implementation.

## Minimal Example Issue

```json
{
  "id": "PF-001",
  "title": "Set up auth middleware",
  "type": "feature",
  "summary": "Add authentication middleware for private routes.",
  "problem": "Private endpoints are reachable without authentication.",
  "scope": [
    "Add middleware module",
    "Apply middleware to private router"
  ],
  "out_of_scope": [
    "SSO integration",
    "Role-based access control"
  ],
  "acceptance_criteria": [
    "Private routes return 401 without a valid token"
  ],
  "how_to_verify": [
    "Run make check",
    "Call private endpoint without token and confirm 401"
  ],
  "labels": [
    "agent-ready",
    "type:feature",
    "priority:p1"
  ],
  "dependencies": [],
  "estimate": "M"
}
```

