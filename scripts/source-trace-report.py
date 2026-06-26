#!/usr/bin/env python3
import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


REPORT_REL = ".forgekit/source-trace-report.md"
DEFAULT_DOCS_ROOT = ".forgekit/docs"
DEFAULT_CHANGE_ROOT = ".forgekit/changes"

SOURCE_RE = re.compile(r"\bSRC-\d{8}-\d{3}\b", re.IGNORECASE)
TASK_RE = re.compile(r"\b(?:TASK|BUG)-\d{3,}\b", re.IGNORECASE)
REQ_RE = re.compile(r"\bREQ-\d{3,}\b", re.IGNORECASE)
CHANGE_RE = re.compile(r"\b(?:CHG|CHANGE)-[A-Za-z0-9._-]+\b", re.IGNORECASE)

DONE_TERMS = ("done", "complete", "completed", "closed", "已完成", "完成", "验证通过")
PENDING_TERMS = ("todo", "pending", "backlog", "ready", "open", "待办", "未开始", "待确认")
BLOCKED_TERMS = ("blocked", "阻塞")
VERIFY_TERMS = ("verification", "verified", "test", "passed", "验证", "测试", "[ok]")
RISK_TERMS = ("risk", "todo_review", "todo-review", "待复查", "风险", "阻塞")


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def fail(message):
    raise SystemExit(f"[fail] {message}")


def read_boundary_value(project_root, key, default):
    boundary_path = project_root / ".forgekit" / "project-boundary.yml"
    if not boundary_path.is_file():
        return default
    for raw_line in boundary_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if line.startswith(f"{key}:"):
            value = line.split(":", 1)[1].strip().strip('"').strip("'")
            return value or default
    return default


def safe_project_path(project_root, rel_value):
    rel = Path(rel_value)
    if rel.is_absolute() or any(part == ".." for part in rel.parts):
        fail(f"unsafe relative path: {rel_value}")
    target = (project_root / rel).resolve()
    root = project_root.resolve()
    if target != root and root not in target.parents:
        fail(f"path escapes project root: {rel_value}")
    return target


def read_text(path):
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def ids(pattern, text):
    return {match.group(0).upper() for match in pattern.finditer(text or "")}


def lines_with_any(text, patterns):
    lines = []
    for idx, line in enumerate((text or "").splitlines(), start=1):
        lowered = line.lower()
        if any(term.lower() in lowered for term in patterns):
            lines.append((idx, line.strip()))
    return lines


def add_finding(findings, severity, stage, rule, record, message, suggestion):
    findings.append({
        "severity": severity,
        "stage": stage,
        "rule": rule,
        "record": record,
        "message": message,
        "suggestion": suggestion,
    })


def extract_source_blocks(task_intake):
    blocks = {}
    current_id = None
    current = []
    for line in task_intake.splitlines():
        match = re.match(r"\s*Source ID:\s*(SRC-\d{8}-\d{3})", line, re.IGNORECASE)
        if match:
            if current_id:
                blocks[current_id] = "\n".join(current)
            current_id = match.group(1).upper()
            current = [line]
        elif current_id:
            current.append(line)
    if current_id:
        blocks[current_id] = "\n".join(current)
    return blocks


def extract_change_texts(change_root):
    changes = {}
    if not change_root.is_dir():
        return changes
    for directory in change_root.iterdir():
        if not directory.is_dir() or directory.name == "_template":
            continue
        parts = []
        for path in sorted(directory.glob("*.md")):
            parts.append(read_text(path))
        changes[directory.name] = "\n".join(parts)
    return changes


