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
SYNC_REPORT = ".forgekit/current-docs-sync-report.md"
SMART_REPORT = ".forgekit/smart-archive-report.md"
SMART_APPLY_REPORT = ".forgekit/smart-archive-apply-report.md"


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
        SYNC_REPORT,
        SMART_REPORT,
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


def normalize_field_value(value):
    normalized = value.strip().lower().replace("_", "-")
    normalized = " ".join(normalized.split())
    if normalized == "not needed":
        return "not-needed"
    return normalized


def parse_review_fields(review_path):
    fields = {}
    wanted = {
        "currentdocssync": "CurrentDocsSync",
        "changelogupdated": "ChangelogUpdated",
        "architectureupdated": "ArchitectureUpdated",
        "testingupdated": "TestingUpdated",
        "requirementsupdated": "RequirementsUpdated",
    }
    for raw_line in review_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        normalized_key = key.strip().replace(" ", "").replace("-", "").lower()
        if normalized_key in wanted:
            fields[wanted[normalized_key]] = normalize_field_value(value)
    return fields


def classify_sync(entry, project_root):
    required = {"change_id", "From", "To", "Risk", "Status"}
    missing_fields = sorted(required - set(entry))
    if missing_fields:
        return {
            "category": "manual_review_needed",
            "review_path": "missing",
            "fields": {},
            "warnings": [f"missing plan fields: {', '.join(missing_fields)}"],
        }

    candidate_rel = safe_relative_path(entry["From"], "Candidate-Path")
    candidate_path = project_root / candidate_rel
    if not candidate_path.is_dir():
        return {
            "category": "manual_review_needed",
            "review_path": (candidate_rel / "review.md").as_posix(),
            "fields": {},
            "warnings": ["candidate path is missing or not a directory"],
        }

    review_rel = candidate_rel / "review.md"
    review_path = project_root / review_rel
    if not review_path.is_file():
        return {
            "category": "manual_review_needed",
            "review_path": review_rel.as_posix(),
            "fields": {},
            "warnings": ["review.md missing"],
        }

    fields = parse_review_fields(review_path)
    current_docs_sync = fields.get("CurrentDocsSync", "unknown")
    changelog_updated = fields.get("ChangelogUpdated", "unknown")
    warnings = []
    if changelog_updated in {"no", "unknown"}:
        warnings.append(f"ChangelogUpdated is {changelog_updated}")
    if "ChangelogUpdated" not in fields:
        warnings.append("ChangelogUpdated missing")

    if current_docs_sync == "confirmed":
        category = "sync_confirmed"
    elif current_docs_sync == "not-needed":
        category = "sync_not_needed"
    elif current_docs_sync == "missing":
        category = "missing_required_docs"
    else:
        category = "missing_sync_metadata"

    return {
        "category": category,
        "review_path": review_rel.as_posix(),
        "fields": fields,
        "warnings": warnings,
    }


def sync_section(record):
    fields = record["fields"]
    warnings = record["warnings"]
    lines = [
        f"### {record['change_id']}",
        "",
        f"Sync-Status: {record['category']}",
        f"Change: {record['change_id']}",
        f"Candidate-Path: {record.get('from') or 'missing'}",
        f"Review-Path: {record['review_path']}",
        f"CurrentDocsSync: {fields.get('CurrentDocsSync', 'missing')}",
        f"ChangelogUpdated: {fields.get('ChangelogUpdated', 'missing')}",
        f"ArchitectureUpdated: {fields.get('ArchitectureUpdated', 'missing')}",
        f"TestingUpdated: {fields.get('TestingUpdated', 'missing')}",
        f"RequirementsUpdated: {fields.get('RequirementsUpdated', 'missing')}",
        "Warnings:",
    ]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("none")
    return "\n".join(lines)


def write_sync_report(project_root, plan_rel, records):
    categories = [
        "sync_confirmed",
        "sync_not_needed",
        "missing_sync_metadata",
        "missing_required_docs",
        "manual_review_needed",
    ]
    grouped = {category: [item for item in records if item["category"] == category] for category in categories}
    lines = [
        "# Current Docs Sync Report",
        "",
        "Status: report-only",
        "Mode: sync-check",
        f"Plan path: {plan_rel.as_posix()}",
        f"Generated: {utc_now()}",
        "",
        "This report checks structured review metadata only. It does not semantically verify current docs content.",
        "",
        "## Summary",
        "",
        "| category | count |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {category} | {len(grouped[category])} |" for category in categories)
    for category in categories:
        lines.extend(["", f"## {category}", ""])
        lines.extend([sync_section(item) + "\n" for item in grouped[category]] or ["None.\n"])

    report_path = project_root / SYNC_REPORT
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return report_path


