#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


LEGACY_NAME_RE = re.compile(r"#U[0-9a-fA-F]{4}")
FORBIDDEN_LEGACY_REFS = [
    "docs/代码库地图.md",
    "docs/本地工具链检查.md",
    "docs/版本路线图.md",
    "docs/版本更新记录.md",
    "使用说明.html",
]
LEGACY_REF_ALLOWLIST = {
    Path("scripts/smoke-test.py"),
    Path("scripts/init-project-template.ps1"),
    Path("scripts/init-project-template.sh"),
}
FORBIDDEN_PRIVATE_PATHS = [
    r"D:\JAVA",
    r"D:\Xilinx",
    r"D:\nodejs",
    r"C:\Users\32390",
]
NOISE_NAMES = {".DS_Store", "Thumbs.db", "__pycache__", ".pytest_cache"}
NOISE_SUFFIXES = (".tmp",)
REQUIRED_REPO_PATHS = [
    "usage.html",
    "project-template/.forgekit/project-boundary.yml",
    "project-template/.forgekit/docs/document-responsibility.md",
    "project-template/.forgekit/docs/document-lifecycle.md",
    "project-template/.forgekit/archive/README.md",
    "project-template/.forgekit/archive/changes/README.md",
    "project-template/.forgekit/archive/releases/README.md",
    "project-template/.forgekit/template-manifest.json",
    "project-template/governance/ai-engineering-loop.md",
    "project-template/changes/README.md",
    "project-template/changes/_template/proposal.md",
    "project-template/changes/_template/design.md",
    "project-template/changes/_template/tasks.md",
    "project-template/changes/_template/verification.md",
    "project-template/changes/_template/review.md",
    "project-template/changes/_template/ship.md",
    "project-template/changes/_template/retro.md",
    "project-template/docs/codebase-map.md",
    "project-template/docs/work-log.md",
    "project-template/docs/task-intake.md",
    "project-template/docs/local-toolchain.md",
    "project-template/docs/loop-readiness.md",
    "project-template/docs/loop-blueprint.md",
    "project-template/docs/loop-operations.md",
    "project-template/docs/maker-checker-protocol.md",
    "project-template/docs/native-agent-adapter.md",
    "project-template/docs/worktree-playbook.md",
    "project-template/docs/version-roadmap.md",
    "project-template/.codex/config.toml",
    "project-template/.codex/agents/forgekit-planner.toml",
    "project-template/.codex/agents/forgekit-reviewer.toml",
    "project-template/.codex/agents/forgekit-verifier.toml",
    "project-template/scripts/check-codex-native-agents.py",
    "scripts/check-codex-native-agents.py",
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
]
REQUIRED_GENERATED_PATHS = [
    "AGENTS.md",
    "CLAUDE.md",
    ".forgekit/project-boundary.yml",
    ".forgekit/template-lock.json",
    ".forgekit/docs/document-responsibility.md",
    ".forgekit/docs/document-lifecycle.md",
    ".forgekit/archive/README.md",
    ".forgekit/archive/changes/README.md",
    ".forgekit/archive/releases/README.md",
    ".forgekit/docs/codebase-map.md",
    ".forgekit/docs/work-log.md",
    ".forgekit/docs/task-intake.md",
    ".forgekit/docs/local-toolchain.md",
    ".forgekit/docs/loop-readiness.md",
    ".forgekit/docs/loop-blueprint.md",
    ".forgekit/docs/loop-operations.md",
    ".forgekit/docs/maker-checker-protocol.md",
    ".forgekit/docs/native-agent-adapter.md",
    ".forgekit/docs/worktree-playbook.md",
    ".forgekit/docs/version-roadmap.md",
    ".forgekit/docs/changelog.md",
    ".codex/config.toml",
    ".codex/agents/forgekit-planner.toml",
    ".codex/agents/forgekit-reviewer.toml",
    ".codex/agents/forgekit-verifier.toml",
    "governance/ai-engineering-loop.md",
    ".forgekit/changes/README.md",
    ".forgekit/changes/_template/proposal.md",
    ".forgekit/changes/_template/design.md",
    ".forgekit/changes/_template/tasks.md",
    ".forgekit/changes/_template/verification.md",
    ".forgekit/changes/_template/review.md",
    ".forgekit/changes/_template/ship.md",
    ".forgekit/changes/_template/retro.md",
    "scripts/run-harness-check.ps1",
    "scripts/check-doc-sync.ps1",
    "scripts/check-codex-native-agents.py",
    "scripts/archive-changes.py",
]


def run(cmd, cwd, check=True):
    result = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        shell=False,
    )
    if check and result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        raise SystemExit(f"Command failed ({result.returncode}): {' '.join(cmd)}")
    return result


def fail(message):
    raise SystemExit(f"[fail] {message}")


def all_files(root):
    skip_dirs = {".git", "__pycache__"}
    for path in root.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.is_file():
            yield path


def assert_no_escaped_filenames(root):
    bad = []
    for path in root.rglob("*"):
        if LEGACY_NAME_RE.search(path.name):
            bad.append(str(path.relative_to(root)))
    if bad:
        fail("Escaped #Uxxxx file names found:\n" + "\n".join(bad))


def assert_no_noise_files(root):
    bad = []
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.name in NOISE_NAMES or path.name.endswith(NOISE_SUFFIXES):
            bad.append(str(path.relative_to(root)))
    if bad:
        fail("Noise files should not be present in templates or generated projects:\n" + "\n".join(bad))


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def assert_no_forbidden_text(root, patterns, label, allowlist=None):
    allowlist = allowlist or set()
    bad = []
    for path in all_files(root):
        try:
            relative = path.relative_to(root)
        except ValueError:
            relative = path
        if relative in allowlist:
            continue
        if path.suffix.lower() not in {".md", ".ps1", ".sh", ".html", ".py", ".json", ".yaml", ".yml"}:
            continue
        text = read_text(path)
        for pattern in patterns:
            if pattern in text:
                bad.append(f"{relative} contains {pattern}")
    if bad:
        fail(f"{label}:\n" + "\n".join(bad))


def assert_paths(root, paths):
    missing = [p for p in paths if not (root / p).exists()]
    if missing:
        fail("Missing required paths:\n" + "\n".join(missing))