def extract_snapshot(project_root):
    docs_root_rel = read_boundary_value(project_root, "managed_docs_root", DEFAULT_DOCS_ROOT)
    change_root_rel = read_boundary_value(project_root, "change_root", DEFAULT_CHANGE_ROOT)
    docs_root = safe_project_path(project_root, docs_root_rel)
    change_root = safe_project_path(project_root, change_root_rel)
    docs = {
        "task-intake": read_text(docs_root / "task-intake.md"),
        "requirements": read_text(docs_root / "requirements.md"),
        "task-board": read_text(docs_root / "task-board.md"),
        "work-log": read_text(docs_root / "work-log.md"),
        "changelog": read_text(docs_root / "changelog.md"),
        "testing": read_text(docs_root / "testing.md"),
        "risk-register": read_text(docs_root / "risk-register.md"),
    }
    return docs_root_rel, change_root_rel, docs, extract_change_texts(change_root)


def trace_sets(docs, changes):
    combined_changes = "\n".join(changes.values())
    verification_text = "\n".join([docs["testing"], docs["work-log"], combined_changes])
    return {
        "sources": ids(SOURCE_RE, docs["task-intake"]),
        "requirements_sources": ids(SOURCE_RE, docs["requirements"]),
        "requirements": ids(REQ_RE, docs["requirements"]),
        "tasks": ids(TASK_RE, docs["task-board"]),
        "task_sources": ids(SOURCE_RE, docs["task-board"]),
        "task_requirements": ids(REQ_RE, docs["task-board"]),
        "change_sources": ids(SOURCE_RE, combined_changes),
        "change_tasks": ids(TASK_RE, combined_changes),
        "change_requirements": ids(REQ_RE, combined_changes),
        "verification_tasks": ids(TASK_RE, verification_text),
        "verification_sources": ids(SOURCE_RE, verification_text),
        "worklog_tasks": ids(TASK_RE, docs["work-log"]),
        "worklog_sources": ids(SOURCE_RE, docs["work-log"]),
        "changelog_tasks": ids(TASK_RE, docs["changelog"]),
        "changelog_sources": ids(SOURCE_RE, docs["changelog"]),
        "changelog_changes": ids(CHANGE_RE, docs["changelog"]),
    }


def check_source_records(findings, docs, sets):
    source_blocks = extract_source_blocks(docs["task-intake"])
    if not sets["sources"]:
        add_finding(findings, "warning", "source", "missing-source-records", "task-intake.md", "No Source ID records found in task-intake.md.", "Record original sources in task-intake.md before deriving tasks.")
    for source_id, block in source_blocks.items():
        missing = []
        for label in ["Source Type:", "Human Review:", "Derived Task IDs:"]:
            if label not in block:
                missing.append(label)
        if "Original Text" not in block and "### 原文" not in block and "原文" not in block:
            missing.append("Original Text / 原文")
        if missing:
            add_finding(findings, "warning", "source", "source-metadata-incomplete", source_id, f"Source record is missing: {', '.join(missing)}.", "Keep source metadata, original text, review status, and derived task links explicit.")
        block_tasks = ids(TASK_RE, block)
        if not block_tasks:
            add_finding(findings, "info", "source", "source-without-task", source_id, "Source has no derived Task ID.", "If this is intentional, keep Task Decision as note-only/rejected; otherwise add Derived Task IDs.")


def check_requirements(findings, sets):
    for source_id in sorted(sets["requirements_sources"] - sets["sources"]):
        add_finding(findings, "warning", "requirements", "requirement-source-missing", source_id, "requirements.md references a Source ID not found in task-intake.md.", "Add or correct the source record in task-intake.md.")
    if sets["requirements"] and not sets["requirements_sources"]:
        add_finding(findings, "warning", "requirements", "requirements-without-source", "requirements.md", "Requirement IDs exist but no Source ID references were found.", "Add Source ID references to each stable requirement fact.")