def run_sync_check(project_root, plan_value):
    plan_rel = safe_relative_path(plan_value, "plan")
    if plan_rel.as_posix() != ".forgekit/archive-plan.md":
        fail("v0.22 only supports --plan .forgekit/archive-plan.md")
    candidates = parse_plan(project_root / plan_rel)
    records = []
    for entry in candidates:
        result = classify_sync(entry, project_root)
        records.append({
            "change_id": entry.get("change_id", "<missing-change>"),
            "from": entry.get("From", ""),
            "category": result["category"],
            "review_path": result["review_path"],
            "fields": result["fields"],
            "warnings": result["warnings"],
        })
    report_path = write_sync_report(project_root, plan_rel, records)
    print(f"[ok] Current docs sync report written: {report_path}")


def parse_machine_report(report_path, status_key):
    if not report_path.is_file():
        return {}, [f"missing report: {report_path}"]
    lines = report_path.read_text(encoding="utf-8", errors="replace").splitlines()
    if "Status: report-only" not in lines:
        return {}, [f"report is not report-only: {report_path}"]

    records = {}
    current = None
    in_warnings = False
    for line in lines:
        if line.startswith("### "):
            if current and current.get("Change"):
                records[current["Change"]] = current
            current = {"Warnings": []}
            in_warnings = False
            continue
        if current is None:
            continue
        if line == "Warnings:":
            in_warnings = True
            continue
        if in_warnings:
            if line.startswith("- "):
                current["Warnings"].append(line[2:].strip())
                continue
            if line == "none":
                continue
            if line and not line.startswith("#"):
                in_warnings = False
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key in {status_key, "Change", "Candidate-Path", "Target-Archive-Path", "Review-Path"}:
            current[key] = value
    if current and current.get("Change"):
        records[current["Change"]] = current
    return records, []


def smart_status_for(plan_entry, reference_record, sync_record, missing_report_errors):
    if missing_report_errors:
        return "blocked_by_missing_report", "; ".join(missing_report_errors)

    required_plan = {"change_id", "From", "To", "Risk", "Status"}
    missing_plan = sorted(required_plan - set(plan_entry))
    if missing_plan:
        return "manual_review_required", "plan candidate is missing fields: " + ", ".join(missing_plan)

    change_id = plan_entry["change_id"]
    if reference_record is None:
        return "blocked_by_missing_report", "missing reference report entry"
    if sync_record is None:
        return "blocked_by_missing_report", "missing sync report entry"

    reference_status = reference_record.get("Reference-Status", "missing")
    sync_status = sync_record.get("Sync-Status", "missing")
    if reference_status == "missing" or sync_status == "missing":
        return "manual_review_required", "reference or sync status field missing"
    if reference_record.get("Change") != change_id or sync_record.get("Change") != change_id:
        return "manual_review_required", "report entry Change field does not match plan candidate"

    if reference_status == "referenced_by_active_change":
        return "blocked_by_active_reference", "candidate is referenced by active change context"
    if reference_status == "referenced_by_current_docs":
        return "blocked_by_current_docs_reference", "candidate is still referenced by current docs"
    if reference_status == "manual_review_needed":
        return "manual_review_required", "reference report requires manual review"
    if sync_status in {"missing_sync_metadata", "missing_required_docs"}:
        return "blocked_by_missing_sync", "current docs sync evidence is missing or incomplete"
    if reference_status == "safe_no_references" and sync_status in {"sync_confirmed", "sync_not_needed"}:
        return "auto_archive_candidate", "no references and current docs sync evidence is acceptable"
    return "manual_review_required", f"unrecognized reference/sync combination: {reference_status} / {sync_status}"


def smart_section(record):
    warnings = record["warnings"]
    lines = [
        f"### {record['change_id']}",
        "",
        f"Smart-Status: {record['category']}",
        f"Change: {record['change_id']}",
        f"Candidate-Path: {record.get('from') or 'missing'}",
        f"Target-Archive-Path: {record.get('to') or 'missing'}",
        f"Reference-Status: {record.get('reference_status') or 'missing'}",
        f"Sync-Status: {record.get('sync_status') or 'missing'}",
        f"Reason: {record['reason']}",
        "Warnings:",
    ]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("none")
    return "\n".join(lines)


