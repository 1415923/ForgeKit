#!/usr/bin/env python3
"""Unified ForgeKit project bootstrap and versioned upgrade entry point."""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


MIN_MIGRATION_VERSION = (0, 36, 0)
STATE_RELATIVE_PATH = Path(".forgekit/state.json")
BOUNDARY_RELATIVE_PATH = Path(".forgekit/project-boundary.yml")
WORKSPACE_MAP_RELATIVE_PATH = Path(".forgekit/workspace-map.json")
LANGUAGES = {"en-US", "zh-CN"}

MESSAGES = {
    "en-US": {
        "lang_prompt": "请选择显示语言 / Select display language:",
        "lang_zh": "  [1] 中文",
        "lang_en": "  [2] English",
        "lang_choice": "Your choice: ",
        "noninteractive_policy": "Review-needed item requires a policy in non-interactive mode.",
        "run_one_of": "Run one of:",
        "no_files_changed": "No files were changed.",
        "safe_apply_prompt": "Continue with safe apply? [y/N]: ",
        "init_prompt": "Continue with initialization? [y/N]: ",
        "safe_apply_skipped": "Safe apply was not executed. The check and plan remain report-only.",
        "init_skipped": "Initialization was not applied. No files were changed.",
        "up_to_date_plan": "Plan summary: no migration is required.",
        "manual_count": "Manual actions count: {count}",
        "safe_count": "Safe actions count: {count}",
        "check_result": "Check result: {status}",
        "plan_summary": "Plan summary:",
        "alias_keep_local": "keep-local is treated as manual-merge.",
        "upgrade_done": "[ok] Upgrade completed. You can continue using this project normally.",
        "upgrade_next": "[next] If your current AI session was opened before the upgrade, start a new session or ask the agent to reload the project entry docs before continuing.",
        "summary_title": "Upgrade result summary:",
        "summary_auto": "Automatically updated/template-aligned files:",
        "summary_preserved": "Preserved local customizations:",
        "summary_manual": "Files still requiring manual merge:",
        "summary_agents_yes": "AGENTS entry action: merge the snippet below into the project AGENTS.md.",
        "summary_agents_no": "AGENTS entry action: none; the project entry already routes to the managed Maker/Checker protocol.",
        "summary_commit": "Governance commit suggestion: review the upgrade diff and create a dedicated governance upgrade commit if appropriate; ForgeKit did not commit or push.",
    },
    "zh-CN": {
        "lang_prompt": "请选择显示语言 / Select display language:",
        "lang_zh": "  [1] 中文",
        "lang_en": "  [2] English",
        "lang_choice": "请输入选择：",
        "noninteractive_policy": "非交互模式下，review-needed 项需要显式策略。",
        "run_one_of": "请运行以下命令之一：",
        "no_files_changed": "未修改文件。",
        "safe_apply_prompt": "是否继续执行安全迁移？[y/N]: ",
        "init_prompt": "是否继续初始化？[y/N]: ",
        "safe_apply_skipped": "未执行安全迁移；check 和 plan 仍为只读报告。",
        "init_skipped": "未执行初始化。未修改文件。",
        "up_to_date_plan": "计划摘要：不需要迁移。",
        "manual_count": "人工/复核项数量：{count}",
        "safe_count": "安全动作数量：{count}",
        "check_result": "检查结果：{status}",
        "plan_summary": "计划摘要：",
        "alias_keep_local": "keep-local is treated as manual-merge.",
        "upgrade_done": "[ok] 升级已完成，可以正常继续使用。",
        "upgrade_next": "[next] 如果当前 AI 会话是在升级前打开的，建议新开会话，或让当前 AI 重新读取项目入口文档后再继续工作。",
        "summary_title": "升级结果汇总：",
        "summary_auto": "自动更新或已与模板对齐的文件：",
        "summary_preserved": "保留的本地定制：",
        "summary_manual": "仍需人工合并的文件：",
        "summary_agents_yes": "AGENTS 入口动作：请把下面的短入口合并到项目 AGENTS.md。",
        "summary_agents_no": "AGENTS 入口动作：无需处理；项目入口已能路由到受管 Maker/Checker 协议。",
        "summary_commit": "治理提交建议：复查升级 diff 后，可按项目惯例创建独立 governance upgrade commit；ForgeKit 未自动 commit 或 push。",
    },
}


