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
VALIDATION_RELEVANCE = {
    "RELEVANT_REGRESSION", "KNOWN_UNRELATED_FAILURE",
    "TEST_INFRASTRUCTURE_FAILURE", "CLAIM_CRITICAL_VALIDATION_FAILURE",
}
IMPACT_SEVERITIES = {"CRITICAL", "MAJOR", "MINOR", "NOTE"}
PRIMARY_CONSEQUENCES = {"C1", "C2", "C3", "C4"}


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


def finding(
    impact_severity,
    blocking,
    code,
    message,
    evidence=None,
    *,
    primary_consequence=None,
    failure_path=None,
    blocked_scope=None,
    validation_relevance=None,
):
    if impact_severity not in IMPACT_SEVERITIES:
        raise RuntimeError(f"invalid impact severity for {code}: {impact_severity}")
    result = {
        "severity": "blocking" if blocking else "warning",
        "impact_severity": impact_severity,
        "blocking": blocking,
        "code": code,
        "message": message,
    }
    if evidence:
        result["evidence"] = evidence
    if validation_relevance:
        if validation_relevance not in VALIDATION_RELEVANCE:
            raise RuntimeError(f"invalid validation relevance for {code}: {validation_relevance}")
        result["validation_relevance"] = validation_relevance
    if blocking:
        if not all([primary_consequence, failure_path, blocked_scope, evidence]):
            raise RuntimeError(f"blocking finding {code} is missing its canonical consequence evidence")
        if primary_consequence not in PRIMARY_CONSEQUENCES:
            raise RuntimeError(f"invalid primary consequence for {code}: {primary_consequence}")
        result["primary_consequence"] = primary_consequence
        result["failure_path"] = failure_path
        result["blocked_scope"] = blocked_scope
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
                    "MAJOR", True, "active-work-completed-archive",
                    "Active tasks exist, so this archive cannot be described as a completed phase archive.",
                    str(resolved),
                    primary_consequence="C4",
                    failure_path="The archive summary declares phase completion while current task records still contain active work.",
                    blocked_scope="completion of this archive capsule",
                ))
    return failures


def closure_writeback_findings(root):
    """Use only explicit existing change markers; do not infer facts from prose."""
    changes = root / ".forgekit/changes"
    if not changes.is_dir():
        return []
    failures = []
    closed = re.compile(r"(?mi)^Status:\s*(?:done|closed|shipped|handed-off)\s*$")
    missing_sync = re.compile(r"(?mi)^CurrentDocsSync:\s*missing(?:\s|$)")
    for change in sorted(path for path in changes.iterdir() if path.is_dir() and path.name != "_template"):
        proposal = change / "proposal.md"
        review = change / "review.md"
        if not proposal.is_file() or not review.is_file():
            continue
        proposal_text = read_text(proposal)
        review_text = read_text(review)
        if not closed.search(proposal_text) or not missing_sync.search(review_text):
            continue
        evidence = f"{proposal.relative_to(root).as_posix()}; {review.relative_to(root).as_posix()}"
        failures.append(finding(
            "MINOR", True, "closure-current-docs-sync-missing",
            f"Change {change.name} declares closure while CurrentDocsSync explicitly remains missing.",
            evidence,
            primary_consequence="C3",
            failure_path="The structured closure marker and explicit missing-sync marker show that confirmed change facts are not traceable from their current owner.",
            blocked_scope=f"closure, handover, or ship declaration for change {change.name}",
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
                "MAJOR", True, "missing-task-source-link",
                f"Active task {task['id']} has no real Source ID backlink.",
                ".forgekit/docs/task-board.md",
                primary_consequence="C3",
                failure_path="The active task has no source backlink, so its assignment authority cannot be recovered from current docs.",
                blocked_scope=f"closure or archive of active task {task['id']}",
            ))
        for source_id in task["sources"]:
            if source_id not in sources:
                findings.append(finding(
                    "MAJOR", True, "missing-source-record",
                    f"{task['id']} references {source_id}, but task-intake.md has no real Source Record.",
                    ".forgekit/docs/task-board.md",
                    primary_consequence="C3",
                    failure_path="The active task points to a Source ID whose authoritative assignment record is absent.",
                    blocked_scope=f"closure or archive of active task {task['id']}",
                ))

    work_log = docs / "work-log.md"
    if work_log.is_file():
        log = read_text(work_log)
        handed_off = re.search(r"Status:\s*handed-off", log, re.IGNORECASE)
        corrected = re.search(r"superseded|corrected|已更正|已覆盖|恢复当前状态", log, re.IGNORECASE)
        if handed_off and active and not corrected:
            supported = bool(re.search(r"TASK-[A-Za-z0-9_-]+", log, re.IGNORECASE))
            if supported:
                findings.append(finding(
                    "MINOR", True, "stale-handed-off-status",
                    "work-log.md contains Status: handed-off while active tasks remain, without a superseded/corrected note.",
                    ".forgekit/docs/work-log.md",
                    primary_consequence="C4",
                    failure_path="The explicit handoff marker conflicts with an identified active task and can direct the next writer from stale current state.",
                    blocked_scope="handover declaration for the identified active task",
                ))
            else:
                findings.append(finding(
                    "MINOR", False, "stale-handed-off-status",
                    "work-log.md contains Status: handed-off while active tasks remain, but no task-specific failure path is established.",
                    ".forgekit/docs/work-log.md",
                ))

    findings.extend(archive_semantics(root, active, archive_summary))
    findings.extend(closure_writeback_findings(root))
    if active:
        plan = root / ".forgekit/archive-capsule-plan.md"
        if plan.is_file() and "TODO_REVIEW" in read_text(plan):
            risk_text = texts["risk-register"].lower()
            if "archive" not in risk_text and "migration" not in risk_text and "归档" not in risk_text and "迁移" not in risk_text:
                findings.append(finding(
                    "NOTE", False, "archive-todo-not-in-current-risk",
                    "Archive or migration TODO_REVIEW exists, but current risk-register has no corresponding open/accepted risk.",
                    ".forgekit/archive-capsule-plan.md",
                ))
    if not (root / ".git").exists():
        findings.append(finding(
            "MAJOR", False, "non-git-project-root",
            "Project root is not a Git repository; integrity checks continue without Git diff evidence.",
            str(root),
            validation_relevance="TEST_INFRASTRUCTURE_FAILURE",
        ))
    blocking = sum(item["blocking"] for item in findings)
    warnings = sum(not item["blocking"] for item in findings)
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
        blocking = "YES" if item["blocking"] else "NO"
        print(f"[{item['severity']}] {item['code']}: {item['message']} (Impact: {item['impact_severity']}; Blocking: {blocking})")
    if report["blocking_count"]:
        print("Current State Restoration Pass required before archive apply.")
        print(report["restoration_guidance"])


def main():
    parser = argparse.ArgumentParser(description="Read-only ForgeKit current docs integrity guard")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true", help="Return 1 when non-blocking findings are present")
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
    return 1 if report["blocking_count"] or (args.strict and report["warning_count"]) else 0


if __name__ == "__main__":
    sys.exit(main())
