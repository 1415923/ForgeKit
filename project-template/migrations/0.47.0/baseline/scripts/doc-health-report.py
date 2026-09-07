#!/usr/bin/env python3
import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


REPORT_REL = ".forgekit/doc-health-report.md"
DEFAULT_DOCS_ROOT = ".forgekit/docs"
CHECK_DOCS = ["task-board", "work-log", "changelog", "testing", "requirements", "task-intake"]
LENGTH_LIMITS = {
    "task-board": 260,
    "work-log": 320,
    "changelog": 220,
    "testing": 240,
    "requirements": 240,
}
NOISE_NAMES = {".DS_Store", "Thumbs.db", "__pycache__", ".pytest_cache"}
NOISE_SUFFIXES = (".tmp", ".bak")


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


def line_count(text):
    if not text:
        return 0
    return len(text.splitlines())


def add_finding(findings, severity, document, rule, message, suggestion):
    findings.append({
        "severity": severity,
        "document": document,
        "rule": rule,
        "message": message,
        "suggestion": suggestion,
    })


def check_length(findings, docs):
    for name, limit in LENGTH_LIMITS.items():
        text = docs.get(name, "")
        count = line_count(text)
        if count > limit:
            add_finding(
                findings,
                "warning",
                f"{name}.md",
                "document-too-long",
                f"{name}.md has {count} lines; suggested soft limit is {limit}.",
                "Move process history to work-log or change artifacts; keep current facts compact.",
            )


def count_terms(text, terms):
    lowered = text.lower()
    return sum(lowered.count(term.lower()) for term in terms)


def check_role_mismatch(findings, docs):
    task_board = docs.get("task-board", "")
    if count_terms(task_board, ["今天", "运行", "验证通过", "提交", "推送", "阶段收口", "工作日志"]) >= 4:
        add_finding(findings, "warning", "task-board.md", "role-mismatch", "task-board looks like it contains process log details.", "Keep task-board to compact task status; move process notes to work-log.md.")

    changelog = docs.get("changelog", "")
    if count_terms(changelog, ["今天", "日报", "提交", "推送", "验证结果", "运行了", "工作日志"]) >= 3:
        add_finding(findings, "warning", "changelog.md", "role-mismatch", "changelog looks like daily work history.", "Keep changelog to user/version-visible changes; move daily flow to work-log.md.")

    testing = docs.get("testing", "")
    if count_terms(testing, ["traceback", "stack trace", "[ok]", "[fail]", "passed", "failed", "运行输出", "日志"]) >= 4:
        add_finding(findings, "warning", "testing.md", "role-mismatch", "testing may contain one-off run output.", "Keep testing.md as verification manual; move run results to work-log.md or changes/<id>/verification.md.")

    requirements = docs.get("requirements", "")
    if count_terms(requirements, ["Original Text", "领导原话", "微信原文", "Human Review: pending", "未经确认"]) >= 2:
        add_finding(findings, "warning", "requirements.md", "role-mismatch", "requirements may contain unconfirmed source text.", "Keep source text in task-intake.md; requirements.md should contain stable facts with Source ID.")

    task_intake = docs.get("task-intake", "")
    if "AI" in task_intake and "AI Interpretation" not in task_intake:
        add_finding(findings, "info", "task-intake.md", "missing-ai-label", "task-intake mentions AI but may not label AI interpretation explicitly.", "Separate Original Text from AI Interpretation and keep Human Review status explicit.")

    work_log = docs.get("work-log", "")
    if count_terms(work_log, ["Open Tasks", "Backlog", "Task Gate", "验收标准", "全部任务", "任务看板"]) >= 2:
        add_finding(findings, "warning", "work-log.md", "role-mismatch", "work-log may be carrying task-board responsibilities.", "Keep work-log to recent execution windows; put task status in task-board.md.")


def normalize_fact(line):
    line = line.strip()
    line = re.sub(r"^[#*\-\d.\s\[\]xX|]+", "", line).strip()
    line = re.sub(r"\s+", " ", line)
    return line


def check_duplicates(findings, docs):
    seen = defaultdict(set)
    for name in ["task-board", "work-log", "changelog", "requirements"]:
        for raw_line in docs.get(name, "").splitlines():
            normalized = normalize_fact(raw_line)
            if len(normalized) < 28:
                continue
            if normalized.lower() in {"none.", "待补充", "n/a"}:
                continue
            seen[normalized].add(f"{name}.md")
    duplicates = [(fact, sorted(paths)) for fact, paths in seen.items() if len(paths) >= 2]
    for fact, paths in duplicates[:20]:
        add_finding(
            findings,
            "info",
            ", ".join(paths),
            "duplicate-fact",
            f"Possible repeated fact appears in {', '.join(paths)}: {fact[:140]}",
            "Keep the fact in the owner document and replace other copies with Source ID, Task ID, or a short link.",
        )


def check_router_boundaries(findings, docs, docs_root):
    router_path = docs_root / "workflow-router.md"
    if not router_path.is_file():
        add_finding(findings, "warning", "workflow-router.md", "missing-router", "workflow-router.md is missing.", "Install or merge the v0.32+ workflow-router.md template.")
        return
    router = read_text(router_path)
    required = ["Read Targets", "Write Targets", "Do Not Write", "Required Output"]
    missing = [item for item in required if item not in router]
    if missing:
        add_finding(findings, "warning", "workflow-router.md", "router-incomplete", "workflow-router.md is missing required sections: " + ", ".join(missing), "Merge the latest workflow-router.md template.")

    if "Original Text" in docs.get("requirements", ""):
        add_finding(findings, "warning", "requirements.md", "router-boundary", "requirements.md appears to contain Original Text.", "workflow-router says source text belongs in task-intake.md; keep requirements to stable facts.")
    if "verification result" in docs.get("testing", "").lower() or "验证结果" in docs.get("testing", ""):
        add_finding(findings, "info", "testing.md", "router-boundary", "testing.md may contain verification results.", "workflow-router says results belong in work-log.md or changes/<id>/verification.md unless the method changed.")