def assert_absent_paths(root, paths):
    present = [p for p in paths if (root / p).exists()]
    if present:
        fail("Unexpected paths found:\n" + "\n".join(present))


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_boundary_config(path):
    text = path.read_text(encoding="utf-8")
    required = [
        'managed_docs_root: ".forgekit/docs"',
        'change_root: ".forgekit/changes"',
        "business_docs_roots:",
        '    - "docs"',
        "task_scoped:",
        "read_mostly:",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        fail("Boundary config is missing required entries:\n" + "\n".join(missing))


def assert_loop_docs(root, readiness_path, blueprint_path):
    readiness = (root / readiness_path).read_text(encoding="utf-8")
    blueprint = (root / blueprint_path).read_text(encoding="utf-8")
    readiness_required = [
        "Readiness Status: not-ready | partial | ready",
        "有状态文件",
        "有验证命令",
        "已定义停止条件",
        "已定义人工升级路径",
        "ForgeKit Loop 五要素",
        "未来路线图内容",
    ]
    blueprint_required = [
        "不是自动执行授权",
        "Default: manual only.",
        "## 触发方式",
        "## 输入来源",
        "## 状态文件",
        "## 允许路径",
        "## 禁止路径",
        "## 验证命令",
        "## 停止条件",
        "## 人工升级",
        "## Token 预算",
        "## 理解复述",
        "## 输出 / 回写",
        "OperationMode: dry-run | one-step | continue | stop-handoff",
        "MaxRounds:",
        "MaxFilesRead:",
        "MaxFilesChanged:",
        "MaxCommands:",
        "RequiresUserConfirmation: yes",
        "WritebackTarget:",
        "agent_mode: native | fallback | simulated",
        "native_agent_status: available | unavailable | unverified",
        "agent_runtime: claude-code | codex | unknown",
        "agent_invocation_observed:",
        "fallback_reason:",
        "StopOnUnclearScope: yes",
        "StopOnValidationFailure: yes",
        "WorktreeStrategy: none | optional | required",
        "WorktreePath:",
        "WorktreeBranch:",
        "IsolationReason:",
        "CleanupRule:",
        "Worktree 字段只是",
        "这些操作字段只是",
        "daemon",
        "cron",
        "MCP",
        "自动 PR",
        "sub-agent 调度器",
        "worktree 自动化",
    ]
    missing_readiness = [item for item in readiness_required if item not in readiness]
    if missing_readiness:
        fail(f"loop-readiness.md missing expected text:\n" + "\n".join(missing_readiness))
    missing_blueprint = [item for item in blueprint_required if item not in blueprint]
    if missing_blueprint:
        fail(f"loop-blueprint.md missing expected text:\n" + "\n".join(missing_blueprint))


def assert_loop_operations(root, operations_path, blueprint_path, agents_path, claude_path, rules_path):
    operations = (root / operations_path).read_text(encoding="utf-8")
    blueprint = (root / blueprint_path).read_text(encoding="utf-8")
    agents = (root / agents_path).read_text(encoding="utf-8")
    claude = (root / claude_path).read_text(encoding="utf-8")
    rules = (root / rules_path).read_text(encoding="utf-8")
    operations_required = [
        "Loop 默认关闭",
        "不是自动 loop runner",
        "## Loop Dry Run",
        "## Loop One Step",
        "## Loop Continue",
        "## Loop Stop / Handoff",
        "只读取 loop 蓝图",
        "不修改文件",
        "只执行一轮",
        "只继续下一轮",
        "不要启动另一轮 loop",
        "每一轮实际执行过的 loop 都必须回写",
        ".forgekit/docs/work-log.md",
        "agent_mode: native | fallback | simulated",
        "native_agent_status: available | unavailable | unverified",
        "fallback_reason",
    ]
    blueprint_required = [
        "OperationMode: dry-run | one-step | continue | stop-handoff",
        "MaxRounds:",
        "MaxFilesRead:",
        "MaxFilesChanged:",
        "MaxCommands:",
        "RequiresUserConfirmation: yes",
        "WritebackTarget:",
        "StopOnUnclearScope: yes",
        "StopOnValidationFailure: yes",
    ]
    entry_required = [
        "Do not enter loop mode unless the user explicitly asks for loop dry-run, one-step, continue, or stop/handoff.",
        "Before loop one-step, restate the blueprint fields",
        "Loop continue must not run continuously",
        "Stop and escalate on unclear scope, budget overrun, validation failure, or forbidden path contact.",
        "Loop output must write back",
        "Generated native agent config is not proof of runtime registration.",
        "Bounded-auto or loop execution must record `agent_mode`",
    ]
    rules_required = [
        "不得自行进入 loop mode",
        "loop one-step 前必须复述 blueprint",
        "loop continue 不得自动连续运行",
        "scope 不清、预算超限、验证失败或触及 forbidden paths",
        "loop 输出必须写回",
        "生成 native agent 配置不等于 runtime 已注册",
        "bounded-auto 或 loop 执行必须写明 `agent_mode`",
    ]
    missing_operations = [item for item in operations_required if item not in operations]
    if missing_operations:
        fail(f"loop-operations.md missing expected text:\n" + "\n".join(missing_operations))
    missing_blueprint = [item for item in blueprint_required if item not in blueprint]
    if missing_blueprint:
        fail(f"loop-blueprint.md missing loop operation fields:\n" + "\n".join(missing_blueprint))
    for label, text in [("AGENTS.md", agents), ("CLAUDE.md", claude)]:
        missing_entry = [item for item in entry_required if item not in text]
        if missing_entry:
            fail(f"{label} missing loop operation rules:\n" + "\n".join(missing_entry))
    missing_rules = [item for item in rules_required if item not in rules]
    if missing_rules:
        fail(".codex/rules.md missing loop operation rules:\n" + "\n".join(missing_rules))


def assert_native_agent_adapter(repo, root, adapter_path):
    adapter = (root / adapter_path).read_text(encoding="utf-8")
    skill = (repo / "native-adapters/claude-code/skills/forgekit-loop/SKILL.md").read_text(encoding="utf-8")
    adapter_required = [
        "RuntimeRegistration: generated | installed | registered | invoked",
        "只有 `invoked` 才能写成 native 真正可用",
        "native | fallback | simulated",
        "native_agent_status",
        "Native Agent Verification Checklist",
        "/agents",
        "developer_instructions",
        "check-codex-native-agents.py",
        "FallbackPolicy: fallback is downgrade mode, not native success",
        "native-only",
        "不得把 fallback 或 simulated 结果描述为 native agent 成功",
    ]
    skill_required = [
        "Generated config is not proof of runtime registration.",
        "Only invoked can be called native available.",
        "agent_mode=fallback",
        "fallback_reason",
        "native-only",
        "Native-only verification is read-only by default.",
        "Never describe fallback or simulated execution as native agent success.",
    ]
    missing_adapter = [item for item in adapter_required if item not in adapter]
    if missing_adapter:
        fail("native-agent-adapter.md missing expected text:\n" + "\n".join(missing_adapter))
    missing_skill = [item for item in skill_required if item not in skill]
    if missing_skill:
        fail("forgekit-loop skill missing fallback contract:\n" + "\n".join(missing_skill))


def assert_codex_native_agents(target):
    expected = {
        "forgekit-planner": target / ".codex/agents/forgekit-planner.toml",
        "forgekit-reviewer": target / ".codex/agents/forgekit-reviewer.toml",
        "forgekit-verifier": target / ".codex/agents/forgekit-verifier.toml",
    }
    for name, path in expected.items():
        if not path.is_file():
            fail(f"missing Codex native agent: {path}")
        text = path.read_text(encoding="utf-8")
        required = [
            f'name = "{name}"',
            "description =",
            "developer_instructions",
        ]
        missing = [item for item in required if item not in text]
        if missing:
            fail(f"{path} missing required TOML fields:\n" + "\n".join(missing))
    config = target / ".codex/config.toml"
    if not config.is_file():
        fail("generated project missing .codex/config.toml")
    config_text = config.read_text(encoding="utf-8")
    for item in ["[agents]", "max_threads", "max_depth"]:
        if item not in config_text:
            fail(f".codex/config.toml missing {item}")
    before_hashes = {
        ".forgekit/template-lock.json": sha256_file(target / ".forgekit/template-lock.json"),
        ".forgekit/docs/document-responsibility.md": sha256_file(target / ".forgekit/docs/document-responsibility.md"),
        "README.md": sha256_file(target / "README.md"),
        "AGENTS.md": sha256_file(target / "AGENTS.md"),
        "CLAUDE.md": sha256_file(target / "CLAUDE.md"),
    }
    run([
        sys.executable,
        "scripts/check-codex-native-agents.py",
        "--repo-root",
        ".",
        "--observed-agent",
        "default,explorer,worker",
    ], cwd=target)
    report = target / ".forgekit/codex-native-agent-report.md"
    if not report.is_file():
        fail("Codex native doctor did not write .forgekit/codex-native-agent-report.md")
    report_text = report.read_text(encoding="utf-8")
    required_report = [
        "Status: report-only",
        "SchemaStatus: pass",
        "NativeAgentStatus: unavailable",
        "RuntimeRegistration: unavailable",
        "Schema pass does not mean runtime registered.",
        "default, explorer, worker",
    ]
    missing_report = [item for item in required_report if item not in report_text]
    if missing_report:
        fail("Codex native agent report missing expected text:\n" + "\n".join(missing_report))
    for rel_path, before in before_hashes.items():
        after = sha256_file(target / rel_path)
        if after != before:
            fail(f"Codex native doctor must not modify {rel_path}")


def assert_maker_checker_protocol(root, protocol_path, review_path, agents_path, claude_path, rules_path):
    protocol = (root / protocol_path).read_text(encoding="utf-8")
    review = (root / review_path).read_text(encoding="utf-8")
    agents = (root / agents_path).read_text(encoding="utf-8")
    claude = (root / claude_path).read_text(encoding="utf-8")
    rules = (root / rules_path).read_text(encoding="utf-8")
    protocol_required = [
        "Maker / Checker 协议",
        "本文是审查流程",
        "不是多 agent 调度器",
        "Maker",
        "Checker",
        "ready-for-check",
        "pass",
        "needs-fix",
        "manual-review",
        "单 agent 使用",
        "不生成 sub-agent 配置",
        "## Worktree 隔离",
        "不会自动创建 worktree",
    ]
    review_required = [
        "## Maker 摘要",
        "MakerStatus: ready-for-check | blocked | partial",
        "FilesChanged:",
        "ImplementationSummary:",
        "ValidationRun:",
        "KnownRisks:",
        "NotVerified:",
        "## Checker 复查",
        "CheckerStatus: pass | needs-fix | manual-review | not-run",
        "DiffReviewed: yes | no",
        "ValidationReviewed: yes | no",
        "DocsReviewed: yes | no",
        "RisksReviewed: yes | no",
        "Findings:",
        "RequiredFixes:",
        "FinalRecommendation:",
    ]
    entry_required = [
        "Maker phase and Checker phase",
        "ready for check",
        "pass",
        "needs-fix",
        "manual-review",
    ]
    rules_required = [
        "Maker phase",
        "Checker phase",
        "ready for check",
        "manual-review",
    ]
    missing_protocol = [item for item in protocol_required if item not in protocol]
    if missing_protocol:
        fail(f"maker-checker-protocol.md missing expected text:\n" + "\n".join(missing_protocol))
    missing_review = [item for item in review_required if item not in review]
    if missing_review:
        fail(f"review.md missing Maker/Checker fields:\n" + "\n".join(missing_review))
    for label, text in [("AGENTS.md", agents), ("CLAUDE.md", claude)]:
        missing_entry = [item for item in entry_required if item not in text]
        if missing_entry:
            fail(f"{label} missing Maker/Checker entry rules:\n" + "\n".join(missing_entry))
    missing_rules = [item for item in rules_required if item not in rules]
    if missing_rules:
        fail(".codex/rules.md missing Maker/Checker rules:\n" + "\n".join(missing_rules))


def assert_worktree_playbook(root, playbook_path, blueprint_path, maker_checker_path, agents_path, claude_path, rules_path):
    playbook = (root / playbook_path).read_text(encoding="utf-8")
    blueprint = (root / blueprint_path).read_text(encoding="utf-8")
    maker_checker = (root / maker_checker_path).read_text(encoding="utf-8")
    agents = (root / agents_path).read_text(encoding="utf-8")
    claude = (root / claude_path).read_text(encoding="utf-8")
    rules = (root / rules_path).read_text(encoding="utf-8")
    playbook_required = [
        "# Worktree 手册",
        "用途：",
        "## 什么时候使用",
        "## 什么时候不要使用",
        "## 命名约定",
        "## 创建前检查清单",
        "## 推荐命令",
        "## Maker / Checker 用法",
        "## 清理",
        "## 安全规则",
        "不是 worktree runner",
        "除非用户明确要求，不要创建 worktree",
        "git status --short",
        "不要自动 merge、push、删除分支、移除 worktree、创建 PR 或启动 agent",
    ]
    blueprint_required = [
        "## Worktree 策略",
        "WorktreeStrategy: none | optional | required",
        "WorktreePath:",
        "WorktreeBranch:",
        "IsolationReason:",
        "CleanupRule:",
        "这些字段只描述可审查的隔离意图",
    ]
    entry_required = [
        "Do not create a worktree unless the user explicitly asks.",
        "Before creating a worktree, confirm `git status --short` is clean",
        "base branch, worktree path, branch name, allowed paths, validation command, and cleanup plan",
        "Do not automatically merge, push, delete branches, remove worktrees, create PRs, start agents, or schedule worktree tasks.",
        "Worktree results must be written to `.forgekit/docs/work-log.md` or the scoped change review.",
    ]
    rules_required = [
        "不得自行创建 worktree",
        "git status --short",
        "base branch、worktree path、branch name、allowed paths、validation command 和 cleanup plan",
        "不得自动 merge、push、delete branch、remove worktree、创建 PR、启动 agent 或调度 worktree 任务",
        "worktree 结果必须写回",
    ]
    missing_playbook = [item for item in playbook_required if item not in playbook]
    if missing_playbook:
        fail(f"worktree-playbook.md missing expected text:\n" + "\n".join(missing_playbook))
    missing_blueprint = [item for item in blueprint_required if item not in blueprint]
    if missing_blueprint:
        fail(f"loop-blueprint.md missing worktree strategy fields:\n" + "\n".join(missing_blueprint))
    if "Worktree 隔离" not in maker_checker or "不会自动创建 worktree" not in maker_checker:
        fail("maker-checker-protocol.md missing worktree isolation boundary")
    for label, text in [("AGENTS.md", agents), ("CLAUDE.md", claude)]:
        missing_entry = [item for item in entry_required if item not in text]
        if missing_entry:
            fail(f"{label} missing worktree safety rules:\n" + "\n".join(missing_entry))
    missing_rules = [item for item in rules_required if item not in rules]
    if missing_rules:
        fail(".codex/rules.md missing worktree safety rules:\n" + "\n".join(missing_rules))


def assert_task_intake(root, intake_path, task_board_path, requirements_path, changelog_path, agents_path, claude_path, rules_path):
    intake = (root / intake_path).read_text(encoding="utf-8")
    task_board = (root / task_board_path).read_text(encoding="utf-8")
    work_log_path = task_board_path.replace("task-board.md", "work-log.md")
    work_log = (root / work_log_path).read_text(encoding="utf-8")
    requirements = (root / requirements_path).read_text(encoding="utf-8")
    changelog = (root / changelog_path).read_text(encoding="utf-8")
    agents = (root / agents_path).read_text(encoding="utf-8")
    claude = (root / claude_path).read_text(encoding="utf-8")
    rules = (root / rules_path).read_text(encoding="utf-8")
    intake_required = [
        "Source Record",
        "Source ID",
        "self-planned",
        "user-feedback",
        "bug-found",
        "tech-debt",
        "Received At",
        "Sender / Source",
        "Original Location",
        "Human Review: pending | confirmed | corrected | rejected",
        "Confidentiality: normal | sensitive-redacted",
        "原文",
        "Update Notes",
        "责任拆分",
        "时间窗口",
        "AI 理解",
        "Task Decision",
        "Derived Tasks",
        "Task Gate",
        "note-only",
        "update-existing-task",
        "create-task",
        "Human Review Status",
    ]
    missing_intake = [item for item in intake_required if item not in intake]
    if missing_intake:
        fail(f"task-intake.md missing expected text:\n" + "\n".join(missing_intake))
    board_required = [
        "任务准入",
        "Source ID",
        "Closed / Dropped / Superseded",
        "Superseded",
        "对齐检查",
    ]
    missing_board = [item for item in board_required if item not in task_board]
    if missing_board:
        fail("task-board.md missing source-to-task alignment rules:\n" + "\n".join(missing_board))
    work_log_required = [
        "Task ID",
        "Source ID",
        "needs-task-decision",
        "工作日志里的待办不得直接进入看板",
    ]
    missing_work_log = [item for item in work_log_required if item not in work_log]
    if missing_work_log:
        fail("work-log.md missing task/source backlink rules:\n" + "\n".join(missing_work_log))
    if "Source ID" not in task_board:
        fail("task-board.md must include Source ID backlinks")
    if "task-intake.md" not in requirements or "不替代" not in requirements:
        fail("requirements.md must not imply it replaces task-intake.md")
    if "task-intake.md" not in changelog or "不替代" not in changelog:
        fail("changelog.md must not imply it replaces task-intake.md")
    entry_required = [
        ".forgekit/docs/task-intake.md",
        "先归并来源，再生成任务",
        "Update Notes",
        "不要默认创建新任务",
        "task-board.md",
        "拆解任务必须引用 Source ID",
        "Human Review: pending",
    ]
    for label, text in [("AGENTS.md", agents), ("CLAUDE.md", claude)]:
        missing_entry = [item for item in entry_required if item not in text]
        if missing_entry:
            fail(f"{label} missing task-intake rules:\n" + "\n".join(missing_entry))
    rules_required = [
        ".forgekit/docs/task-intake.md",
        "先归并来源，再生成任务",
        "Update Notes",
        "不要默认创建新任务",
        "task-board.md",
        "拆解任务必须引用 Source ID",
        "Human Review: pending",
        "不得把账号、密码、token、证书、环境地址或敏感配置原样写入 managed docs",
    ]
    missing_rules = [item for item in rules_required if item not in rules]
    if missing_rules:
        fail(".codex/rules.md missing task-intake rules:\n" + "\n".join(missing_rules))


def assert_managed_docs_responsibility_v2(root, responsibility_path, codebase_path, agents_path, claude_path, rules_path):
    responsibility = (root / responsibility_path).read_text(encoding="utf-8")
    codebase = (root / codebase_path).read_text(encoding="utf-8")
    agents = (root / agents_path).read_text(encoding="utf-8")
    claude = (root / claude_path).read_text(encoding="utf-8")
    rules = (root / rules_path).read_text(encoding="utf-8")

    responsibility_required = [
        "Managed Docs 职责矩阵 v2",
        "文档分类",
        "读者",
        "默认读取",
        "写什么",
        "不写什么",
        "更新触发",
        "相关文档",
        "core",
        "current",
        "working",
        "triggered",
        "generated",
        "archive",
    ]
    missing = [item for item in responsibility_required if item not in responsibility]
    if missing:
        fail("document-responsibility.md missing v2 fields:\n" + "\n".join(missing))

    codebase_required = [
        "本文只做代码搜索入口，不做项目百科",
        "不要默认读取 `.forgekit/docs/**` 全量内容",
        ".DS_Store",
        "Thumbs.db",
        "__pycache__",
        ".pytest_cache",
        "*.tmp",
    ]
    missing_codebase = [item for item in codebase_required if item not in codebase]
    if missing_codebase:
        fail("codebase-map.md missing responsibility-v2 boundaries:\n" + "\n".join(missing_codebase))

    entry_required = [
        "默认不要读取全部 `.forgekit/docs/**`",
        "document-responsibility.md",
        "不要把同一事实重复写进多个文档",
        "触发式文档只有对应事件发生时才更新",
    ]
    for label, text in [("AGENTS.md", agents), ("CLAUDE.md", claude)]:
        missing_entry = [item for item in entry_required if item not in text]
        if missing_entry:
            fail(f"{label} missing managed-docs v2 entry rules:\n" + "\n".join(missing_entry))

    rules_required = [
        "不要默认全量读取 `.forgekit/docs/**`",
        "document-responsibility.md",
        "同一事实只写到负责的文档",
        "触发式文档只有事件发生才更新",
        "给用户看的文档要短、自然、可确认",
    ]
    missing_rules = [item for item in rules_required if item not in rules]
    if missing_rules:
        fail(".codex/rules.md missing managed-docs v2 rules:\n" + "\n".join(missing_rules))


def assert_json(path):
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Invalid JSON: {path}: {exc}")


def assert_manifest_lock(target):
    lock_path = target / ".forgekit" / "template-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if lock.get("installed_version") != "0.30.1":
        fail("template-lock installed_version must be 0.30.1")
    if lock.get("managed_docs_root") != ".forgekit/docs":
        fail("template-lock managed_docs_root must match boundary")
    if lock.get("change_root") != ".forgekit/changes":
        fail("template-lock change_root must match boundary")
    text = lock_path.read_text(encoding="utf-8")
    if "current_checksum" in text or "local_modified" in text:
        fail("template-lock must not store current_checksum or local_modified")
    for item in lock.get("files", []):
        target_path = item.get("target_path", "")
        if target_path.startswith("docs/") or target_path.startswith("changes/"):
            fail(f"template-lock contains unmanaged root target: {target_path}")


def assert_upgrade_report(repo, target):
    before_lock = (target / ".forgekit" / "template-lock.json").read_bytes()
    doc_path = target / ".forgekit" / "docs" / "project-plan.md"
    before_doc = doc_path.read_bytes()
    if os.name == "nt":
        run([
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(repo / "scripts" / "init-project-template.ps1"),
            "-TargetPath",
            str(target),
            "-ProjectName",
            "forgekit-smoke",
            "-Mode",
            "Standard",
            "-Upgrade",
            "-ExportUpgradeTemplates",
        ], cwd=repo)
    else:
        run([
            "bash",
            str(repo / "scripts" / "init-project-template.sh"),
            "--target-path",
            str(target),
            "--project-name",
            "forgekit-smoke",
            "--mode",
            "Standard",
            "--upgrade",
            "--export-upgrade-templates",
        ], cwd=repo)
    if before_lock != (target / ".forgekit" / "template-lock.json").read_bytes():
        fail("upgrade must not update template-lock.json")
    if before_doc != doc_path.read_bytes():
        fail("upgrade must not overwrite managed docs")
    assert_paths(target, [
        ".forgekit/upgrade-report.md",
        ".forgekit/upgrade-export/0.30.1/.forgekit/docs/project-plan.md",
    ])


def assert_guided_upgrade(repo, target):
    before_lock = (target / ".forgekit" / "template-lock.json").read_bytes()
    doc_path = target / ".forgekit" / "docs" / "project-plan.md"
    before_doc = doc_path.read_bytes()
    business_note = target / "docs" / "business.md"
    before_business = business_note.read_bytes()
    if os.name == "nt":
        run([
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(repo / "scripts" / "upgrade-forgekit.ps1"),
            "-ProjectPath",
            str(target),
        ], cwd=repo)
    else:
        run([
            "bash",
            str(repo / "scripts" / "upgrade-forgekit.sh"),
            "--project-path",
            str(target),
        ], cwd=repo)
    if before_lock != (target / ".forgekit" / "template-lock.json").read_bytes():
        fail("guided upgrade must not update template-lock.json")
    if before_doc != doc_path.read_bytes():
        fail("guided upgrade must not overwrite managed docs")
    if before_business != business_note.read_bytes():
        fail("guided upgrade must not write business docs")
    assert_paths(target, [
        ".forgekit/upgrade/upgrade-plan.md",
        ".forgekit/upgrade/upgrade-actions.md",
        ".forgekit/upgrade/upgrade-inventory.json",
        ".forgekit/upgrade/candidates/0.30.1/.forgekit/docs/project-plan.md",
    ])
    plan = (target / ".forgekit" / "upgrade" / "upgrade-plan.md").read_text(encoding="utf-8")
    actions = (target / ".forgekit" / "upgrade" / "upgrade-actions.md").read_text(encoding="utf-8")
    required_plan = [
        "Status: report-only",
        "Mode: guided-upgrade",
        "must_review",
        "merge_carefully",
        "can_add",
        "template_only",
    ]
    missing_plan = [item for item in required_plan if item not in plan]
    if missing_plan:
        fail("guided upgrade plan missing expected text:\n" + "\n".join(missing_plan))
    if "Do not overwrite project facts" not in actions or "template-lock" not in actions:
        fail("guided upgrade actions must include safety policy")


def write_change(root, change_id, metadata, files):
    change_dir = root / ".forgekit" / "changes" / change_id
    change_dir.mkdir(parents=True, exist_ok=True)
    if metadata is not None:
        (change_dir / "proposal.md").write_text(metadata, encoding="utf-8")
    for name in files:
        (change_dir / name).write_text(f"# {name}\n", encoding="utf-8")


def assert_smart_apply_flow(source_target):
    target = source_target.parent / f"{source_target.name}-smart-apply"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source_target, target)

    before_lock = (target / ".forgekit" / "template-lock.json").read_bytes()
    before_readme = (target / "README.md").read_bytes()
    before_agents = (target / "AGENTS.md").read_bytes()
    before_claude = (target / "CLAUDE.md").read_bytes()
    business_note = target / "docs" / "business.md"
    before_business = business_note.read_bytes()
    docs_hashes = {path.relative_to(target).as_posix(): path.read_bytes() for path in (target / ".forgekit" / "docs").rglob("*") if path.is_file()}
    plan_path = target / ".forgekit" / "archive-plan.md"
    reference_report_path = target / ".forgekit" / "archive-reference-report.md"
    sync_report_path = target / ".forgekit" / "current-docs-sync-report.md"
    smart_report_path = target / ".forgekit" / "smart-archive-report.md"
    before_plan = plan_path.read_bytes()
    before_reference = reference_report_path.read_bytes()
    before_sync = sync_report_path.read_bytes()
    before_smart = smart_report_path.read_bytes()

    run(["git", "add", "."], cwd=target)
    run(["git", "commit", "-m", "smart-apply-smoke-baseline"], cwd=target)

    no_report = run([sys.executable, "scripts/archive-changes.py", "--smart-apply", "--confirm"], cwd=target, check=False)
    if no_report.returncode == 0 or "requires --report" not in (no_report.stdout + no_report.stderr):
        fail("smart archive apply without --report must refuse")

    no_confirm = run([
        sys.executable,
        "scripts/archive-changes.py",
        "--smart-apply",
        "--report",
        ".forgekit/smart-archive-report.md",
    ], cwd=target, check=False)
    if no_confirm.returncode == 0 or "requires --confirm" not in (no_confirm.stdout + no_confirm.stderr):
        fail("smart archive apply without --confirm must refuse")
    if not (target / ".forgekit" / "changes" / "20260101-done-medium").is_dir():
        fail("smart archive apply without confirm must not move candidates")

    (target / "README.md").write_bytes(before_readme + b"\n")
    dirty = run([
        sys.executable,
        "scripts/archive-changes.py",
        "--smart-apply",
        "--report",
        ".forgekit/smart-archive-report.md",
        "--confirm",
    ], cwd=target, check=False)
    if dirty.returncode == 0 or "working tree must be clean" not in (dirty.stdout + dirty.stderr):
        fail("smart archive apply with dirty git status must refuse")
    (target / "README.md").write_bytes(before_readme)
    if not (target / ".forgekit" / "changes" / "20260101-done-medium").is_dir():
        fail("dirty smart archive apply must not move candidates")

    run([
        sys.executable,
        "scripts/archive-changes.py",
        "--smart-apply",
        "--report",
        ".forgekit/smart-archive-report.md",
        "--confirm",
    ], cwd=target)
    moved_medium = target / ".forgekit" / "archive" / "changes" / "2026" / "20260101-done-medium"
    if not moved_medium.is_dir():
        fail("smart archive apply must move auto_archive_candidate changes")
    if (target / ".forgekit" / "changes" / "20260101-done-medium").exists():
        fail("smart archive apply must remove auto_archive_candidate source directory")
    for not_moved in [
        "20260105-done-high",
        "20260106-current-ref",
        "20260107-manual-ref",
        "20260110-missing-sync-safe",
        "20260102-blocked-high",
    ]:
        if not (target / ".forgekit" / "changes" / not_moved).is_dir():
            fail(f"smart archive apply must not move manual/blocked/non-smart change: {not_moved}")
    if "Status: archived" not in (moved_medium / "proposal.md").read_text(encoding="utf-8"):
        fail("smart archive apply must update moved proposal status to archived")
    apply_report_path = target / ".forgekit" / "smart-archive-apply-report.md"
    if not apply_report_path.is_file():
        fail("smart archive apply must write .forgekit/smart-archive-apply-report.md")
    apply_report = apply_report_path.read_text(encoding="utf-8")
    for text in [
        "Mode: smart-apply",
        "Smart report path: .forgekit/smart-archive-report.md",
        "Applied Smart-Status: auto_archive_candidate entries only.",
        "20260101-done-medium",
        "blocked_by_current_docs_reference: 1",
        "blocked_by_active_reference: 1",
        "blocked_by_missing_sync: 1",
    ]:
        if text not in apply_report:
            fail(f"smart archive apply report missing expected text: {text}")

    if before_lock != (target / ".forgekit" / "template-lock.json").read_bytes():
        fail("smart archive apply must not update template-lock.json")
    if before_readme != (target / "README.md").read_bytes():
        fail("smart archive apply must not update README.md")
    if before_agents != (target / "AGENTS.md").read_bytes():
        fail("smart archive apply must not update AGENTS.md")
    if before_claude != (target / "CLAUDE.md").read_bytes():
        fail("smart archive apply must not update CLAUDE.md")
    if before_business != business_note.read_bytes():
        fail("smart archive apply must not write business docs")
    if before_plan != plan_path.read_bytes():
        fail("smart archive apply must not update archive-plan.md")
    if before_reference != reference_report_path.read_bytes():
        fail("smart archive apply must not update archive-reference-report.md")
    if before_sync != sync_report_path.read_bytes():
        fail("smart archive apply must not update current-docs-sync-report.md")
    if before_smart != smart_report_path.read_bytes():
        fail("smart archive apply must not update smart-archive-report.md")
    for relative, content in docs_hashes.items():
        if content != (target / relative).read_bytes():
            fail(f"smart archive apply must not modify current docs: {relative}")


