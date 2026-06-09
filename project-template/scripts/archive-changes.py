#!/usr/bin/env python3
import argparse
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_BY_RISK = {
    "low": ["proposal.md", "verification.md", "review.md"],
    "medium": ["proposal.md", "tasks.md", "verification.md", "review.md"],
    "high": ["proposal.md", "design.md", "tasks.md", "verification.md", "review.md", "ship.md"],
}


def fail(message):
    raise SystemExit(f"[fail] {message}")


def read_boundary_change_root(project_root):
    boundary_path = project_root / ".forgekit" / "project-boundary.yml"
    if not boundary_path.is_file():
        return ".forgekit/changes"

    for raw_line in boundary_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if line.startswith("change_root:"):
            value = line.split(":", 1)[1].strip().strip('"').strip("'")
            return value or ".forgekit/changes"
    return ".forgekit/changes"


def safe_relative_path(value, label):
    path = Path(value)
    if path.is_absolute():
        fail(f"{label} must be a relative path: {value}")
    if any(part == ".." for part in path.parts):
        fail(f"{label} must not contain '..': {value}")
    if path.parts and path.parts[0] == ".git":
        fail(f"{label} must not target .git: {value}")
    return path


def parse_metadata(path):
    metadata = {}
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in raw_line:
            if raw_line.strip():
                break
            continue
        key, value = raw_line.split(":", 1)
        key = key.strip().lower()
        if key in {"status", "risk", "created", "owner", "reason"}:
            metadata[key] = value.strip()
    return metadata


def change_year(metadata):
    created = metadata.get("created", "")
    if len(created) >= 4 and created[:4].isdigit():
        return created[:4], ""
    return str(datetime.now().year), "Created: missing and fallback year used"


def required_check(change_dir, risk):
    required = REQUIRED_BY_RISK.get(risk, [])
    missing = [name for name in required if not (change_dir / name).is_file()]
    if missing:
        return "missing " + ", ".join(missing), missing
    return "ok", []


def build_record(change_dir, project_root, change_root_rel):
    change_id = change_dir.name
    relative = change_dir.relative_to(project_root).as_posix()
    proposal = change_dir / "proposal.md"
    if not proposal.is_file():
        return {
            "group": "blocked",
            "change_id": change_id,
            "from": relative,
            "target": "",
            "risk": "missing",
            "status": "missing",
            "reason": "missing proposal.md",
            "required_check": "missing proposal.md",
            "created_note": "",
        }

    metadata = parse_metadata(proposal)
    status = metadata.get("status", "").lower()
    risk = metadata.get("risk", "").lower()
    reason = metadata.get("reason", "missing")
    year, created_note = change_year(metadata)
    target = f".forgekit/archive/changes/{year}/{change_id}"

    base = {
        "change_id": change_id,
        "from": relative,
        "target": target,
        "risk": risk or "missing",
        "status": status or "missing",
        "reason": reason,
        "created_note": created_note,
    }

    if status == "archived":
        return {**base, "group": "skipped", "required_check": "not checked", "skip_reason": "already archived by status"}
    if status in {"draft", "active"}:
        return {**base, "group": "skipped", "required_check": "not checked", "skip_reason": f"status is {status}"}
    if status != "done":
        return {**base, "group": "blocked", "required_check": "unknown or missing Status metadata"}

    if not risk:
        return {**base, "group": "blocked", "required_check": "missing Risk metadata"}
    if risk not in REQUIRED_BY_RISK:
        return {**base, "group": "blocked", "required_check": f"unknown Risk value: {risk}"}

    check, missing = required_check(change_dir, risk)
    if missing:
        return {**base, "group": "blocked", "required_check": check}
    return {**base, "group": "candidates", "required_check": "ok"}


def section_for_record(record):
    lines = [
        f"### {record['change_id']}",
        "",
        f"- From: `{record['from']}`",
        f"- Target archive path: `{record.get('target') or 'n/a'}`",
        f"- Risk: {record['risk']}",
        f"- Status: {record['status']}",
        f"- Reason: {record['reason']}",
        f"- Required file check: {record['required_check']}",
        "- Current docs sync: not verified by script",
    ]
    if record.get("created_note"):
        lines.append(f"- Created: {record['created_note']}")
    if record.get("skip_reason"):
        lines.append(f"- Skip reason: {record['skip_reason']}")
    return "\n".join(lines)


def write_plan(project_root, change_root_rel, records):
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    groups = {
        "candidates": [item for item in records if item["group"] == "candidates"],
        "blocked": [item for item in records if item["group"] == "blocked"],
        "skipped": [item for item in records if item["group"] == "skipped"],
    }
    lines = [
        "# Archive Plan",
        "",
        f"Generated: {now}",
        "Mode: dry-run",
        "Status: report-only",
        f"ChangeRoot: {change_root_rel.as_posix()}",
        "",
        "This dry-run only creates or overwrites `.forgekit/archive-plan.md`.",
        "It does not move files, change proposal status, rewrite links, update current docs, write business docs, update template-lock, commit, or push.",
        "",
        "## Summary",
        "",
        "| group | count |",
        "| --- | ---: |",
        f"| candidates | {len(groups['candidates'])} |",
        f"| blocked | {len(groups['blocked'])} |",
        f"| skipped | {len(groups['skipped'])} |",
        "",
        "## Candidates",
        "",
    ]
    lines.extend([section_for_record(item) + "\n" for item in groups["candidates"]] or ["None.\n"])
    lines.extend(["## Blocked", ""])
    lines.extend([section_for_record(item) + "\n" for item in groups["blocked"]] or ["None.\n"])
    lines.extend(["## Skipped", ""])
    lines.extend([section_for_record(item) + "\n" for item in groups["skipped"]] or ["None.\n"])

    plan_path = project_root / ".forgekit" / "archive-plan.md"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return plan_path


def run_dry_run(project_root):
    raw_change_root = read_boundary_change_root(project_root)
    change_root_rel = safe_relative_path(raw_change_root, "change_root")
    change_root = project_root / change_root_rel
    records = []
    if change_root.is_dir():
        for child in sorted(change_root.iterdir(), key=lambda item: item.name):
            if not child.is_dir() or child.name == "_template":
                continue
            records.append(build_record(child, project_root, change_root_rel))
    plan_path = write_plan(project_root, change_root_rel, records)
    print(f"[ok] Archive dry-run plan written: {plan_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate a ForgeKit archive dry-run plan.")
    parser.add_argument("--dry-run", action="store_true", help="Generate .forgekit/archive-plan.md without moving or changing project files.")
    args = parser.parse_args()
    if not args.dry_run:
        fail("Only --dry-run is supported in v0.19.0")
    run_dry_run(Path.cwd().resolve())


if __name__ == "__main__":
    main()