def msg(lang, key, **kwargs):
    template = MESSAGES.get(lang, MESSAGES["en-US"]).get(key, MESSAGES["en-US"].get(key, key))
    return template.format(**kwargs)


def fail(message):
    raise SystemExit(f"[fail] {message}")


def validate_lang(value, label):
    if value not in LANGUAGES:
        fail(f"Invalid {label}: {value}. Allowed values: zh-CN, en-US")
    return value


def resolve_language(args):
    if args.lang:
        return validate_lang(args.lang, "--lang")
    env_lang = os.environ.get("FORGEKIT_LANG")
    if env_lang:
        return validate_lang(env_lang, "FORGEKIT_LANG")
    if args.yes or args.dry_run or args.no_apply or not sys.stdin.isatty():
        return "en-US"
    print(msg("en-US", "lang_prompt"))
    print(msg("en-US", "lang_zh"))
    print(msg("en-US", "lang_en"))
    choice = input(msg("en-US", "lang_choice")).strip()
    return "zh-CN" if choice == "1" else "en-US"


def parse_version(value, label):
    try:
        parts = tuple(int(part) for part in str(value).strip().lstrip("v").split("."))
    except ValueError:
        fail(f"Invalid {label} version: {value}")
    if len(parts) != 3:
        fail(f"{label} version must use major.minor.patch: {value}")
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


def try_load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except FileNotFoundError:
        return None, f"not found: {path}"
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"invalid JSON at {path}: {exc}"


def parse_boundary(governance_root):
    path = governance_root / BOUNDARY_RELATIVE_PATH
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError as exc:
        return None, f"cannot read boundary {path}: {exc}"
    section = None
    roots = {}
    write_policy = {}
    policy_name = None
    for raw in lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        if indent == 0 and stripped.endswith(":"):
            section = stripped[:-1]
            policy_name = None
            continue
        if section == "roots" and indent >= 2 and ":" in stripped:
            key, value = stripped.split(":", 1)
            roots[key.strip()] = value.strip().strip('"').strip("'")
        elif section == "write_policy" and indent == 2 and stripped.endswith(":"):
            policy_name = stripped[:-1]
            write_policy[policy_name] = []
        elif section == "write_policy" and indent >= 4 and stripped.startswith("-") and policy_name:
            write_policy[policy_name].append(stripped[1:].strip().strip('"').strip("'"))
    if not roots.get("project_root") or not roots.get("forgekit_root"):
        return None, f"boundary roots are incomplete: {path}"
    return {"path": path, "roots": roots, "write_policy": write_policy}, None


def resolved_boundary_path(governance_root, raw):
    value = str(raw).strip()
    if not value or value.startswith("<"):
        return None
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (governance_root / path).resolve()


def valid_state(governance_root):
    state, error = try_load_json(governance_root / STATE_RELATIVE_PATH)
    if error:
        return None, error
    required = {
        "schema_version", "forgekit_version", "managed_docs_root", "change_root",
        "mode", "features", "last_upgrade",
    }
    if not isinstance(state, dict) or state.get("schema_version") != 1 or required - set(state):
        return None, f"invalid active state: {governance_root / STATE_RELATIVE_PATH}"
    try:
        parse_version(state.get("forgekit_version", ""), "installed ForgeKit")
    except SystemExit as exc:
        return None, str(exc)
    return state, None


def is_within(path, parent):
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def classified_shadow(candidate, requested):
    lowered = [part.lower() for part in candidate.parts]
    for index, part in enumerate(lowered[:-1]):
        if part == ".forgekit" and lowered[index + 1] in {"archive", "upgrade", "upgrade-export", "reports"}:
            return True
    for owner in candidate.parents:
        workspace_map, error = try_load_json(owner / WORKSPACE_MAP_RELATIVE_PATH)
        if error or not isinstance(workspace_map, dict) or not workspace_map.get("enabled"):
            continue
        workspace = workspace_map.get("workspace", {})
        raw_roots = [workspace.get("archive_root"), workspace.get("artifact_root")]
        raw_roots.extend(item.get("path") for item in workspace_map.get("artifacts", []) if isinstance(item, dict))
        for raw in raw_roots:
            if not isinstance(raw, str) or not raw.strip():
                continue
            classified = (owner / raw).resolve()
            if is_within(candidate, classified) or is_within(requested, classified):
                return True
    return False