def assert_archive_flow(target):
    before_lock = (target / ".forgekit" / "template-lock.json").read_bytes()
    before_readme = (target / "README.md").read_bytes()
    before_agents = (target / "AGENTS.md").read_bytes()
    before_claude = (target / "CLAUDE.md").read_bytes()
    business_docs = target / "docs"
    business_docs.mkdir(exist_ok=True)
    business_note = business_docs / "business.md"
    business_note.write_text("# Business Docs\n", encoding="utf-8")
    before_business = business_note.read_bytes()

    write_change(
        target,
        "20260101-done-medium",
        "Status: done\nRisk: medium\nCreated: 2026-01-01\nOwner: smoke\nReason: smoke candidate\n\n# Proposal\n",
        ["tasks.md", "verification.md", "review.md"],
    )
    write_change(
        target,
        "20260102-blocked-high",
        "Status: done\nRisk: high\nCreated: 2026-01-02\nOwner: smoke\nReason: smoke blocked\n\n# Proposal\n",
        ["tasks.md", "verification.md", "review.md"],
    )
    write_change(
        target,
        "20260103-active",
        "Status: active\nRisk: medium\nCreated: 2026-01-03\nOwner: smoke\nReason: smoke active\n\n# Proposal\n\nReferences 20260105-done-high.\n",
        ["tasks.md", "verification.md", "review.md"],
    )
    write_change(
        target,
        "20260104-archived",
        "Status: archived\nRisk: medium\nOwner: smoke\nReason: smoke archived\n\n# Proposal\n",
        ["tasks.md", "verification.md", "review.md"],
    )
    write_change(
        target,
        "20260105-done-high",
        "Status: done\nRisk: high\nCreated: 2026-01-05\nOwner: smoke\nReason: smoke high\n\n# Proposal\n",
        ["design.md", "tasks.md", "verification.md", "review.md", "ship.md"],
    )
    write_change(
        target,
        "20260106-current-ref",
        "Status: done\nRisk: medium\nCreated: 2026-01-06\nOwner: smoke\nReason: smoke current ref\n\n# Proposal\n",
        ["tasks.md", "verification.md", "review.md"],
    )
    write_change(
        target,
        "20260107-manual-ref",
        "Status: done\nRisk: medium\nCreated: 2026-01-07\nOwner: smoke\nReason: smoke manual ref\n\n# Proposal\n",
        ["tasks.md", "verification.md", "review.md"],
    )
    write_change(
        target,
        "20260110-missing-sync-safe",
        "Status: done\nRisk: medium\nCreated: 2026-01-10\nOwner: smoke\nReason: smoke missing sync safe reference\n\n# Proposal\n",
        ["tasks.md", "verification.md", "review.md"],
    )
    with (target / ".forgekit" / "docs" / "project-plan.md").open("a", encoding="utf-8") as handle:
        handle.write("\nReference check smoke mentions 20260106-current-ref.\n")
    with (target / "README.md").open("a", encoding="utf-8") as handle:
        handle.write("\nReference check smoke mentions 20260107-manual-ref.\n")

    before_readme = (target / "README.md").read_bytes()
    before_agents = (target / "AGENTS.md").read_bytes()
    before_claude = (target / "CLAUDE.md").read_bytes()
    docs_hashes = {path.relative_to(target).as_posix(): path.read_bytes() for path in (target / ".forgekit" / "docs").rglob("*") if path.is_file()}

    run(["git", "init"], cwd=target)
    run(["git", "config", "user.email", "smoke@example.invalid"], cwd=target)
    run(["git", "config", "user.name", "ForgeKit Smoke"], cwd=target)
    run(["git", "add", "."], cwd=target)
    run(["git", "commit", "-m", "baseline"], cwd=target)

    run([sys.executable, "scripts/archive-changes.py", "--dry-run"], cwd=target)
    plan_path = target / ".forgekit" / "archive-plan.md"
    if not plan_path.is_file():
        fail("archive dry-run must create .forgekit/archive-plan.md")
    plan = plan_path.read_text(encoding="utf-8")
    required_text = [
        "Mode: dry-run",
        "This dry-run only creates or overwrites `.forgekit/archive-plan.md`.",
        "It does not move files",
        "Archive-Status: candidate",
        "From: .forgekit/changes/20260101-done-medium",
        "To: .forgekit/archive/changes/2026/20260101-done-medium",
        "## Candidates",
        "### 20260101-done-medium",
        "Target archive path: `.forgekit/archive/changes/2026/20260101-done-medium`",
        "Required file check: ok",
        "### 20260105-done-high",
        "Current docs sync: not verified by script",
        "## Blocked",
        "### 20260102-blocked-high",
        "missing design.md, ship.md",
        "## Skipped",
        "### 20260103-active",
        "Skip reason: status is active",
        "### 20260104-archived",
        "Skip reason: already archived by status",
        "Created: missing and fallback year used",
    ]
    missing = [item for item in required_text if item not in plan]
    if missing:
        fail("archive plan missing expected text:\n" + "\n".join(missing))

    if not (target / ".forgekit" / "changes" / "20260101-done-medium").is_dir():
        fail("archive dry-run must not move change directories")
    if before_lock != (target / ".forgekit" / "template-lock.json").read_bytes():
        fail("archive dry-run must not update template-lock.json")
    if before_business != business_note.read_bytes():
        fail("archive dry-run must not write business docs")

    with plan_path.open("a", encoding="utf-8") as handle:
        handle.write("\n## Missing Field Smoke\n\n### 20260108-missing-field\n\nArchive-Status: candidate\nRisk: medium\nStatus: done\n")
    run([sys.executable, "scripts/archive-changes.py", "--reference-check", "--plan", ".forgekit/archive-plan.md"], cwd=target)
    reference_report_path = target / ".forgekit" / "archive-reference-report.md"
    if not reference_report_path.is_file():
        fail("archive reference check must create .forgekit/archive-reference-report.md")
    reference_report = reference_report_path.read_text(encoding="utf-8")
    reference_required = [
        "Reference-Status: safe_no_references",
        "Change: 20260101-done-medium",
        "Reference-Status: referenced_by_current_docs",
        "Change: 20260106-current-ref",
        ".forgekit/docs/project-plan.md",
        "Reference-Status: referenced_by_active_change",
        "Change: 20260105-done-high",
        ".forgekit/changes/20260103-active/proposal.md",
        "Reference-Status: manual_review_needed",
        "Change: 20260107-manual-ref",
        "README.md",
        "Change: 20260108-missing-field",
        "Missing-Fields:",
    ]
    missing_reference_text = [item for item in reference_required if item not in reference_report]
    if missing_reference_text:
        fail("archive reference report missing expected text:\n" + "\n".join(missing_reference_text))
    if not (target / ".forgekit" / "changes" / "20260101-done-medium").is_dir():
        fail("archive reference check must not move candidates")

    (target / ".forgekit" / "changes" / "20260101-done-medium" / "review.md").write_text(
        "# review.md\n\nCurrentDocsSync: confirmed\nChangelogUpdated: yes\nArchitectureUpdated: not-needed\nTestingUpdated: yes\nRequirementsUpdated: not-needed\n",
        encoding="utf-8",
    )
    (target / ".forgekit" / "changes" / "20260106-current-ref" / "review.md").write_text(
        "# review.md\n\nCurrentDocsSync: not needed\nChangelogUpdated: not-needed\nArchitectureUpdated: not-needed\nTestingUpdated: not-needed\nRequirementsUpdated: not-needed\n",
        encoding="utf-8",
    )
    (target / ".forgekit" / "changes" / "20260107-manual-ref" / "review.md").write_text(
        "# review.md\n\nChangelogUpdated: no\nArchitectureUpdated: unknown\nTestingUpdated: unknown\nRequirementsUpdated: unknown\n",
        encoding="utf-8",
    )
    (target / ".forgekit" / "changes" / "20260105-done-high" / "review.md").write_text(
        "# review.md\n\nCurrentDocsSync: missing\nChangelogUpdated: unknown\nArchitectureUpdated: yes\nTestingUpdated: yes\nRequirementsUpdated: not-needed\n",
        encoding="utf-8",
    )
    (target / ".forgekit" / "changes" / "20260110-missing-sync-safe" / "review.md").write_text(
        "# review.md\n\nCurrentDocsSync: missing\nChangelogUpdated: yes\nArchitectureUpdated: not-needed\nTestingUpdated: yes\nRequirementsUpdated: not-needed\n",
        encoding="utf-8",
    )
    missing_review_dir = target / ".forgekit" / "changes" / "20260109-plan-missing-review"
    missing_review_dir.mkdir(parents=True, exist_ok=True)
    (missing_review_dir / "proposal.md").write_text(
        "Status: done\nRisk: medium\nCreated: 2026-01-09\nOwner: smoke\nReason: sync check missing review smoke\n",
        encoding="utf-8",
    )
    (missing_review_dir / "tasks.md").write_text("# tasks.md\n", encoding="utf-8")
    (missing_review_dir / "verification.md").write_text("# verification.md\n", encoding="utf-8")
    with plan_path.open("a", encoding="utf-8") as handle:
        handle.write(
            "\n## Sync Missing Review Smoke\n\n"
            "### 20260109-plan-missing-review\n\n"
            "Archive-Status: candidate\n"
            "From: .forgekit/changes/20260109-plan-missing-review\n"
            "To: .forgekit/archive/changes/2026/20260109-plan-missing-review\n"
            "Risk: medium\n"
            "Status: done\n"
        )
    before_sync_plan = plan_path.read_bytes()
    before_sync_lock = (target / ".forgekit" / "template-lock.json").read_bytes()
    before_sync_business = business_note.read_bytes()
    before_sync_docs = {path.relative_to(target).as_posix(): path.read_bytes() for path in (target / ".forgekit" / "docs").rglob("*") if path.is_file()}
    run([sys.executable, "scripts/archive-changes.py", "--sync-check", "--plan", ".forgekit/archive-plan.md"], cwd=target)
    sync_report_path = target / ".forgekit" / "current-docs-sync-report.md"
    if not sync_report_path.is_file():
        fail("current docs sync check must create .forgekit/current-docs-sync-report.md")
    sync_report = sync_report_path.read_text(encoding="utf-8")
    sync_required = [
        "Mode: sync-check",
        "Status: report-only",
        "Sync-Status: sync_confirmed",
        "Change: 20260101-done-medium",
        "CurrentDocsSync: confirmed",
        "Sync-Status: sync_not_needed",
        "Change: 20260106-current-ref",
        "CurrentDocsSync: not-needed",
        "Sync-Status: missing_sync_metadata",
        "Change: 20260107-manual-ref",
        "ChangelogUpdated is no",
        "Sync-Status: missing_required_docs",
        "Change: 20260105-done-high",
        "CurrentDocsSync: missing",
        "Change: 20260110-missing-sync-safe",
        "Sync-Status: manual_review_needed",
        "Change: 20260109-plan-missing-review",
        "review.md missing",
    ]
    missing_sync_text = [item for item in sync_required if item not in sync_report]
    if missing_sync_text:
        fail("current docs sync report missing expected text:\n" + "\n".join(missing_sync_text))
    if before_sync_plan != plan_path.read_bytes():
        fail("current docs sync check must not update archive-plan.md")
    if before_sync_lock != (target / ".forgekit" / "template-lock.json").read_bytes():
        fail("current docs sync check must not update template-lock.json")
    if before_sync_business != business_note.read_bytes():
        fail("current docs sync check must not write business docs")
    for relative, content in before_sync_docs.items():
        if content != (target / relative).read_bytes():
            fail(f"current docs sync check must not modify current docs: {relative}")
    if not (target / ".forgekit" / "changes" / "20260101-done-medium").is_dir():
        fail("current docs sync check must not move candidates")

    before_smart_plan = plan_path.read_bytes()
    before_smart_reference = reference_report_path.read_bytes()
    before_smart_sync = sync_report_path.read_bytes()
    before_smart_lock = (target / ".forgekit" / "template-lock.json").read_bytes()
    before_smart_business = business_note.read_bytes()
    before_smart_docs = {path.relative_to(target).as_posix(): path.read_bytes() for path in (target / ".forgekit" / "docs").rglob("*") if path.is_file()}
    run([
        sys.executable,
        "scripts/archive-changes.py",
        "--smart-check",
        "--plan",
        ".forgekit/archive-plan.md",
        "--reference-report",
        ".forgekit/archive-reference-report.md",
        "--sync-report",
        ".forgekit/current-docs-sync-report.md",
    ], cwd=target)
    smart_report_path = target / ".forgekit" / "smart-archive-report.md"
    if not smart_report_path.is_file():
        fail("smart archive check must create .forgekit/smart-archive-report.md")
    smart_report = smart_report_path.read_text(encoding="utf-8")
    smart_required = [
        "Mode: smart-check",
        "Status: report-only",
        "Smart-Status: auto_archive_candidate",
        "Change: 20260101-done-medium",
        "Reference-Status: safe_no_references",
        "Sync-Status: sync_confirmed",
        "Smart-Status: blocked_by_current_docs_reference",
        "Change: 20260106-current-ref",
        "Smart-Status: blocked_by_active_reference",
        "Change: 20260105-done-high",
        "Smart-Status: manual_review_required",
        "Change: 20260107-manual-ref",
        "Smart-Status: blocked_by_missing_sync",
        "Change: 20260110-missing-sync-safe",
    ]
    missing_smart_text = [item for item in smart_required if item not in smart_report]
    if missing_smart_text:
        fail("smart archive report missing expected text:\n" + "\n".join(missing_smart_text))
    if before_smart_plan != plan_path.read_bytes():
        fail("smart archive check must not update archive-plan.md")
    if before_smart_reference != reference_report_path.read_bytes():
        fail("smart archive check must not update archive-reference-report.md")
    if before_smart_sync != sync_report_path.read_bytes():
        fail("smart archive check must not update current-docs-sync-report.md")
    if before_smart_lock != (target / ".forgekit" / "template-lock.json").read_bytes():
        fail("smart archive check must not update template-lock.json")
    if before_smart_business != business_note.read_bytes():
        fail("smart archive check must not write business docs")
    for relative, content in before_smart_docs.items():
        if content != (target / relative).read_bytes():
            fail(f"smart archive check must not modify current docs: {relative}")
    if not (target / ".forgekit" / "changes" / "20260101-done-medium").is_dir():
        fail("smart archive check must not move candidates")

    assert_smart_apply_flow(target)

    sync_report_path.unlink()
    run([
        sys.executable,
        "scripts/archive-changes.py",
        "--smart-check",
        "--plan",
        ".forgekit/archive-plan.md",
        "--reference-report",
        ".forgekit/archive-reference-report.md",
        "--sync-report",
        ".forgekit/current-docs-sync-report.md",
    ], cwd=target)
    smart_missing_report = smart_report_path.read_text(encoding="utf-8")
    if "Smart-Status: blocked_by_missing_report" not in smart_missing_report or "missing report:" not in smart_missing_report:
        fail("smart archive check must classify missing reports as blocked_by_missing_report")
    smart_report_path.unlink()
    reference_report_path.unlink()
    run([sys.executable, "scripts/archive-changes.py", "--dry-run"], cwd=target)
    run(["git", "add", "."], cwd=target)
    run(["git", "commit", "-m", "sync-check-smoke-baseline"], cwd=target)

    no_confirm = run([sys.executable, "scripts/archive-changes.py", "--apply", "--plan", ".forgekit/archive-plan.md"], cwd=target, check=False)
    if no_confirm.returncode == 0 or "requires --confirm" not in (no_confirm.stdout + no_confirm.stderr):
        fail("archive apply without --confirm must refuse")
    if not (target / ".forgekit" / "changes" / "20260101-done-medium").is_dir():
        fail("archive apply without confirm must not move candidates")

    (target / "README.md").write_bytes(before_readme + b"\n")
    dirty = run([sys.executable, "scripts/archive-changes.py", "--apply", "--plan", ".forgekit/archive-plan.md", "--confirm"], cwd=target, check=False)
    if dirty.returncode == 0 or "working tree must be clean" not in (dirty.stdout + dirty.stderr):
        fail("archive apply with dirty git status must refuse")
    (target / "README.md").write_bytes(before_readme)
    if not (target / ".forgekit" / "changes" / "20260105-done-high").is_dir():
        fail("dirty archive apply must not move candidates")

    run([sys.executable, "scripts/archive-changes.py", "--apply", "--plan", ".forgekit/archive-plan.md", "--confirm"], cwd=target)
    moved_medium = target / ".forgekit" / "archive" / "changes" / "2026" / "20260101-done-medium"
    moved_high = target / ".forgekit" / "archive" / "changes" / "2026" / "20260105-done-high"
    if not moved_medium.is_dir() or not moved_high.is_dir():
        fail("archive apply must move candidate changes")
    if (target / ".forgekit" / "changes" / "20260101-done-medium").exists() or (target / ".forgekit" / "changes" / "20260105-done-high").exists():
        fail("archive apply must remove candidate source directories")
    for still_active in ["20260102-blocked-high", "20260103-active", "20260104-archived"]:
        if not (target / ".forgekit" / "changes" / still_active).is_dir():
            fail(f"archive apply must not move blocked/skipped change: {still_active}")
    if "Status: archived" not in (moved_medium / "proposal.md").read_text(encoding="utf-8"):
        fail("archive apply must update moved proposal status to archived")
    report_path = target / ".forgekit" / "archive-apply-report.md"
    if not report_path.is_file():
        fail("archive apply must write .forgekit/archive-apply-report.md")
    report = report_path.read_text(encoding="utf-8")
    for text in [
        "Status: applied",
        "No current docs modified.",
        "No business docs modified.",
        "No lock updated.",
        "No commit created.",
        "20260101-done-medium",
        "20260105-done-high",
    ]:
        if text not in report:
            fail(f"archive apply report missing expected text: {text}")

    if before_lock != (target / ".forgekit" / "template-lock.json").read_bytes():
        fail("archive apply must not update template-lock.json")
    if before_readme != (target / "README.md").read_bytes():
        fail("archive apply must not update README.md")
    if before_agents != (target / "AGENTS.md").read_bytes():
        fail("archive apply must not update AGENTS.md")
    if before_claude != (target / "CLAUDE.md").read_bytes():
        fail("archive apply must not update CLAUDE.md")
    if before_business != business_note.read_bytes():
        fail("archive apply must not write business docs")
    for relative, content in docs_hashes.items():
        if content != (target / relative).read_bytes():
            fail(f"archive apply must not modify current docs: {relative}")