def check_tasks(findings, sets):
    for task_id in sorted(sets["tasks"]):
        task_related = task_id in sets["change_tasks"] or task_id in sets["verification_tasks"] or task_id in sets["worklog_tasks"] or task_id in sets["changelog_tasks"]
        if not task_related:
            add_finding(findings, "info", "task", "task-without-downstream-evidence", task_id, "Task appears in task-board but has no change, verification, work-log, or changelog reference.", "If work started, add references in work-log/change/verification; otherwise keep status accurate.")
    for source_id in sorted(sets["task_sources"] - sets["sources"]):
        add_finding(findings, "warning", "task", "task-source-missing", source_id, "task-board.md references a Source ID not found in task-intake.md.", "Correct Source ID or add the missing source record.")
    if sets["tasks"] and not sets["task_sources"] and not sets["task_requirements"]:
        add_finding(findings, "warning", "task", "task-without-source", "task-board.md", "Tasks exist but no Source ID or Requirement ID references were found.", "Each executable task should link to Source ID or Requirement ID.")


def check_changes(findings, sets):
    change_refs = sets["change_tasks"] | sets["change_sources"] | sets["change_requirements"]
    if not change_refs:
        return
    for task_id in sorted(sets["change_tasks"] - sets["tasks"]):
        add_finding(findings, "info", "change", "change-task-missing", task_id, "Change artifact references a task not found in task-board.md.", "Confirm whether the task was closed, renamed, or should be added to task-board.md.")
    for source_id in sorted(sets["change_sources"] - sets["sources"]):
        add_finding(findings, "warning", "change", "change-source-missing", source_id, "Change artifact references a Source ID not found in task-intake.md.", "Correct Source ID or add the missing source record.")


def check_verification(findings, docs, sets):
    done_lines = lines_with_any(docs["task-board"], DONE_TERMS)
    for _, line in done_lines:
        for task_id in ids(TASK_RE, line):
            if task_id not in sets["verification_tasks"]:
                add_finding(findings, "warning", "verification", "done-task-without-verification", task_id, "Task appears done/complete but no verification reference was found.", "Add verification evidence in work-log.md or changes/<id>/verification.md.")

    verification_lines = lines_with_any("\n".join([docs["testing"], docs["work-log"]]), VERIFY_TERMS)
    for line_no, line in verification_lines:
        if not ids(TASK_RE, line) and not ids(SOURCE_RE, line):
            add_finding(findings, "info", "verification", "verification-without-task", f"line {line_no}", "Verification-looking line has no Task ID or Source ID.", "Attach Task ID or Source ID to verification results.")


def check_worklog_changelog(findings, docs, sets):
    done_worklog = lines_with_any(docs["work-log"], DONE_TERMS)
    for line_no, line in done_worklog:
        line_tasks = ids(TASK_RE, line)
        line_sources = ids(SOURCE_RE, line)
        if not line_tasks and not line_sources:
            add_finding(findings, "info", "work-log", "completed-log-without-id", f"line {line_no}", "Work-log completion line has no Task ID or Source ID.", "Reference Task ID or Source ID in completion entries.")
        for task_id in line_tasks:
            if task_id not in sets["verification_tasks"]:
                add_finding(findings, "warning", "work-log", "completed-log-without-verification", task_id, "Work-log marks completion but verification evidence was not found.", "Add verification evidence or mark the task as not verified.")

    changelog_lines = [line for _, line in lines_with_any(docs["changelog"], DONE_TERMS + ("added", "changed", "fixed", "removed"))]
    for idx, line in enumerate(changelog_lines, start=1):
        if not ids(TASK_RE, line) and not ids(SOURCE_RE, line) and not ids(CHANGE_RE, line):
            add_finding(findings, "info", "changelog", "changelog-entry-without-link", f"entry {idx}", "Changelog-looking entry has no task/source/change reference.", "Link changelog entries to Task ID, Source ID, or change ID when practical.")


