#!/usr/bin/env python3
"""Read-only integrity checks for ForgeKit current-state documents."""

import argparse
import json
import re
import sys
from pathlib import Path


ACTIVE_STATUSES = {
    "in progress", "waiting", "review", "backend ready", "needs fix",
    "submitted", "mitigating", "open", "blocked",
}
PLACEHOLDER_MARKERS = {
    "待补充", "src-example-001", "src-yyyymmdd-001", "task-example-001",
    "epic-001", "feat-001", "risk-001",
}
SOURCE_RE = re.compile(r"\bSRC-[A-Za-z0-9][A-Za-z0-9_-]*\b", re.IGNORECASE)
TASK_RE = re.compile(r"\b(?:TASK|BUG)-[A-Za-z0-9][A-Za-z0-9_-]*\b", re.IGNORECASE)


def read_text(path):
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise RuntimeError(f"cannot read {path}: {exc}") from exc


def normalized(value):
    return re.sub(r"\s+", " ", value.strip()).lower()


def is_example(identifier):
    value = identifier.upper()
    return "EXAMPLE" in value or "YYYY" in value or value.endswith("-000")


def table_cells(line):
    if not line.lstrip().startswith("|"):
        return []
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def active_tasks(task_board):
    tasks = []
    for line in task_board.splitlines():
        cells = table_cells(line)
        if not cells or "待补充" in line:
            continue
        task_ids = TASK_RE.findall(line)
        if not task_ids:
            continue
        status = next((state for state in ACTIVE_STATUSES if any(normalized(cell) == state for cell in cells)), None)
        if not status:
            continue
        for task_id in task_ids[:1]:
            if not is_example(task_id):
                sources = [item.upper() for item in SOURCE_RE.findall(line) if not is_example(item)]
                tasks.append({"id": task_id.upper(), "status": status, "sources": sources})
    return tasks


def real_source_records(task_intake):
    records = set()
    for line in task_intake.splitlines():
        if "待补充" in line:
            continue
        for source_id in SOURCE_RE.findall(line):
            if not is_example(source_id):
                records.add(source_id.upper())
    return records


def placeholder_only(text, kind):
    lowered = text.lower()
    if kind == "task-intake":
        return not any(not is_example(item) for item in SOURCE_RE.findall(text))
    if kind == "risk-register":
        no_risk = re.search(r"当前无开放风险.{0,30}(人工确认|confirmed)", text, re.IGNORECASE)
        real_risk = any(
            "待补充" not in line and "RISK-001" not in line.upper()
            and re.search(r"\bRISK-[A-Za-z0-9_-]+\b", line, re.IGNORECASE)
            for line in text.splitlines()
        )
        return not (no_risk or real_risk)
    if kind == "traceability":
        return not any(
            "待补充" not in line and TASK_RE.search(line)
            for line in text.splitlines()
        )
    if kind == "testing":
        if "TODO_REVIEW" in text:
            return False
        meaningful_rows = [
            line for line in text.splitlines() if line.lstrip().startswith("|")
            and "---" not in line and "待补充" not in line
            and not any(header in line for header in ["区域 | 覆盖内容", "场景 | 命令", "ID | 场景", "缺口 | 影响"])
        ]
        return not meaningful_rows
    return all(marker in lowered for marker in [])


def finding(severity, code, message, evidence=None):
    result = {"severity": severity, "code": code, "message": message}
    if evidence:
        result["evidence"] = evidence
    return result


def archive_semantics(root, active, explicit_summary=None):
    if not active:
        return []
    paths = []
    if explicit_summary:
        paths.append(Path(explicit_summary))
    else:
        plan = root / ".forgekit/archive-capsule-plan.md"
        if plan.is_file():
            paths.append(plan)
    failures = []
    completed = re.compile(r"completed phase archive|phase completed|phase complete|阶段完成归档|已完成阶段归档|阶段完成", re.IGNORECASE)
    allowed = re.compile(r"legacy transition snapshot|provisional archive|evidence snapshot|active-work cleanup snapshot", re.IGNORECASE)
    for path in paths:
        resolved = path if path.is_absolute() else root / path
        if resolved.is_file():
            text = read_text(resolved)
            if completed.search(text) and not allowed.search(text):
                failures.append(finding(
                    "blocking", "active-work-completed-archive",
                    "Active tasks exist, so this archive cannot be described as a completed phase archive.",
                    str(resolved),
                ))
    return failures