def assert_legacy_upgrade_no_lock(repo, target):
    target.mkdir(parents=True, exist_ok=True)
    (target / ".forgekit").mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        run([
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(repo / "scripts" / "upgrade-forgekit.ps1"),
            "-ProjectPath",
            str(target),
        ], cwd=repo)
    else:
        run([
            "bash",
            str(repo / "scripts" / "upgrade-forgekit.sh"),
            "--project-path",
            str(target),
        ], cwd=repo)
    report = target / ".forgekit" / "upgrade" / "upgrade-plan.md"
    legacy = target / ".forgekit" / "upgrade" / "legacy-inventory.md"
    if not report.is_file() or not legacy.is_file():
        fail("legacy guided upgrade must write upgrade-plan.md and legacy-inventory.md")
    if (target / ".forgekit" / "template-lock.json").exists():
        fail("legacy guided upgrade must not create template-lock.json")
    if "legacy_needs_inventory" not in report.read_text(encoding="utf-8"):
        fail("legacy guided upgrade report must mention legacy_needs_inventory")
    if "does not have `.forgekit/template-lock.json`" not in legacy.read_text(encoding="utf-8"):
        fail("legacy inventory must explain missing lock")


def assert_skill_frontmatter(root):
    skill_files = list(root.rglob("SKILL.md"))
    if not skill_files:
        fail("No SKILL.md files found")
    bad = []
    for path in skill_files:
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) < 4 or lines[0] != "---":
            bad.append(f"{path}: missing frontmatter")
            continue
        if not any(line.startswith("name: ") for line in lines[:10]):
            bad.append(f"{path}: missing name")
        if not any(line.startswith("description: ") for line in lines[:10]):
            bad.append(f"{path}: missing description")
    if bad:
        fail("Invalid skill frontmatter:\n" + "\n".join(bad))