def topology_from_governance_root(governance_root):
    state, state_error = valid_state(governance_root)
    boundary, boundary_error = parse_boundary(governance_root)
    if state_error or boundary_error:
        return None, state_error or boundary_error
    project_root = resolved_boundary_path(governance_root, boundary["roots"]["project_root"])
    if project_root is None:
        return None, f"boundary project_root is unresolved: {boundary['path']}"
    forgekit_root = resolved_boundary_path(governance_root, boundary["roots"]["forgekit_root"])
    return {
        "governance_root": governance_root.resolve(),
        "workspace_root": governance_root.resolve(),
        "project_root": project_root,
        "forgekit_root": forgekit_root,
        "state": state,
        "boundary": boundary,
    }, None


def discover_existing_topology(requested):
    direct_state = requested / STATE_RELATIVE_PATH
    direct_boundary = requested / BOUNDARY_RELATIVE_PATH
    if direct_state.exists() or direct_boundary.exists():
        topology, error = topology_from_governance_root(requested)
        return {"status": "FOUND", "topology": topology} if topology else {"status": "INVALID", "reason": error}

    candidates = []
    for candidate in requested.parents:
        if not (candidate / STATE_RELATIVE_PATH).is_file() or not (candidate / BOUNDARY_RELATIVE_PATH).is_file():
            continue
        topology, error = topology_from_governance_root(candidate)
        if error or topology["project_root"] != requested.resolve() or classified_shadow(candidate, requested):
            continue
        candidates.append(topology)
    if len(candidates) == 1:
        return {"status": "FOUND", "topology": candidates[0]}
    if len(candidates) > 1:
        return {"status": "AMBIGUOUS", "candidates": candidates}
    return {"status": "NOT_FOUND"}


def git_top_level(path):
    probe = path if path.exists() else next((parent for parent in path.parents if parent.exists()), None)
    if probe is None:
        return None
    try:
        completed = subprocess.run(
            ["git", "-C", str(probe), "rev-parse", "--show-toplevel"],
            text=True, encoding="utf-8", errors="replace",
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False,
        )
    except OSError:
        return None
    return Path(completed.stdout.strip()).resolve() if completed.returncode == 0 and completed.stdout.strip() else None


def mapped_repo_root(topology, requested):
    workspace_map, error = try_load_json(topology["governance_root"] / WORKSPACE_MAP_RELATIVE_PATH)
    if error or not isinstance(workspace_map, dict) or not workspace_map.get("enabled"):
        return None
    candidates = []
    for repo in workspace_map.get("repos", []):
        if not isinstance(repo, dict) or not isinstance(repo.get("repo_path"), str):
            continue
        path = (topology["governance_root"] / repo["repo_path"]).resolve()
        if requested.resolve() == path or is_within(requested, path):
            candidates.append(path)
    unique = sorted(set(candidates), key=str)
    if len(unique) == 1:
        return unique[0]
    if len(unique) > 1:
        return "AMBIGUOUS"
    return None


def root_outputs(topology, requested, current_write_scope):
    if topology is None:
        return {
            "GovernanceRoot": "UNKNOWN",
            "WorkspaceRoot": "UNKNOWN",
            "ProjectRoot": str(requested),
            "RepoRoot": str(git_top_level(requested) or "UNKNOWN"),
            "ForgeKitRoot": "UNKNOWN",
            "CurrentWriteScope": current_write_scope,
        }
    repo_root = git_top_level(requested) or mapped_repo_root(topology, requested) or git_top_level(topology["project_root"])
    return {
        "GovernanceRoot": str(topology["governance_root"]),
        "WorkspaceRoot": str(topology["workspace_root"]),
        "ProjectRoot": str(topology["project_root"]),
        "RepoRoot": str(repo_root or "UNKNOWN"),
        "ForgeKitRoot": str(topology["forgekit_root"] or "UNKNOWN"),
        "CurrentWriteScope": current_write_scope,
    }


def toolkit_version(toolkit_root):
    state = load_json(toolkit_root / "project-template/.forgekit/state.json", "toolkit state")
    return parse_version(state.get("forgekit_version", ""), "toolkit")


