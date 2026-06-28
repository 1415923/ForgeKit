#!/usr/bin/env python3
import argparse
import datetime as _dt
import importlib.util
import json
import shutil
from pathlib import Path


def _load_versioning_module():
    module_path = Path(__file__).resolve().with_name("update-template-manifest.py")
    spec = importlib.util.spec_from_file_location("forgekit_template_versioning", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


versioning = _load_versioning_module()


CORE_REVIEW_TARGETS = {
    "AGENTS.md",
    "CLAUDE.md",
    ".codex/rules.md",
    ".forgekit/docs/document-responsibility.md",
    ".forgekit/docs/codebase-map.md",
    ".forgekit/docs/task-intake.md",
    ".forgekit/docs/task-board.md",
    ".forgekit/docs/work-log.md",
}


def fail(message):
    raise SystemExit(f"[fail] {message}")


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def safe_project_path(path):
    root = Path(path).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def rel(path):
    return versioning.normalize_posix(path)


def load_lock(project_root):
    lock_path = project_root / ".forgekit" / "template-lock.json"
    if not lock_path.exists():
        return None
    return versioning.load_json(lock_path)


def target_is_do_not_touch(target_path, boundary):
    if versioning.path_matches_root(target_path, ".git"):
        return True
    if versioning.path_matches_root(target_path, ".forgekit/archive"):
        return True
    if versioning.path_matches_root(target_path, ".forgekit/upgrade"):
        return True
    if target_path in {
        ".forgekit/template-lock.json",
        ".forgekit/upgrade-report.md",
        ".forgekit/archive-plan.md",
        ".forgekit/archive-apply-report.md",
        ".forgekit/archive-reference-report.md",
        ".forgekit/current-docs-sync-report.md",
        ".forgekit/smart-archive-report.md",
        ".forgekit/smart-archive-apply-report.md",
    }:
        return True
    for business_root in boundary.get("business_docs_roots", []):
        if versioning.path_matches_root(target_path, business_root):
            return True
    return False


def high_level_status(low_level, target_path, item, lock_missing=False):
    if lock_missing:
        return "legacy_needs_inventory"
    if target_path in CORE_REVIEW_TARGETS:
        return "must_review"
    if item.get("role") in {"agent_entry", "codex_rule", "boundary_config"}:
        return "must_review"
    if item.get("role") == "change_template":
        return "template_only"
    if item.get("update_policy") in {"ask", "readonly"}:
        return "template_only"
    if low_level == "needs_merge_report":
        return "merge_carefully"
    if low_level == "can_restore":
        return "can_add"
    if low_level == "can_replace":
        if item.get("role") in {"managed_doc", "readme"}:
            return "must_review"
        return "can_ignore"
    return "can_ignore"


def classify_entries(repo_root, project_root, manifest, boundary, lock):
    template_root = repo_root / "project-template"
    lock_by_target = {}
    if lock:
        lock_by_target = {
            versioning.normalize_posix(item.get("target_path", "")): item
            for item in lock.get("files", [])
        }

    entries = []
    for item in manifest["files"]:
        target_path = versioning.expand_target_path(item["target_path"], boundary)
        versioning.validate_target_path(target_path, boundary)
        item = dict(item)
        item["target_path_expanded"] = target_path
        target_file = project_root / Path(target_path)
        current_checksum = versioning.sha256_file(target_file) if target_file.is_file() else ""

        if target_is_do_not_touch(target_path, boundary):
            low_level = "report_only"
            status = "do_not_touch"
        elif lock is None:
            low_level = "legacy_no_lock"
            status = high_level_status(low_level, target_path, item, lock_missing=True)
        else:
            low_level = versioning.classify_entry(item, lock_by_target, target_file, current_checksum)
            status = high_level_status(low_level, target_path, item)

        entries.append({
            "status": status,
            "low_level_status": low_level,
            "source_path": versioning.normalize_posix(item["source_path"]),
            "target_path": target_path,
            "role": item["role"],
            "update_policy": item["update_policy"],
            "render_mode": item["render_mode"],
            "source_checksum": item.get("checksum", ""),
            "current_checksum": current_checksum,
            "exists": target_file.exists(),
        })

        candidate_path = project_root / ".forgekit" / "upgrade" / "candidates" / manifest["template_version"] / Path(target_path)
        candidate_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(template_root / Path(item["source_path"]), candidate_path)
    return entries


def summarize(entries):
    keys = [
        "must_review",
        "merge_carefully",
        "can_add",
        "can_ignore",
        "template_only",
        "do_not_touch",
        "legacy_needs_inventory",
    ]
    counts = {key: 0 for key in keys}
    for entry in entries:
        counts[entry["status"]] = counts.get(entry["status"], 0) + 1
    return counts


def render_plan(project_root, manifest, boundary, lock, entries):
    version = manifest["template_version"]
    counts = summarize(entries)
    from_version = "unknown" if lock is None else lock.get("installed_version", "unknown")
    generated = _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    lines = [
        "# ForgeKit Upgrade Plan",
        "",
        "Status: report-only",
        "Mode: guided-upgrade",
        f"From Version: {from_version}",
        f"To Version: {version}",
        f"Generated: {generated}",
        f"ProjectRoot: {project_root}",
        f"ManagedDocsRoot: {boundary['managed_docs_root']}",
        f"ChangeRoot: {boundary['change_root']}",
        "",
        "## Policy",
        "",
        "- No project files were overwritten.",
        "- No current docs were modified.",
        "- No business docs were modified.",
        "- No template-lock was created or updated.",
        "- Candidate templates are comparison material only.",
        "",
        "## Start Here",
        "",
        "1. Read `.forgekit/upgrade/upgrade-actions.md`.",
        "2. Review `must_review` first.",
        "3. Merge only useful rules or template sections; do not overwrite project facts.",
        "4. Ignore `template_only` unless you actively use that workflow.",
        "5. After manual merge, run `.forgekit/scripts/check-doc-sync` if available or project validation commands.",
        "",
        "## Summary",
        "",
    ]
    for key in [
        "must_review",
        "merge_carefully",
        "can_add",
        "can_ignore",
        "template_only",
        "do_not_touch",
        "legacy_needs_inventory",
    ]:
        lines.append(f"- {key}: {counts.get(key, 0)}")
    lines.extend(["", "## Files", ""])
    for status in [
        "must_review",
        "merge_carefully",
        "can_add",
        "legacy_needs_inventory",
        "template_only",
        "can_ignore",
        "do_not_touch",
    ]:
        subset = [entry for entry in entries if entry["status"] == status]
        if not subset:
            continue
        lines.extend([f"### {status}", "", "| target_path | source_path | role | reason |", "| --- | --- | --- | --- |"])
        for entry in subset:
            reason = entry["low_level_status"]
            if status == "must_review":
                reason = "entry or daily workflow changed"
            elif status == "legacy_needs_inventory":
                reason = "project has no template-lock baseline"
            lines.append(f"| `{entry['target_path']}` | `{entry['source_path']}` | {entry['role']} | {reason} |")
        lines.append("")
    return "\n".join(lines)


def render_actions(entries):
    lines = [
        "# ForgeKit Upgrade Actions",
        "",
        "Status: report-only",
        "Mode: guided-upgrade-actions",
        "",
        "1. Read `.forgekit/upgrade/upgrade-plan.md`.",
        "2. Inspect only `must_review`, `merge_carefully`, and needed `can_add` files.",
        "3. Do not overwrite project facts, business docs, source code, secrets, deploy files, CI, or `.forgekit/template-lock.json`.",
        "4. Merge stable new rules into the existing project files by hand or with AI assistance.",
        "5. Keep `.forgekit/upgrade/candidates/**` as comparison material, not current-state docs.",
        "6. After merging, run project validation and document sync checks.",
        "7. Summarize changed files, skipped files, and any remaining manual review.",
        "",
        "## Recommended Review Order",
        "",
    ]
    for status in ["must_review", "merge_carefully", "can_add"]:
        subset = [entry for entry in entries if entry["status"] == status]
        if not subset:
            continue
        lines.append(f"### {status}")
        for entry in subset[:25]:
            lines.append(f"- `{entry['target_path']}`")
        lines.append("")
    return "\n".join(lines)


def render_legacy_inventory(project_root, boundary, entries):
    paths = [
        "AGENTS.md",
        "CLAUDE.md",
        ".codex/rules.md",
        ".forgekit/project-boundary.yml",
        ".forgekit/docs/document-responsibility.md",
        ".forgekit/docs/codebase-map.md",
        ".forgekit/docs/task-intake.md",
        ".forgekit/docs/task-board.md",
        ".forgekit/docs/work-log.md",
        "docs",
    ]
    lines = [
        "# ForgeKit Legacy Inventory",
        "",
        "Status: report-only",
        "Mode: legacy-inventory",
        "",
        "This project does not have `.forgekit/template-lock.json`. ForgeKit did not infer a baseline, create a lock, overwrite files, or migrate docs.",
        "",
        "## Detected Paths",
        "",
        "| path | exists |",
        "| --- | --- |",
    ]
    for item in paths:
        lines.append(f"| `{item}` | {str((project_root / Path(item)).exists()).lower()} |")
    lines.extend([
        "",
        "## Recommendation",
        "",
        "- Review `must_review` in `upgrade-plan.md` first.",
        "- If an old project still uses root `docs/*.md` as ForgeKit managed docs, do not auto-move them. Merge manually into the configured managed docs root.",
        f"- Managed docs root from boundary/default: `{boundary['managed_docs_root']}`.",
        f"- Change root from boundary/default: `{boundary['change_root']}`.",
    ])
    return "\n".join(lines)


def write_inventory(project_root, manifest, boundary, entries):
    data = {
        "schema_version": 1,
        "status": "report-only",
        "mode": "guided-upgrade",
        "template_version": manifest["template_version"],
        "managed_docs_root": boundary["managed_docs_root"],
        "change_root": boundary["change_root"],
        "entries": entries,
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def run(args):
    print("[legacy] Guided template-diff upgrade is retained for compatibility only.")
    print("[legacy] For v0.36+ projects use scripts/forgekit-upgrade.py check, plan, and apply --safe.")
    print("[legacy] Pre-v0.36 projects should use existing-project adoption instead of automatic upgrade.")
    repo_root = Path(args.repo_root).resolve()
    project_root = safe_project_path(args.project_path)
    manifest = versioning.load_manifest(repo_root)
    boundary = versioning.read_boundary(project_root)
    lock = load_lock(project_root)
    upgrade_root = project_root / ".forgekit" / "upgrade"
    candidates = upgrade_root / "candidates" / manifest["template_version"]
    if candidates.exists():
        shutil.rmtree(candidates)
    entries = classify_entries(repo_root, project_root, manifest, boundary, lock)
    write_text(upgrade_root / "upgrade-plan.md", render_plan(project_root, manifest, boundary, lock, entries))
    write_text(upgrade_root / "upgrade-actions.md", render_actions(entries))
    write_text(upgrade_root / "upgrade-inventory.json", write_inventory(project_root, manifest, boundary, entries))
    if lock is None:
        write_text(upgrade_root / "legacy-inventory.md", render_legacy_inventory(project_root, boundary, entries))
    print("[copy] .forgekit/upgrade/upgrade-plan.md")
    print("[copy] .forgekit/upgrade/upgrade-actions.md")
    print("[copy] .forgekit/upgrade/upgrade-inventory.json")
    print(f"[copy] .forgekit/upgrade/candidates/{manifest['template_version']}")
    if lock is None:
        print("[copy] .forgekit/upgrade/legacy-inventory.md")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--project-path", required=True)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