def write_smart_report(project_root, plan_rel, reference_rel, sync_rel, records):
    categories = [
        "auto_archive_candidate",
        "manual_review_required",
        "blocked_by_active_reference",
        "blocked_by_current_docs_reference",
        "blocked_by_missing_sync",
        "blocked_by_missing_report",
    ]
    grouped = {category: [item for item in records if item["category"] == category] for category in categories}
    lines = [
        "# Smart Archive Report",
        "",
        "Status: report-only",
        "Mode: smart-check",
        f"Plan path: {plan_rel.as_posix()}",
        f"Reference report path: {reference_rel.as_posix()}",
        f"Sync report path: {sync_rel.as_posix()}",
        f"Generated: {utc_now()}",
        "",
        "This report only combines machine-readable fields from existing reports. It does not perform AI semantic judgment.",
        "",
        "## Summary",
        "",
        "| category | count |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {category} | {len(grouped[category])} |" for category in categories)
    for category in categories:
        lines.extend(["", f"## {category}", ""])
        lines.extend([smart_section(item) + "\n" for item in grouped[category]] or ["None.\n"])

    report_path = project_root / SMART_REPORT
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return report_path


def run_smart_check(project_root, plan_value, reference_value, sync_value):
    plan_rel = safe_relative_path(plan_value, "plan")
    reference_rel = safe_relative_path(reference_value, "reference-report")
    sync_rel = safe_relative_path(sync_value, "sync-report")
    if plan_rel.as_posix() != ".forgekit/archive-plan.md":
        fail("v0.23 only supports --plan .forgekit/archive-plan.md")
    if reference_rel.as_posix() != REFERENCE_REPORT:
        fail(f"v0.23 only supports --reference-report {REFERENCE_REPORT}")
    if sync_rel.as_posix() != SYNC_REPORT:
        fail(f"v0.23 only supports --sync-report {SYNC_REPORT}")

    missing_report_errors = []
    try:
        candidates = parse_plan(project_root / plan_rel)
    except SystemExit as exc:
        candidates = []
        missing_report_errors.append(str(exc).replace("[fail] ", ""))

    reference_records, reference_errors = parse_machine_report(project_root / reference_rel, "Reference-Status")
    sync_records, sync_errors = parse_machine_report(project_root / sync_rel, "Sync-Status")
    missing_report_errors.extend(reference_errors)
    missing_report_errors.extend(sync_errors)

    records = []
    if not candidates and missing_report_errors:
        records.append({
            "change_id": "<missing-candidate>",
            "from": "",
            "to": "",
            "reference_status": "missing",
            "sync_status": "missing",
            "category": "blocked_by_missing_report",
            "reason": "; ".join(missing_report_errors),
            "warnings": [],
        })
    for entry in candidates:
        change_id = entry.get("change_id", "<missing-change>")
        reference_record = reference_records.get(change_id)
        sync_record = sync_records.get(change_id)
        category, reason = smart_status_for(entry, reference_record, sync_record, missing_report_errors)
        warnings = []
        if sync_record:
            warnings.extend(sync_record.get("Warnings", []))
        records.append({
            "change_id": change_id,
            "from": entry.get("From", ""),
            "to": entry.get("To", ""),
            "reference_status": reference_record.get("Reference-Status", "missing") if reference_record else "missing",
            "sync_status": sync_record.get("Sync-Status", "missing") if sync_record else "missing",
            "category": category,
            "reason": reason,
            "warnings": warnings,
        })

    report_path = write_smart_report(project_root, plan_rel, reference_rel, sync_rel, records)
    print(f"[ok] Smart archive report written: {report_path}")


def git_status_allowing_path(project_root, allowed_rel, label):
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

    allowed = {allowed_rel.as_posix(), allowed_rel.as_posix().replace("/", "\\")}
    dirty = []
    for raw_line in result.stdout.splitlines():
        path_text = raw_line[3:].strip()
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1].strip()
        if path_text not in allowed:
            dirty.append(raw_line)
    if dirty:
        fail(f"Git working tree must be clean except the selected {label}:\n" + "\n".join(dirty))


def git_status_allowing_plan(project_root, plan_rel):
    git_status_allowing_path(project_root, plan_rel, "archive plan")


def git_status_allowing_report(project_root, report_rel):
    git_status_allowing_path(project_root, report_rel, "smart archive report")


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
            status_value = line.split(":", 1)[1].strip().lower()
            if status_value == "done":
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