def check_orphans(findings, sets):
    for source_id in sorted(sets["sources"] - sets["task_sources"] - sets["requirements_sources"] - sets["worklog_sources"] - sets["changelog_sources"] - sets["change_sources"]):
        add_finding(findings, "info", "orphan", "source-without-task", source_id, "Source is not referenced outside task-intake.md.", "Keep as note-only/rejected if intentional; otherwise link it to a requirement, task, or work-log entry.")
    for task_id in sorted(sets["verification_tasks"] - sets["tasks"] - sets["change_tasks"] - sets["worklog_tasks"] - sets["changelog_tasks"]):
        add_finding(findings, "info", "orphan", "verification-without-task", task_id, "Verification references a task not found elsewhere.", "Correct Task ID or add the missing task context.")
    for task_id in sorted(sets["changelog_tasks"] - sets["tasks"] - sets["change_tasks"]):
        add_finding(findings, "info", "orphan", "changelog-task-without-task", task_id, "Changelog references a task not found in task-board or changes.", "Confirm whether the task was archived, renamed, or should be added.")


def check_status_conflicts(findings, docs, sets):
    pending_task_ids = set()
    for _, line in lines_with_any(docs["task-board"], PENDING_TERMS):
        pending_task_ids |= ids(TASK_RE, line)
    completed_elsewhere = set()
    for _, line in lines_with_any(docs["work-log"] + "\n" + docs["changelog"], DONE_TERMS):
        completed_elsewhere |= ids(TASK_RE, line)
    for task_id in sorted(pending_task_ids & completed_elsewhere):
        add_finding(findings, "warning", "status", "pending-but-completed", task_id, "task-board shows pending/open while work-log or changelog suggests completion.", "Align task-board status with verified completion or correct the completion note.")

    for line_no, line in lines_with_any(docs["task-board"], BLOCKED_TERMS):
        if not any(term.lower() in (docs["risk-register"] + "\n" + line).lower() for term in RISK_TERMS):
            add_finding(findings, "info", "status", "blocked-without-risk", f"line {line_no}", "Blocked task may lack risk/TODO_REVIEW context.", "Record blocker in risk-register.md or mark TODO_REVIEW with owner and next step.")


def severity_rank(severity):
    return {"error": 0, "warning": 1, "info": 2}.get(severity, 3)


