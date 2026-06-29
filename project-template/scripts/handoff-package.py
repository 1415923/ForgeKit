#!/usr/bin/env python3
import argparse
import re
from datetime import datetime, timezone
from pathlib import Path


REPORT_REL = ".forgekit/handoff-package.md"
DEFAULT_DOCS_ROOT = ".forgekit/docs"
DEFAULT_CHANGE_ROOT = ".forgekit/changes"

SOURCE_RE = re.compile(r"\bSRC-\d{8}-\d{3}\b", re.IGNORECASE)
TASK_RE = re.compile(r"\b(?:TASK|BUG)-\d{3,}\b", re.IGNORECASE)
REQ_RE = re.compile(r"\bREQ-\d{3,}\b", re.IGNORECASE)
CHANGE_RE = re.compile(r"\b(?:CHG|CHANGE)-[A-Za-z0-9._-]+\b", re.IGNORECASE)

VERIFY_TERMS = ("verification", "verified", "test", "passed", "[ok]", "验证", "测试", "通过")
RISK_TERMS = ("risk", "blocked", "blocker", "todo_review", "todo-review", "风险", "阻塞", "待复查")
CHANGED_TERMS = ("changed", "added", "fixed", "done", "completed", "完成", "修复", "新增", "变更")
NOT_CHANGED_TERMS = ("non-goal", "not changed", "out of scope", "未改", "不变", "非目标", "不包含")
WARNING_TERMS = ("warning", "error", "TODO_REVIEW", "manual_review", "blocked", "缺失", "风险")
REVIEW_TERMS = ("ReviewDecision:", "ReviewType:", "ReviewerAgent:", "ReviewedRange:", "FinalVerdict:")


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
    return sorted({match.group(0).upper() for match in pattern.finditer(text or "")})


def first_lines(text, limit=8):
    result = []
    for line in (text or "").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        result.append(stripped)
        if len(result) >= limit:
            break
    return result