def parse_smart_report(report_path):
    if not report_path.is_file():
        fail(f"Smart archive report not found: {report_path}")
    lines = report_path.read_text(encoding="utf-8", errors="replace").splitlines()
    if "Mode: smart-check" not in lines or "Status: report-only" not in lines:
        fail("Smart archive report must contain 'Mode: smart-check' and 'Status: report-only'")

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
        if key in {
            "Smart-Status",
            "Change",
            "Candidate-Path",
            "Target-Archive-Path",
            "Reference-Status",
            "Sync-Status",
            "Reason",
        }:
            current[key] = value.strip()
    if current:
        entries.append(current)
    return [item for item in entries if item.get("Smart-Status") == "auto_archive_candidate"]


def count_smart_groups(report_path):
    text = report_path.read_text(encoding="utf-8", errors="replace")
    categories = {
        "manual_review_required": 0,
        "blocked_by_active_reference": 0,
        "blocked_by_current_docs_reference": 0,
        "blocked_by_missing_sync": 0,
        "blocked_by_missing_report": 0,
    }
    for line in text.splitlines():
        for category in categories:
            if line.startswith(f"| {category} |"):
                categories[category] = int(line.split("|")[2].strip())
    return categories


def validate_smart_candidate(entry, project_root):
    required = {"Smart-Status", "Change", "Candidate-Path", "Target-Archive-Path", "change_id"}
    missing = sorted(required - set(entry))
    if missing:
        fail(f"Smart candidate is missing machine-readable fields: {entry.get('change_id', '<unknown>')}: {', '.join(missing)}")

    change_id = entry["Change"]
    if entry["change_id"] != change_id:
        fail(f"Smart candidate heading must match Change field: {entry['change_id']} / {change_id}")
    from_rel = safe_relative_path(entry["Candidate-Path"], "Candidate-Path")
    to_rel = safe_relative_path(entry["Target-Archive-Path"], "Target-Archive-Path")

    expected_from = f".forgekit/changes/{change_id}"
    to_parts = to_rel.parts
    if from_rel.as_posix() != expected_from:
        fail(f"Smart candidate source must be .forgekit/changes/<change-id>: {entry['Candidate-Path']}")
    if len(to_parts) != 5 or to_parts[:3] != (".forgekit", "archive", "changes") or to_parts[4] != change_id:
        fail(f"Smart candidate target must be .forgekit/archive/changes/YYYY/<change-id>: {entry['Target-Archive-Path']}")
    if len(to_parts[3]) != 4 or not to_parts[3].isdigit():
        fail(f"Smart candidate target year must be YYYY: {entry['Target-Archive-Path']}")
    if entry.get("Reference-Status") != "safe_no_references":
        fail(f"Smart candidate Reference-Status must be safe_no_references: {change_id}")
    if entry.get("Sync-Status") not in {"sync_confirmed", "sync_not_needed"}:
        fail(f"Smart candidate Sync-Status must be sync_confirmed or sync_not_needed: {change_id}")
    if forbidden_path(from_rel.as_posix()) or forbidden_path(to_rel.as_posix()):
        fail(f"Smart candidate path violates archive apply policy: {change_id}")

    from_path = project_root / from_rel
    to_path = project_root / to_rel
    if not from_path.is_dir():
        fail(f"Smart candidate source directory not found: {from_rel.as_posix()}")
    proposal_status = read_change_status(from_path)
    if proposal_status != "done":
        fail(f"Smart candidate proposal Status must be done before archive: {change_id}")
    if to_path.exists():
        fail(f"Smart candidate target already exists: {to_rel.as_posix()}")
    return from_rel, to_rel


def write_smart_apply_report(project_root, report_rel, moved, skipped_summary):
    lines = [
        "# Smart Archive Apply Report",
        "",
        "Status: applied",
        "Mode: smart-apply",
        f"Smart report path: {report_rel.as_posix()}",
        f"Applied time: {utc_now()}",
        "",
        "## Policy Summary",
        "",
        "- Applied Smart-Status: auto_archive_candidate entries only.",
        "- Manual review and blocked entries were not moved.",
        "- No current docs modified.",
        "- No business docs modified.",
        "- No README, AGENTS, or CLAUDE modified.",
        "- No template-lock updated.",
        "- No archive plan, reference report, sync report, or smart report modified.",
        "- No commit created.",
        "- No markdown links rewritten.",
        "",
        "## Moved Entries",
        "",
    ]
    if moved:
        for item in moved:
            lines.extend([
                f"### {item['change_id']}",
                "",
                f"- From: `{item['from']}`",
                f"- To: `{item['to']}`",
                f"- Proposal status updated: {item['proposal_status']}",
                "",
            ])
    else:
        lines.append("None.\n")
    lines.extend([
        "## Not Applied",
        "",
        f"- manual_review_required: {skipped_summary['manual_review_required']}",
        f"- blocked_by_active_reference: {skipped_summary['blocked_by_active_reference']}",
        f"- blocked_by_current_docs_reference: {skipped_summary['blocked_by_current_docs_reference']}",
        f"- blocked_by_missing_sync: {skipped_summary['blocked_by_missing_sync']}",
        f"- blocked_by_missing_report: {skipped_summary['blocked_by_missing_report']}",
    ])
    report_path = project_root / SMART_APPLY_REPORT
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