def write_report(project_root, report_path, docs_root_rel, change_root_rel, sets, findings):
    by_severity = defaultdict(list)
    by_stage = defaultdict(list)
    for item in findings:
        by_severity[item["severity"]].append(item)
        by_stage[item["stage"]].append(item)

    lines = [
        "# Source Trace Report",
        "",
        "Status: report-only",
        "Mode: source-trace",
        f"Generated: {utc_now()}",
        f"DocsRoot: {docs_root_rel}",
        f"ChangeRoot: {change_root_rel}",
        "",
        "Report-only Notice: this report does not modify task-intake, requirements, task-board, changes, testing, work-log, changelog, template-lock, Git state, or business docs.",
        "",
        "## Summary",
        "",
        "| item | count |",
        "| --- | ---: |",
        f"| Source IDs | {len(sets['sources'])} |",
        f"| Requirement IDs | {len(sets['requirements'])} |",
        f"| Task IDs | {len(sets['tasks'])} |",
        f"| error findings | {len(by_severity['error'])} |",
        f"| warning findings | {len(by_severity['warning'])} |",
        f"| info findings | {len(by_severity['info'])} |",
        "",
        "## Trace Chain Overview",
        "",
        "- Source: task-intake.md",
        "- Requirement facts: requirements.md",
        "- Task breakdown: task-board.md",
        "- Change / implementation evidence: .forgekit/changes/<id>/",
        "- Verification evidence: testing.md, work-log.md, changes/<id>/verification.md",
        "- Status / delivery evidence: work-log.md and changelog.md",
        "",
        "## Findings by Severity",
        "",
    ]
    for severity in ["error", "warning", "info"]:
        lines.extend([f"### {severity}", ""])
        items = sorted(by_severity[severity], key=lambda item: (item["stage"], item["rule"], item["record"]))
        if not items:
            lines.extend(["None.", ""])
            continue
        for item in items:
            lines.extend([
                f"#### {item['stage']} - {item['rule']} - {item['record']}",
                "",
                f"- Severity: {item['severity']}",
                f"- Message: {item['message']}",
                f"- Suggested manual fix: {item['suggestion']}",
                "",
            ])

    lines.extend(["## Findings by Trace Stage", ""])
    if not by_stage:
        lines.extend(["None.", ""])
    else:
        for stage in sorted(by_stage):
            lines.extend([f"### {stage}", ""])
            for item in sorted(by_stage[stage], key=lambda value: (severity_rank(value["severity"]), value["rule"], value["record"])):
                lines.append(f"- [{item['severity']}] {item['rule']} `{item['record']}`: {item['message']}")
            lines.append("")

    orphan_items = [item for item in findings if item["stage"] == "orphan" or "without" in item["rule"]]
    lines.extend(["## Orphan Records", ""])
    if not orphan_items:
        lines.extend(["None.", ""])
    else:
        for item in orphan_items:
            lines.append(f"- [{item['severity']}] {item['rule']} `{item['record']}`: {item['message']}")
        lines.append("")

    status_items = [item for item in findings if item["stage"] == "status" or "completed" in item["rule"] or "done-task" in item["rule"]]
    lines.extend(["## Status Consistency", ""])
    if not status_items:
        lines.extend(["None.", ""])
    else:
        for item in status_items:
            lines.append(f"- [{item['severity']}] {item['rule']} `{item['record']}`: {item['message']}")
        lines.append("")

    lines.extend([
        "## Suggested Manual Fixes",
        "",
        "- Add missing Source ID references manually after checking the original source.",
        "- Link requirements to Source ID; link executable tasks to Source ID or Requirement ID.",
        "- Link completed tasks to verification evidence before treating them as done.",
        "- Link changelog entries to Task ID, Source ID, or change ID when practical.",
        "- Resolve status conflicts by updating the owner document, not by duplicating facts across docs.",
        "",
        "## Report-only Notice",
        "",
        "- No automatic Source ID creation.",
        "- No automatic task-intake, requirements, task-board, work-log, changelog, or change artifact edits.",
        "- No automatic archive, link rewriting, runner, daemon, auto PR, worktree automation, commit, tag, or push.",
        "",
    ])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def run(project_root):
    project_root = project_root.resolve()
    if not project_root.is_dir():
        fail(f"project root does not exist: {project_root}")
    docs_root_rel, change_root_rel, docs, changes = extract_snapshot(project_root)
    report_path = safe_project_path(project_root, REPORT_REL)
    sets = trace_sets(docs, changes)
    findings = []
    check_source_records(findings, docs, sets)
    check_requirements(findings, sets)
    check_tasks(findings, sets)
    check_changes(findings, sets)
    check_verification(findings, docs, sets)
    check_worklog_changelog(findings, docs, sets)
    check_orphans(findings, sets)
    check_status_conflicts(findings, docs, sets)

    manifest_path = project_root / ".forgekit" / "template-manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for item in manifest.get("files", []):
                if "source-trace-report.md" in item.get("source_path", "") or "source-trace-report.md" in item.get("target_path", ""):
                    add_finding(findings, "error", "report", "report-in-manifest", "template-manifest.json", "source-trace-report.md is listed in template manifest.", "Remove generated reports from manifest.")
        except Exception as exc:
            add_finding(findings, "warning", "report", "manifest-parse", "template-manifest.json", f"Could not parse template manifest: {exc}", "Fix manifest JSON.")

    write_report(project_root, report_path, docs_root_rel, change_root_rel, sets, findings)
    print(f"[ok] Source trace report written: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate a report-only ForgeKit source trace report.")
    parser.add_argument("--project-root", default=".", help="Project root. Defaults to current directory.")
    args = parser.parse_args()
    run(Path(args.project_root))


if __name__ == "__main__":
    main()
