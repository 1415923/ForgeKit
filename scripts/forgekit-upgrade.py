#!/usr/bin/env python3
"""Versioned, safe-only ForgeKit migration entry point."""

import argparse
import datetime as dt
import difflib
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path


MIN_SUPPORTED_VERSION = (0, 36, 0)
STATE_RELATIVE_PATH = Path(".forgekit/state.json")
SAFE_ROOTS = {".forgekit", ".codex", ".agents", ".claude", "governance", "scripts", "migrations"}
REVIEW_REPORT_MD = Path(".forgekit/reports/upgrade-review-needed.md")
REVIEW_REPORT_JSON = Path(".forgekit/reports/upgrade-review-needed.json")
REVIEW_EXPORT_ROOT = Path(".forgekit/reports/review-needed")
REVIEW_POLICIES = {"ask", "keep-local", "manual-merge", "replace-template", "abort"}
LANGUAGES = {"en-US", "zh-CN"}

MESSAGES = {
    "en-US": {
        "review_found_one": "ForgeKit found 1 file that cannot be safely overwritten automatically.",
        "review_found_many": "ForgeKit found {count} files that cannot be safely overwritten automatically.",
        "action_label": "Action:",
        "reason_label": "Reason:",
        "impact_label": "Impact:",
        "recommendation_label": "Recommendation:",
        "choose_action": "Choose an action:",
        "choice_replace": "  [r] replace this file with the current ForgeKit template",
        "choice_manual": "  [m] keep the local file and export the new template sample plus diff",
        "choice_diff": "  [d] show diff",
        "choice_abort": "  [a] abort this upgrade",
        "choice_prompt": "Your choice: ",
        "choice_invalid": "Choose r, m, d, or a.",
        "diff_unavailable_no_source": "[diff unavailable] This review-needed action has no incoming file template.",
        "diff_unavailable_not_file": "[diff unavailable] Target is not a file.",
        "diff_empty": "[diff] no content difference",
        "noninteractive_policy": "Review-needed item requires a policy in non-interactive mode.",
        "run_one_of": "Run one of:",
        "alias_keep_local": "keep-local is treated as manual-merge.",
        "abort_policy": "Review-needed item was aborted by policy; no migration actions were applied.",
        "abort_interactive": "Review-needed item was aborted; no migration actions were applied.",
        "manual_final": "[ok] project is updated to {version} with {count} manual-merge {noun}",
        "manual_exported": "[ok] new template sample exported to {path}",
        "fully_updated": "[ok] project is fully updated to {version}",
        "no_migration": "[ok] No migration is required; no files were changed.",
        "reason_not_directory": "The target path exists but is not a directory.",
        "reason_different_content": "This local file differs from the expected ForgeKit baseline.",
        "reason_not_file": "The target path exists but is not a file.",
        "reason_checksum": "This local file differs from the expected ForgeKit baseline.",
        "impact_replace": "Safe migration can continue, but {target} will remain old or customized until you merge the new template.",
        "impact_copy": "Safe migration can continue, but {target} will keep the local content instead of the incoming ForgeKit template.",
        "impact_default": "Safe migration cannot decide this item automatically without user review.",
        "recommendation_default": "If you never edited this file manually, replace it with the current ForgeKit template. If you customized it, choose manual-merge and merge the exported sample later.",
        "readme_title": "# Review Needed Manual Merge",
        "readme_not_overwritten": "The local target file was not overwritten.",
        "readme_incoming": "The `.incoming` file is the current ForgeKit template.",
        "readme_diff": "The `.diff` file shows differences between the local file and the incoming template.",
        "readme_ai": "You can merge manually, or ask an AI assistant to use `.local`, `.incoming`, and `.diff` to help prepare a merge.",
        "readme_rerun": "After merging, run the ForgeKit unified entry again to confirm the upgrade state.",
        "readme_prompt_label": "AI-assisted merge prompt:",
        "readme_prompt": "Please read the .local, .incoming, and .diff files in this directory. Help me merge the new template capabilities from incoming into the target file while preserving the existing local changes from local as much as possible. Do not overwrite directly; first output a merge plan and risks.",
    },
    "zh-CN": {
        "review_found_one": "[warning] ForgeKit 发现 1 个文件不能安全自动覆盖。",
        "review_found_many": "[warning] ForgeKit 发现 {count} 个文件不能安全自动覆盖。",
        "action_label": "action:",
        "reason_label": "原因：",
        "impact_label": "影响：",
        "recommendation_label": "建议：",
        "choose_action": "请选择处理方式：",
        "choice_replace": "  [r] 用当前 ForgeKit 模板替换这个文件",
        "choice_manual": "  [m] 保留本地文件，并生成新版模板参考文件和差异文件",
        "choice_diff": "  [d] 查看差异",
        "choice_abort": "  [a] 中止本次升级",
        "choice_prompt": "请输入选择：",
        "choice_invalid": "请输入 r、m、d 或 a。",
        "diff_unavailable_no_source": "[diff unavailable] 这个 review-needed action 没有 incoming 模板文件。",
        "diff_unavailable_not_file": "[diff unavailable] 目标路径不是文件。",
        "diff_empty": "[diff] 内容没有差异",
        "noninteractive_policy": "非交互模式下，review-needed 项需要显式策略。",
        "run_one_of": "请运行以下命令之一：",
        "alias_keep_local": "keep-local is treated as manual-merge.",
        "abort_policy": "review-needed 项已按策略中止；未执行迁移写入。",
        "abort_interactive": "review-needed 项已中止；未执行迁移写入。",
        "manual_final": "[ok] 项目已升级到 {version}，并保留了 {count} 个需要后续手动合并的本地文件",
        "manual_exported": "[ok] 新版模板参考文件已生成：\n     {path}",
        "fully_updated": "[ok] 项目已完整升级到 {version}",
        "no_migration": "[ok] 不需要迁移；未修改文件。",
        "reason_not_directory": "目标路径已存在，但不是目录。",
        "reason_different_content": "这个本地文件和 ForgeKit 的预期基线不一致。",
        "reason_not_file": "目标路径已存在，但不是文件。",
        "reason_checksum": "这个本地文件和 ForgeKit 的预期基线不一致。",
        "impact_replace": "迁移可以继续，但 {target} 会保持旧版本或自定义版本，直到你合并新版模板。",
        "impact_copy": "迁移可以继续，但 {target} 会保留本地内容，而不是 incoming ForgeKit 模板。",
        "impact_default": "安全迁移无法自动判断这个项目，需要用户复核。",
        "recommendation_default": "如果你没有手动改过这个文件，建议替换为当前 ForgeKit 模板。如果你确实改过它，建议选择 manual-merge，并在之后合并导出的新版模板参考文件。",
        "readme_title": "# Review Needed 手动合并",
        "readme_not_overwritten": "本地目标文件没有被覆盖。",
        "readme_incoming": "`.incoming` 文件是当前 ForgeKit 模板。",
        "readme_diff": "`.diff` 文件展示本地文件和 incoming 模板的差异。",
        "readme_ai": "你可以手动合并，也可以让 AI 根据 `.local`、`.incoming` 和 `.diff` 辅助合并。",
        "readme_rerun": "合并完成后，请再次运行 ForgeKit 统一入口确认升级状态。",
        "readme_prompt_label": "AI 辅助合并提示词：",
        "readme_prompt": "请读取本目录下的 .local、.incoming 和 .diff 文件，帮我把 incoming 中的新模板能力合并进目标文件，同时尽量保留 local 中已有的本地修改。不要直接覆盖，先输出合并计划和风险。",
    },
}