def run_smart_apply(project_root, report_value, confirm):
    if not confirm:
        fail(f"Smart archive apply requires --confirm. Review {SMART_REPORT}, then rerun with --smart-apply --report {SMART_REPORT} --confirm.")
    if not report_value:
        fail(f"Smart archive apply requires --report {SMART_REPORT}")
    report_rel = safe_relative_path(report_value, "report")
    if report_rel.as_posix() != SMART_REPORT:
        fail(f"v0.24 only supports --report {SMART_REPORT}")

    git_status_allowing_report(project_root, report_rel)
    report_path = project_root / report_rel
    candidates = parse_smart_report(report_path)
    if not candidates:
        fail("Smart report has no Smart-Status: auto_archive_candidate entries to apply")

    planned = []
    for entry in candidates:
        from_rel, to_rel = validate_smart_candidate(entry, project_root)
        planned.append((entry, from_rel, to_rel))

    moved = []
    for entry, from_rel, to_rel in planned:
        from_path = project_root / from_rel
        to_path = project_root / to_rel
        to_path.parent.mkdir(parents=True, exist_ok=True)
        from_path.rename(to_path)
        proposal_status = update_archived_proposal(to_path / "proposal.md")
        moved.append({
            "change_id": entry["Change"],
            "from": from_rel.as_posix(),
            "to": to_rel.as_posix(),
            "proposal_status": proposal_status,
        })

    report_path = write_smart_apply_report(project_root, report_rel, moved, count_smart_groups(report_path))
    print(f"[ok] Smart archive apply moved candidates: {len(moved)}")
    print(f"[ok] Smart archive apply report written: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate or apply a ForgeKit archive plan.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Generate .forgekit/archive-plan.md without moving or changing project files.")
    mode.add_argument("--apply", action="store_true", help="Apply candidates from a reviewed archive plan.")
    mode.add_argument("--reference-check", action="store_true", help="Generate .forgekit/archive-reference-report.md from archive-plan candidates.")
    mode.add_argument("--sync-check", action="store_true", help="Generate .forgekit/current-docs-sync-report.md from archive-plan candidates.")
    mode.add_argument("--smart-check", action="store_true", help="Generate .forgekit/smart-archive-report.md from archive, reference, and sync reports.")
    mode.add_argument("--smart-apply", action="store_true", help="Apply Smart-Status: auto_archive_candidate entries from a reviewed smart archive report.")
    parser.add_argument("--plan", default=".forgekit/archive-plan.md", help="Archive plan path. v0.23 supports .forgekit/archive-plan.md.")
    parser.add_argument("--reference-report", default=REFERENCE_REPORT, help="Reference report path. v0.23 supports .forgekit/archive-reference-report.md.")
    parser.add_argument("--sync-report", default=SYNC_REPORT, help="Sync report path. v0.23 supports .forgekit/current-docs-sync-report.md.")
    parser.add_argument("--report", help="Smart archive report path. Required with --smart-apply; v0.24 supports .forgekit/smart-archive-report.md.")
    parser.add_argument("--confirm", action="store_true", help="Required with --apply or --smart-apply to move candidates.")
    args = parser.parse_args()
    project_root = Path.cwd().resolve()
    if args.dry_run:
        run_dry_run(project_root)
    elif args.apply:
        run_apply(project_root, args.plan, args.confirm)
    elif args.reference_check:
        run_reference_check(project_root, args.plan)
    elif args.sync_check:
        run_sync_check(project_root, args.plan)
    elif args.smart_check:
        run_smart_check(project_root, args.plan, args.reference_report, args.sync_report)
    else:
        run_smart_apply(project_root, args.report, args.confirm)


if __name__ == "__main__":
    main()