def matching_lines(text, terms, limit=10):
    result = []
    for idx, line in enumerate((text or "").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if any(term.lower() in lowered for term in terms):
            result.append((idx, stripped))
            if len(result) >= limit:
                break
    return result


def bullet_lines(items, empty="- TODO_REVIEW: missing"):
    if not items:
        return [empty]
    return [f"- {item}" for item in items]


def id_summary(label, values):
    if not values:
        return f"- {label}: TODO_REVIEW missing"
    shown = ", ".join(values[:12])
    if len(values) > 12:
        shown += f", ... (+{len(values) - 12})"
    return f"- {label}: {shown}"


def load_docs(project_root, docs_root):
    names = [
        "task-intake",
        "requirements",
        "task-board",
        "work-log",
        "testing",
        "changelog",
        "risk-register",
    ]
    docs = {}
    for name in names:
        path = docs_root / f"{name}.md"
        docs[name] = {"path": path, "text": read_text(path), "exists": path.is_file()}
    return docs


def load_change_files(change_dir):
    if not change_dir or not change_dir.is_dir():
        return {}
    result = {}
    for path in sorted(change_dir.glob("*.md")):
        result[path.name] = {"path": path, "text": read_text(path)}
    return result


def collect_scope(docs, change_files):
    combined = "\n".join([doc["text"] for doc in docs.values()] + [item["text"] for item in change_files.values()])
    return {
        "source_ids": ids(SOURCE_RE, combined),
        "task_ids": ids(TASK_RE, combined),
        "requirement_ids": ids(REQ_RE, combined),
        "change_ids": ids(CHANGE_RE, combined),
    }


def collect_verification(docs, change_files):
    sources = []
    for name in ("testing", "work-log"):
        for idx, line in matching_lines(docs[name]["text"], VERIFY_TERMS, limit=8):
            sources.append(f"{docs[name]['path'].as_posix()}:{idx}: {line}")
    for file_name, item in change_files.items():
        if "verification" in file_name.lower() or "review" in file_name.lower() or "ship" in file_name.lower():
            for idx, line in matching_lines(item["text"], VERIFY_TERMS, limit=6):
                sources.append(f"{item['path'].as_posix()}:{idx}: {line}")
    return sources


def collect_risks(docs, change_files):
    risks = []
    for name in ("risk-register", "task-board", "work-log"):
        for idx, line in matching_lines(docs[name]["text"], RISK_TERMS, limit=8):
            risks.append(f"{docs[name]['path'].as_posix()}:{idx}: {line}")
    for file_name, item in change_files.items():
        if file_name in {"review.md", "ship.md", "retro.md"}:
            for idx, line in matching_lines(item["text"], RISK_TERMS, limit=5):
                risks.append(f"{item['path'].as_posix()}:{idx}: {line}")
    return risks


def collect_review_evidence(change_files):
    review = change_files.get("review.md")
    if not review:
        return []
    evidence = []
    for idx, line in enumerate(review["text"].splitlines(), start=1):
        if any(line.strip().startswith(term) for term in REVIEW_TERMS):
            evidence.append(f"{review['path'].as_posix()}:{idx}: {line.strip()}")
    return evidence


def summarize_report(path):
    if not path.is_file():
        return [f"- {path.as_posix()}: missing"]
    text = read_text(path)
    lines = matching_lines(text, WARNING_TERMS, limit=8)
    if not lines:
        return [f"- {path.as_posix()}: present; no warning/error keywords found by handoff script"]
    return [f"- {path.as_posix()}:{idx}: {line}" for idx, line in lines]


def build_report(project_root, docs_root, change_root, change_id=None):
    docs = load_docs(project_root, docs_root)
    missing_docs = [item["path"].as_posix() for item in docs.values() if not item["exists"]]
    change_dir = None
    if change_id:
        if Path(change_id).is_absolute() or any(part == ".." for part in Path(change_id).parts):
            fail(f"unsafe change id: {change_id}")
        change_dir = safe_project_path(project_root, f"{change_root.relative_to(project_root).as_posix()}/{change_id}")
    change_files = load_change_files(change_dir)
    scope = collect_scope(docs, change_files)
    verification = collect_verification(docs, change_files)
    risks = collect_risks(docs, change_files)
    review_evidence = collect_review_evidence(change_files)

    changed = []
    for name in ("changelog", "work-log", "task-board"):
        for idx, line in matching_lines(docs[name]["text"], CHANGED_TERMS, limit=8):
            changed.append(f"{docs[name]['path'].as_posix()}:{idx}: {line}")
    for file_name, item in change_files.items():
        if file_name in {"tasks.md", "review.md", "ship.md"}:
            for idx, line in matching_lines(item["text"], CHANGED_TERMS, limit=6):
                changed.append(f"{item['path'].as_posix()}:{idx}: {line}")

    not_changed = []
    for name in ("requirements", "changelog"):
        for idx, line in matching_lines(docs[name]["text"], NOT_CHANGED_TERMS, limit=5):
            not_changed.append(f"{docs[name]['path'].as_posix()}:{idx}: {line}")
    for file_name, item in change_files.items():
        if file_name in {"proposal.md", "ship.md"}:
            for idx, line in matching_lines(item["text"], NOT_CHANGED_TERMS, limit=5):
                not_changed.append(f"{item['path'].as_posix()}:{idx}: {line}")

    todo = []
    if missing_docs:
        todo.append("TODO_REVIEW: some source docs are missing; do not infer missing facts.")
    if not scope["source_ids"] and not scope["requirement_ids"]:
        todo.append("TODO_REVIEW: source or requirement trace is unclear.")
    if not verification:
        todo.append("TODO_REVIEW: verification evidence is missing or not machine-detectable.")
    if not risks:
        todo.append("TODO_REVIEW: risk/blocker status is not explicit; confirm whether there are open risks.")
    if change_id and not review_evidence:
        todo.append("TODO_REVIEW: independent code review evidence is missing from change review.md.")

    doc_health_path = project_root / ".forgekit" / "doc-health-report.md"
    source_trace_path = project_root / ".forgekit" / "source-trace-report.md"

    artifact_lines = []
    for name, item in docs.items():
        state = "present" if item["exists"] else "missing"
        artifact_lines.append(f"- {item['path'].as_posix()}: {state}")
    if change_id:
        if change_dir and change_dir.is_dir():
            for item in sorted(change_dir.glob("*.md")):
                artifact_lines.append(f"- {item.as_posix()}: present")
        else:
            artifact_lines.append(f"- {change_dir.as_posix() if change_dir else change_id}: missing")
    artifact_lines.append(f"- {doc_health_path.as_posix()}: {'present' if doc_health_path.is_file() else 'missing'}")
    artifact_lines.append(f"- {source_trace_path.as_posix()}: {'present' if source_trace_path.is_file() else 'missing'}")

    summary = [
        "# Review-Ready Handoff Package",
        "",
        "Status: report-only",
        "Mode: handoff-package",
        f"Generated: {utc_now()}",
        f"ScopeType: {'change' if change_id else 'project'}",
        f"ChangeId: {change_id or 'not-scoped'}",
        "",
        "## Summary",
        "",
        "- This package summarizes existing ForgeKit records for human review.",
        "- It does not modify current docs, business docs, task state, changelog, Git, PRs, or archive files.",
        "- Missing or unclear evidence is marked TODO_REVIEW instead of being invented.",
        "",
        "## Scope",
        "",
        f"- ProjectRoot: {project_root.as_posix()}",
        f"- ManagedDocsRoot: {docs_root.relative_to(project_root).as_posix() if project_root in docs_root.parents else docs_root.as_posix()}",
        f"- ChangeRoot: {change_root.relative_to(project_root).as_posix() if project_root in change_root.parents else change_root.as_posix()}",
        f"- ChangeDir: {change_dir.as_posix() if change_dir else 'not-scoped'}",
        "",
        "## Source / Requirement Trace",
        "",
        id_summary("Source IDs", scope["source_ids"]),
        id_summary("Requirement IDs", scope["requirement_ids"]),
        id_summary("Task IDs", scope["task_ids"]),
        id_summary("Change IDs", scope["change_ids"]),
        "",
        "## What Changed",
        "",
        *bullet_lines(changed, "- TODO_REVIEW: no explicit changed/done lines found in source docs."),
        "",
        "## What Did Not Change",
        "",
        *bullet_lines(not_changed, "- TODO_REVIEW: non-goals or unchanged scope are not explicit."),
        "",
        "## Verification Evidence",
        "",
        *bullet_lines(verification, "- TODO_REVIEW: verification evidence missing."),
        "",
        "## Independent Code Review",
        "",
        *bullet_lines(review_evidence, "- TODO_REVIEW: independent review evidence is not available for this handoff scope."),
        "",
        "## Doc Health / Source Trace Status",
        "",
        *summarize_report(doc_health_path),
        *summarize_report(source_trace_path),
        "",
        "## Risks / Blockers / TODO_REVIEW",
        "",
        *bullet_lines(risks + todo, "- No explicit risks/blockers found; confirm manually if this is expected."),
        "",
        "## Files / Artifacts",
        "",
        *artifact_lines,
        "",
        "## Human Review Checklist",
        "",
        "- [ ] Source / Requirement Trace is acceptable, or TODO_REVIEW items are resolved.",
        "- [ ] What Changed matches the actual implementation and user-visible behavior.",
        "- [ ] What Did Not Change is explicit enough for reviewer / tester / leader review.",
        "- [ ] Verification Evidence is enough for the current risk level.",
        "- [ ] Independent Review is pass, or needs-fix/manual-review has explicit human risk acceptance.",
        "- [ ] Doc Health / Source Trace warnings are acknowledged or intentionally deferred.",
        "- [ ] Risks / Blockers are accepted, assigned, or closed.",
        "",
        "## Report-only Notice",
        "",
        "This handoff package is generated report-only output. It must not be treated as a source of current truth, and it must not trigger automatic fixes, doc rewrites, commits, PRs, runner execution, daemon execution, or worktree automation.",
        "",
    ]
    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(description="Generate a report-only ForgeKit handoff package.")
    parser.add_argument("--project-root", default=".", help="Project root containing .forgekit")
    parser.add_argument("--change-id", help="Optional change id; writes .forgekit/changes/<id>/handoff.md")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if not project_root.is_dir():
        fail(f"project root does not exist: {project_root}")

    docs_root_rel = read_boundary_value(project_root, "managed_docs_root", DEFAULT_DOCS_ROOT)
    change_root_rel = read_boundary_value(project_root, "change_root", DEFAULT_CHANGE_ROOT)
    docs_root = safe_project_path(project_root, docs_root_rel)
    change_root = safe_project_path(project_root, change_root_rel)

    if args.change_id:
        output_path = safe_project_path(project_root, f"{change_root_rel.rstrip('/')}/{args.change_id}/handoff.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_path = safe_project_path(project_root, REPORT_REL)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    report = build_report(project_root, docs_root, change_root, args.change_id)
    output_path.write_text(report, encoding="utf-8")
    print(f"[ok] Wrote report-only handoff package: {output_path}")
    print("[ok] No current docs, business docs, task state, Git, PR, runner, daemon, or worktree automation was modified.")


if __name__ == "__main__":
    main()
