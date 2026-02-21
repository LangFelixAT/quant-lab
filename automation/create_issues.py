#!/usr/bin/env python3
"""Create GitHub issues from planning JSON with dry-run by default."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


REQUIRED_TOP_LEVEL = ("version", "milestone", "issues")
REQUIRED_ISSUE_FIELDS = (
    "id",
    "title",
    "type",
    "summary",
    "problem",
    "scope",
    "out_of_scope",
    "acceptance_criteria",
    "how_to_verify",
    "labels",
    "dependencies",
    "estimate",
)
ALLOWED_TYPES = {"feature", "bug", "chore"}


class ValidationError(Exception):
    """Raised when issue JSON fails schema validation."""


@dataclass
class ParsedInput:
    version: str
    milestone: str
    issues: list[dict[str, Any]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create GitHub issues from planning JSON."
    )
    parser.add_argument(
        "--input",
        default="planning/issues/v0.json",
        help="Path to issue JSON file (default: planning/issues/v0.json).",
    )
    parser.add_argument(
        "--mode",
        choices=("dry-run", "apply"),
        default="dry-run",
        help="Execution mode. dry-run prints actions, apply calls GitHub API.",
    )
    parser.add_argument(
        "--milestone",
        default=None,
        help="Override milestone title. Defaults to JSON top-level milestone.",
    )
    parser.add_argument(
        "--repo",
        default=os.getenv("GITHUB_REPOSITORY"),
        help="GitHub repository in owner/repo format. Defaults to GITHUB_REPOSITORY env var.",
    )
    parser.add_argument(
        "--ensure-agent-ready",
        action="store_true",
        default=True,
        help="Ensure each issue has the agent-ready label (default: enabled).",
    )
    parser.add_argument(
        "--no-ensure-agent-ready",
        action="store_false",
        dest="ensure_agent_ready",
        help="Disable automatic agent-ready label insertion.",
    )
    return parser.parse_args()


def load_and_validate_input(path: str) -> ParsedInput:
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError as exc:
        raise ValidationError(f"Input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValidationError("Top-level JSON must be an object.")

    for key in REQUIRED_TOP_LEVEL:
        if key not in raw:
            raise ValidationError(f"Missing top-level field: {key}")
        if raw[key] in ("", None):
            raise ValidationError(f"Top-level field {key} cannot be empty.")

    issues = raw["issues"]
    if not isinstance(issues, list) or not issues:
        raise ValidationError("Top-level issues must be a non-empty array.")

    ids: set[str] = set()
    for index, issue in enumerate(issues):
        if not isinstance(issue, dict):
            raise ValidationError(f"Issue at index {index} must be an object.")
        for field in REQUIRED_ISSUE_FIELDS:
            if field not in issue:
                raise ValidationError(f"Issue {index} missing required field: {field}")
            if issue[field] in ("", None):
                raise ValidationError(f"Issue {index} field {field} cannot be empty.")
        issue_id = issue["id"]
        if not isinstance(issue_id, str):
            raise ValidationError(f"Issue index {index} field id must be a string.")
        if issue_id in ids:
            raise ValidationError(f"Duplicate issue id: {issue_id}")
        ids.add(issue_id)

        issue_type = issue["type"]
        if issue_type not in ALLOWED_TYPES:
            raise ValidationError(
                f"Issue {issue_id} has invalid type {issue_type!r}. "
                f"Allowed values: {sorted(ALLOWED_TYPES)}"
            )

        for list_field in (
            "scope",
            "out_of_scope",
            "acceptance_criteria",
            "how_to_verify",
            "labels",
            "dependencies",
        ):
            value = issue[list_field]
            if not isinstance(value, list):
                raise ValidationError(
                    f"Issue {issue_id} field {list_field} must be an array."
                )
            if (
                list_field in ("acceptance_criteria", "how_to_verify")
                and len(value) == 0
            ):
                raise ValidationError(
                    f"Issue {issue_id} field {list_field} must have at least one item."
                )
            if any((not isinstance(item, str) or item.strip() == "") for item in value):
                raise ValidationError(
                    f"Issue {issue_id} field {list_field} must contain non-empty strings."
                )

    for issue in issues:
        issue_id = issue["id"]
        for dep in issue["dependencies"]:
            if dep not in ids:
                raise ValidationError(f"Issue {issue_id} depends on unknown id: {dep}")

    return ParsedInput(
        version=str(raw["version"]), milestone=str(raw["milestone"]), issues=issues
    )


def build_issue_body(issue: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Summary")
    lines.append(issue["summary"])
    lines.append("")
    lines.append("## Problem")
    lines.append(issue["problem"])
    lines.append("")
    lines.append("## Scope")
    for item in issue["scope"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Out of Scope")
    for item in issue["out_of_scope"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Acceptance Criteria")
    for item in issue["acceptance_criteria"]:
        lines.append(f"- [ ] {item}")
    lines.append("")
    lines.append("## How To Verify")
    for item in issue["how_to_verify"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Planning Metadata")
    lines.append(f"- Planning ID: `{issue['id']}`")
    lines.append(f"- Type: `{issue['type']}`")
    lines.append(f"- Estimate: `{issue['estimate']}`")
    if issue["dependencies"]:
        lines.append(
            f"- Dependencies: {', '.join(f'`{dep}`' for dep in issue['dependencies'])}"
        )
    else:
        lines.append("- Dependencies: none")
    return "\n".join(lines)


def github_request(
    method: str,
    path: str,
    token: str,
    body: dict[str, Any] | None = None,
) -> Any:
    url = f"https://api.github.com{path}"
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if body is not None:
        req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as response:
            text = response.read().decode("utf-8")
            return json.loads(text) if text else None
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API error {exc.code} for {method} {path}: {details}"
        ) from exc


def get_or_create_milestone(repo: str, title: str, token: str) -> int:
    milestones = github_request(
        "GET", f"/repos/{repo}/milestones?state=all&per_page=100", token
    )
    for m in milestones:
        if m.get("title") == title:
            return int(m["number"])
    created = github_request(
        "POST",
        f"/repos/{repo}/milestones",
        token,
        body={"title": title},
    )
    return int(created["number"])


def ensure_label(repo: str, label: str, token: str) -> None:
    try:
        github_request(
            "POST",
            f"/repos/{repo}/labels",
            token,
            body={"name": label, "color": "0e8a16"},
        )
    except RuntimeError as exc:
        text = str(exc)
        if "422" in text and "already_exists" in text:
            return
        raise


def create_issue(repo: str, payload: dict[str, Any], token: str) -> int:
    created = github_request("POST", f"/repos/{repo}/issues", token, body=payload)
    return int(created["number"])


def run() -> int:
    args = parse_args()
    try:
        parsed = load_and_validate_input(args.input)
    except ValidationError as exc:
        print(f"VALIDATION_ERROR: {exc}", file=sys.stderr)
        return 2

    milestone_title = args.milestone or parsed.milestone
    if not milestone_title:
        print("VALIDATION_ERROR: milestone cannot be empty", file=sys.stderr)
        return 2

    print(f"Input file: {args.input}")
    print(f"Version: {parsed.version}")
    print(f"Milestone: {milestone_title}")
    print(f"Mode: {args.mode}")
    print(f"Issues: {len(parsed.issues)}")
    print("")

    for issue in parsed.issues:
        labels = list(issue["labels"])
        if args.ensure_agent_ready and "agent-ready" not in labels:
            labels.append("agent-ready")
        print(f"- {issue['id']}: {issue['title']}")
        print(f"  type={issue['type']} estimate={issue['estimate']}")
        print(f"  labels={labels}")
        print(
            f"  dependencies={issue['dependencies'] if issue['dependencies'] else '[]'}"
        )

    if args.mode == "dry-run":
        print("\nDRY_RUN: no GitHub API changes were made.")
        return 0

    if not args.repo:
        print(
            "CONFIG_ERROR: --repo is required in apply mode (or set GITHUB_REPOSITORY).",
            file=sys.stderr,
        )
        return 2

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("AUTH_ERROR: GITHUB_TOKEN is required in apply mode.", file=sys.stderr)
        return 2

    try:
        milestone_number = get_or_create_milestone(args.repo, milestone_title, token)
        print(f"\nUsing milestone number: {milestone_number}")
        created_count = 0
        for issue in parsed.issues:
            labels = list(issue["labels"])
            if args.ensure_agent_ready and "agent-ready" not in labels:
                labels.append("agent-ready")
            for label in labels:
                ensure_label(args.repo, label, token)
            payload = {
                "title": issue["title"],
                "body": build_issue_body(issue),
                "labels": labels,
                "milestone": milestone_number,
            }
            number = create_issue(args.repo, payload, token)
            created_count += 1
            print(f"CREATED: #{number} {issue['title']}")
        print(f"\nSUCCESS: Created {created_count} issues in {args.repo}.")
        return 0
    except RuntimeError as exc:
        print(f"API_ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
