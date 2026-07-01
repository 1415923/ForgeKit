#!/usr/bin/env python3
"""Plan and apply reviewable ForgeKit archive capsules."""

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


PLAN_REL = Path(".forgekit/archive-capsule-plan.md")
ARCHIVE_ROOT = Path(".forgekit/archive")
DENIED_FILES = {
    ".forgekit/archive-capsule-plan.md",
    ".forgekit/project-boundary.yml",
    ".forgekit/state.json",
    ".forgekit/template-lock.json",
    ".forgekit/upgrade-report.md",
}


def integrity_check(root, archive_summary=None):
    checker = Path(__file__).resolve().with_name("check-current-docs-integrity.py")
    if not checker.is_file():
        fail(f"Current docs integrity checker not found: {checker}")
    command = [sys.executable, str(checker), "--repo-root", str(root), "--json"]
    if archive_summary:
        command.extend(["--archive-summary", str(archive_summary)])
    completed = subprocess.run(
        command, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    if completed.returncode == 2:
        fail("Current docs integrity checker could not run: " + completed.stdout.strip())
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError:
        fail("Current docs integrity checker returned invalid JSON")
    return report


def print_integrity_summary(label, report):
    print(f"Current docs integrity {label}: {report['status']}")
    print(f"Active tasks: {len(report['active_tasks'])}; blocking: {report['blocking_count']}; warnings: {report['warning_count']}")
    for item in report["findings"]:
        print(f"[{item['severity']}] {item['code']}: {item['message']}")


def fail(message):
    raise SystemExit(f"[fail] {message}")


def relative_safe(root, value, label):
    path = Path(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        fail(f"Unsafe {label}: {value}")
    resolved = (root / path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        fail(f"{label} escapes project root: {value}")
    return path, resolved


def slugify(value):
    pieces = []
    previous_dash = False
    for char in value.strip().lower():
        if char.isalnum():
            pieces.append(char)
            previous_dash = False
        elif not previous_dash and pieces:
            pieces.append("-")
            previous_dash = True
    return "".join(pieces).strip("-") or "phase-close"


def digest_path(path):
    digest = hashlib.sha256()
    if path.is_file():
        digest.update(path.read_bytes())
        return "sha256:" + digest.hexdigest()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(child.read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def classify_item(relative):
    posix = relative.as_posix()
    if posix in DENIED_FILES:
        fail(f"Archive policy denies managed state or plan file: {posix}")
    if relative.parts[:2] == (".forgekit", "docs"):
        fail(f"Archive policy denies current docs: {posix}")
    if relative.parts[:2] == (".forgekit", "archive"):
        fail(f"Archive policy denies existing archive and legacy archive: {posix}")
    if relative.parts[:2] == (".forgekit", "upgrade-export") or relative.parts[:2] == (".forgekit", "upgrade"):
        fail(f"Archive policy denies upgrade artifacts: {posix}")
    if relative.parts[:2] == (".forgekit", "changes") and len(relative.parts) >= 3:
        return "change", Path("items/changes").joinpath(*relative.parts[2:])
    if len(relative.parts) == 2 and relative.parts[0] == ".forgekit" and relative.suffix.lower() == ".md":
        return "report", Path("items/reports") / relative.name
    fail(f"Archive items must be explicit change artifacts or generated .forgekit reports: {posix}")


def plan_command(args):
    root = Path(args.repo_root).resolve()
    if not root.is_dir() or not (root / ".forgekit").is_dir():
        fail(f"Project root with .forgekit directory is required: {root}")
    if not args.item:
        fail("plan requires at least one explicit --item")

    integrity = integrity_check(root)
    print_integrity_summary("preflight", integrity)

    today = dt.date.today()
    name = args.name or "phase-close"
    slug = slugify(name)
    archive_id = f"{today.isoformat()}-{slug}"
    target = ARCHIVE_ROOT / f"{today.year:04d}" / f"{today.year:04d}-{today.month:02d}" / archive_id
    entries = []
    seen_sources = []
    seen_targets = set()
    for value in args.item:
        relative, source = relative_safe(root, value, "archive source")
        if not source.exists():
            fail(f"Archive source does not exist: {relative.as_posix()}")
        source_key = relative.as_posix()
        if any(relative == existing or relative.is_relative_to(existing) or existing.is_relative_to(relative) for existing in seen_sources):
            fail(f"Duplicate or overlapping archive source: {source_key}")
        item_type, item_target = classify_item(relative)
        target_relative = target / item_target
        if target_relative.as_posix() in seen_targets:
            fail(f"Archive target collision: {target_relative.as_posix()}")
        seen_sources.append(relative)
        seen_targets.add(target_relative.as_posix())
        entries.append({
            "change": relative.name,
            "from": source_key,
            "to": target_relative.as_posix(),
            "type": item_type,
            "checksum": digest_path(source),
        })

    reason = args.reason or "TODO_REVIEW: archive reason not provided"
    phase = args.phase or name
    lines = [
        "# ForgeKit Archive Capsule Plan",
        "",
        "Status: report-only",
        "Mode: archive-capsule-plan",
        f"Project: {root.name}",
        f"Project-Root: {root}",
        f"Archive-ID: {archive_id}",
        f"Archive-Target: {target.as_posix()}",
        f"Date: {today.isoformat()}",
        f"Phase: {phase}",
        f"Reason: {reason}",
        f"Items: {len(entries)}",
        f"Current-Docs-Integrity: {integrity['status']}",
        f"Active-Tasks: {len(integrity['active_tasks'])}",
        "",
        "Plan only. No files were moved. Review every item before apply.",
        "",
        "## Items",
    ]
    for index, entry in enumerate(entries, 1):
        lines.extend([
            "",
            f"### Item {index}",
            "",
            "Archive-Status: candidate",
            f"Change: {entry['change']}",
            f"From: {entry['from']}",
            f"To: {entry['to']}",
            f"Type: {entry['type']}",
            f"Reason: {reason}",
            f"Source-Checksum: {entry['checksum']}",
            "Notes: TODO_REVIEW",
        ])
    lines.extend([
        "",
        "## Confirmation",
        "",
        "Apply requires explicit user confirmation and `apply --confirm`.",
        "The apply step may only move the candidates listed above.",
        "Legacy archive content is not scanned or rearranged.",
    ])
    plan_path = root / PLAN_REL
    plan_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("ForgeKit Archive Capsule Plan")
    print("Status: report-only")
    print(f"Archive ID: {archive_id}")
    print(f"Target: {target.as_posix()}")
    print(f"Planned items: {len(entries)}")
    for entry in entries:
        print(f"[planned] {entry['from']} -> {entry['to']}")
    print(f"Plan path: {PLAN_REL.as_posix()}")
    print("No files were moved.")
    if integrity["blocking_count"]:
        print("[needs-fix] Apply will be blocked until a Current State Restoration Pass succeeds.")


def parse_fields(lines):
    fields = {}
    for line in lines:
        match = re.match(r"^([A-Za-z][A-Za-z0-9-]*):\s*(.*)$", line.strip())
        if match:
            fields[match.group(1)] = match.group(2).strip()
    return fields


def load_plan(plan_path):
    try:
        text = plan_path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        fail(f"Archive capsule plan not found: {plan_path}")
    sections = re.split(r"(?m)^### Item \d+\s*$", text)
    header = parse_fields(sections[0].splitlines())
    if header.get("Status") != "report-only" or header.get("Mode") != "archive-capsule-plan":
        fail("Plan must contain Status: report-only and Mode: archive-capsule-plan")
    required_header = {"Project-Root", "Archive-ID", "Archive-Target", "Date", "Phase", "Reason"}
    missing_header = sorted(required_header - set(header))
    if missing_header:
        fail("Plan missing fields: " + ", ".join(missing_header))
    entries = []
    required_item = {"Archive-Status", "From", "To", "Type", "Reason", "Source-Checksum"}
    for section in sections[1:]:
        item = parse_fields(section.splitlines())
        if item.get("Archive-Status") != "candidate":
            continue
        missing = sorted(required_item - set(item))
        if missing:
            fail("Candidate plan entry missing fields: " + ", ".join(missing))
        entries.append(item)
    if not entries:
        fail("Plan contains no Archive-Status: candidate entries")
    return header, entries


def ensure_capsule_target(root, value, date_value, archive_id):
    relative, resolved = relative_safe(root, value, "archive target")
    try:
        date = dt.date.fromisoformat(date_value)
    except ValueError:
        fail(f"Invalid plan date: {date_value}")
    expected = ARCHIVE_ROOT / f"{date.year:04d}" / f"{date.year:04d}-{date.month:02d}" / archive_id
    if relative.as_posix() != expected.as_posix():
        fail(f"Archive target does not match date/id policy: {relative.as_posix()}")
    return relative, resolved


def append_index(index_path, header, summary_relative, entries):
    if index_path.exists():
        content = index_path.read_text(encoding="utf-8-sig").rstrip()
        if f"Archive ID: {header['Archive-ID']}" in content:
            fail(f"Archive index already contains Archive ID: {header['Archive-ID']}")
    else:
        content = "# Archive Index\n\n默认先读本索引，不默认读取全量 archive。归档不是删除。"
    links = ", ".join(f"`{entry['To']}`" for entry in entries)
    block = [
        "",
        f"## {header['Date']} - {header['Archive-ID']}",
        "",
        f"- Date: {header['Date']}",
        f"- Archive ID: {header['Archive-ID']}",
        f"- Phase / Version: {header['Phase']}",
        f"- Reason: {header['Reason']}",
        f"- Summary path: `{summary_relative.as_posix()}`",
        f"- Key links: {links}",
    ]
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(content + "\n" + "\n".join(block) + "\n", encoding="utf-8")


def apply_command(args):
    if not args.confirm:
        fail("Archive capsule apply requires --confirm after reviewing the plan")
    root = Path(args.repo_root).resolve()
    if not root.is_dir() or not (root / ".forgekit").is_dir():
        fail(f"Project root with .forgekit directory is required: {root}")
    preflight = integrity_check(root)
    print_integrity_summary("preflight", preflight)
    if preflight["blocking_count"]:
        fail("Archive apply blocked by current docs integrity failures. Run a Current State Restoration Pass first.")
    plan_relative, plan_path = relative_safe(root, args.plan, "plan path")
    if plan_relative.as_posix() != PLAN_REL.as_posix():
        fail(f"Only {PLAN_REL.as_posix()} is accepted as the archive capsule plan")
    header, entries = load_plan(plan_path)
    if Path(header["Project-Root"]).resolve() != root:
        fail("Plan Project-Root does not match --repo-root")
    capsule_relative, capsule_path = ensure_capsule_target(root, header["Archive-Target"], header["Date"], header["Archive-ID"])
    if capsule_path.exists():
        fail(f"Archive capsule already exists: {capsule_relative.as_posix()}")

    index_path = root / ARCHIVE_ROOT / "index.md"
    if index_path.exists() and f"Archive ID: {header['Archive-ID']}" in index_path.read_text(encoding="utf-8-sig"):
        fail(f"Archive index already contains Archive ID: {header['Archive-ID']}")

    prepared = []
    prepared_sources = []
    for item in entries:
        source_relative, source = relative_safe(root, item["From"], "archive source")
        if any(source_relative == existing or source_relative.is_relative_to(existing) or existing.is_relative_to(source_relative) for existing in prepared_sources):
            fail(f"Candidate sources overlap: {source_relative.as_posix()}")
        item_type, expected_item_target = classify_item(source_relative)
        target_relative, target = relative_safe(root, item["To"], "archive item target")
        expected = capsule_relative / expected_item_target
        if item_type != item["Type"] or target_relative.as_posix() != expected.as_posix():
            fail(f"Candidate target/type violates archive policy: {source_relative.as_posix()}")
        if not source.exists():
            fail(f"Archive source no longer exists: {source_relative.as_posix()}")
        if digest_path(source) != item["Source-Checksum"]:
            fail(f"Archive source changed after plan: {source_relative.as_posix()}")
        if target.exists():
            fail(f"Archive target already exists: {target_relative.as_posix()}")
        prepared.append((item, source, target))
        prepared_sources.append(source_relative)

    capsule_path.mkdir(parents=True)
    moved = []
    for item, source, target in prepared:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        moved.append(item)

    archived_items = ["# Archived Items", ""]
    for index, item in enumerate(moved, 1):
        archived_items.extend([
            f"## Item {index}",
            "",
            f"- from: `{item['From']}`",
            f"- to: `{item['To']}`",
            f"- type: {item['Type']}",
            f"- reason: {item['Reason']}",
            "- status: moved",
            f"- notes: {item.get('Notes', 'TODO_REVIEW')}",
            "",
        ])
    items_path = capsule_path / "archived-items.md"
    items_path.write_text("\n".join(archived_items), encoding="utf-8")

    change_ids = [Path(item["From"]).name for item in moved if item["Type"] == "change"]
    summary = [
        "# Archive Summary",
        "",
        f"- Archive ID: {header['Archive-ID']}",
        f"- Date: {header['Date']}",
        f"- Project: {root.name}",
        f"- Phase / Version: {header['Phase']}",
        f"- Reason: {header['Reason']}",
        f"- Scope: {len(moved)} planned item(s)",
        f"- Archive Status: {'provisional snapshot' if preflight['active_tasks'] else 'completed phase archive'}",
        "- Current Facts Entry: `.forgekit/docs/`",
        "- Archived Items: `archived-items.md`",
        "- Key Decisions: TODO_REVIEW",
        "- Completed Work: TODO_REVIEW",
        "- Verification Evidence: TODO_REVIEW",
        "- Risks / TODO_REVIEW: TODO_REVIEW",
        "- Related Source IDs: TODO_REVIEW",
        "- Related Task IDs: TODO_REVIEW",
        f"- Related Change IDs: {', '.join(change_ids) if change_ids else 'TODO_REVIEW'}",
        "- Related Commits / Tags: TODO_REVIEW",
        f"- How to Find This Later: `.forgekit/archive/index.md` -> {header['Archive-ID']}",
        "",
        "Archive is historical context, not current truth.",
    ]
    summary_path = capsule_path / "archive-summary.md"
    summary_path.write_text("\n".join(summary) + "\n", encoding="utf-8")
    postflight = integrity_check(root, summary_path)
    print_integrity_summary("postflight", postflight)
    if postflight["blocking_count"]:
        with summary_path.open("a", encoding="utf-8") as handle:
            handle.write("\nArchive Status: needs-fix\nCurrent State Restoration Pass is required.\n")
        fail("Archive postflight failed. Capsule is needs-fix; follow restoration guidance and do not treat it as completed.")
    append_index(index_path, header, capsule_relative / "archive-summary.md", moved)

    print("ForgeKit Archive Capsule Apply")
    print("Status: applied")
    print(f"Archive ID: {header['Archive-ID']}")
    print(f"Moved items: {len(moved)}")
    print(f"Summary: {(capsule_relative / 'archive-summary.md').as_posix()}")
    print(f"Items log: {(capsule_relative / 'archived-items.md').as_posix()}")
    print("Archive index: .forgekit/archive/index.md")
    print("Current docs integrity postflight: passed")
    print("No business docs were modified. No Git commit was created.")


def main():
    parser = argparse.ArgumentParser(description="ForgeKit Archive Capsule plan/apply")
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan = subparsers.add_parser("plan", help="Create or replace the report-only capsule plan")
    plan.add_argument("--repo-root", default=".")
    plan.add_argument("--name", help="Phase/version name used for the capsule slug")
    plan.add_argument("--phase", help="Human-readable phase or version")
    plan.add_argument("--reason", help="Archive reason")
    plan.add_argument("--item", action="append", help="Explicit relative item path; repeat as needed")
    apply_parser = subparsers.add_parser("apply", help="Apply the reviewed capsule plan")
    apply_parser.add_argument("--repo-root", default=".")
    apply_parser.add_argument("--plan", default=PLAN_REL.as_posix())
    apply_parser.add_argument("--confirm", action="store_true")
    args = parser.parse_args()
    if args.command == "plan":
        plan_command(args)
    else:
        apply_command(args)


if __name__ == "__main__":
    main()