def run_checks(root, strict=False, archive_summary=None):
    docs = root / ".forgekit/docs"
    required = {
        "task-board": docs / "task-board.md",
        "task-intake": docs / "task-intake.md",
        "risk-register": docs / "risk-register.md",
        "traceability": docs / "traceability.md",
        "testing": docs / "testing.md",
    }
    missing = [str(path.relative_to(root)) for path in required.values() if not path.is_file()]
    if missing:
        raise RuntimeError("required current docs missing: " + ", ".join(missing))

    texts = {name: read_text(path) for name, path in required.items()}
    active = active_tasks(texts["task-board"])
    sources = real_source_records(texts["task-intake"])
    findings = []

    for task in active:
        if not task["sources"]:
            findings.append(finding(
                "blocking", "missing-task-source-link",
                f"Active task {task['id']} has no real Source ID backlink.",
                ".forgekit/docs/task-board.md",
            ))
        for source_id in task["sources"]:
            if source_id not in sources:
                findings.append(finding(
                    "blocking", "missing-source-record",
                    f"{task['id']} references {source_id}, but task-intake.md has no real Source Record.",
                    ".forgekit/docs/task-board.md",
                ))
        if task["id"].upper() not in texts["traceability"].upper():
            findings.append(finding(
                "blocking", "missing-task-trace",
                f"Active task {task['id']} has no minimum traceability entry.",
                ".forgekit/docs/traceability.md",
            ))

    if active:
        for name in ["task-intake", "risk-register", "traceability", "testing"]:
            if placeholder_only(texts[name], name):
                findings.append(finding(
                    "blocking", f"placeholder-only-{name}",
                    f"Active tasks exist, but {name}.md contains only template placeholders.",
                    f".forgekit/docs/{name}.md",
                ))

        review_states = {"review", "backend ready", "submitted", "needs fix"}
        if any(task["status"] in review_states for task in active) and placeholder_only(texts["testing"], "testing"):
            # Keep a dedicated code for callers even when the generic placeholder finding also exists.
            findings.append(finding(
                "blocking", "missing-testing-baseline",
                "A review/submission task exists, but testing.md has no current validation baseline or TODO_REVIEW.",
                ".forgekit/docs/testing.md",
            ))

    work_log = docs / "work-log.md"
    if work_log.is_file():
        log = read_text(work_log)
        handed_off = re.search(r"Status:\s*handed-off", log, re.IGNORECASE)
        corrected = re.search(r"superseded|corrected|已更正|已覆盖|恢复当前状态", log, re.IGNORECASE)
        if handed_off and active and not corrected:
            severity = "blocking" if re.search(r"TASK-[A-Za-z0-9_-]+", log, re.IGNORECASE) else "warning"
            findings.append(finding(
                severity, "stale-handed-off-status",
                "work-log.md contains Status: handed-off while active tasks remain, without a superseded/corrected note.",
                ".forgekit/docs/work-log.md",
            ))

    findings.extend(archive_semantics(root, active, archive_summary))
    if active:
        plan = root / ".forgekit/archive-capsule-plan.md"
        if plan.is_file() and "TODO_REVIEW" in read_text(plan):
            risk_text = texts["risk-register"].lower()
            if "archive" not in risk_text and "migration" not in risk_text and "归档" not in risk_text and "迁移" not in risk_text:
                findings.append(finding(
                    "warning", "archive-todo-not-in-current-risk",
                    "Archive or migration TODO_REVIEW exists, but current risk-register has no corresponding open/accepted risk.",
                    ".forgekit/archive-capsule-plan.md",
                ))
    if not (root / ".git").exists():
        findings.append(finding(
            "warning", "non-git-project-root",
            "Project root is not a Git repository; integrity checks continue without Git diff evidence.",
            str(root),
        ))
    if strict:
        findings = [
            {**item, "severity": "blocking"} if item["severity"] == "warning" else item
            for item in findings
        ]
    blocking = sum(item["severity"] == "blocking" for item in findings)
    warnings = sum(item["severity"] == "warning" for item in findings)
    return {
        "status": "failed" if blocking else "passed",
        "mode": "read-only",
        "repo_root": str(root),
        "active_tasks": active,
        "blocking_count": blocking,
        "warning_count": warnings,
        "findings": findings,
        "restoration_guidance": (
            "Run a Current State Restoration Pass from authoritative evidence. Restore only current Source, Task, "
            "Risk, Traceability, and Testing facts; do not copy the full archive back into current docs."
            if blocking else "not required"
        ),
    }


def print_human(report):
    print("ForgeKit Current Docs Integrity Check")
    print("Mode: read-only")
    print(f"Status: {report['status']}")
    print(f"Active tasks: {len(report['active_tasks'])}")
    print(f"Blocking: {report['blocking_count']}")
    print(f"Warnings: {report['warning_count']}")
    for item in report["findings"]:
        print(f"[{item['severity']}] {item['code']}: {item['message']}")
    if report["blocking_count"]:
        print("Current State Restoration Pass required before archive apply.")
        print(report["restoration_guidance"])


def main():
    parser = argparse.ArgumentParser(description="Read-only ForgeKit current docs integrity guard")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as blocking")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    parser.add_argument("--archive-summary", help=argparse.SUPPRESS)
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    if not root.is_dir():
        print(json.dumps({"status": "error", "error": f"repo root not found: {root}"}) if args.json else f"[error] repo root not found: {root}")
        return 2
    try:
        report = run_checks(root, args.strict, args.archive_summary)
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}) if args.json else f"[error] {exc}")
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 1 if report["blocking_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