def check_generated_noise(findings, project_root, manifest_path):
    noisy = []
    for path in project_root.rglob("*"):
        rel = path.relative_to(project_root).as_posix()
        if ".git/" in rel or rel.startswith(".git/"):
            continue
        if path.name in NOISE_NAMES or path.suffix in NOISE_SUFFIXES or "forgekit-smoke-" in rel:
            noisy.append(rel)
    for rel in noisy[:30]:
        add_finding(findings, "warning", rel, "generated-noise", f"Generated or temporary artifact found: {rel}", "Remove cache/temp files from the project and keep them out of manifest and current docs.")

    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            add_finding(findings, "warning", manifest_path.relative_to(project_root).as_posix(), "manifest-parse", f"template-manifest.json cannot be parsed: {exc}", "Fix manifest JSON before upgrade checks.")
            return
        for item in manifest.get("files", []):
            source = item.get("source_path", "")
            target = item.get("target_path", "")
            if "doc-health-report.md" in source or "doc-health-report.md" in target:
                add_finding(findings, "error", "template-manifest.json", "report-in-manifest", "doc-health-report.md is listed in template manifest.", "Remove generated reports from manifest; reports are not current managed docs.")


def severity_rank(severity):
    return {"error": 0, "warning": 1, "info": 2}.get(severity, 3)


def write_report(project_root, report_path, docs_root_rel, findings):
    grouped_by_severity = defaultdict(list)
    grouped_by_doc = defaultdict(list)
    for item in findings:
        grouped_by_severity[item["severity"]].append(item)
        grouped_by_doc[item["document"]].append(item)

    lines = [
        "# Doc Health Report",
        "",
        "Status: report-only",
        "Mode: doc-health",
        f"Generated: {utc_now()}",
        f"DocsRoot: {docs_root_rel}",
        "",
        "This report does not modify managed docs, business docs, archive files, template-lock, Git state, or external systems.",
        "",
        "## Summary",
        "",
        "| severity | count |",
        "| --- | ---: |",
    ]
    for severity in ["error", "warning", "info"]:
        lines.append(f"| {severity} | {len(grouped_by_severity[severity])} |")

    lines.extend(["", "## Findings by Severity", ""])
    for severity in ["error", "warning", "info"]:
        lines.extend([f"### {severity}", ""])
        items = sorted(grouped_by_severity[severity], key=lambda item: (item["document"], item["rule"]))
        if not items:
            lines.extend(["None.", ""])
            continue
        for item in items:
            lines.extend([
                f"#### {item['document']} - {item['rule']}",
                "",
                f"- Severity: {item['severity']}",
                f"- Message: {item['message']}",
                f"- Suggested manual fix: {item['suggestion']}",
                "",
            ])

    lines.extend(["## Findings by Document", ""])
    if not grouped_by_doc:
        lines.extend(["None.", ""])
    else:
        for document in sorted(grouped_by_doc):
            lines.extend([f"### {document}", ""])
            for item in sorted(grouped_by_doc[document], key=lambda value: (severity_rank(value["severity"]), value["rule"])):
                lines.append(f"- [{item['severity']}] {item['rule']}: {item['message']}")
            lines.append("")

    lines.extend([
        "## Suggested Manual Fixes",
        "",
        "- Keep source text in `task-intake.md`; keep executable status in `task-board.md`; keep recent process in `work-log.md`.",
        "- Keep `testing.md` as a verification manual; move one-off run output to `work-log.md` or `changes/<id>/verification.md`.",
        "- Keep `changelog.md` to user/version-visible changes, not daily work history.",
        "- Replace duplicate long facts with `Source ID`, `Task ID`, or links.",
        "- Review `workflow-router.md` before editing managed docs.",
        "",
        "## Non-Goals",
        "",
        "- No automatic doc slimming.",
        "- No automatic archive or link rewriting.",
        "- No semantic AI judgment.",
        "- No runner, daemon, scheduler, auto PR, worktree automation, commit, tag, or push.",
        "",
    ])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def run(project_root):
    project_root = project_root.resolve()
    if not project_root.is_dir():
        fail(f"project root does not exist: {project_root}")

    docs_root_rel = read_boundary_value(project_root, "managed_docs_root", DEFAULT_DOCS_ROOT)
    docs_root = safe_project_path(project_root, docs_root_rel)
    report_path = safe_project_path(project_root, REPORT_REL)
    manifest_path = project_root / ".forgekit" / "template-manifest.json"

    docs = {}
    for name in CHECK_DOCS:
        docs[name] = read_text(docs_root / f"{name}.md")

    findings = []
    check_length(findings, docs)
    check_role_mismatch(findings, docs)
    check_duplicates(findings, docs)
    check_router_boundaries(findings, docs, docs_root)
    check_generated_noise(findings, project_root, manifest_path)
    write_report(project_root, report_path, docs_root_rel, findings)
    print(f"[ok] Doc health report written: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate a report-only ForgeKit managed docs health report.")
    parser.add_argument("--project-root", default=".", help="Project root. Defaults to current directory.")
    args = parser.parse_args()
    run(Path(args.project_root))


if __name__ == "__main__":
    main()