def init_project(repo, target):
    if os.name == "nt":
        run([
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(repo / "scripts" / "init-project-template.ps1"),
            "-TargetPath",
            str(target),
            "-ProjectName",
            "forgekit-smoke",
            "-Mode",
            "Standard",
        ], cwd=repo)
    else:
        run([
            "bash",
            str(repo / "scripts" / "init-project-template.sh"),
            "--target-path",
            str(target),
            "--project-name",
            "forgekit-smoke",
            "--mode",
            "Standard",
        ], cwd=repo)


def run_generated_checks(target):
    if os.name == "nt":
        run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ".\\scripts\\run-harness-check.ps1"], cwd=target)
        run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ".\\scripts\\check-doc-sync.ps1"], cwd=target)
    else:
        run(["bash", "./scripts/check-doc-sync.sh"], cwd=target)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--keep-temp", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve()
    assert_paths(repo, REQUIRED_REPO_PATHS)
    assert_no_escaped_filenames(repo)
    assert_no_noise_files(repo / "project-template")
    assert_no_forbidden_text(repo, FORBIDDEN_LEGACY_REFS, "Forbidden legacy path text found", LEGACY_REF_ALLOWLIST)
    assert_no_forbidden_text(repo / "templates", FORBIDDEN_PRIVATE_PATHS, "Private machine paths found in templates")
    assert_json(repo / ".codex-plugin" / "plugin.json")
    assert_json(repo / ".claude-plugin" / "plugin.json")
    assert_json(repo / "project-template" / ".forgekit" / "template-manifest.json")
    assert_loop_docs(repo / "project-template", "docs/loop-readiness.md", "docs/loop-blueprint.md")
    assert_loop_operations(
        repo / "project-template",
        "docs/loop-operations.md",
        "docs/loop-blueprint.md",
        "AGENTS.md",
        "CLAUDE.md",
        ".codex/rules.md",
    )
    assert_maker_checker_protocol(
        repo / "project-template",
        "docs/maker-checker-protocol.md",
        "changes/_template/review.md",
        "AGENTS.md",
        "CLAUDE.md",
        ".codex/rules.md",
    )
    assert_worktree_playbook(
        repo / "project-template",
        "docs/worktree-playbook.md",
        "docs/loop-blueprint.md",
        "docs/maker-checker-protocol.md",
        "AGENTS.md",
        "CLAUDE.md",
        ".codex/rules.md",
    )
    assert_native_agent_adapter(repo, repo / "project-template", "docs/native-agent-adapter.md")
    assert_task_intake(
        repo / "project-template",
        "docs/task-intake.md",
        "docs/task-board.md",
        "docs/requirements.md",
        "docs/changelog.md",
        "AGENTS.md",
        "CLAUDE.md",
        ".codex/rules.md",
    )
    assert_managed_docs_responsibility_v2(
        repo / "project-template",
        ".forgekit/docs/document-responsibility.md",
        "docs/codebase-map.md",
        "AGENTS.md",
        "CLAUDE.md",
        ".codex/rules.md",
    )
    assert_absent_paths(repo, [
        "scripts/maker-checker-runner.py",
        "scripts/checker-runner.py",
        "project-template/scripts/maker-checker-runner.py",
        "project-template/scripts/checker-runner.py",
        "scripts/loop-runner.py",
        "project-template/scripts/loop-runner.py",
        "scripts/loop-daemon.py",
        "project-template/scripts/loop-daemon.py",
        "scripts/loop-scheduler.py",
        "project-template/scripts/loop-scheduler.py",
        "scripts/worktree-runner.py",
        "project-template/scripts/worktree-runner.py",
        "scripts/worktree-scheduler.py",
        "project-template/scripts/worktree-scheduler.py",
        "scripts/worktree-agent.py",
        "project-template/scripts/worktree-agent.py",
        "project-template/.codex/agents/maker.md",
        "project-template/.codex/agents/checker.md",
        "project-template/.codex/agents/loop-runner.md",
        "project-template/.codex/agents/worktree-runner.md",
    ])
    run([sys.executable, str(repo / "scripts" / "update-template-manifest.py"), "--check"], cwd=repo)
    assert_skill_frontmatter(repo / "skills")
    assert_skill_frontmatter(repo / "project-template" / ".agents" / "skills")

    temp_parent = Path(tempfile.mkdtemp(prefix="forgekit-smoke-"))
    target = temp_parent / "generated"
    try:
        init_project(repo, target)
        assert_paths(target, REQUIRED_GENERATED_PATHS)
        assert_absent_paths(target, [
            "docs/codebase-map.md",
            "docs/local-toolchain.md",
            "docs/changelog.md",
            "changes/README.md",
            ".forgekit/template-manifest.json",
            "archive",
        ])
        assert_boundary_config(target / ".forgekit" / "project-boundary.yml")
        assert_loop_docs(target, ".forgekit/docs/loop-readiness.md", ".forgekit/docs/loop-blueprint.md")
        assert_loop_operations(
            target,
            ".forgekit/docs/loop-operations.md",
            ".forgekit/docs/loop-blueprint.md",
            "AGENTS.md",
            "CLAUDE.md",
            ".codex/rules.md",
        )
        assert_maker_checker_protocol(
            target,
            ".forgekit/docs/maker-checker-protocol.md",
            ".forgekit/changes/_template/review.md",
            "AGENTS.md",
            "CLAUDE.md",
            ".codex/rules.md",
        )
        assert_worktree_playbook(
            target,
            ".forgekit/docs/worktree-playbook.md",
            ".forgekit/docs/loop-blueprint.md",
            ".forgekit/docs/maker-checker-protocol.md",
            "AGENTS.md",
            "CLAUDE.md",
            ".codex/rules.md",
        )
        assert_native_agent_adapter(repo, target, ".forgekit/docs/native-agent-adapter.md")
        assert_codex_native_agents(target)
        assert_task_intake(
            target,
            ".forgekit/docs/task-intake.md",
            ".forgekit/docs/task-board.md",
            ".forgekit/docs/requirements.md",
            ".forgekit/docs/changelog.md",
            "AGENTS.md",
            "CLAUDE.md",
            ".codex/rules.md",
        )
        assert_managed_docs_responsibility_v2(
            target,
            ".forgekit/docs/document-responsibility.md",
            ".forgekit/docs/codebase-map.md",
            "AGENTS.md",
            "CLAUDE.md",
            ".codex/rules.md",
        )
        assert_absent_paths(target, [
            "scripts/maker-checker-runner.py",
            "scripts/checker-runner.py",
            "scripts/loop-runner.py",
            "scripts/loop-daemon.py",
            "scripts/loop-scheduler.py",
            "scripts/worktree-runner.py",
            "scripts/worktree-scheduler.py",
            "scripts/worktree-agent.py",
            ".codex/agents/maker.md",
            ".codex/agents/checker.md",
            ".codex/agents/loop-runner.md",
            ".codex/agents/worktree-runner.md",
        ])
        assert_manifest_lock(target)
        assert_no_escaped_filenames(target)
        assert_no_noise_files(target)
        assert_no_forbidden_text(target, FORBIDDEN_LEGACY_REFS, "Forbidden legacy path text found in generated project")
        run_generated_checks(target)
        assert_archive_flow(target)
        assert_guided_upgrade(repo, target)
        assert_upgrade_report(repo, target)
        run_generated_checks(target)
        assert_legacy_upgrade_no_lock(repo, temp_parent / "legacy")
    finally:
        if args.keep_temp:
            print(f"[info] temp kept: {temp_parent}")
        else:
            shutil.rmtree(temp_parent, ignore_errors=True)

    print("[ok] Smoke test passed")


if __name__ == "__main__":
    main()