def msg(lang, key, **kwargs):
    template = MESSAGES.get(lang, MESSAGES["en-US"]).get(key, MESSAGES["en-US"].get(key, key))
    return template.format(**kwargs)


def fail(message):
    raise SystemExit(f"[fail] {message}")


def parse_version(value):
    try:
        parts = tuple(int(part) for part in str(value).strip().lstrip("v").split("."))
    except ValueError:
        fail(f"Invalid ForgeKit version: {value}")
    if len(parts) != 3:
        fail(f"ForgeKit version must use major.minor.patch: {value}")
    return parts


def version_text(value):
    return ".".join(str(part) for part in value)


def load_json(path, label):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        fail(f"{label} not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"Invalid {label} JSON at {path}: {exc}")


def state_status(project_root):
    state_path = project_root / STATE_RELATIVE_PATH
    if not state_path.is_file():
        return None, "missing_state"
    state = load_json(state_path, "state")
    required = {
        "schema_version",
        "forgekit_version",
        "managed_docs_root",
        "change_root",
        "mode",
        "features",
        "last_upgrade",
    }
    missing = sorted(required - set(state))
    if missing:
        return state, "invalid_state:" + ",".join(missing)
    if state.get("schema_version") != 1:
        return state, "unsupported_schema"
    if parse_version(state["forgekit_version"]) < MIN_SUPPORTED_VERSION:
        return state, "unsupported_version"
    return state, "supported"


def print_adoption_guidance(project_root, reason, state=None):
    detected = "none" if state is None else state.get("forgekit_version", "unknown")
    print("ForgeKit Upgrade Check")
    print("Status: adoption-required")
    print(f"Project: {project_root}")
    print(f"Detected version: {detected}")
    print(f"Reason: {reason}")
    print("")
    print("Pre-v0.36 projects are treated as existing projects for adoption.")
    print("1. Keep existing project and ForgeKit documents unchanged.")
    print("2. Build an adoption inventory; use handoff, doc-health, or source-trace reports when useful.")
    print("3. Review boundaries and current facts with the user.")
    print("4. Create .forgekit/state.json only after explicit user confirmation and a v0.36+ initialization/adoption step.")
    print("No automatic upgrade or migration was performed.")


def load_migrations(migration_root):
    if not migration_root.is_dir():
        fail(f"Migration directory not found: {migration_root}")
    migrations = []
    for path in sorted(migration_root.glob("*/migration.json")):
        item = load_json(path, "migration")
        required = {"id", "title", "from", "to", "risk", "actions", "manual_review", "non_goals"}
        missing = sorted(required - set(item))
        if missing:
            fail(f"Migration {path} missing fields: {', '.join(missing)}")
        item["_path"] = path
        item["_from_versions"] = item["from"] if isinstance(item["from"], list) else [item["from"]]
        item["_to_version"] = parse_version(item["to"])
        migrations.append(item)
    return sorted(migrations, key=lambda item: item["_to_version"])


def migration_matches(item, current):
    return any(value == "*" or parse_version(value) == current for value in item["_from_versions"])


def pending_migrations(current, migrations):
    pending = []
    cursor = current
    for item in migrations:
        if item["_to_version"] <= cursor:
            continue
        if migration_matches(item, cursor):
            pending.append(item)
            cursor = item["_to_version"]
    return pending, cursor


def latest_available(migrations, current):
    return max([current] + [item["_to_version"] for item in migrations])


def command_check(project_root, migration_root):
    state, status = state_status(project_root)
    if status != "supported":
        print_adoption_guidance(project_root, status, state)
        return
    current = parse_version(state["forgekit_version"])
    migrations = load_migrations(migration_root)
    pending, target = pending_migrations(current, migrations)
    print("ForgeKit Upgrade Check")
    print(f"Status: {'update-available' if pending else 'current'}")
    print(f"Project: {project_root}")
    print(f"Current version: {version_text(current)}")
    print(f"Latest available: {version_text(latest_available(migrations, current))}")
    print(f"Planned target: {version_text(target)}")
    print(f"Pending migrations: {len(pending)}")
    print("Next: run `plan` to review the migration plan." if pending else "No migration is required.")


def action_status(project_root, migration, action, state):
    """Return the plan/apply classification without modifying project files."""
    if action.get("safety") != "safe":
        return "manual", "action is not marked safe"
    action_type = action.get("type")
    if action_type == "ensure_directory":
        target = safe_target(project_root, action["target"])
        if target.is_dir():
            return "already-present", "directory already exists"
        if target.exists():
            return "review-needed", "target exists and is not a directory"
        return "safe", "directory will be created"
    if action_type == "copy_file_if_missing":
        source = migration_source(migration, action)
        target = safe_target(project_root, action["target"])
        if not target.exists():
            return "safe", "file will be installed"
        if target.is_file() and sha256(target) == sha256(source):
            return "already-present", "same content; no write needed"
        return "review-needed", "target exists with different content; preserve and skip"
    if action_type == "replace_file_if_baseline_matches":
        source = migration_source(migration, action)
        baseline = migration_source(migration, {"source": action["baseline"]})
        target = safe_target(project_root, action["target"])
        if not target.exists():
            return "safe", "file will be installed"
        if not target.is_file():
            return "review-needed", "target exists and is not a file; preserve and skip"
        if sha256(target) == sha256(source):
            return "already-present", "same content; no write needed"
        if sha256(target) == sha256(baseline):
            return "safe", "target matches the known previous-version baseline and will be replaced"
        return "review-needed", "checksum does not match the known baseline; preserve and skip"
    if action_type == "set_state_feature":
        if not action.get("name"):
            fail(f"Migration {migration['id']} has a state feature without a name")
        if state.get("features", {}).get(action["name"]) == action["value"]:
            return "already-present", "state feature already has the requested value"
        return "safe", "state feature will be updated"
    fail(f"Unsupported safe migration action: {action_type}")


def render_plan(project_root, state, migrations):
    current = parse_version(state["forgekit_version"])
    pending, target = pending_migrations(current, migrations)
    lines = [
        "ForgeKit Versioned Migration Plan",
        "Status: report-only",
        "Mode: versioned-migration-plan",
        f"Project: {project_root}",
        f"From: {version_text(current)}",
        f"To: {version_text(target)}",
        f"Migrations: {len(pending)}",
        "",
    ]
    if not pending:
        lines.extend(["No migration is required.", "No files were changed."])
        return "\n".join(lines), pending
    for item in pending:
        classified = [(action, *action_status(project_root, item, action, state)) for action in item["actions"]]
        safe_actions = [entry for entry in classified if entry[1] == "safe"]
        already_present = [entry for entry in classified if entry[1] == "already-present"]
        review_needed = [entry for entry in classified if entry[1] == "review-needed"]
        non_safe = [entry for entry in classified if entry[1] == "manual"]
        lines.extend([
            f"## {item['to']} - {item['title']}",
            f"Risk: {item['risk']}",
            f"Safe actions: {len(safe_actions)}",
            f"Already present: {len(already_present)}",
            f"Review needed: {len(review_needed)}",
            f"Manual actions: {len(non_safe)}",
        ])
        for action, _, reason in safe_actions:
            lines.append(f"- SAFE: {action.get('description', action.get('id', action.get('type', 'action')))}")
        for action, _, reason in already_present:
            lines.append(f"- ALREADY-PRESENT: {action.get('id', action.get('type', 'action'))} ({reason})")
        for action, _, reason in review_needed:
            lines.append(f"- REVIEW-NEEDED: {action.get('id', action.get('type', 'action'))} ({reason}; apply result: skipped-existing-review-needed)")
            if action.get("skip_warning"):
                lines.append(f"  - WARNING: {action['skip_warning']}")
        for review in item["manual_review"]:
            lines.append(f"- REVIEW: {review}")
        lines.append("")
    lines.extend([
        "Apply command: python scripts/forgekit-upgrade.py apply --safe --repo-root <project>",
        "No files were changed by plan.",
    ])
    return "\n".join(lines), pending


def command_plan(project_root, migration_root):
    state, status = state_status(project_root)
    if status != "supported":
        print_adoption_guidance(project_root, status, state)
        return
    plan, _ = render_plan(project_root, state, load_migrations(migration_root))
    print(plan)


def safe_target(project_root, relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        fail(f"Unsafe migration target: {relative}")
    if path.parts[0] not in SAFE_ROOTS:
        fail(f"Safe migration target is outside ForgeKit governance roots: {relative}")
    target = (project_root / path).resolve()
    try:
        target.relative_to(project_root)
    except ValueError:
        fail(f"Migration target escapes project root: {relative}")
    return target


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def migration_source(migration, action):
    source = (migration["_path"].parent / action["source"]).resolve()
    try:
        source.relative_to(migration["_path"].parent.resolve())
    except ValueError:
        fail(f"Migration source escapes package: {action['source']}")
    if not source.is_file():
        fail(f"Migration source not found: {source}")
    return source


def utc_now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def action_id(action):
    return action.get("id", action.get("type", "action"))


def review_key(item):
    return f"{item['source_migration']}::{item['action_id']}::{item['target_path']}"


def checksum_or_none(path):
    return sha256(path) if path.is_file() else None


def reason_text(lang, reason):
    if "not a directory" in reason:
        return msg(lang, "reason_not_directory")
    if "not a file" in reason:
        return msg(lang, "reason_not_file")
    if "checksum" in reason:
        return msg(lang, "reason_checksum")
    if "different content" in reason:
        return msg(lang, "reason_different_content")
    return reason


def review_impact(action, lang):
    if action.get("review_impact"):
        return action["review_impact"]
    target = action.get("target", "the target file")
    if action.get("type") == "replace_file_if_baseline_matches":
        return msg(lang, "impact_replace", target=target)
    if action.get("type") == "copy_file_if_missing":
        return msg(lang, "impact_copy", target=target)
    return msg(lang, "impact_default")


def review_recommendation(action, lang):
    if action.get("recommended_action"):
        return action["recommended_action"]
    return msg(lang, "recommendation_default")


def review_item(project_root, migration, action, reason, lang="en-US"):
    source = None
    baseline = None
    if action.get("type") in {"copy_file_if_missing", "replace_file_if_baseline_matches"}:
        source = migration_source(migration, action)
    if action.get("type") == "replace_file_if_baseline_matches":
        baseline = migration_source(migration, {"source": action["baseline"]})
    target = safe_target(project_root, action["target"])
    item = {
        "action_id": action_id(action),
        "target_path": action["target"],
        "source_migration": migration["id"],
        "migration_to": migration["to"],
        "reason": reason_text(lang, reason),
        "raw_reason": reason,
        "expected_baseline_checksum": checksum_or_none(baseline) if baseline else None,
        "actual_checksum": checksum_or_none(target),
        "incoming_template_checksum": checksum_or_none(source) if source else None,
        "impact": review_impact(action, lang),
        "recommended_action": review_recommendation(action, lang),
        "status": "pending",
    }
    item["key"] = review_key(item)
    return item


def load_review_report(project_root):
    path = project_root / REVIEW_REPORT_JSON
    if not path.is_file():
        return {"items": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {"items": []}
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        return {"items": []}
    return data


def previous_review_decision(report, item):
    previous = {entry.get("key"): entry for entry in report.get("items", [])}.get(item["key"])
    if not previous:
        return None
    status = previous.get("status")
    if status in {"resolved_manual_merge", "resolved_keep_local"} and previous.get("actual_checksum") == item.get("actual_checksum"):
        return "manual-merge"
    if status == "resolved_replace_template" and item.get("actual_checksum") == item.get("incoming_template_checksum"):
        return "replace-template"
    return None


def copy_previous_review_exports(report, item):
    previous = {entry.get("key"): entry for entry in report.get("items", [])}.get(item["key"])
    if not previous:
        return
    for key in ("export_path", "exported_files"):
        if key in previous:
            item[key] = previous[key]


def write_review_reports(project_root, target_version, items):
    reports_dir = (project_root / REVIEW_REPORT_JSON).parent
    reports_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "project_root": str(project_root),
        "target_version": target_version,
        "items": items,
    }
    (project_root / REVIEW_REPORT_JSON).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Upgrade Review Needed",
        "",
        f"Generated: {data['generated_at']}",
        f"Target version: {target_version}",
        "",
    ]
    if not items:
        lines.append("No review-needed items were recorded.")
    for index, item in enumerate(items, start=1):
        lines.extend([
            f"## {index}. {item['target_path']}",
            "",
            f"- Status: {item['status']}",
            f"- Action: {item['action_id']}",
            f"- Source migration: {item['source_migration']}",
            f"- Reason: {item['reason']}",
            f"- Expected baseline checksum: {item.get('expected_baseline_checksum') or 'n/a'}",
            f"- Actual checksum: {item.get('actual_checksum') or 'n/a'}",
            f"- Incoming template checksum: {item.get('incoming_template_checksum') or 'n/a'}",
            f"- Impact: {item['impact']}",
            f"- Recommended action: {item['recommended_action']}",
            "",
        ])
    (project_root / REVIEW_REPORT_MD).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def merge_review_items(project_root, target_version, updates):
    report = load_review_report(project_root)
    merged = {entry.get("key"): entry for entry in report.get("items", []) if entry.get("key")}
    for item in updates:
        merged[item["key"]] = item
    items = sorted(merged.values(), key=lambda entry: (entry.get("source_migration", ""), entry.get("action_id", ""), entry.get("target_path", "")))
    write_review_reports(project_root, target_version, items)


def safe_review_dir_name(migration_id, item_action_id, used_names=None):
    raw = item_action_id or "review-item"
    if "\x00" in raw or "/" in raw or "\\" in raw or ".." in Path(raw).parts:
        raw = f"{migration_id}__{item_action_id}"
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", raw).strip("._")
    if not name or name in {".", ".."}:
        name = re.sub(r"[^A-Za-z0-9._-]+", "_", f"{migration_id}__review-item").strip("._")
    if used_names is not None and name in used_names:
        base = re.sub(r"[^A-Za-z0-9._-]+", "_", f"{migration_id}__{item_action_id}").strip("._") or "review-item"
        name = base
        counter = 2
        while name in used_names:
            name = f"{base}-{counter}"
            counter += 1
    if used_names is not None:
        used_names.add(name)
    return name


def diff_text(local_path, incoming_path, target_path):
    old = local_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    new = incoming_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    diff = difflib.unified_diff(old, new, fromfile=target_path, tofile=f"incoming/{target_path}")
    return "".join(diff)


def manual_merge_readme(item, export_dir, lang):
    lines = [
        msg(lang, "readme_title"),
        "",
        f"- action_id: {item['action_id']}",
        f"- target_path: {item['target_path']}",
        f"- source_migration: {item['source_migration']}",
        f"- reason: {item['reason']}",
        f"- impact: {item['impact']}",
        "",
        msg(lang, "readme_not_overwritten"),
        msg(lang, "readme_incoming"),
        msg(lang, "readme_diff"),
        msg(lang, "readme_ai"),
        msg(lang, "readme_rerun"),
        "",
        "Files:",
        f"- local: {item['exported_files']['local']}",
        f"- incoming: {item['exported_files']['incoming']}",
        f"- diff: {item['exported_files']['diff']}",
        "",
        msg(lang, "readme_prompt_label"),
        "",
        "```text",
        msg(lang, "readme_prompt"),
        "```",
        "",
    ]
    return "\n".join(lines)


def export_manual_merge(project_root, migration, action, item, lang, used_names=None):
    if action.get("type") not in {"copy_file_if_missing", "replace_file_if_baseline_matches"}:
        fail(f"Cannot export manual merge files for action without a source file: {action_id(action)}")
    target = safe_target(project_root, action["target"])
    source = migration_source(migration, action)
    if not target.is_file():
        fail(f"Cannot export manual merge files because target is not a file: {action['target']}")
    directory_name = safe_review_dir_name(migration["id"], item["action_id"], used_names)
    export_dir = project_root / REVIEW_EXPORT_ROOT / directory_name
    export_dir.mkdir(parents=True, exist_ok=True)
    filename = Path(action["target"]).name
    local_path = export_dir / f"{filename}.local"
    incoming_path = export_dir / f"{filename}.incoming"
    diff_path = export_dir / f"{filename}.diff"
    readme_path = export_dir / "README.md"
    shutil.copyfile(target, local_path)
    shutil.copyfile(source, incoming_path)
    diff_path.write_text(diff_text(local_path, incoming_path, action["target"]), encoding="utf-8")
    item["export_path"] = (REVIEW_EXPORT_ROOT / directory_name).as_posix()
    item["exported_files"] = {
        "local": local_path.name,
        "incoming": incoming_path.name,
        "diff": diff_path.name,
        "readme": readme_path.name,
    }
    readme_path.write_text(manual_merge_readme(item, export_dir, lang), encoding="utf-8")
    return (REVIEW_EXPORT_ROOT / directory_name).as_posix()


def collect_review_needed(project_root, migrations, state, lang):
    report = load_review_report(project_root)
    pending = []
    decisions = {}
    all_items = []
    pending_by_file = {}
    virtual_files = {}

    def virtual_entry(relative):
        target = safe_target(project_root, relative)
        key = Path(relative).as_posix()
        if key not in virtual_files:
            if target.is_file():
                virtual_files[key] = {"exists": True, "file": True, "checksum": sha256(target), "migration_owned": False}
            elif target.exists():
                virtual_files[key] = {"exists": True, "file": False, "checksum": None, "migration_owned": False}
            else:
                virtual_files[key] = {"exists": False, "file": False, "checksum": None, "migration_owned": False}
        return key, virtual_files[key]

    for migration in migrations:
        for action in migration["actions"]:
            if action.get("safety") != "safe":
                continue
            action_type = action.get("type")
            if action_type == "ensure_directory":
                key, entry = virtual_entry(action["target"])
                if not entry["exists"]:
                    entry.update({"exists": True, "file": False, "checksum": None, "migration_owned": True})
                elif entry["file"]:
                    item = review_item(project_root, migration, action, "target exists and is not a directory", lang)
                    pending.append((migration, action, item))
                    all_items.append(item)
                continue
            if action_type == "copy_file_if_missing":
                source_checksum = sha256(migration_source(migration, action))
                key, entry = virtual_entry(action["target"])
                if not entry["exists"]:
                    entry.update({"exists": True, "file": True, "checksum": source_checksum, "migration_owned": True})
                    continue
                if entry["file"] and entry["checksum"] == source_checksum:
                    continue
                if entry["migration_owned"]:
                    item = review_item(project_root, migration, action, "same-run migration file will be refreshed to the incoming template", lang)
                    decisions[item["key"]] = "auto-replace-template"
                    entry.update({"exists": True, "file": True, "checksum": source_checksum, "migration_owned": True})
                    continue
                reason = "target exists with different content; preserve and skip" if entry["file"] else "target exists and is not a file; preserve and skip"
                item = review_item(project_root, migration, action, reason, lang)
            elif action_type == "replace_file_if_baseline_matches":
                source_checksum = sha256(migration_source(migration, action))
                baseline_checksum = sha256(migration_source(migration, {"source": action["baseline"]}))
                key, entry = virtual_entry(action["target"])
                if not entry["exists"]:
                    entry.update({"exists": True, "file": True, "checksum": source_checksum, "migration_owned": True})
                    continue
                if not entry["file"]:
                    item = review_item(project_root, migration, action, "target exists and is not a file; preserve and skip", lang)
                elif entry["checksum"] == source_checksum:
                    continue
                elif entry["checksum"] == baseline_checksum or entry["migration_owned"]:
                    entry.update({"exists": True, "file": True, "checksum": source_checksum, "migration_owned": True})
                    continue
                else:
                    item = review_item(project_root, migration, action, "checksum does not match the known baseline; preserve and skip", lang)
            elif action_type == "set_state_feature":
                continue
            else:
                continue
            decision = previous_review_decision(report, item)
            if decision:
                decisions[item["key"]] = decision
                item["status"] = "resolved_manual_merge" if decision == "manual-merge" else "resolved_replace_template"
                copy_previous_review_exports(report, item)
            elif (item["target_path"], item.get("actual_checksum")) in pending_by_file:
                pending_by_file[(item["target_path"], item.get("actual_checksum"))].setdefault("related_keys", []).append(item["key"])
            else:
                pending.append((migration, action, item))
                pending_by_file[(item["target_path"], item.get("actual_checksum"))] = item
            all_items.append(item)
    return pending, decisions, all_items


def show_review_item(index, total, item, lang):
    print("")
    print(f"{index}. {item['target_path']}")
    print(f"   {msg(lang, 'action_label')}")
    print(f"     {item['action_id']}")
    print("")
    print(f"   {msg(lang, 'reason_label')}")
    print(f"     {item['reason']}")
    print("")
    print(f"   {msg(lang, 'impact_label')}")
    print(f"     {item['impact']}")
    print("")
    print(f"   {msg(lang, 'recommendation_label')}")
    print(f"     {item['recommended_action']}")
    print("")


def show_diff(project_root, migration, action, lang):
    if action.get("type") not in {"copy_file_if_missing", "replace_file_if_baseline_matches"}:
        print(msg(lang, "diff_unavailable_no_source"))
        return
    source = migration_source(migration, action)
    target = safe_target(project_root, action["target"])
    if not target.is_file():
        print(msg(lang, "diff_unavailable_not_file"))
        return
    old = target.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    new = source.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    diff = difflib.unified_diff(
        old,
        new,
        fromfile=action["target"],
        tofile=f"incoming/{action['target']}",
    )
    text = "".join(diff).rstrip()
    print(text if text else msg(lang, "diff_empty"))


def print_noninteractive_policy_help(project_root, lang):
    script = Path(sys.argv[0])
    script_text = str(script)
    print(msg(lang, "noninteractive_policy"))
    print("")
    print(msg(lang, "run_one_of"))
    print("")
    print(f'python {script_text} apply --repo-root "{project_root}" --safe --review-needed-policy manual-merge')
    print(f'python {script_text} apply --repo-root "{project_root}" --safe --review-needed-policy replace-template')


def resolve_review_needed(project_root, pending, decisions, target_version, policy, lang):
    if not pending:
        return decisions, []
    if policy == "keep-local":
        print(msg(lang, "alias_keep_local"))
        policy = "manual-merge"
    if policy not in REVIEW_POLICIES:
        fail(f"Invalid review-needed policy: {policy}")
    items = [entry[2] for entry in pending]
    print("")
    print(msg(lang, "review_found_one") if len(items) == 1 else msg(lang, "review_found_many", count=len(items)))
    resolved = []
    if policy == "abort":
        now = utc_now()
        for item in items:
            item["status"] = "aborted"
            item["resolved_at"] = now
            resolved.append(item)
        merge_review_items(project_root, target_version, resolved)
        fail(msg(lang, "abort_policy"))
    if policy in {"manual-merge", "replace-template"}:
        now = utc_now()
        used_names = set()
        for migration, action, item in pending:
            decision = policy
            item["status"] = "resolved_manual_merge" if decision == "manual-merge" else "resolved_replace_template"
            item["resolved_at"] = now
            if decision == "manual-merge":
                export_manual_merge(project_root, migration, action, item, lang, used_names)
            decisions[item["key"]] = decision
            for key in item.get("related_keys", []):
                decisions[key] = decision
            resolved.append(item)
        merge_review_items(project_root, target_version, resolved)
        return decisions, resolved
    if not sys.stdin.isatty():
        merge_review_items(project_root, target_version, items)
        print_noninteractive_policy_help(project_root, lang)
        raise SystemExit(2)
    now = utc_now()
    used_names = set()
    for index, (migration, action, item) in enumerate(pending, start=1):
        while True:
            show_review_item(index, len(pending), item, lang)
            print(msg(lang, "choose_action"))
            print(msg(lang, "choice_replace"))
            print(msg(lang, "choice_manual"))
            print(msg(lang, "choice_diff"))
            print(msg(lang, "choice_abort"))
            print("")
            choice = input(msg(lang, "choice_prompt")).strip().lower()
            if choice == "d":
                show_diff(project_root, migration, action, lang)
                continue
            if choice == "a":
                item["status"] = "aborted"
                item["resolved_at"] = now
                merge_review_items(project_root, target_version, [item])
                fail(msg(lang, "abort_interactive"))
            if choice in {"r", "m"}:
                decision = "replace-template" if choice == "r" else "manual-merge"
                item["status"] = "resolved_replace_template" if decision == "replace-template" else "resolved_manual_merge"
                item["resolved_at"] = now
                if decision == "manual-merge":
                    export_manual_merge(project_root, migration, action, item, lang, used_names)
                decisions[item["key"]] = decision
                for key in item.get("related_keys", []):
                    decisions[key] = decision
                resolved.append(item)
                merge_review_items(project_root, target_version, [item])
                break
            print(msg(lang, "choice_invalid"))
    return decisions, resolved


def replace_with_template(project_root, migration, action):
    if action.get("type") not in {"copy_file_if_missing", "replace_file_if_baseline_matches"}:
        fail(f"Cannot replace template for action without a source file: {action_id(action)}")
    source = migration_source(migration, action)
    target = safe_target(project_root, action["target"])
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def apply_action(project_root, migration, action, state, review_decisions):
    action_type = action.get("type")
    if action.get("safety") != "safe":
        return "manual"
    status, reason = action_status(project_root, migration, action, state)
    if status == "review-needed":
        item = review_item(project_root, migration, action, reason)
        decision = review_decisions.get(item["key"])
        if decision == "manual-merge":
            return "resolved-manual-merge"
        if decision in {"replace-template", "auto-replace-template"}:
            replace_with_template(project_root, migration, action)
            if decision == "auto-replace-template":
                return "applied"
            return "resolved-replace-template"
    if action_type == "ensure_directory":
        target = safe_target(project_root, action["target"])
        if target.is_dir():
            return "already-present"
        if target.exists():
            return "skipped-existing-review-needed"
        target.mkdir(parents=True, exist_ok=True)
        return "applied"
    if action_type == "copy_file_if_missing":
        source = migration_source(migration, action)
        target = safe_target(project_root, action["target"])
        if target.exists():
            if target.is_file() and sha256(target) == sha256(source):
                return "already-present"
            return "skipped-existing-review-needed"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        return "applied"
    if action_type == "replace_file_if_baseline_matches":
        source = migration_source(migration, action)
        baseline = migration_source(migration, {"source": action["baseline"]})
        target = safe_target(project_root, action["target"])
        if target.exists():
            if not target.is_file():
                return "skipped-existing-review-needed"
            if sha256(target) == sha256(source):
                return "already-present"
            if sha256(target) != sha256(baseline):
                return "skipped-existing-review-needed"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        return "applied"
    if action_type == "set_state_feature":
        state.setdefault("features", {})[action["name"]] = action["value"]
        return "applied"
    fail(f"Unsupported safe migration action: {action_type}")


def preflight_action(project_root, migration, action):
    if action.get("safety") != "safe":
        fail(f"Migration {migration['id']} contains a non-safe action: {action.get('id', action.get('type'))}")
    action_type = action.get("type")
    if action_type == "ensure_directory":
        safe_target(project_root, action["target"])
        return
    if action_type == "copy_file_if_missing":
        migration_source(migration, action)
        safe_target(project_root, action["target"])
        return
    if action_type == "replace_file_if_baseline_matches":
        migration_source(migration, action)
        migration_source(migration, {"source": action["baseline"]})
        safe_target(project_root, action["target"])
        return
    if action_type == "set_state_feature":
        if not action.get("name"):
            fail(f"Migration {migration['id']} has a state feature without a name")
        return
    fail(f"Unsupported safe migration action: {action_type}")


def write_state(path, state):
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def command_apply(project_root, migration_root, safe, review_needed_policy, lang):
    if not safe:
        fail("apply requires --safe")
    state, status = state_status(project_root)
    if status != "supported":
        print_adoption_guidance(project_root, status, state)
        return
    migrations = load_migrations(migration_root)
    current = parse_version(state["forgekit_version"])
    pending, target = pending_migrations(current, migrations)
    if not pending:
        print(msg(lang, "no_migration"))
        return
    for migration in pending:
        for action in migration["actions"]:
            preflight_action(project_root, migration, action)
    review_pending, review_decisions, review_items = collect_review_needed(project_root, pending, state, lang)
    if review_pending:
        review_decisions, resolved_items = resolve_review_needed(
            project_root,
            review_pending,
            review_decisions,
            version_text(target),
            review_needed_policy,
            lang,
        )
    elif review_items:
        merge_review_items(project_root, version_text(target), review_items)
    applied_ids = []
    unresolved_review_needed = []
    start = state["forgekit_version"]
    for migration in pending:
        for action in migration["actions"]:
            result = apply_action(project_root, migration, action, state, review_decisions)
            print(f"[{result}] {action_id(action)}")
            if result == "skipped-existing-review-needed":
                unresolved_review_needed.append(action)
                if action.get("skip_warning"):
                    print(f"[warning] {action['skip_warning']}")
        state["forgekit_version"] = migration["to"]
        applied_ids.append(migration["id"])
    state["last_upgrade"] = {
        "from": start,
        "to": state["forgekit_version"],
        "applied_at": utc_now(),
        "migrations": applied_ids,
        "mode": "safe",
        "review_needed_actions": [action_id(action) for action in unresolved_review_needed],
        "manual_merge_items": len({
            key.split("::", 2)[2] for key, decision in review_decisions.items() if decision == "manual-merge"
        }),
    }
    write_state(project_root / STATE_RELATIVE_PATH, state)
    if unresolved_review_needed:
        print(f"[warning] {len(unresolved_review_needed)} action(s) were skipped-existing-review-needed; the project requires manual review and is not fully updated.")
        return
    manual_keys = {key.split("::", 2)[2] for key, decision in review_decisions.items() if decision == "manual-merge"}
    manual_count = len(manual_keys)
    if manual_count:
        noun = "item" if manual_count == 1 else "items"
        print(msg(lang, "manual_final", version=state["forgekit_version"], count=manual_count, noun=noun))
        exported_paths = sorted({
            item.get("export_path")
            for item in load_review_report(project_root).get("items", [])
            if item.get("status") == "resolved_manual_merge" and item.get("export_path")
        })
        for path in exported_paths:
            print(msg(lang, "manual_exported", path=path))
    else:
        print(msg(lang, "fully_updated", version=state["forgekit_version"]))


def main():
    parser = argparse.ArgumentParser(description="ForgeKit versioned migration upgrade")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "plan"):
        command = subparsers.add_parser(name)
        command.add_argument("--repo-root", default=".", help="Target project root")
        command.add_argument("--migration-root", help="Migration package directory")
    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--repo-root", default=".", help="Target project root")
    apply_parser.add_argument("--migration-root", help="Migration package directory")
    apply_parser.add_argument("--safe", action="store_true", help="Apply safe actions only")
    apply_parser.add_argument("--review-needed-policy", choices=sorted(REVIEW_POLICIES), default="ask", help="How to resolve review-needed safe migration items")
    apply_parser.add_argument("--lang", choices=sorted(LANGUAGES), default="en-US", help="Display language for user-facing output")
    args = parser.parse_args()

    project_root = Path(args.repo_root).resolve()
    if not project_root.is_dir():
        fail(f"Project root does not exist: {project_root}")
    migration_root = Path(args.migration_root).resolve() if args.migration_root else Path(__file__).resolve().parents[1] / "migrations"
    if args.command == "check":
        command_check(project_root, migration_root)
    elif args.command == "plan":
        command_plan(project_root, migration_root)
    else:
        command_apply(project_root, migration_root, args.safe, args.review_needed_policy, args.lang)


if __name__ == "__main__":
    main()
