#!/usr/bin/env python3
"""Validate the approved v0.45.0 atomic rule ownership matrix."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath


MATRIX_HEADER = "| rule_id | rule | normative_owner | application_sites | deterministic_enforcement | migration_action |"
EXPECTED_SHARED = {
    "ENTRY-BOUNDARY": "project-template/governance/agent-entry-contract.md#project-and-write-boundary",
    "ENTRY-EVIDENCE": "project-template/governance/agent-entry-contract.md#evidence-and-no-fabrication",
    "ENTRY-AUDIT": "project-template/governance/agent-entry-contract.md#audit-default",
    "ENTRY-AUTH": "project-template/governance/agent-entry-contract.md#bounded-local-authorization",
    "ENTRY-EXTERNAL": "project-template/governance/agent-entry-contract.md#external-and-irreversible-actions",
    "WRITEBACK-BASE": "project-template/governance/agent-entry-contract.md#minimum-evidence-based-writeback",
    "SKILL-ROUTING": "project-template/governance/agent-entry-contract.md#skill-routing",
}
ROOT_ROUTE_PREFIX = "ROUTE-"
CLAUDE_PREFIX = "CLAUDE-"
FORBIDDEN_OWNER_TEXT = ("对应文件", "共享合同", "各 Skill", "AGENTS/CLAUDE", "*", "?", "{", "}", "<", ">")


class OwnershipError(ValueError):
    pass


def slug(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"[\s-]+", "-", text).strip("-")


def split_owner(owner: str) -> tuple[str, str | None]:
    if owner.count("#") > 1:
        raise OwnershipError(f"owner has multiple anchors: {owner}")
    path, separator, anchor = owner.partition("#")
    return path, anchor if separator else None


def validate_owner(repo: Path, rule_id: str, owner: str) -> None:
    if any(marker in owner for marker in FORBIDDEN_OWNER_TEXT):
        raise OwnershipError(f"{rule_id} has a wildcard, placeholder, or natural-language owner: {owner}")
    path_text, anchor = split_owner(owner)
    if "\\" in path_text or re.match(r"^[A-Za-z]:", path_text):
        raise OwnershipError(f"{rule_id} owner is not a POSIX repository-relative path: {owner}")
    path = PurePosixPath(path_text)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise OwnershipError(f"{rule_id} owner is unsafe: {owner}")
    full = repo.joinpath(*path.parts)
    if not full.is_file():
        raise OwnershipError(f"{rule_id} owner file does not exist: {path_text}")
    if full.is_dir():
        raise OwnershipError(f"{rule_id} owner must be one concrete file: {path_text}")
    if anchor:
        headings = {
            slug(match.group(1))
            for match in re.finditer(r"^#{1,6}\s+(.+?)\s*$", full.read_text(encoding="utf-8"), re.MULTILINE)
        }
        if anchor not in headings:
            raise OwnershipError(f"{rule_id} owner anchor does not exist: {owner}")


def parse_matrix(design: Path) -> list[dict[str, str]]:
    lines = design.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index(MATRIX_HEADER)
    except ValueError as exc:
        raise OwnershipError("approved ownership matrix header was not found") from exc
    rows = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6:
            raise OwnershipError(f"matrix row must have six cells: {line}")
        owner_match = re.fullmatch(r"`([^`]+)`", cells[2])
        if not owner_match:
            raise OwnershipError(f"normative owner must be one backticked concrete path: {cells[0]}")
        rows.append(
            dict(
                rule_id=cells[0],
                rule=cells[1],
                owner=owner_match.group(1),
                application_sites=cells[3],
                deterministic_enforcement=cells[4],
                migration_action=cells[5],
            )
        )
    return rows


def validate_projection_manifest(repo: Path, root_routes: list[dict[str, str]]) -> None:
    manifest_path = repo / "config/skill-projections.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OwnershipError(f"cannot read projection manifest: {exc}") from exc
    entries = manifest.get("entries") if isinstance(manifest, dict) else None
    if not isinstance(entries, list):
        raise OwnershipError("projection manifest entries must be an array")
    manifest_skills = [entry.get("skill") for entry in entries if isinstance(entry, dict)]
    route_skills = [PurePosixPath(row["owner"]).parts[1] for row in root_routes]
    if len(manifest_skills) != len(set(manifest_skills)) or set(manifest_skills) != set(route_skills):
        raise OwnershipError(
            "projection manifest Skills must equal the nine ROUTE owners derived from the approved ownership matrix"
        )


def validate(repo: Path, design_relative: str) -> list[dict[str, str]]:
    design = repo / design_relative
    rows = parse_matrix(design)
    if len(rows) != 41:
        raise OwnershipError(f"expected 41 ownership rules, actual {len(rows)}")
    ids = [row["rule_id"] for row in rows]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        raise OwnershipError("duplicate rule IDs: " + ", ".join(duplicates))
    by_id = {row["rule_id"]: row for row in rows}
    for row in rows:
        validate_owner(repo, row["rule_id"], row["owner"])
        if row["owner"].startswith("project-template/.agents/"):
            raise OwnershipError(f".agents is a managed projection, not an owner: {row['rule_id']}")
    for rule_id, owner in EXPECTED_SHARED.items():
        row = by_id.get(rule_id)
        if not row or row["owner"] != owner:
            raise OwnershipError(f"{rule_id} owner must be {owner}")
        if "project-template/AGENTS.md" not in row["application_sites"] or "project-template/CLAUDE.md" not in row["application_sites"]:
            raise OwnershipError(f"{rule_id} must list AGENTS and CLAUDE as application sites")
    if by_id.get("REVIEW-CONVERGENCE", {}).get("owner") != "skills/code-review/SKILL.md":
        raise OwnershipError("REVIEW-CONVERGENCE must be owned by skills/code-review/SKILL.md")
    root_routes = [row for row in rows if row["rule_id"].startswith(ROOT_ROUTE_PREFIX)]
    if len(root_routes) != 9 or any(not row["owner"].startswith("skills/") or not row["owner"].endswith("/SKILL.md") for row in root_routes):
        raise OwnershipError("the nine common Skill routes must use concrete root SKILL.md owners")
    validate_projection_manifest(repo, root_routes)
    claude_rows = [row for row in rows if row["rule_id"].startswith(CLAUDE_PREFIX) and row["rule_id"] != "CLAUDE-ENTRY-ADAPTER"]
    if len(claude_rows) != 6 or any("project-template/.claude/skills/" not in row["owner"] for row in claude_rows):
        raise OwnershipError("the six Claude Skill rules must use concrete Claude SKILL.md owners")
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument(
        "--design",
        default=".forgekit/changes/v045-rule-ownership-skill-convergence/design.md",
    )
    args = parser.parse_args(argv)
    try:
        rows = validate(Path(args.repo_root).resolve(), args.design)
    except (OSError, UnicodeError, OwnershipError) as exc:
        print(f"[fail] Rule ownership: {exc}", file=sys.stderr)
        return 1
    print(f"[ok] Rule ownership passed: {len(rows)} unique rules, one concrete owner each")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
