#!/usr/bin/env python3
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_BY_RISK = {
    "low": ["proposal.md", "verification.md", "review.md"],
    "medium": ["proposal.md", "tasks.md", "verification.md", "review.md"],
    "high": ["proposal.md", "design.md", "tasks.md", "verification.md", "review.md", "ship.md"],
}

FORBIDDEN_PATH_PREFIXES = (
    ".forgekit/docs/",
    "docs/",
    "src/",
    "tests/",
    "scripts/",
    ".forgekit/upgrade-export/",
    ".git/",
)

FORBIDDEN_EXACT_PATHS = {
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".forgekit/template-lock.json",
    ".forgekit/upgrade-report.md",
}

REFERENCE_REPORT = ".forgekit/archive-reference-report.md"


def fail(message):
    raise SystemExit(f"[fail] {message}")


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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
    normalized = path.as_posix()
    if normalized == ".git" or normalized.startswith(".git/"):
        fail(f"{label} must not target .git: {value}")
    return path


def normalize_rel(value):
    return safe_relative_path(value.strip().strip("`"), "path").as_posix()


def forbidden_path(path_value):
    normalized = normalize_rel(path_value)
    if normalized in FORBIDDEN_EXACT_PATHS:
        return True
    return any(normalized == prefix.rstrip("/") or normalized.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES)


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
    return str(datetime.now().year), "missing and fallback year used"


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


def archive_status_for_group(group):
    if group == "candidates":
        return "candidate"
    if group == "blocked":
        return "blocked"
    return "skipped"