def looks_like_legacy_forgekit(target):
    if (target / ".forgekit").exists():
        return True
    legacy_pairs = [
        (target / ".codex", target / "governance"),
        (target / "AGENTS.md", target / "CLAUDE.md"),
    ]
    return any(first.exists() and second.exists() for first, second in legacy_pairs)


def detect_project(target):
    state_path = target / STATE_RELATIVE_PATH
    if not state_path.is_file():
        if looks_like_legacy_forgekit(target):
            return "legacy-adoption", None, None
        return "init", None, None
    state = load_json(state_path, "project state")
    required = {
        "schema_version", "forgekit_version", "managed_docs_root", "change_root",
        "mode", "features", "last_upgrade",
    }
    if required - set(state) or state.get("schema_version") != 1:
        return "legacy-adoption", None, state
    installed = parse_version(state["forgekit_version"], "installed ForgeKit")
    if installed < MIN_MIGRATION_VERSION:
        return "legacy-adoption", installed, state
    return "versioned", installed, state


def run_capture(command, cwd=None):
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        print(completed.stdout.rstrip())
        fail(f"Command failed with exit code {completed.returncode}: {' '.join(command)}")
    return completed.stdout.rstrip()


def run_stream(command, cwd=None):
    completed = subprocess.run(command, cwd=cwd, check=False)
    if completed.returncode != 0:
        fail(f"Command failed with exit code {completed.returncode}: {' '.join(command)}")


