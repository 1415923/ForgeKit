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
        [sys.executable, str(checker), "--repo-root", str(target)],
        text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    print(completed.stdout.rstrip())
    if completed.returncode == 1:
        print("[needs-fix] Safe migration may continue, but run a Current State Restoration Pass before archive or cleanup.")
    elif completed.returncode == 2:
        print("[warn] Current docs integrity could not be evaluated; safe migration is not blocked.")


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


def print_detection(target, installed, toolkit, action):
    print("ForgeKit Unified Project Entry")
    print(f"ProjectRoot: {target}")
    print(f"Installed ForgeKit version: {version_text(installed) if installed else 'not installed'}")
    print(f"Toolkit ForgeKit version: {version_text(toolkit)}")
    print(f"Detected action: {action}")


def target_has_content(target):
    return target.is_dir() and any(target.iterdir())


def default_project_name(target):
    suffix = "-workspace"
    return target.name[:-len(suffix)] if target.name.lower().endswith(suffix) else target.name


def init_project(args, toolkit_root, target, toolkit, lang):
    print_detection(target, None, toolkit, "init")
    nonempty = target_has_content(target)
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
    if not confirmed(msg(lang, "init_prompt"), args.yes, args.dry_run or args.no_apply):
        print(msg(lang, "init_skipped"))
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        command = [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
            str(toolkit_root / "scripts/init-project-template.ps1"),
            "-TargetPath", str(target), "-ProjectName", default_project_name(target),
        ]
    else:
        command = [
            "bash", str(toolkit_root / "scripts/init-project-template.sh"),
            "--target-path", str(target), "--project-name", default_project_name(target),
        ]
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


def upgrade_project(args, toolkit_root, target, installed, toolkit, lang):
    upgrade_script = toolkit_root / "scripts/forgekit-upgrade.py"
    base = [sys.executable, str(upgrade_script)]
    check_output = run_capture(base + ["check", "--repo-root", str(target)], cwd=toolkit_root)
    plan_output = run_capture(base + ["plan", "--repo-root", str(target)], cwd=toolkit_root)
    safe_count, manual_count = migration_counts(plan_output)
    check_status = re.search(r"(?m)^Status:\s*(.+)$", check_output)

    print_detection(target, installed, toolkit, "upgrade-sync")
    show_current_docs_integrity(toolkit_root, target)
    print(msg(lang, "check_result", status=check_status.group(1).strip() if check_status else "unknown"))
    print(msg(lang, "plan_summary"))
    print(plan_output)
    print(msg(lang, "safe_count", count=safe_count))
    print(msg(lang, "manual_count", count=manual_count))

    planned_target = re.search(r"(?m)^To:\s*(\d+\.\d+\.\d+)\s*$", plan_output)
    if not planned_target or parse_version(planned_target.group(1), "planned target") != toolkit:
        print("[stop] The available migration chain does not reach the toolkit version. Manual review is required.")
        print("No files were changed.")
        return 2
    has_review_needed = review_needed_count(plan_output) > 0
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
    print("Run ManagedDocsWriteback=minimal, then refresh the session before starting new work.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Install or upgrade a ForgeKit-managed project")
    parser.add_argument("--target", required=True, help="Project root to inspect")
    parser.add_argument("--yes", action="store_true", help="Confirm initialization or safe migration apply")
    parser.add_argument("--dry-run", action="store_true", help="Detect and show the plan without writing")
    parser.add_argument("--force-init", action="store_true", help="Allow initialization only when ForgeKit is not installed")
    parser.add_argument("--no-apply", action="store_true", help="Run detection/check/plan only")
    parser.add_argument("--review-needed-policy", choices=["ask", "keep-local", "manual-merge", "replace-template", "abort"], help="How to resolve review-needed safe migration items during upgrade")
    parser.add_argument("--lang", help="Display language: zh-CN or en-US")
    args = parser.parse_args()
    if args.yes and (args.dry_run or args.no_apply):
        fail("--yes cannot be combined with --dry-run or --no-apply")
    lang = resolve_language(args)

    toolkit_root = Path(__file__).resolve().parents[1]
    toolkit = toolkit_version(toolkit_root)
    target = Path(args.target).expanduser().resolve()
    if target.exists() and not target.is_dir():
        fail(f"Target must be a directory path: {target}")
    status, installed, _ = detect_project(target)
    if args.force_init and status != "init":
        fail("--force-init is only valid when ForgeKit is not installed")
    if status == "init":
        return init_project(args, toolkit_root, target, toolkit, lang)
    if status == "legacy-adoption":
        print_detection(target, installed, toolkit, "legacy-adoption")
        print("Check result: adoption-required")
        print("Plan summary: treat this as an existing project; inventory facts and confirm adoption before creating new state.")
        print("Safe actions count: 0")
        print("Manual actions count: 1")
        print("No automatic upgrade or initialization was performed.")
        return 0
    if installed > toolkit:
        print_detection(target, installed, toolkit, "stop-toolkit-too-old")
        print("[stop] Project ForgeKit version is newer than this toolkit. Update ForgeKitRoot before continuing.")
        return 2
    if installed == toolkit:
        print_detection(target, installed, toolkit, "up-to-date")
        print(msg(lang, "check_result", status="current"))
        print(msg(lang, "up_to_date_plan"))
        print(msg(lang, "safe_count", count=0))
        print(msg(lang, "manual_count", count=0))
        print(msg(lang, "no_files_changed"))
        return 0
    return upgrade_project(args, toolkit_root, target, installed, toolkit, lang)


if __name__ == "__main__":
    raise SystemExit(main())