def section_for_record(record):
    lines = [
        f"### {record['change_id']}",
        "",
        f"Archive-Status: {archive_status_for_group(record['group'])}",
        f"From: {record['from']}",
        f"To: {record.get('target') or 'n/a'}",
        f"Risk: {record['risk']}",
        f"Status: {record['status']}",
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
    groups = {
        "candidates": [item for item in records if item["group"] == "candidates"],
        "blocked": [item for item in records if item["group"] == "blocked"],
        "skipped": [item for item in records if item["group"] == "skipped"],
    }
    lines = [
        "# Archive Plan",
        "",
        f"Generated: {utc_now()}",
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


def parse_plan(plan_path):
    if not plan_path.is_file():
        fail(f"Plan file not found: {plan_path}")
    lines = plan_path.read_text(encoding="utf-8", errors="replace").splitlines()
    if "Mode: dry-run" not in lines or "Status: report-only" not in lines:
        fail("Plan must contain 'Mode: dry-run' and 'Status: report-only'")

    entries = []
    current = None
    for line in lines:
        if line.startswith("### "):
            if current:
                entries.append(current)
            current = {"change_id": line[4:].strip()}
            continue
        if current is None or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key in {"Archive-Status", "From", "To", "Risk", "Status"}:
            current[key] = value.strip()
    if current:
        entries.append(current)
    return [item for item in entries if item.get("Archive-Status") == "candidate"]


def reference_patterns(entry):
    change_id = entry.get("change_id", "")
    candidate_path = entry.get("From", "")
    patterns = [change_id]
    if candidate_path:
        normalized = candidate_path.replace("\\", "/")
        patterns.extend([normalized, normalized.replace("/", "\\")])
    return [item for item in dict.fromkeys(patterns) if item]


def read_change_status(change_dir):
    proposal = change_dir / "proposal.md"
    if not proposal.is_file():
        return "missing"
    return parse_metadata(proposal).get("status", "missing").lower() or "missing"


def iter_reference_files(project_root, candidate_source):
    excluded_prefixes = (
        ".forgekit/archive/",
        ".forgekit/upgrade-export/",
        ".forgekit/changes/_template/",
    )
    excluded_exact = {
        ".forgekit/archive-plan.md",
        ".forgekit/archive-apply-report.md",
        REFERENCE_REPORT,
    }
    candidate_prefix = candidate_source.rstrip("/") + "/"

    files = []
    docs_root = project_root / ".forgekit" / "docs"
    if docs_root.is_dir():
        files.extend(("current_docs", path) for path in docs_root.rglob("*.md") if path.is_file())

    changes_root = project_root / ".forgekit" / "changes"
    if changes_root.is_dir():
        for change_dir in sorted(changes_root.iterdir(), key=lambda item: item.name):
            if not change_dir.is_dir() or change_dir.name == "_template":
                continue
            status = read_change_status(change_dir)
            if status in {"done", "archived"}:
                continue
            files.extend(("active_change", path) for path in change_dir.rglob("*.md") if path.is_file())

    for name in ("README.md", "AGENTS.md", "CLAUDE.md"):
        path = project_root / name
        if path.is_file():
            files.append(("entry_doc", path))

    for kind, path in files:
        relative = path.relative_to(project_root).as_posix()
        if relative in excluded_exact:
            continue
        if any(relative.startswith(prefix) for prefix in excluded_prefixes):
            continue
        if relative == candidate_source or relative.startswith(candidate_prefix):
            continue
        yield kind, path, relative


def find_references(project_root, entry):
    patterns = reference_patterns(entry)
    references = []
    candidate_source = entry.get("From", "")
    for kind, path, relative in iter_reference_files(project_root, candidate_source):
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for line_number, line in enumerate(lines, start=1):
            if any(pattern in line for pattern in patterns):
                references.append({"kind": kind, "path": relative, "line": line_number})
    return references


def classify_reference(entry, references):
    required = {"change_id", "From", "To", "Risk", "Status"}
    if required - set(entry):
        return "manual_review_needed"
    if any(item["kind"] == "active_change" for item in references):
        return "referenced_by_active_change"
    if any(item["kind"] == "current_docs" for item in references):
        return "referenced_by_current_docs"
    if any(item["kind"] == "entry_doc" for item in references):
        return "manual_review_needed"
    return "safe_no_references"


def reference_section(record):
    lines = [
        f"### {record['change_id']}",
        "",
        f"Reference-Status: {record['category']}",
        f"Change: {record['change_id']}",
        f"Candidate-Path: {record.get('from') or 'missing'}",
        f"Target-Archive-Path: {record.get('to') or 'missing'}",
        "References:",
    ]
    if record["references"]:
        lines.extend(f"- {item['path']}:{item['line']}" for item in record["references"])
    else:
        lines.append("none")
    if record.get("missing_fields"):
        lines.append(f"Missing-Fields: {', '.join(record['missing_fields'])}")
    return "\n".join(lines)


def write_reference_report(project_root, plan_rel, records):
    categories = [
        "safe_no_references",
        "referenced_by_current_docs",
        "referenced_by_active_change",
        "manual_review_needed",
    ]
    grouped = {category: [item for item in records if item["category"] == category] for category in categories}
    lines = [
        "# Archive Reference Report",
        "",
        "Status: report-only",
        "Mode: reference-check",
        f"Plan path: {plan_rel.as_posix()}",
        f"Generated: {utc_now()}",
        "",
        "This report is string-match only. It does not decide whether a reference is harmful.",
        "",
        "## Summary",
        "",
        "| category | count |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {category} | {len(grouped[category])} |" for category in categories)
    for category in categories:
        lines.extend(["", f"## {category}", ""])
        lines.extend([reference_section(item) + "\n" for item in grouped[category]] or ["None.\n"])

    report_path = project_root / REFERENCE_REPORT
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return report_path


def run_reference_check(project_root, plan_value):
    plan_rel = safe_relative_path(plan_value, "plan")
    if plan_rel.as_posix() != ".forgekit/archive-plan.md":
        fail("v0.21 only supports --plan .forgekit/archive-plan.md")
    candidates = parse_plan(project_root / plan_rel)
    records = []
    for entry in candidates:
        missing_fields = sorted({"change_id", "From", "To", "Risk", "Status"} - set(entry))
        references = [] if missing_fields else find_references(project_root, entry)
        category = "manual_review_needed" if missing_fields else classify_reference(entry, references)
        records.append({
            "change_id": entry.get("change_id", "<missing-change>"),
            "from": entry.get("From", ""),
            "to": entry.get("To", ""),
            "category": category,
            "references": references,
            "missing_fields": missing_fields,
        })
    report_path = write_reference_report(project_root, plan_rel, records)
    print(f"[ok] Archive reference report written: {report_path}")


def git_status_allowing_plan(project_root, plan_rel):
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=project_root,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        shell=False,
    )
    if result.returncode != 0:
        fail("Git status failed; archive apply requires a Git repository with clean status")

    allowed = {plan_rel.as_posix(), plan_rel.as_posix().replace("/", "\\")}
    dirty = []
    for raw_line in result.stdout.splitlines():
        path_text = raw_line[3:].strip()
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1].strip()
        if path_text not in allowed:
            dirty.append(raw_line)
    if dirty:
        fail("Git working tree must be clean except the selected archive plan:\n" + "\n".join(dirty))


def validate_candidate(entry, project_root, change_root_rel):
    required = {"Archive-Status", "From", "To", "Risk", "Status", "change_id"}
    missing = sorted(required - set(entry))
    if missing:
        fail(f"Plan candidate is missing machine-readable fields: {entry.get('change_id', '<unknown>')}: {', '.join(missing)}")

    from_rel = safe_relative_path(entry["From"], "From")
    to_rel = safe_relative_path(entry["To"], "To")
    change_id = entry["change_id"]
    expected_from = (change_root_rel / change_id).as_posix()
    expected_to_prefix = f".forgekit/archive/changes/"
    if from_rel.as_posix() != expected_from:
        fail(f"Candidate From must match change_root/<change-id>: {entry['From']}")
    if not to_rel.as_posix().startswith(expected_to_prefix) or not to_rel.as_posix().endswith(f"/{change_id}"):
        fail(f"Candidate To must be .forgekit/archive/changes/YYYY/<change-id>: {entry['To']}")
    if entry["Status"].lower() != "done":
        fail(f"Candidate Status must be done: {change_id}")
    if forbidden_path(from_rel.as_posix()) or forbidden_path(to_rel.as_posix()):
        fail(f"Candidate path violates archive apply policy: {change_id}")

    from_path = project_root / from_rel
    to_path = project_root / to_rel
    if not from_path.is_dir():
        fail(f"Candidate source directory not found: {from_rel.as_posix()}")
    if to_path.exists():
        fail(f"Candidate target already exists: {to_rel.as_posix()}")
    return from_rel, to_rel