def show_current_docs_integrity(toolkit_root, target):
    checker = toolkit_root / "scripts/check-current-docs-integrity.py"
    if not checker.is_file():
        print("Current docs integrity: unavailable (checker missing in ForgeKitRoot)")
        return
    completed = subprocess.run(
        [sys.executable, str(checker), "--repo-root", str(target), "--json"],
        text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError:
        report = None
    if completed.returncode == 2 or not isinstance(report, dict) or report.get("status") == "error":
        print("[warn] Current docs integrity could not be evaluated; safe migration is not blocked.")
        return
    print("ForgeKit Current Docs Integrity Check")
    print("Mode: read-only")
    print(f"Status: {report.get('status', 'error')}")
    print(f"Active tasks: {len(report.get('active_tasks', []))}")
    print(f"Blocking: {report.get('blocking_count', 0)}")
    print(f"Warnings: {report.get('warning_count', 0)}")
    blocking_findings = [item for item in report.get("findings", []) if item.get("blocking") is True]
    for item in report.get("findings", []):
        print(f"[{item.get('severity', 'warning')}] {item.get('code', 'unknown')}: {item.get('message', '')}")
    if blocking_findings:
        scopes = sorted({item.get("blocked_scope", "UNKNOWN") for item in blocking_findings})
        print("[needs-fix] Blocking is scoped to: " + "; ".join(scopes))


def confirmed(prompt, assume_yes, non_writing):
    if non_writing:
        return False
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        print("Non-interactive session detected; no files were changed. Re-run with --yes to apply.")
        return False
    answer = input(prompt).strip().lower()
    return answer in {"y", "yes"}


def derived_current_write_scope(args, task_scope, write_constraints_met=True):
    if args.dry_run or args.no_apply:
        return "read-only (dry-run/no-apply; no write authorization)"
    if not write_constraints_met:
        return f"UNKNOWN ({task_scope} write constraints are not satisfied; no write authorization)"
    if args.yes:
        return f"boundary policy intersection {task_scope} intersection apply authorization granted by --yes"
    if sys.stdin.isatty():
        return f"boundary policy intersection {task_scope} intersection user authorization pending confirmation"
    return f"boundary policy intersection {task_scope} intersection user authorization not granted (--yes absent)"


def print_detection(target, installed, toolkit, action, topology=None, *, layout=None, current_write_scope="read-only"):
    print("ForgeKit Unified Project Entry")
    print(f"RequestedTarget: {target}")
    for name, value in root_outputs(topology, target, current_write_scope).items():
        print(f"{name}: {value}")
    if layout:
        print(f"Layout: {layout}")
    print(f"Installed ForgeKit version: {version_text(installed) if installed else 'not installed'}")
    print(f"Toolkit ForgeKit version: {version_text(toolkit)}")
    print(f"Detected action: {action}")


def target_has_content(target):
    return target.is_dir() and any(target.iterdir())


def default_project_name(target):
    suffix = "-workspace"
    return target.name[:-len(suffix)] if target.name.lower().endswith(suffix) else target.name


def init_project(args, toolkit_root, target, toolkit, lang):
    layout = args.layout or "in-place"
    project_root = target if layout == "in-place" else target / default_project_name(target)
    nonempty = target_has_content(target)
    write_constraints_met = (not nonempty or args.force_init) and (not args.yes or args.layout is not None)
    topology = {
        "governance_root": target,
        "workspace_root": target,
        "project_root": project_root,
        "forgekit_root": toolkit_root,
    }
    print_detection(
        target, None, toolkit, "init", topology,
        layout=layout,
        current_write_scope=derived_current_write_scope(
            args, "fresh initialization task scope", write_constraints_met,
        ),
    )
    if nonempty and not args.force_init:
        print("Check result: uninstalled-nonempty")
        print("Plan summary: initialization requires --force-init because the target is not empty.")
        print("Safe actions count: 0")
        print("Manual actions count: 1")
        print("No files were changed.")
        return 0 if args.dry_run or args.no_apply else 2
    print("Check result: uninstalled")
    print("Plan summary: initialize the ForgeKit project template using the existing init script.")
    print("Safe actions count: 1")
    print("Manual actions count: 0")
    if args.yes and args.layout is None:
        print("[stop] Fresh noninteractive initialization requires an explicit --layout.")
        print(f'python scripts/forgekit-project.py --target "{target}" --yes --layout in-place')
        print(f'python scripts/forgekit-project.py --target "{target}" --yes --layout legacy-nested')
        print("No files were changed.")
        return 2
    if not confirmed(msg(lang, "init_prompt"), args.yes, args.dry_run or args.no_apply):
        print(msg(lang, "init_skipped"))
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        command = [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
            str(toolkit_root / "scripts/init-project-template.ps1"),
            "-TargetPath", str(target),
        ]
        if layout == "legacy-nested":
            command.extend(["-ProjectName", default_project_name(target)])
    else:
        command = [
            "bash", str(toolkit_root / "scripts/init-project-template.sh"),
            "--target-path", str(target),
        ]
        if layout == "legacy-nested":
            command.extend(["--project-name", default_project_name(target)])
    run_stream(command, cwd=toolkit_root)
    print("[ok] ForgeKit initialization completed through the existing init entry point.")
    return 0


def migration_counts(plan_output):
    safe = sum(int(value) for value in re.findall(r"(?m)^Safe actions:\s*(\d+)\s*$", plan_output))
    non_safe = sum(int(value) for value in re.findall(r"(?m)^Manual actions:\s*(\d+)\s*$", plan_output))
    review_needed = sum(int(value) for value in re.findall(r"(?m)^Review needed:\s*(\d+)\s*$", plan_output))
    reviews = len(re.findall(r"(?m)^- REVIEW:", plan_output))
    return safe, non_safe + review_needed + reviews


def review_needed_count(plan_output):
    return sum(int(value) for value in re.findall(r"(?m)^Review needed:\s*(\d+)\s*$", plan_output))


def print_project_review_policy_help(target, lang):
    print(msg(lang, "noninteractive_policy"))
    print("")
    print(msg(lang, "run_one_of"))
    print("")
    print(f'python .\\scripts\\forgekit-project.py --target "{target}" --yes --review-needed-policy manual-merge')
    print(f'python .\\scripts\\forgekit-project.py --target "{target}" --yes --review-needed-policy replace-template')


def normalize_review_policy(policy, lang):
    if policy == "keep-local":
        print(msg(lang, "alias_keep_local"))
        return "manual-merge"
    return policy


AGENTS_MAKER_CHECKER_MARKER = "Before medium/high risk implementation, freeze scope"
AGENTS_MAKER_CHECKER_SNIPPET = """- For medium/high risk changes, read `.forgekit/docs/maker-checker-protocol.md` and the active `.forgekit/changes/<id>/` artifacts.
- Before implementation, freeze scope, trust boundary, non-goals, stage authorization, and a risk-proportional acceptance matrix.
- Re-review defaults to prior blockers; fix-introduced contract/real-error regressions may still block, while unrelated suggestions stay follow-up."""


def print_upgrade_summary(toolkit_root, target, lang):
    state = load_json(target / STATE_RELATIVE_PATH, "project state")
    last_upgrade = state.get("last_upgrade") or {}
    migration_ids = set(last_upgrade.get("migrations") or [])
    actions = []
    for manifest_path in (toolkit_root / "migrations").glob("*/migration.json"):
        manifest = load_json(manifest_path, "migration manifest")
        if manifest.get("id") in migration_ids:
            actions.extend(action for action in manifest.get("actions", []) if action.get("target"))
    report_path = target / ".forgekit/reports/upgrade-review-needed.json"
    report = load_json(report_path, "upgrade review report") if report_path.is_file() else {"items": []}
    review_items = [item for item in (report.get("items") or []) if item.get("source_migration") in migration_ids]
    preserved = sorted({item.get("target_path") for item in review_items if item.get("status") in {"resolved_manual_merge", "skipped_existing_review_needed"} and item.get("target_path")})
    manual = sorted({item.get("target_path") for item in review_items if item.get("status") == "resolved_manual_merge" and item.get("target_path")})
    automated = sorted({action.get("target") for action in actions if action.get("target") and action.get("target") not in preserved})

    print(msg(lang, "summary_title"))
    print(msg(lang, "summary_auto"))
    for path in automated:
        print(f"- {path}")
    if not automated:
        print("- none")
    print(msg(lang, "summary_preserved"))
    for path in preserved:
        print(f"- {path}")
    if not preserved:
        print("- none")
    print(msg(lang, "summary_manual"))
    for path in manual:
        print(f"- {path}")
    if not manual:
        print("- none")
    agents_text = (target / "AGENTS.md").read_text(encoding="utf-8", errors="replace") if (target / "AGENTS.md").is_file() else ""
    if AGENTS_MAKER_CHECKER_MARKER in agents_text:
        print(msg(lang, "summary_agents_no"))
    else:
        print(msg(lang, "summary_agents_yes"))
        print(AGENTS_MAKER_CHECKER_SNIPPET)
    print(f"ForgeKit version: {state.get('forgekit_version')}")
    print(f"maker_checker_review_convergence: {state.get('features', {}).get('maker_checker_review_convergence', False)}")
    print(msg(lang, "summary_commit"))


def upgrade_project(args, toolkit_root, target, installed, toolkit, lang, topology, requested):
    upgrade_script = toolkit_root / "scripts/forgekit-upgrade.py"
    # JSON pipes must use the same encoding on Windows regardless of console locale.
    base = [sys.executable, '-X', 'utf8', str(upgrade_script)]
    pipe_env = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
    resolution_args = ['--entry-resolutions', str(Path(args.entry_resolutions).resolve())] if args.entry_resolutions else []
    current_descriptor = toolkit_root / 'migrations' / version_text(toolkit) / 'migration.json'
    if current_descriptor.is_file() and load_json(current_descriptor, 'migration').get('schema_version') == 2:
        completed = subprocess.run(base + ['plan', '--repo-root', str(target), '--json'] + resolution_args, cwd=toolkit_root,
                                   text=True, encoding='utf-8', errors='strict', capture_output=True, env=pipe_env)
        try:
            plan = json.loads(completed.stdout)
        except ValueError:
            print(completed.stdout + completed.stderr)
            return 2
        if completed.returncode not in (0, 2) or plan.get('to') != version_text(toolkit):
            if plan.get('reason'):
                print('[冲突] ' + plan['reason'] if lang == 'zh-CN' else '[conflict] ' + plan['reason'])
            print('[stop] No complete migration plan reaches the toolkit version.')
            return 2
        chinese = lang == 'zh-CN'
        if chinese:
            print(f"升级预检：{plan.get('from')} → {plan.get('to')}。尚未写入任何文件。")
            print('迁移链：' + ' → '.join(plan.get('version_chain', [plan['from'], plan['to']])))
        else:
            print(f"Upgrade preflight: {plan.get('from')} -> {plan.get('to')}. No files have been changed.")
            print('Migration chain: ' + ' -> '.join(plan.get('version_chain', [plan['from'], plan['to']])))
        if plan.get('conflicts') or completed.returncode:
            for item in plan.get('conflicts', []):
                print(f"{'[冲突]' if chinese else '[conflict]'} {item['target']}: {item['reason']}")
            print('升级未执行：请先解决上述冲突，项目版本和文件保持原样。' if chinese else '[stop] Resolve the named conflicts and rerun. No files were changed.')
            return 2
        if chinese:
            print(f"待执行 {len(plan['actions'])} 个动作；保留 {len(plan.get('preserved_documents', []))} 份项目事实文档，搬迁 {len(plan.get('preserved', []))} 个定制章节。")
        else:
            print(f"Planned: {len(plan['actions'])} actions; {len(plan.get('preserved_documents', []))} project documents preserved; {len(plan.get('preserved', []))} sections relocated.")
        if plan.get('entry_resolution'):
            for item in plan['entry_resolution']['entries']:
                print(f"{'显式保留入口' if chinese else 'Explicit entry preservation'}: {item['target']} (sha256: {item['sha256']})")
        for action in plan.get('actions', []):
            label = ('计划移除' if action['operation'] == 'remove' else '计划写入') if chinese else 'planned ' + action['operation']
            print(f"  {label}: {action['target']}")
        if not confirmed(msg(lang, 'safe_apply_prompt'), args.yes, args.dry_run or args.no_apply):
            print(msg(lang, 'safe_apply_skipped'))
            return 0
        result = subprocess.run(base + ['apply', '--safe', '--repo-root', str(target), '--json', '--plan-hash', plan['plan_hash']] + resolution_args,
                                cwd=toolkit_root, text=True, encoding='utf-8', errors='strict', capture_output=True, env=pipe_env)
        if result.returncode:
            print(result.stdout + result.stderr)
            return result.returncode
        actual = json.loads(result.stdout)
        if chinese:
            print(f"[完成] 已执行 {len(actual['actions'])} 个校验过的动作；报告：{actual['report']}")
            print('请新开 AI 会话。AGENTS/CLAUDE 已自动迁移，无需手工粘贴规则。')
        else:
            print(f"[ok] Applied {len(actual['actions'])} verified actions; report: {actual['report']}")
            print('[next] Start a fresh AI session. AGENTS/CLAUDE entries were migrated automatically; no manual snippet is needed.')
        return 0
    if resolution_args:
        print('[stop] Entry resolutions require a pending structured upgrade. No files changed.')
        return 2
    check_output = run_capture(base + ["check", "--repo-root", str(target)], cwd=toolkit_root)
    plan_output = run_capture(base + ["plan", "--repo-root", str(target)], cwd=toolkit_root)
    safe_count, manual_count = migration_counts(plan_output)
    check_status = re.search(r"(?m)^Status:\s*(.+)$", check_output)
    planned_target = re.search(r"(?m)^To:\s*(\d+\.\d+\.\d+)\s*$", plan_output)
    chain_reaches_toolkit = bool(
        planned_target and parse_version(planned_target.group(1), "planned target") == toolkit
    )
    has_review_needed = review_needed_count(plan_output) > 0
    policy_constraint_met = not (args.yes and has_review_needed and args.review_needed_policy is None)

    print_detection(
        requested, installed, toolkit, "upgrade-sync", topology,
        current_write_scope=derived_current_write_scope(
            args, "upgrade task scope", chain_reaches_toolkit and policy_constraint_met,
        ),
    )
    show_current_docs_integrity(toolkit_root, target)
    print(msg(lang, "check_result", status=check_status.group(1).strip() if check_status else "unknown"))
    print(msg(lang, "plan_summary"))
    print(plan_output)
    print(msg(lang, "safe_count", count=safe_count))
    print(msg(lang, "manual_count", count=manual_count))

    if not chain_reaches_toolkit:
        print("[stop] The available migration chain does not reach the toolkit version. Manual review is required.")
        print("No files were changed.")
        return 2
    if has_review_needed and args.review_needed_policy is None and (args.yes or not sys.stdin.isatty()):
        print_project_review_policy_help(target, lang)
        print(msg(lang, "no_files_changed"))
        return 2
    if not confirmed(msg(lang, "safe_apply_prompt"), args.yes, args.dry_run or args.no_apply):
        print(msg(lang, "safe_apply_skipped"))
        return 0
    apply_command = base + ["apply", "--safe", "--repo-root", str(target)]
    if args.review_needed_policy:
        apply_command.extend(["--review-needed-policy", normalize_review_policy(args.review_needed_policy, lang)])
    apply_command.extend(["--lang", lang])
    run_stream(apply_command, cwd=toolkit_root)
    print("[ok] Safe migration apply completed through forgekit-upgrade.py.")
    print_upgrade_summary(toolkit_root, target, lang)
    print(msg(lang, "upgrade_done"))
    print(msg(lang, "upgrade_next"))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Install or upgrade a ForgeKit-managed project")
    parser.add_argument("--target", required=True, help="Project root to inspect")
    parser.add_argument("--layout", choices=["in-place", "legacy-nested"], help="Fresh init layout; existing topology is never moved")
    parser.add_argument("--yes", action="store_true", help="Confirm initialization or safe migration apply")
    parser.add_argument("--dry-run", action="store_true", help="Detect and show the plan without writing")
    parser.add_argument("--force-init", action="store_true", help="Allow initialization only when ForgeKit is not installed")
    parser.add_argument("--no-apply", action="store_true", help="Run detection/check/plan only")
    parser.add_argument("--review-needed-policy", choices=["ask", "keep-local", "manual-merge", "replace-template", "abort"], help="How to resolve review-needed safe migration items during upgrade")
    parser.add_argument("--lang", help="Display language: zh-CN or en-US")
    parser.add_argument("--entry-resolutions", help="Explicit reviewed full-entry preservation packet; requires a pending structured upgrade")
    args = parser.parse_args()
    if args.yes and (args.dry_run or args.no_apply):
        fail("--yes cannot be combined with --dry-run or --no-apply")
    lang = resolve_language(args)

    toolkit_root = Path(__file__).resolve().parents[1]
    toolkit = toolkit_version(toolkit_root)
    requested = Path(args.target).expanduser().resolve()
    if requested.exists() and not requested.is_dir():
        fail(f"Target must be a directory path: {requested}")
    discovery = discover_existing_topology(requested)
    if discovery["status"] == "AMBIGUOUS":
        print("ForgeKit Unified Project Entry")
        print(f"RequestedTarget: {requested}")
        for name in ["GovernanceRoot", "WorkspaceRoot", "ProjectRoot", "RepoRoot", "ForgeKitRoot", "CurrentWriteScope"]:
            print(f"{name}: AMBIGUOUS")
        for candidate in discovery["candidates"]:
            print(f"CandidateGovernanceRoot: {candidate['governance_root']}")
        print("[blocking] C4: multiple exact boundary candidates make the write target ambiguous.")
        print("BlockedScope: init, adoption, upgrade, or write through this unified entry")
        print("No files were changed.")
        return 2
    if discovery["status"] == "INVALID":
        print(f"[stop] Existing ForgeKit markers are invalid: {discovery['reason']}")
        print("No files were changed.")
        return 2
    topology = discovery.get("topology")
    target = topology["governance_root"] if topology else requested
    status, installed, _ = detect_project(target)
    if args.force_init and status != "init":
        fail("--force-init is only valid when ForgeKit is not installed")
    if args.entry_resolutions and (status != 'versioned' or installed is None or installed >= toolkit):
        fail('Entry resolutions require a pending structured upgrade; no files changed')
    if status == "init":
        return init_project(args, toolkit_root, target, toolkit, lang)
    if status == "legacy-adoption":
        print_detection(requested, installed, toolkit, "legacy-adoption", topology, current_write_scope="UNKNOWN")
        print("Check result: adoption-required")
        print("Plan summary: treat this as an existing project; inventory facts and confirm adoption before creating new state.")
        print("Safe actions count: 0")
        print("Manual actions count: 1")
        print("No automatic upgrade or initialization was performed.")
        return 0
    if installed > toolkit:
        print_detection(requested, installed, toolkit, "stop-toolkit-too-old", topology)
        print("[stop] Project ForgeKit version is newer than this toolkit. Update ForgeKitRoot before continuing.")
        return 2
    if installed == toolkit:
        print_detection(requested, installed, toolkit, "up-to-date", topology)
        print(msg(lang, "check_result", status="current"))
        print(msg(lang, "up_to_date_plan"))
        print(msg(lang, "safe_count", count=0))
        print(msg(lang, "manual_count", count=0))
        print(msg(lang, "no_files_changed"))
        return 0
    return upgrade_project(args, toolkit_root, target, installed, toolkit, lang, topology, requested)


if __name__ == "__main__":
    raise SystemExit(main())