def update_archived_proposal(proposal_path):
    if not proposal_path.is_file():
        return "warning: proposal.md missing after move"
    lines = proposal_path.read_text(encoding="utf-8", errors="replace").splitlines()
    for index, line in enumerate(lines):
        if line.lower().startswith("status:"):
            if line.strip().lower() == "status: done":
                lines[index] = "Status: archived"
                proposal_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                return "done -> archived"
            return f"warning: proposal status was not done ({line.strip()})"
    return "warning: proposal status missing"


def write_apply_report(project_root, plan_rel, moved, skipped_summary):
    lines = [
        "# Archive Apply Report",
        "",
        "Status: applied",
        f"Plan path: {plan_rel.as_posix()}",
        f"Applied time: {utc_now()}",
        "",
        "## Policy Summary",
        "",
        "- Applied candidates only.",
        "- Blocked and skipped entries were not moved.",
        "- No current docs modified.",
        "- No business docs modified.",
        "- No lock updated.",
        "- No commit created.",
        "- No markdown links rewritten.",
        "",
        "## Moved Entries",
        "",
    ]
    for item in moved:
        lines.extend([
            f"### {item['change_id']}",
            "",
            f"- From: `{item['from']}`",
            f"- To: `{item['to']}`",
            f"- Proposal status updated: {item['proposal_status']}",
            "",
        ])
    lines.extend([
        "## Skipped Entries",
        "",
        f"- Blocked entries from plan were not applied: {skipped_summary['blocked']}",
        f"- Skipped entries from plan were not applied: {skipped_summary['skipped']}",
    ])
    report_path = project_root / ".forgekit" / "archive-apply-report.md"
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return report_path


def count_plan_groups(plan_path):
    text = plan_path.read_text(encoding="utf-8", errors="replace")
    counts = {"blocked": 0, "skipped": 0}
    for line in text.splitlines():
        if line.startswith("| blocked |"):
            counts["blocked"] = int(line.split("|")[2].strip())
        elif line.startswith("| skipped |"):
            counts["skipped"] = int(line.split("|")[2].strip())
    return counts


def run_apply(project_root, plan_value, confirm):
    if not confirm:
        fail("Archive apply requires --confirm. Review the dry-run plan, then rerun with --apply --plan .forgekit/archive-plan.md --confirm.")
    plan_rel = safe_relative_path(plan_value, "plan")
    if plan_rel.as_posix() != ".forgekit/archive-plan.md":
        fail("v0.20 only supports --plan .forgekit/archive-plan.md")

    git_status_allowing_plan(project_root, plan_rel)
    change_root_rel = safe_relative_path(read_boundary_change_root(project_root), "change_root")
    plan_path = project_root / plan_rel
    candidates = parse_plan(plan_path)
    if not candidates:
        fail("Plan has no Archive-Status: candidate entries to apply")

    planned = []
    for entry in candidates:
        from_rel, to_rel = validate_candidate(entry, project_root, change_root_rel)
        planned.append((entry, from_rel, to_rel))

    moved = []
    for entry, from_rel, to_rel in planned:
        from_path = project_root / from_rel
        to_path = project_root / to_rel
        to_path.parent.mkdir(parents=True, exist_ok=True)
        from_path.rename(to_path)
        proposal_status = update_archived_proposal(to_path / "proposal.md")
        moved.append({
            "change_id": entry["change_id"],
            "from": from_rel.as_posix(),
            "to": to_rel.as_posix(),
            "proposal_status": proposal_status,
        })

    report_path = write_apply_report(project_root, plan_rel, moved, count_plan_groups(plan_path))
    print(f"[ok] Archive apply moved candidates: {len(moved)}")
    print(f"[ok] Archive apply report written: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate or apply a ForgeKit archive plan.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Generate .forgekit/archive-plan.md without moving or changing project files.")
    mode.add_argument("--apply", action="store_true", help="Apply candidates from a reviewed archive plan.")
    mode.add_argument("--reference-check", action="store_true", help="Generate .forgekit/archive-reference-report.md from archive-plan candidates.")
    parser.add_argument("--plan", default=".forgekit/archive-plan.md", help="Archive plan path. v0.21 supports .forgekit/archive-plan.md.")
    parser.add_argument("--confirm", action="store_true", help="Required with --apply to move candidates.")
    args = parser.parse_args()
    project_root = Path.cwd().resolve()
    if args.dry_run:
        run_dry_run(project_root)
    elif args.apply:
        run_apply(project_root, args.plan, args.confirm)
    else:
        run_reference_check(project_root, args.plan)


if __name__ == "__main__":
    main()
