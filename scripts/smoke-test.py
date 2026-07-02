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
import tomllib
import types
from pathlib import Path

sys.dont_write_bytecode = True


LEGACY_NAME_RE = re.compile(r"#U[0-9a-fA-F]{4}")
FORBIDDEN_LEGACY_REFS = [
    "docs/代码库地图.md",
    "docs/本地工具链检查.md",
    "docs/版本路线图.md",
    "docs/版本更新记录.md",
    "使用说明.html",
]
LEGACY_REF_ALLOWLIST = {
    Path("CHANGELOG.md"),
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
    "project-template/.forgekit/state.json",
    "project-template/.forgekit/workspace-map.json",
    "project-template/.forgekit/docs/scoped-docs.md",
    "project-template/.forgekit/docs/work-session-checkpoint.md",
    "project-template/.forgekit/docs/usage-playbook.md",
    "project-template/.forgekit/projects/_template/project-card.md",
    "project-template/.forgekit/projects/_template/source-links.md",
    "project-template/migrations/0.36.0/migration.json",
    "project-template/scripts/forgekit-upgrade.py",
    "migrations/0.36.0/migration.json",
    "scripts/forgekit-upgrade.py",
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
    "project-template/docs/workflow-router.md",
    "project-template/docs/work-log.md",
    "project-template/docs/task-intake.md",
    "project-template/docs/local-toolchain.md",
    "project-template/docs/loop-readiness.md",
    "project-template/docs/loop-blueprint.md",
    "project-template/docs/loop-operations.md",
    "project-template/docs/bounded-auto-loop-policy.md",
    "project-template/docs/context-continuity.md",
    "project-template/docs/project-maintenance.md",
    "project-template/docs/archive-capsule.md",
    "project-template/docs/current-docs-integrity.md",
    "project-template/docs/reasoning-review.md",
    "project-template/docs/maker-checker-protocol.md",
    "project-template/docs/native-agent-adapter.md",
    "project-template/docs/worktree-playbook.md",
    "project-template/docs/version-roadmap.md",
    "project-template/.codex/config.toml",
    "project-template/.codex/agents/forgekit-planner.toml",
    "project-template/.codex/agents/forgekit-reviewer.toml",
    "project-template/.codex/agents/forgekit-verifier.toml",
    "project-template/.codex/agents/forgekit-code-reviewer.toml",
    "project-template/.claude/agents/forgekit-code-reviewer.md",
    "project-template/.claude/skills/forgekit-request-code-review/SKILL.md",
    "project-template/.claude/skills/forgekit-code-review/SKILL.md",
    "project-template/.claude/skills/forgekit-code-review/references/universal-review.md",
    "project-template/.claude/skills/forgekit-code-review/references/security-review.md",
    "project-template/.claude/skills/forgekit-code-review/references/testing-review.md",
    "project-template/.claude/skills/forgekit-maintenance/SKILL.md",
    "project-template/.claude/skills/forgekit-first-principles/SKILL.md",
    "project-template/.claude/skills/forgekit-adversarial-review/SKILL.md",
    "project-template/migrations/0.37.0/migration.json",
    "project-template/migrations/0.38.0/migration.json",
    "project-template/migrations/0.39.0/migration.json",
    "project-template/migrations/0.40.0/migration.json",
    "project-template/migrations/0.40.1/migration.json",
    "project-template/migrations/0.40.2/migration.json",
    "project-template/migrations/0.41.0/migration.json",
    "project-template/migrations/0.41.1/migration.json",
    "project-template/migrations/0.42.0/migration.json",
    "project-template/migrations/0.43.0/migration.json",
    "migrations/0.37.0/migration.json",
    "migrations/0.38.0/migration.json",
    "migrations/0.39.0/migration.json",
    "migrations/0.40.0/migration.json",
    "migrations/0.40.1/migration.json",
    "migrations/0.40.2/migration.json",
    "migrations/0.41.0/migration.json",
    "migrations/0.41.1/migration.json",
    "migrations/0.42.0/migration.json",
    "migrations/0.43.0/migration.json",
    "project-template/scripts/check-codex-native-agents.py",
    "project-template/scripts/doc-health-report.py",
    "project-template/scripts/source-trace-report.py",
    "project-template/scripts/handoff-package.py",
    "project-template/scripts/archive-capsule.py",
    "project-template/scripts/check-current-docs-integrity.py",
    "project-template/scripts/check-workspace-integrity.py",
    "project-template/scripts/bootstrap-project-capsule.py",
    "scripts/check-codex-native-agents.py",
    "scripts/doc-health-report.py",
    "scripts/source-trace-report.py",
    "scripts/handoff-package.py",
    "scripts/archive-capsule.py",
    "scripts/check-current-docs-integrity.py",
    "scripts/check-workspace-integrity.py",
    "scripts/bootstrap-project-capsule.py",
    "scripts/forgekit-project.py",
    "scripts/forgekit-project.ps1",
    "scripts/forgekit-project.sh",
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
]
REQUIRED_GENERATED_PATHS = [
    "AGENTS.md",
    "CLAUDE.md",
    ".forgekit/project-boundary.yml",
    ".forgekit/template-lock.json",
    ".forgekit/state.json",
    ".forgekit/workspace-map.json",
    ".forgekit/docs/scoped-docs.md",
    ".forgekit/docs/work-session-checkpoint.md",
    ".forgekit/docs/usage-playbook.md",
    ".forgekit/projects/_template/project-card.md",
    ".forgekit/projects/_template/source-links.md",
    ".forgekit/projects/_template/task-board.md",
    ".forgekit/projects/_template/testing.md",
    ".forgekit/projects/_template/risk-register.md",
    ".forgekit/projects/_template/decisions/0001-example.md",
    ".forgekit/docs/document-responsibility.md",
    ".forgekit/docs/document-lifecycle.md",
    ".forgekit/archive/README.md",
    ".forgekit/archive/changes/README.md",
    ".forgekit/archive/releases/README.md",
    ".forgekit/docs/codebase-map.md",
    ".forgekit/docs/workflow-router.md",
    ".forgekit/docs/work-log.md",
    ".forgekit/docs/task-intake.md",
    ".forgekit/docs/local-toolchain.md",
    ".forgekit/docs/loop-readiness.md",
    ".forgekit/docs/loop-blueprint.md",
    ".forgekit/docs/loop-operations.md",
    ".forgekit/docs/bounded-auto-loop-policy.md",
    ".forgekit/docs/context-continuity.md",
    ".forgekit/docs/project-maintenance.md",
    ".forgekit/docs/archive-capsule.md",
    ".forgekit/docs/current-docs-integrity.md",
    ".forgekit/docs/reasoning-review.md",
    ".forgekit/docs/maker-checker-protocol.md",
    ".forgekit/docs/native-agent-adapter.md",
    ".forgekit/docs/worktree-playbook.md",
    ".forgekit/docs/version-roadmap.md",
    ".forgekit/docs/changelog.md",
    ".codex/config.toml",
    ".codex/agents/forgekit-planner.toml",
    ".codex/agents/forgekit-reviewer.toml",
    ".codex/agents/forgekit-verifier.toml",
    ".codex/agents/forgekit-code-reviewer.toml",
    ".claude/agents/forgekit-code-reviewer.md",
    ".claude/skills/forgekit-request-code-review/SKILL.md",
    ".claude/skills/forgekit-code-review/SKILL.md",
    ".claude/skills/forgekit-code-review/references/universal-review.md",
    ".claude/skills/forgekit-code-review/references/security-review.md",
    ".claude/skills/forgekit-code-review/references/testing-review.md",
    ".claude/skills/forgekit-maintenance/SKILL.md",
    ".claude/skills/forgekit-first-principles/SKILL.md",
    ".claude/skills/forgekit-adversarial-review/SKILL.md",
    "migrations/0.37.0/migration.json",
    "migrations/0.38.0/migration.json",
    "migrations/0.39.0/migration.json",
    "migrations/0.40.0/migration.json",
    "migrations/0.40.1/migration.json",
    "migrations/0.40.2/migration.json",
    "migrations/0.41.0/migration.json",
    "migrations/0.41.1/migration.json",
    "migrations/0.42.0/migration.json",
    "migrations/0.43.0/migration.json",
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
    "scripts/doc-health-report.py",
    "scripts/source-trace-report.py",
    "scripts/handoff-package.py",
    "scripts/archive-capsule.py",
    "scripts/check-current-docs-integrity.py",
    "scripts/check-workspace-integrity.py",
    "scripts/bootstrap-project-capsule.py",
    "scripts/forgekit-upgrade.py",
    "migrations/0.36.0/migration.json",
    "scripts/archive-changes.py",
]


def run(cmd, cwd, check=True, input_text=None, env_updates=None):
    environment = os.environ.copy()
    environment["GIT_CONFIG_GLOBAL"] = os.devnull
    environment["GIT_CONFIG_NOSYSTEM"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["HOME"] = str(Path(cwd).resolve())
    environment["XDG_CONFIG_HOME"] = str(Path(cwd).resolve() / ".config")
    if env_updates:
        environment.update(env_updates)
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=environment,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        input=input_text,
        shell=False,
    )
    if check and result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        raise SystemExit(f"Command failed ({result.returncode}): {' '.join(cmd)}")
    return result


def run_pty(cmd, cwd, input_text, check=True):
    if os.name == "nt":
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")
    import pty
    import select
    environment = os.environ.copy()
    environment["GIT_CONFIG_GLOBAL"] = os.devnull
    environment["GIT_CONFIG_NOSYSTEM"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPYCACHEPREFIX"] = str(Path(tempfile.gettempdir()) / "forgekit-pycache")
    environment["HOME"] = str(Path(cwd).resolve())
    environment["XDG_CONFIG_HOME"] = str(Path(cwd).resolve() / ".config")
    master, slave = pty.openpty()
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=environment,
        text=False,
        stdin=slave,
        stdout=slave,
        stderr=slave,
        close_fds=True,
    )
    os.close(slave)
    if input_text:
        os.write(master, input_text.encode("utf-8"))
    chunks = []
    while True:
        ready, _, _ = select.select([master], [], [], 0.2)
        if ready:
            try:
                chunk = os.read(master, 4096)
            except OSError:
                break
            if not chunk:
                break
            chunks.append(chunk)
        if process.poll() is not None:
            while True:
                ready, _, _ = select.select([master], [], [], 0)
                if not ready:
                    break
                try:
                    chunk = os.read(master, 4096)
                except OSError:
                    break
                if not chunk:
                    break
                chunks.append(chunk)
            break
    os.close(master)
    stdout = b"".join(chunks).decode("utf-8", errors="replace")
    result = types.SimpleNamespace(returncode=process.wait(), stdout=stdout, stderr="")
    if check and result.returncode != 0:
        print(result.stdout, end="")
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


def load_manifest_tool(repo):
    script = repo / "scripts" / "update-template-manifest.py"
    namespace = {"__name__": "forgekit_template_manifest", "__file__": str(script)}
    exec(compile(script.read_text(encoding="utf-8"), str(script), "exec"), namespace)
    return types.SimpleNamespace(sha256_file=namespace["sha256_file"])


def assert_manifest_checksum_stability(repo):
    tool = load_manifest_tool(repo)
    manifest = json.loads(
        (repo / "project-template/.forgekit/template-manifest.json").read_text(encoding="utf-8")
    )
    entries = {item["source_path"]: item for item in manifest["files"]}
    checked = ("AGENTS.md", "CLAUDE.md", ".codex/rules.md")

    with tempfile.TemporaryDirectory(prefix="forgekit-checksum-") as temp_dir:
        temp = Path(temp_dir)
        for source_path in checked:
            entry = entries.get(source_path)
            if entry is None or entry.get("render_mode") != "copy":
                fail(f"Manifest copy entry missing for checksum regression: {source_path}")
            source = repo / "project-template" / source_path
            text = source.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
            lf_path = temp / (source.name + ".lf")
            crlf_path = temp / (source.name + ".crlf")
            lf_path.write_bytes(text.encode("utf-8"))
            crlf_path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
            expected = entry["checksum"]
            if tool.sha256_file(source) != expected:
                fail(f"Manifest checksum does not match source: {source_path}")
            if tool.sha256_file(lf_path) != expected or tool.sha256_file(crlf_path) != expected:
                fail(f"Manifest checksum is not LF/CRLF stable: {source_path}")

    if ".forgekit/state.json" in entries:
        fail("Generated .forgekit/state.json must not be manifest-managed")


def assert_generated_entry_checksums(repo, target):
    tool = load_manifest_tool(repo)
    manifest = json.loads(
        (repo / "project-template/.forgekit/template-manifest.json").read_text(encoding="utf-8")
    )
    entries = {item["source_path"]: item for item in manifest["files"]}
    for source_path in ("AGENTS.md", "CLAUDE.md", ".codex/rules.md"):
        expected = entries[source_path]["checksum"]
        generated = target / source_path
        if tool.sha256_file(generated) != expected:
            fail(f"Generated file checksum mismatch: {source_path}")


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
        "LoopMode: one-step | bounded-auto | review-only",
        "AuthorizationScope:",
        "AgentModeRequired: native | fallback-allowed | any",
        "AllowedStages:",
        "MaxRounds:",
        "MaxStageCount:",
        "MaxFixAttempts:",
        "MaxFilesRead:",
        "MaxFilesChanged:",
        "MaxCommands:",
        "ForbiddenActions:",
        "StopConditions:",
        "CheckpointWriteback:",
        "FinalHandoffRequired: yes",
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
        "## Loop Bounded Auto",
        "## Loop Review Only",
        "## Loop Continue",
        "## Loop Stop / Handoff",
        "只读取 loop 蓝图",
        "不修改文件",
        "只执行一轮",
        "只继续下一轮",
        "不要启动另一轮 loop",
        "每一轮实际执行过的 loop 都必须回写",
        "AgentModeRequired",
        "bounded-auto",
        ".forgekit/docs/work-log.md",
        "agent_mode: native | fallback | simulated",
        "native_agent_status: available | unavailable | unverified",
        "fallback_reason",
    ]
    blueprint_required = [
        "OperationMode: dry-run | one-step | continue | stop-handoff",
        "LoopMode: one-step | bounded-auto | review-only",
        "AuthorizationScope:",
        "AgentModeRequired: native | fallback-allowed | any",
        "MaxRounds:",
        "MaxStageCount:",
        "MaxFixAttempts:",
        "MaxFilesRead:",
        "MaxFilesChanged:",
        "MaxCommands:",
        "RequiresUserConfirmation: yes",
        "WritebackTarget:",
        "StopOnUnclearScope: yes",
        "StopOnValidationFailure: yes",
    ]
    entry_required = [
        "Do not enter loop mode unless the user explicitly asks for loop dry-run, one-step, bounded-auto, review-only, continue, or stop/handoff.",
        "Before one-step or bounded-auto, restate scope",
        "Bounded-auto must stop",
        "Review-only must not modify files",
        "Loop continue must not run continuously",
        "Stop and escalate on unclear scope, budget overrun, validation failure, or forbidden path contact.",
        "Loop output must write back",
        "Generated native agent config is not proof of runtime registration.",
        "Bounded-auto or loop execution must record `agent_mode`",
        "Implementation Scope from Governance Writeback Scope",
        "ManagedDocsWriteback: minimal",
        "Review-only writes nothing, and report-only outputs never trigger automatic fixes.",
    ]
    rules_required = [
        "不得自行进入 loop mode",
        "bounded-auto、review-only",
        "one-step 或 bounded-auto 前必须复述",
        "bounded-auto 遇到范围不清",
        "loop continue 不得自动连续运行",
        "scope 不清、预算超限、验证失败或触及 forbidden paths",
        "loop 输出必须写回",
        "生成 native agent 配置不等于 runtime 已注册",
        "bounded-auto 或 loop 执行必须写明 `agent_mode`",
        "Implementation Scope` 与 `Governance Writeback Scope",
        "ManagedDocsWriteback: minimal",
        "`review-only` 不写，report-only 报告不得触发自动修复",
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

    policy = (root / operations_path).with_name("bounded-auto-loop-policy.md")
    policy_text = policy.read_text(encoding="utf-8")
    policy_required = [
        "LoopMode",
        "`one-step`",
        "`bounded-auto`",
        "`review-only`",
        "AuthorizationScope",
        "AgentModeRequired",
        "Stop Conditions",
        "Checkpoint Writeback",
        "Final Handoff",
        "ManagedDocsWriteback: off | minimal | full-review",
        "Implementation Scope",
        "Governance Writeback Scope",
        "只改这些业务文件",
        "`review-only` 绝不写文件",
        "report-only 脚本仍然只生成报告",
        "不是 runner、daemon、cron、scheduler、多 agent dispatcher、自动 PR 或 worktree orchestration",
    ]
    missing_policy = [item for item in policy_required if item not in policy_text]
    if missing_policy:
        fail("bounded-auto-loop-policy.md missing expected text:\n" + "\n".join(missing_policy))


def assert_native_agent_adapter(repo, root, adapter_path):
    adapter = (root / adapter_path).read_text(encoding="utf-8")
    skill = (repo / "native-adapters/claude-code/skills/forgekit-loop/SKILL.md").read_text(encoding="utf-8")
    adapter_required = [
        "native_agent_lifecycle: generated | installed | registered | invoked",
        "native_agent_status` 合法值只允许 `available | unavailable | unverified`",
        "只有 `invoked` 才能写成 native 真正可用",
        "子 agent 可以报告",
        "容量阻塞",
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
        "Keep native_agent_status limited to available, unavailable, or unverified.",
        "capacity blocked rather than native unavailable",
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
        "forgekit-code-reviewer": target / ".codex/agents/forgekit-code-reviewer.toml",
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
        "NativeAgentLifecycle: installed",
        "RuntimeRegistration: installed",
        "NativeAgentStatusAllowed: available | unavailable | unverified",
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

    malformed_agent = target / ".codex/agents/forgekit-planner.toml"
    original_agent = malformed_agent.read_text(encoding="utf-8")
    try:
        malformed_agent.write_text(
            'name = "forgekit-planner"\n'
            'description = "malformed schema smoke test"\n'
            "\n"
            "[developer_instructions]\n"
            'text = "this table must be rejected; Codex expects a string"\n',
            encoding="utf-8",
        )
        malformed = run([sys.executable, "scripts/check-codex-native-agents.py", "--repo-root", "."], cwd=target, check=False)
        combined = malformed.stdout + malformed.stderr
        if malformed.returncode == 0:
            fail("Codex native doctor must reject developer_instructions table schema")
        if "developer_instructions must be string" not in combined and "developer_instructions must be string" not in report.read_text(encoding="utf-8"):
            fail("Codex native doctor must report developer_instructions type errors")
    finally:
        malformed_agent.write_text(original_agent, encoding="utf-8")


def assert_doc_health_report(target):
    report_path = target / ".forgekit" / "doc-health-report.md"
    if report_path.exists():
        report_path.unlink()

    before_hashes = {}
    for rel_path in [
        ".forgekit/docs/task-board.md",
        ".forgekit/docs/work-log.md",
        ".forgekit/docs/changelog.md",
        ".forgekit/docs/testing.md",
        ".forgekit/docs/requirements.md",
    ]:
        path = target / rel_path
        if path.is_file():
            before_hashes[rel_path] = sha256_file(path)

    run([sys.executable, "scripts/doc-health-report.py", "--project-root", "."], cwd=target)
    if not report_path.is_file():
        fail("doc-health-report.py did not write .forgekit/doc-health-report.md")

    report = report_path.read_text(encoding="utf-8")
    required = [
        "Status: report-only",
        "Mode: doc-health",
        "## Summary",
        "## Findings by Severity",
        "## Findings by Document",
        "## Suggested Manual Fixes",
        "## Non-Goals",
        "No automatic doc slimming",
        "No runner, daemon, scheduler, auto PR, worktree automation, commit, tag, or push",
    ]
    missing = [item for item in required if item not in report]
    if missing:
        fail("doc-health-report.md missing expected content:\n" + "\n".join(missing))

    for rel_path, before in before_hashes.items():
        after = sha256_file(target / rel_path)
        if after != before:
            fail(f"doc-health-report.py must not modify managed doc: {rel_path}")


def assert_source_trace_report(target):
    report_path = target / ".forgekit" / "source-trace-report.md"
    if report_path.exists():
        report_path.unlink()

    before_hashes = {}
    for rel_path in [
        ".forgekit/docs/task-intake.md",
        ".forgekit/docs/requirements.md",
        ".forgekit/docs/task-board.md",
        ".forgekit/docs/work-log.md",
        ".forgekit/docs/changelog.md",
        ".forgekit/docs/testing.md",
    ]:
        path = target / rel_path
        if path.is_file():
            before_hashes[rel_path] = sha256_file(path)

    run([sys.executable, "scripts/source-trace-report.py", "--project-root", "."], cwd=target)
    if not report_path.is_file():
        fail("source-trace-report.py did not write .forgekit/source-trace-report.md")

    report = report_path.read_text(encoding="utf-8")
    required = [
        "Status: report-only",
        "Mode: source-trace",
        "## Summary",
        "## Trace Chain Overview",
        "## Findings by Severity",
        "## Findings by Trace Stage",
        "## Orphan Records",
        "## Status Consistency",
        "## Suggested Manual Fixes",
        "## Report-only Notice",
        "No automatic Source ID creation",
        "No automatic archive, link rewriting, runner, daemon, auto PR, worktree automation, commit, tag, or push",
    ]
    missing = [item for item in required if item not in report]
    if missing:
        fail("source-trace-report.md missing expected content:\n" + "\n".join(missing))

    for rel_path, before in before_hashes.items():
        after = sha256_file(target / rel_path)
        if after != before:
            fail(f"source-trace-report.py must not modify managed doc: {rel_path}")


def assert_handoff_package(target):
    report_path = target / ".forgekit" / "handoff-package.md"
    if report_path.exists():
        report_path.unlink()

    before_hashes = {}
    for rel_path in [
        ".forgekit/docs/task-intake.md",
        ".forgekit/docs/requirements.md",
        ".forgekit/docs/task-board.md",
        ".forgekit/docs/work-log.md",
        ".forgekit/docs/testing.md",
        ".forgekit/docs/changelog.md",
        ".forgekit/docs/risk-register.md",
        ".forgekit/template-lock.json",
    ]:
        path = target / rel_path
        if path.is_file():
            before_hashes[rel_path] = sha256_file(path)

    run([sys.executable, "scripts/handoff-package.py", "--project-root", "."], cwd=target)
    if not report_path.is_file():
        fail("handoff-package.py did not write .forgekit/handoff-package.md")

    report = report_path.read_text(encoding="utf-8")
    required = [
        "Status: report-only",
        "Mode: handoff-package",
        "## Summary",
        "## Scope",
        "## Source / Requirement Trace",
        "## What Changed",
        "## What Did Not Change",
        "## Verification Evidence",
        "## Independent Code Review",
        "## Doc Health / Source Trace Status",
        "## Risks / Blockers / TODO_REVIEW",
        "## Files / Artifacts",
        "## Human Review Checklist",
        "## Report-only Notice",
        "TODO_REVIEW",
        "must not trigger automatic fixes",
    ]
    missing = [item for item in required if item not in report]
    if missing:
        fail("handoff-package.md missing expected content:\n" + "\n".join(missing))

    for rel_path, before in before_hashes.items():
        after = sha256_file(target / rel_path)
        if after != before:
            fail(f"handoff-package.py must not modify source doc or lock: {rel_path}")


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
        "不提供 runner、自动派发",
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


def assert_independent_code_review(root):
    paths = {
        "claude_agent": root / ".claude/agents/forgekit-code-reviewer.md",
        "codex_agent": root / ".codex/agents/forgekit-code-reviewer.toml",
        "request_skill": root / ".claude/skills/forgekit-request-code-review/SKILL.md",
        "review_skill": root / ".claude/skills/forgekit-code-review/SKILL.md",
        "universal": root / ".claude/skills/forgekit-code-review/references/universal-review.md",
        "security": root / ".claude/skills/forgekit-code-review/references/security-review.md",
        "testing": root / ".claude/skills/forgekit-code-review/references/testing-review.md",
    }
    assert_paths(root, [path.relative_to(root).as_posix() for path in paths.values()])

    codex = tomllib.loads(paths["codex_agent"].read_text(encoding="utf-8"))
    for field in ("name", "description", "developer_instructions"):
        if not isinstance(codex.get(field), str) or not codex[field].strip():
            fail(f"Codex code reviewer {field} must be a non-empty string")
    if codex["name"] != "forgekit-code-reviewer":
        fail("Codex code reviewer name is incorrect")

    claude = paths["claude_agent"].read_text(encoding="utf-8")
    for marker in ("name: forgekit-code-reviewer", "tools: Read, Grep, Glob, Bash", "permissionMode: plan", "ReviewDecision"):
        if marker not in claude:
            fail(f"Claude code reviewer missing marker: {marker}")

    request = paths["request_skill"].read_text(encoding="ascii")
    review = paths["review_skill"].read_text(encoding="ascii")
    for marker in ("Do not provide the maker's full conversation history", "forgekit-code-reviewer", "manual-review"):
        if marker not in request:
            fail(f"Request code review skill missing marker: {marker}")
    for marker in ("read-only", "ReviewDecision", "needs-fix", "manual-review", "Do not modify files"):
        if marker not in review:
            fail(f"Code review skill missing marker: {marker}")
    for path in paths.values():
        raw = path.read_bytes()
        if any(byte > 127 for byte in raw):
            fail(f"Independent review agent/skill must be ASCII-only: {path}")
        if len(raw.splitlines()) > 180:
            fail(f"Independent review agent/skill is too large: {path}")

    protocol_path = root / ".forgekit/docs/maker-checker-protocol.md"
    if not protocol_path.is_file():
        protocol_path = root / "docs/maker-checker-protocol.md"
    protocol = protocol_path.read_text(encoding="utf-8")
    for marker in ("mandatory independent review", "ReviewType: self-review", "reviewer agent 不可用时", "read-only"):
        if marker not in protocol:
            fail(f"Independent review protocol missing marker: {marker}")
    for entry in ("AGENTS.md", "CLAUDE.md", ".codex/rules.md"):
        entry_text = (root / entry).read_text(encoding="utf-8")
        for marker in ("self-review", "manual-review", "needs-fix"):
            if marker not in entry_text:
                fail(f"{entry} missing independent review rule: {marker}")

def assert_context_continuity(root, doc_path):
    protocol = (root / doc_path).read_text(encoding="utf-8")
    required = [
        "## Purpose",
        "## Why Chat Context Is Not Durable State",
        "## Critical Facts",
        "## Context Checkpoint Triggers",
        "## Context Survival Map",
        "## Compact / Clear Readiness",
        "## Post-Upgrade Session Refresh",
        "## Subagent Output Handling",
        "## Large Output Handling",
        "## Writeback Boundaries",
        "## Examples",
        "TODO_REVIEW",
        "upgrade 后旧会话只用于收口",
        "新任务应新开会话",
        "不假设当前会话自动加载新规则",
    ]
    missing = [item for item in required if item not in protocol]
    if missing:
        fail("context-continuity.md missing expected sections:\n" + "\n".join(missing))

    for entry in ("AGENTS.md", "CLAUDE.md"):
        entry_text = (root / entry).read_text(encoding="utf-8")
        for marker in ("Critical conclusions must not live only in chat", "After a ForgeKit upgrade", "updated disk files do not prove", "Summarize large outputs", "TODO_REVIEW"):
            if marker not in entry_text:
                fail(f"{entry} missing context continuity rule: {marker}")
    rules = (root / ".codex/rules.md").read_text(encoding="utf-8")
    for marker in ("关键结论不能只留在聊天里", "新任务应新开会话", "不假设当前会话自动加载新规则", "长工具输出只保留摘要", "TODO_REVIEW"):
        if marker not in rules:
            fail(f".codex/rules.md missing context continuity rule: {marker}")

    router_path = root / (".forgekit/docs/workflow-router.md" if doc_path.startswith(".forgekit/") else "docs/workflow-router.md")
    router = router_path.read_text(encoding="utf-8")
    for marker in ("保存关键结论", "ForgeKit 升级后继续工作", "compact", "clear", "Context Checkpoint"):
        if marker not in router:
            fail(f"workflow-router.md missing context route: {marker}")

    policy_path = root / (".forgekit/docs/bounded-auto-loop-policy.md" if doc_path.startswith(".forgekit/") else "docs/bounded-auto-loop-policy.md")
    policy = policy_path.read_text(encoding="utf-8")
    if "Context Checkpoint" not in policy or "长工具输出只保留摘要" not in policy:
        fail("bounded-auto policy missing context checkpoint boundary")


def assert_work_session_checkpoint(root, docs_prefix):
    checkpoint = (root / docs_prefix / "work-session-checkpoint.md").read_text(encoding="utf-8")
    playbook = (root / docs_prefix / "usage-playbook.md").read_text(encoding="utf-8")
    for marker in [
        "Micro Update", "Checkpoint Update", "Ship Update", "Pre-Compact Checkpoint",
        "Post-Compact Recovery Check", "auto compact", "业务 README", "TODO_REVIEW",
    ]:
        if marker not in checkpoint:
            fail(f"work-session-checkpoint.md missing marker: {marker}")
    for marker in [
        "初始化新项目", "接手已有项目", "更新项目中的 ForgeKit", "开始今天工作",
        "执行具体任务", "文档 Checkpoint", "Compact / Clear", "提交前检查",
        "阶段结束归档", "生成 Handoff", "多项目 Workspace", "启用 Multi-Project Map",
    ]:
        if marker not in playbook:
            fail(f"usage-playbook.md missing scenario: {marker}")
    for entry in ["AGENTS.md", "CLAUDE.md", ".codex/rules.md"]:
        text = (root / entry).read_text(encoding="utf-8")
        for marker in ["work-session-checkpoint.md", "pre-compact checkpoint", "post-compact recovery check"]:
            if marker not in text:
                fail(f"{entry} missing work-session checkpoint rule: {marker}")


def assert_reasoning_review(root, doc_path):
    doc = (root / doc_path).read_text(encoding="utf-8")
    required = [
        "First-Principles Pass", "Adversarial Review Pass", "Problem / Goal",
        "Known Facts", "Assumptions", "Constraints", "Surface Fix vs Root Fix",
        "Minimal Verifiable Outcome", "Failure Scenario", "Trigger Condition",
        "Expected Failure", "Evidence / Reproduction", "Verification Needed",
        "Relationship to Independent Code Review", "Critical Facts",
    ]
    missing = [item for item in required if item not in doc]
    if missing:
        fail("reasoning-review.md missing markers:\n" + "\n".join(missing))
    for skill in ["forgekit-first-principles", "forgekit-adversarial-review"]:
        skill_path = root / ".claude/skills" / skill / "SKILL.md"
        raw = skill_path.read_bytes()
        if any(byte > 127 for byte in raw):
            fail(f"Reasoning/review skill must be ASCII-only: {skill_path}")
    for entry in ["AGENTS.md", "CLAUDE.md", ".codex/rules.md"]:
        text = (root / entry).read_text(encoding="utf-8")
        if "First-Principles Pass" not in text or "Adversarial Review Pass" not in text:
            fail(f"{entry} missing short reasoning/review rules")
    bounded = (root / ("docs/bounded-auto-loop-policy.md" if (root / "docs").is_dir() else ".forgekit/docs/bounded-auto-loop-policy.md")).read_text(encoding="utf-8")
    if "blocking finding" not in bounded or "TODO_REVIEW" not in bounded:
        fail("bounded-auto missing high-risk reasoning/review stop gate")
    context = (root / ("docs/context-continuity.md" if (root / "docs").is_dir() else ".forgekit/docs/context-continuity.md")).read_text(encoding="utf-8")
    if "Critical Facts" not in context or "blocking finding" not in context:
        fail("context continuity missing reasoning/review Critical Facts")


def assert_project_maintenance(root):
    docs_root = root / "docs" if (root / "docs/project-maintenance.md").is_file() else root / ".forgekit/docs"
    maintenance = (docs_root / "project-maintenance.md").read_text(encoding="utf-8")
    capsule = (docs_root / "archive-capsule.md").read_text(encoding="utf-8")
    skill = (root / ".claude/skills/forgekit-maintenance/SKILL.md").read_text(encoding="ascii")
    for marker in [
        "Maintenance Intents", "Unified Project Bootstrap / Install-or-Upgrade Entry", "Upgrade Sync", "Archive Capsule", "Plan before Apply",
        "Confirmation Rules", "Post-Operation Summary", "intent -> plan -> confirm/apply -> summary/index",
    ]:
        if marker not in maintenance:
            fail(f"project-maintenance.md missing marker: {marker}")
    for marker in [
        "Archive is not deletion", "Capsule structure", "Archive index", "Archived items log",
        "Legacy archive handling", "Plan / apply boundary",
    ]:
        if marker not in capsule:
            fail(f"archive-capsule.md missing marker: {marker}")
    for marker in ["project-bootstrap", "upgrade-sync", "archive-capsule", "context-checkpoint", "handoff", "doc-health", "source-trace"]:
        if marker not in skill:
            fail(f"forgekit-maintenance skill missing intent: {marker}")
    for entry in ["AGENTS.md", "CLAUDE.md", ".codex/rules.md"]:
        text = (root / entry).read_text(encoding="utf-8")
        for marker in ["MaintenanceIntent", "plan", "归档不是删除"]:
            if marker not in text:
                fail(f"{entry} missing project maintenance rule: {marker}")


def assert_workspace_integrity(target, temp_parent):
    checker = target / "scripts/check-workspace-integrity.py"
    disabled = run([sys.executable, str(checker), "--repo-root", str(target)], cwd=target)
    if "Status: not-enabled" not in disabled.stdout:
        fail("disabled scoped docs must report not-enabled")
    strict_disabled = run([sys.executable, str(checker), "--repo-root", str(target), "--strict"], cwd=target)
    if strict_disabled.returncode != 0:
        fail("--strict must not fail for not-enabled scoped docs")
    required = run([sys.executable, str(checker), "--repo-root", str(target), "--require-enabled"], cwd=target, check=False)
    if required.returncode != 1:
        fail("--require-enabled must fail when scoped docs are disabled")

    workspace = temp_parent / "workspace-integrity"
    shutil.copytree(target, workspace)
    state_path = workspace / ".forgekit/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8-sig"))
    state["features"]["multi_project_scoped_docs_available"] = True
    state["features"]["multi_project_scoped_docs_enabled"] = True
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    project_path = workspace / ".forgekit/projects/backend"
    repo_path = workspace / "backend-repo"
    repo_path.mkdir()
    run(["git", "init"], cwd=repo_path)
    workspace_map = {
        "schema_version": 1,
        "enabled": True,
        "workspace": {
            "id": "delivery-workspace", "name": "Delivery Workspace",
            "docs_path": ".forgekit/docs", "projects_path": ".forgekit/projects",
            "artifact_root": "artifacts", "archive_root": ".forgekit/archive",
            "docs_profile": "workspace-full",
            "default_read_scope": "workspace",
        },
        "projects": [{
            "id": "backend", "name": "Backend", "docs_path": ".forgekit/projects/backend",
            "docs_profile": "workspace-only", "repo_ids": ["backend-repo"], "depends_on": [],
            "default_read_scope": "project",
        }],
        "repos": [{
            "id": "backend-repo", "project_id": "backend", "repo_path": "backend-repo",
            "docs_profile": "repo-lite", "default_read_scope": "repo",
        }],
        "artifacts": [],
    }
    map_path = workspace / ".forgekit/workspace-map.json"
    map_path.write_text(json.dumps(workspace_map, indent=2) + "\n", encoding="utf-8")

    root_warning = run([sys.executable, str(checker), "--repo-root", str(workspace)], cwd=workspace)
    if root_warning.returncode != 0 or "workspace_root_not_git" not in root_warning.stdout or "Status: warning" not in root_warning.stdout:
        fail("non-Git WorkspaceRoot must warn without blocking")
    strict_root = run([sys.executable, str(checker), "--repo-root", str(workspace), "--strict"], cwd=workspace, check=False)
    if strict_root.returncode != 1 or "workspace_root_not_git" not in strict_root.stdout:
        fail("--strict must promote the non-Git WorkspaceRoot warning to exit code 1")

    run(["git", "init"], cwd=workspace)
    workspace_only = run([sys.executable, str(checker), "--repo-root", str(workspace)], cwd=workspace)
    if "Status: passed" not in workspace_only.stdout or "capsule_missing" in workspace_only.stdout:
        fail("workspace-only project must not require or warn about a Project Capsule")

    workspace_map["projects"][0]["docs_profile"] = "project-capsule"
    map_path.write_text(json.dumps(workspace_map, indent=2) + "\n", encoding="utf-8")
    missing_capsule = run([sys.executable, str(checker), "--repo-root", str(workspace)], cwd=workspace, check=False)
    if missing_capsule.returncode != 1 or "capsule_missing" not in missing_capsule.stdout:
        fail("project-capsule project without docs_path must be blocking")
    shutil.copytree(workspace / ".forgekit/projects/_template", project_path)
    passed = run([sys.executable, str(checker), "--repo-root", str(workspace)], cwd=workspace)
    if "Status: passed" not in passed.stdout:
        fail("valid enabled workspace must pass integrity check")
    if "workspace_root_not_git" in passed.stdout:
        fail("Git WorkspaceRoot must not produce workspace_root_not_git")

    workspace_map["projects"][0]["docs_profile"] = "invalid-profile"
    map_path.write_text(json.dumps(workspace_map, indent=2) + "\n", encoding="utf-8")
    invalid_profile = run([sys.executable, str(checker), "--repo-root", str(workspace)], cwd=workspace, check=False)
    if invalid_profile.returncode != 1 or "invalid_docs_profile" not in invalid_profile.stdout:
        fail("invalid project docs_profile must be blocking")
    workspace_map["projects"][0]["docs_profile"] = "project-capsule"

    workspace_map["workspace"]["docs_profile"] = "repo-lite"
    map_path.write_text(json.dumps(workspace_map, indent=2) + "\n", encoding="utf-8")
    wrong_workspace_profile = run([sys.executable, str(checker), "--repo-root", str(workspace)], cwd=workspace, check=False)
    if wrong_workspace_profile.returncode != 1 or "workspace_profile_mismatch" not in wrong_workspace_profile.stdout:
        fail("workspace profile used in the wrong position must be blocking")
    workspace_map["workspace"]["docs_profile"] = "workspace-full"

    workspace_map["repos"][0]["docs_profile"] = "workspace-only"
    map_path.write_text(json.dumps(workspace_map, indent=2) + "\n", encoding="utf-8")
    wrong_repo_profile = run([sys.executable, str(checker), "--repo-root", str(workspace)], cwd=workspace, check=False)
    if wrong_repo_profile.returncode != 1 or "repo_profile_mismatch" not in wrong_repo_profile.stdout:
        fail("repo profile used in the wrong position must be blocking")
    workspace_map["repos"][0]["docs_profile"] = "repo-lite"
    map_path.write_text(json.dumps(workspace_map, indent=2) + "\n", encoding="utf-8")

    extra = project_path / "notes.md"
    extra.write_text("# Local notes\n", encoding="utf-8")
    warning = run([sys.executable, str(checker), "--repo-root", str(workspace)], cwd=workspace)
    if "Status: warning" not in warning.stdout:
        fail("extra capsule notes must produce a warning")
    strict_warning = run([sys.executable, str(checker), "--repo-root", str(workspace), "--strict"], cwd=workspace, check=False)
    if strict_warning.returncode != 1:
        fail("--strict must promote warnings to exit code 1")
    extra.unlink()

    forbidden = project_path / "AGENTS.md"
    forbidden.write_text("# copied entry\n", encoding="utf-8")
    blocked = run([sys.executable, str(checker), "--repo-root", str(workspace)], cwd=workspace, check=False)
    if blocked.returncode != 1 or "full_forgekit_copy" not in blocked.stdout:
        fail("Project Capsule must not copy complete ForgeKit managed docs / AGENTS / CLAUDE / governance / skills / agents")
    forbidden.unlink()

    workspace_map["artifacts"] = [{"id": "report", "project_id": "backend", "path": "backend-repo"}]
    map_path.write_text(json.dumps(workspace_map, indent=2) + "\n", encoding="utf-8")
    collision = run([sys.executable, str(checker), "--repo-root", str(workspace)], cwd=workspace, check=False)
    if collision.returncode != 1 or "repo_artifact_collision" not in collision.stdout:
        fail("artifact configured as a repo path must be blocking")
    workspace_map["artifacts"] = []

    workspace_map["repos"][0]["repo_path"] = ".forgekit/archive/backend-repo"
    map_path.write_text(json.dumps(workspace_map, indent=2) + "\n", encoding="utf-8")
    archived_repo = run([sys.executable, str(checker), "--repo-root", str(workspace)], cwd=workspace, check=False)
    if archived_repo.returncode != 1 or "repo_in_archive" not in archived_repo.stdout:
        fail("repo path under archive must be blocking")
    workspace_map["repos"][0]["repo_path"] = "backend-repo"

    workspace_map["projects"][0]["repo_ids"] = ["unknown-repo"]
    map_path.write_text(json.dumps(workspace_map, indent=2) + "\n", encoding="utf-8")
    unknown_repo = run([sys.executable, str(checker), "--repo-root", str(workspace)], cwd=workspace, check=False)
    if unknown_repo.returncode != 1 or "unknown_repo" not in unknown_repo.stdout:
        fail("unknown project repo id must be blocking")
    workspace_map["projects"][0]["repo_ids"] = ["backend-repo"]

    workspace_map["projects"][0]["docs_path"] = "../outside"
    map_path.write_text(json.dumps(workspace_map, indent=2) + "\n", encoding="utf-8")
    unsafe = run([sys.executable, str(checker), "--repo-root", str(workspace)], cwd=workspace, check=False)
    if unsafe.returncode != 1 or "unsafe_path" not in unsafe.stdout:
        fail("unsafe project docs path must be blocking")
    workspace_map["projects"][0]["docs_path"] = ".forgekit/projects/backend"

    workspace_map["workspace"]["id"] = "TODO_REVIEW"
    map_path.write_text(json.dumps(workspace_map, indent=2) + "\n", encoding="utf-8")
    placeholder = run([sys.executable, str(checker), "--repo-root", str(workspace)], cwd=workspace, check=False)
    if placeholder.returncode != 1 or "placeholder_workspace_id" not in placeholder.stdout:
        fail("enabled workspace must reject placeholder workspace.id")

    map_path.unlink()
    missing = run([sys.executable, str(checker), "--repo-root", str(workspace)], cwd=workspace, check=False)
    if missing.returncode != 1 or "Status: blocking" not in missing.stdout:
        fail("enabled state without workspace map must be blocking")


def assert_project_capsule_bootstrap(target, temp_parent):
    workspace = temp_parent / "project-capsule-bootstrap"
    shutil.copytree(target, workspace)
    script = workspace / "scripts/bootstrap-project-capsule.py"
    checker = workspace / "scripts/check-workspace-integrity.py"
    state_path = workspace / ".forgekit/state.json"
    map_path = workspace / ".forgekit/workspace-map.json"
    capsule = workspace / ".forgekit/projects/backend"

    state = json.loads(state_path.read_text(encoding="utf-8-sig"))
    workspace_map = json.loads(map_path.read_text(encoding="utf-8-sig"))
    workspace_map["workspace"]["id"] = "capsule-smoke"
    workspace_map["projects"] = [{
        "id": "backend", "name": "Backend", "docs_path": ".forgekit/projects/backend",
        "docs_profile": "workspace-only", "repo_ids": [], "depends_on": [],
        "default_read_scope": "project",
    }]

    disabled = run([sys.executable, str(script), "plan", "--repo-root", str(workspace), "--project", "backend"], cwd=workspace)
    if "Status: not-enabled" not in disabled.stdout or capsule.exists():
        fail("disabled map capsule plan must return not-enabled without writing")

    state["features"]["multi_project_scoped_docs_available"] = False
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    unsupported = run([sys.executable, str(script), "plan", "--repo-root", str(workspace), "--project", "backend"], cwd=workspace, check=False)
    if unsupported.returncode != 1 or "unsupported" not in unsupported.stdout:
        fail("project without scoped docs capability must be blocking")
    state["features"]["multi_project_scoped_docs_available"] = True
    state["features"]["multi_project_scoped_docs_enabled"] = True
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    workspace_map["enabled"] = True
    map_path.write_text(json.dumps(workspace_map, indent=2) + "\n", encoding="utf-8")

    workspace_only = run([sys.executable, str(script), "plan", "--repo-root", str(workspace), "--project", "backend"], cwd=workspace)
    if "Status: skipped_workspace_only" not in workspace_only.stdout or capsule.exists():
        fail("workspace-only project must be skipped without creating a capsule")

    workspace_map["projects"][0]["docs_profile"] = "project-capsule"
    map_path.write_text(json.dumps(workspace_map, indent=2) + "\n", encoding="utf-8")
    planned = run([sys.executable, str(script), "plan", "--repo-root", str(workspace), "--project", "backend"], cwd=workspace)
    if "Status: planned" not in planned.stdout or "create: 6" not in planned.stdout or "will_write: no" not in planned.stdout or capsule.exists():
        fail("project-capsule plan must list six create actions without writing")

    no_confirm = run([sys.executable, str(script), "apply", "--repo-root", str(workspace), "--project", "backend"], cwd=workspace, check=False)
    if no_confirm.returncode != 1 or "Status: confirmation-required" not in no_confirm.stdout or capsule.exists():
        fail("capsule apply without --confirm must fail without writing")

    unknown = run([sys.executable, str(script), "plan", "--repo-root", str(workspace), "--project", "missing"], cwd=workspace, check=False)
    if unknown.returncode != 1 or "not listed" not in unknown.stdout:
        fail("unknown project capsule request must be blocking")

    original_docs_path = workspace_map["projects"][0]["docs_path"]
    for unsafe_path in ("../outside", ".git/capsule", "backend-repo", "artifacts/report"):
        workspace_map["projects"][0]["docs_path"] = unsafe_path
        if unsafe_path == "backend-repo":
            workspace_map["repos"] = [{"id": "backend-repo", "project_id": "backend", "repo_path": "backend-repo", "docs_profile": "repo-lite"}]
        elif unsafe_path == "artifacts/report":
            workspace_map["artifacts"] = [{"id": "report", "project_id": "backend", "path": "artifacts/report"}]
        map_path.write_text(json.dumps(workspace_map, indent=2) + "\n", encoding="utf-8")
        blocked = run([sys.executable, str(script), "plan", "--repo-root", str(workspace), "--project", "backend"], cwd=workspace, check=False)
        if blocked.returncode != 1 or "Status: blocking" not in blocked.stdout:
            fail(f"unsafe or conflicting capsule docs_path must be blocking: {unsafe_path}")
        workspace_map["repos"] = []
        workspace_map["artifacts"] = []
    workspace_map["projects"][0]["docs_path"] = ".forgekit/archive/backend"
    workspace_map["workspace"]["projects_path"] = ".forgekit/archive"
    map_path.write_text(json.dumps(workspace_map, indent=2) + "\n", encoding="utf-8")
    archived = run([sys.executable, str(script), "plan", "--repo-root", str(workspace), "--project", "backend"], cwd=workspace, check=False)
    if archived.returncode != 1 or "conflicts with archive" not in archived.stdout:
        fail("capsule docs_path under archive must be blocking")
    workspace_map["workspace"]["projects_path"] = ".forgekit/projects"
    workspace_map["projects"][0]["docs_path"] = original_docs_path
    map_path.write_text(json.dumps(workspace_map, indent=2) + "\n", encoding="utf-8")

    applied = run([sys.executable, str(script), "apply", "--repo-root", str(workspace), "--project", "backend", "--confirm"], cwd=workspace)
    if "Status: completed" not in applied.stdout or "will_write: yes" not in applied.stdout:
        fail("confirmed capsule apply must create the minimal capsule")
    expected = {
        "project-card.md", "source-links.md", "task-board.md", "testing.md", "risk-register.md",
        "decisions/0001-example.md",
    }
    actual = {path.relative_to(capsule).as_posix() for path in capsule.rglob("*") if path.is_file()}
    if actual != expected:
        fail(f"capsule bootstrap created an unexpected file set: {sorted(actual)}")
    checked = run([sys.executable, str(checker), "--repo-root", str(workspace)], cwd=workspace)
    if "capsule_missing" in checked.stdout:
        fail("workspace checker must not report capsule_missing after bootstrap")

    repeated = run([sys.executable, str(script), "apply", "--repo-root", str(workspace), "--project", "backend", "--confirm"], cwd=workspace)
    if "already-present: 6" not in repeated.stdout or "will_write: no" not in repeated.stdout:
        fail("same-content capsule apply must be an idempotent no-op")

    customized = capsule / "project-card.md"
    customized.write_text("# User-owned project card\n", encoding="utf-8")
    before = hashlib.sha256(customized.read_bytes()).hexdigest()
    reviewed = run([sys.executable, str(script), "apply", "--repo-root", str(workspace), "--project", "backend", "--confirm"], cwd=workspace)
    after = hashlib.sha256(customized.read_bytes()).hexdigest()
    if "Status: completed_with_review_needed" not in reviewed.stdout or "review-needed: 1" not in reviewed.stdout or before != after:
        fail("different capsule file must be review-needed and preserved")

    forbidden = capsule / "AGENTS.md"
    forbidden.write_text("# Forbidden full entry\n", encoding="utf-8")
    full_copy = run([sys.executable, str(script), "plan", "--repo-root", str(workspace), "--project", "backend"], cwd=workspace, check=False)
    if full_copy.returncode != 1 or "forbidden ForgeKit entry" not in full_copy.stdout:
        fail("capsule containing a full ForgeKit entry must be blocking")

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
        ".forgekit/state.json",
        "versioned migration",
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


def assert_workflow_router(root, router_path, responsibility_path, codebase_path, agents_path, claude_path, rules_path):
    router = (root / router_path).read_text(encoding="utf-8")
    responsibility = (root / responsibility_path).read_text(encoding="utf-8")
    codebase = (root / codebase_path).read_text(encoding="utf-8")
    agents = (root / agents_path).read_text(encoding="utf-8")
    claude = (root / claude_path).read_text(encoding="utf-8")
    rules = (root / rules_path).read_text(encoding="utf-8")

    router_required = [
        "Purpose",
        "How to Use",
        "Intent Routing Table",
        "Read Targets",
        "Write Targets",
        "Do Not Write",
        "Required Output",
        "Escalation Rules",
        "Examples",
        "task-intake.md",
        "task-board.md",
        "requirements.md",
        "work-log.md",
        "testing.md",
        "changelog.md",
        "risk-register.md",
        "bounded-auto-loop-policy.md",
        "loop-blueprint.md",
        "loop-operations.md",
        "native-agent-adapter.md",
        "maker-checker-protocol.md",
        "worktree-playbook.md",
        "handoff",
        "ForgeKit 版本升级",
        "forgekit-upgrade.py",
        "adoption guidance",
        "不要默认全量读取 `.forgekit/docs/**`",
    ]
    missing_router = [item for item in router_required if item not in router]
    if missing_router:
        fail("workflow-router.md missing expected routing content:\n" + "\n".join(missing_router))

    matrix_required = [
        "workflow-router.md",
        "用户意图",
        "不是任务看板",
        "不授权自动执行",
    ]
    missing_matrix = [item for item in matrix_required if item not in responsibility]
    if missing_matrix:
        fail("document-responsibility.md missing workflow-router entry:\n" + "\n".join(missing_matrix))

    codebase_required = [
        "workflow-router.md",
        "用户意图类问题先看",
        "不复制路由表",
    ]
    missing_codebase = [item for item in codebase_required if item not in codebase]
    if missing_codebase:
        fail("codebase-map.md missing workflow-router index:\n" + "\n".join(missing_codebase))

    entry_required = [
        "workflow-router.md",
        "intent routing",
        "Read Targets",
        "Write Targets",
        "Do Not Write",
        "没有写入触发条件",
    ]
    for label, text in [("AGENTS.md", agents), ("CLAUDE.md", claude)]:
        missing_entry = [item for item in entry_required if item not in text]
        if missing_entry:
            fail(f"{label} missing workflow-router entry rules:\n" + "\n".join(missing_entry))

    rules_required = [
        "workflow-router.md",
        "intent routing",
        "Read Targets",
        "Write Targets",
        "Do Not Write",
        "没有写入触发",
    ]
    missing_rules = [item for item in rules_required if item not in rules]
    if missing_rules:
        fail(".codex/rules.md missing workflow-router rules:\n" + "\n".join(missing_rules))


def assert_json(path):
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Invalid JSON: {path}: {exc}")


def assert_manifest_lock(target):
    lock_path = target / ".forgekit" / "template-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if lock.get("installed_version") != "0.43.2":
        fail("template-lock installed_version must be 0.43.2")
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


def assert_versioned_migration_upgrade(repo, target, temp_parent):
    state_path = target / ".forgekit" / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8-sig"))
    expected = {
        "schema_version": 1,
        "forgekit_version": "0.43.2",
        "managed_docs_root": ".forgekit/docs",
        "change_root": ".forgekit/changes",
        "mode": "Standard",
        "last_upgrade": None,
    }
    for key, value in expected.items():
        if state.get(key) != value:
            fail(f"state.json {key} mismatch: {state.get(key)!r}")
    if state.get("features", {}).get("versioned_migrations") is not True:
        fail("state.json must enable versioned_migrations")
    if state.get("features", {}).get("independent_code_review") is not True:
        fail("state.json must enable independent_code_review")
    if state.get("features", {}).get("context_continuity") is not True:
        fail("state.json must enable context_continuity")
    if state.get("features", {}).get("project_maintenance_operations") is not True:
        fail("state.json must enable project_maintenance_operations")
    if state.get("features", {}).get("first_principles_adversarial_review") is not True:
        fail("state.json must enable first_principles_adversarial_review")
    if state.get("features", {}).get("idempotent_safe_migrations") is not True:
        fail("state.json must enable idempotent_safe_migrations")
    if state.get("features", {}).get("active_current_docs_integrity_guard") is not True:
        fail("state.json must enable active_current_docs_integrity_guard")
    if state.get("features", {}).get("multi_project_scoped_docs_available") is not True:
        fail("state.json must install multi_project_scoped_docs_available")
    if state.get("features", {}).get("multi_project_scoped_docs_enabled") is not False:
        fail("state.json must keep multi_project_scoped_docs_enabled false by default")
    if state.get("features", {}).get("work_session_checkpoint") is not True:
        fail("state.json must enable work_session_checkpoint")
    if state.get("features", {}).get("usage_playbook") is not True:
        fail("state.json must enable usage_playbook")
    if state.get("features", {}).get("minimal_project_capsule_bootstrap") is not True:
        fail("state.json must enable minimal_project_capsule_bootstrap")

    script = target / "scripts" / "forgekit-upgrade.py"
    before_state = state_path.read_bytes()
    before_docs = {
        path.relative_to(target).as_posix(): path.read_bytes()
        for path in (target / ".forgekit" / "docs").rglob("*")
        if path.is_file()
    }
    check = run([sys.executable, str(script), "check", "--repo-root", "."], cwd=target)
    if "Status: current" not in check.stdout or "Current version: 0.43.2" not in check.stdout:
        fail("versioned migration check did not report current v0.43.2 state")
    plan = run([sys.executable, str(script), "plan", "--repo-root", "."], cwd=target)
    for marker in ["Status: report-only", "Mode: versioned-migration-plan", "No files were changed."]:
        if marker not in plan.stdout:
            fail(f"versioned migration plan missing marker: {marker}")
    refused = run([sys.executable, str(script), "apply", "--repo-root", "."], cwd=target, check=False)
    if refused.returncode == 0 or "apply requires --safe" not in (refused.stdout + refused.stderr):
        fail("versioned migration apply must refuse without --safe")
    run([sys.executable, str(script), "apply", "--safe", "--repo-root", "."], cwd=target)
    if state_path.read_bytes() != before_state:
        fail("no-op apply --safe must not rewrite state.json")
    after_docs = {
        path.relative_to(target).as_posix(): path.read_bytes()
        for path in (target / ".forgekit" / "docs").rglob("*")
        if path.is_file()
    }
    if after_docs != before_docs:
        fail("check/plan/no-op apply modified managed docs")
    v036_target = temp_parent / "v036-to-v037"
    shutil.copytree(target, v036_target)
    v036_state_path = v036_target / ".forgekit/state.json"
    v036_state = json.loads(v036_state_path.read_text(encoding="utf-8-sig"))
    v036_state["forgekit_version"] = "0.36.0"
    v036_state.setdefault("features", {}).pop("independent_code_review", None)
    v036_state.setdefault("features", {}).pop("context_continuity", None)
    v036_state.setdefault("features", {}).pop("project_maintenance_operations", None)
    v036_state.setdefault("features", {}).pop("first_principles_adversarial_review", None)
    v036_state.setdefault("features", {}).pop("idempotent_safe_migrations", None)
    v036_state.setdefault("features", {}).pop("active_current_docs_integrity_guard", None)
    v036_state_path.write_text(json.dumps(v036_state, indent=2) + "\n", encoding="utf-8")
    for introduced_file in [
        ".forgekit/docs/context-continuity.md",
        ".forgekit/docs/project-maintenance.md",
        ".forgekit/docs/archive-capsule.md",
        "scripts/archive-capsule.py",
        ".forgekit/docs/reasoning-review.md",
        ".forgekit/docs/current-docs-integrity.md",
        "scripts/check-current-docs-integrity.py",
        ".claude/agents/forgekit-code-reviewer.md",
        ".codex/agents/forgekit-code-reviewer.toml",
        ".forgekit/docs/work-session-checkpoint.md",
        ".forgekit/docs/usage-playbook.md",
        "scripts/bootstrap-project-capsule.py",
    ]:
        path = v036_target / introduced_file
        if path.is_file():
            path.unlink()
    maintenance_skill = v036_target / ".claude/skills/forgekit-maintenance"
    if maintenance_skill.is_dir():
        shutil.rmtree(maintenance_skill)
    for skill_name in [
        "forgekit-request-code-review", "forgekit-code-review",
        "forgekit-first-principles", "forgekit-adversarial-review",
    ]:
        skill_path = v036_target / ".claude/skills" / skill_name
        if skill_path.is_dir():
            shutil.rmtree(skill_path)
    run([sys.executable, str(v036_target / "scripts/forgekit-upgrade.py"), "apply", "--safe", "--repo-root", ".", "--review-needed-policy", "replace-template"], cwd=v036_target)
    migrated = json.loads(v036_state_path.read_text(encoding="utf-8"))
    if migrated.get("forgekit_version") != "0.43.2":
        fail("version chain did not update state to v0.43.2")
    if migrated.get("features", {}).get("independent_code_review") is not True:
        fail("v0.37 migration did not enable independent_code_review")
    if migrated.get("features", {}).get("context_continuity") is not True:
        fail("v0.38 migration did not enable context_continuity")
    if migrated.get("features", {}).get("project_maintenance_operations") is not True:
        fail("v0.39 migration did not enable project_maintenance_operations")
    if migrated.get("features", {}).get("first_principles_adversarial_review") is not True:
        fail("v0.40 migration did not enable first_principles_adversarial_review")
    if migrated.get("features", {}).get("idempotent_safe_migrations") is not True:
        fail("v0.40.1 migration did not enable idempotent_safe_migrations")
    if migrated.get("features", {}).get("active_current_docs_integrity_guard") is not True:
        fail("v0.40.2 migration did not enable active_current_docs_integrity_guard")
    if migrated.get("features", {}).get("multi_project_scoped_docs_available") is not True:
        fail("v0.41 migration did not register scoped docs capability")
    if migrated.get("features", {}).get("multi_project_scoped_docs_enabled") is not False:
        fail("v0.41 migration must not automatically enable scoped docs")
    if migrated.get("features", {}).get("work_session_checkpoint") is not True:
        fail("v0.42 migration did not enable work_session_checkpoint")
    if migrated.get("features", {}).get("usage_playbook") is not True:
        fail("v0.42 migration did not enable usage_playbook")
    if migrated.get("features", {}).get("minimal_project_capsule_bootstrap") is not True:
        fail("v0.43 migration did not enable minimal_project_capsule_bootstrap")
    if any(path.name != "_template" for path in (v036_target / ".forgekit/projects").iterdir() if path.is_dir()):
        fail("v0.41 migration must not create real project capsules")

    legacy = temp_parent / "pre-v036-adoption"
    (legacy / ".forgekit").mkdir(parents=True)
    (legacy / "README.md").write_text("# Existing project\n", encoding="utf-8")
    legacy_check = run(
        [sys.executable, str(repo / "scripts" / "forgekit-upgrade.py"), "check", "--repo-root", str(legacy)],
        cwd=repo,
    )
    if "Status: adoption-required" not in legacy_check.stdout or "No automatic upgrade" not in legacy_check.stdout:
        fail("pre-v0.36 project must receive adoption guidance")
    if (legacy / ".forgekit" / "state.json").exists():
        fail("pre-v0.36 check must not create state.json")

    hotfix_target = temp_parent / "v0410-hotfix-baseline"
    shutil.copytree(target, hotfix_target)
    hotfix_state_path = hotfix_target / ".forgekit/state.json"
    hotfix_state = json.loads(hotfix_state_path.read_text(encoding="utf-8-sig"))
    hotfix_state["forgekit_version"] = "0.41.0"
    hotfix_state_path.write_text(json.dumps(hotfix_state, indent=2) + "\n", encoding="utf-8")
    baseline_root = repo / "migrations/0.41.1/baseline"
    for relative in [
        "scripts/check-workspace-integrity.py",
        "scripts/forgekit-upgrade.py",
        ".forgekit/docs/scoped-docs.md",
    ]:
        shutil.copyfile(baseline_root / relative, hotfix_target / relative)
    hotfix_plan = run([sys.executable, str(repo / "scripts/forgekit-upgrade.py"), "plan", "--repo-root", str(hotfix_target)], cwd=repo)
    if "SAFE: update-workspace-integrity-checker" not in hotfix_plan.stdout:
        fail("v0.41.1 plan must classify an unchanged v0.41.0 checker as safe to replace")
    hotfix_apply = run([sys.executable, str(repo / "scripts/forgekit-upgrade.py"), "apply", "--safe", "--repo-root", str(hotfix_target), "--review-needed-policy", "replace-template"], cwd=repo)
    if "[applied] update-workspace-integrity-checker" not in hotfix_apply.stdout:
        fail("v0.41.1 safe apply did not replace the unchanged v0.41.0 checker")
    if (hotfix_target / "scripts/check-workspace-integrity.py").read_bytes() != (repo / "scripts/check-workspace-integrity.py").read_bytes():
        fail("v0.41.1 safe apply installed the wrong workspace checker")

    modified_target = temp_parent / "v0410-hotfix-modified"
    shutil.copytree(target, modified_target)
    modified_state_path = modified_target / ".forgekit/state.json"
    modified_state = json.loads(modified_state_path.read_text(encoding="utf-8-sig"))
    modified_state["forgekit_version"] = "0.41.0"
    modified_state_path.write_text(json.dumps(modified_state, indent=2) + "\n", encoding="utf-8")
    modified_checker = modified_target / "scripts/check-workspace-integrity.py"
    modified_checker.write_text("# user-modified v0.41.0 checker\n", encoding="utf-8")
    modified_before = modified_checker.read_bytes()
    modified_plan = run([sys.executable, str(repo / "scripts/forgekit-upgrade.py"), "plan", "--repo-root", str(modified_target)], cwd=repo)
    for marker in ["skipped-existing-review-needed", "may still use v0.41.0 workspace Git/profile logic"]:
        if marker not in modified_plan.stdout:
            fail(f"v0.41.1 modified-checker plan missing review-needed marker: {marker}")
    modified_apply = run([
        sys.executable, str(repo / "scripts/forgekit-upgrade.py"), "apply", "--safe",
        "--repo-root", str(modified_target), "--review-needed-policy", "manual-merge",
    ], cwd=repo)
    for marker in ["resolved-manual-merge", "manual-merge item"]:
        if marker not in modified_apply.stdout:
            fail(f"v0.41.1 modified-checker apply missing review-needed marker: {marker}")
    if modified_checker.read_bytes() != modified_before:
        fail("v0.41.1 migration overwrote a user-modified workspace checker")
    review_report = json.loads((modified_target / ".forgekit/reports/upgrade-review-needed.json").read_text(encoding="utf-8"))
    checker_item = next((item for item in review_report["items"] if item["action_id"] == "update-workspace-integrity-checker"), None)
    if checker_item is None:
        fail("v0.41.1 review report missing update-workspace-integrity-checker item")
    if checker_item["status"] != "resolved_manual_merge":
        fail("v0.41.1 manual-merge must record resolved_manual_merge")
    export_dir = modified_target / checker_item["export_path"]
    exported = checker_item["exported_files"]
    if (export_dir / exported["local"]).read_bytes() != modified_before:
        fail("manual-merge .local must match the original target file")
    if not (export_dir / exported["incoming"]).is_file() or not (export_dir / exported["diff"]).read_text(encoding="utf-8"):
        fail("manual-merge must export incoming and diff files")
    if "Please read the .local, .incoming, and .diff files" not in (export_dir / "README.md").read_text(encoding="utf-8"):
        fail("manual-merge README must include the AI-assisted merge prompt")

    capsule_migration = temp_parent / "v0420-capsule-bootstrap-migration"
    shutil.copytree(target, capsule_migration)
    capsule_state_path = capsule_migration / ".forgekit/state.json"
    capsule_state = json.loads(capsule_state_path.read_text(encoding="utf-8-sig"))
    capsule_state["forgekit_version"] = "0.42.0"
    capsule_state["features"].pop("minimal_project_capsule_bootstrap", None)
    capsule_state_path.write_text(json.dumps(capsule_state, indent=2) + "\n", encoding="utf-8")
    (capsule_migration / "scripts/bootstrap-project-capsule.py").unlink()
    shutil.copyfile(
        repo / "migrations/0.43.0/baseline/.forgekit/docs/scoped-docs.md",
        capsule_migration / ".forgekit/docs/scoped-docs.md",
    )
    shutil.copyfile(
        repo / "migrations/0.43.0/baseline/.forgekit/docs/usage-playbook.md",
        capsule_migration / ".forgekit/docs/usage-playbook.md",
    )
    capsule_apply = run([sys.executable, str(repo / "scripts/forgekit-upgrade.py"), "apply", "--safe", "--repo-root", str(capsule_migration)], cwd=repo)
    capsule_state = json.loads(capsule_state_path.read_text(encoding="utf-8"))
    if capsule_state.get("forgekit_version") != "0.43.2" or capsule_state["features"].get("minimal_project_capsule_bootstrap") is not True:
        fail("v0.43 migration did not register minimal Project Capsule Bootstrap")
    if not (capsule_migration / "scripts/bootstrap-project-capsule.py").is_file():
        fail("v0.43 migration did not install bootstrap-project-capsule.py")
    capsule_rerun = run([sys.executable, str(repo / "scripts/forgekit-upgrade.py"), "apply", "--safe", "--repo-root", str(capsule_migration)], cwd=repo)
    if "No migration is required; no files were changed" not in capsule_rerun.stdout:
        fail("v0.43 migration rerun must be an up-to-date no-op")

    customized_capsule_migration = temp_parent / "v0420-capsule-bootstrap-custom-docs"
    shutil.copytree(target, customized_capsule_migration)
    customized_state_path = customized_capsule_migration / ".forgekit/state.json"
    customized_state = json.loads(customized_state_path.read_text(encoding="utf-8-sig"))
    customized_state["forgekit_version"] = "0.42.0"
    customized_state["features"].pop("minimal_project_capsule_bootstrap", None)
    customized_state_path.write_text(json.dumps(customized_state, indent=2) + "\n", encoding="utf-8")
    customized_guide = customized_capsule_migration / ".forgekit/docs/scoped-docs.md"
    customized_guide.write_text("# User-owned scoped docs\n", encoding="utf-8")
    customized_before = customized_guide.read_bytes()
    customized_apply = run([
        sys.executable, str(repo / "scripts/forgekit-upgrade.py"), "apply", "--safe",
        "--repo-root", str(customized_capsule_migration), "--review-needed-policy", "manual-merge",
    ], cwd=repo)
    if "resolved-manual-merge" not in customized_apply.stdout or customized_guide.read_bytes() != customized_before:
        fail("v0.43 migration must preserve and report a user-modified scoped docs guide")

    apply_target = temp_parent / "versioned-apply"
    shutil.copytree(target, apply_target)
    migration_root = temp_parent / "migration-packages"
    package = migration_root / "0.43.2"
    package.mkdir(parents=True)
    (package / "proof.txt").write_text("safe migration\n", encoding="utf-8")
    migration = {
        "id": "0.43.2-smoke",
        "title": "Smoke safe migration",
        "from": "0.43.0",
        "to": "0.43.2",
        "risk": "low",
        "actions": [{
            "id": "copy-proof",
            "type": "copy_file_if_missing",
            "safety": "safe",
            "source": "proof.txt",
            "target": ".forgekit/migration-proof.txt",
            "description": "Copy an isolated smoke proof file",
        }],
        "manual_review": [],
        "non_goals": ["No business docs changes"],
    }
    (package / "migration.json").write_text(json.dumps(migration, indent=2) + "\n", encoding="utf-8")
    apply_script = apply_target / "scripts" / "forgekit-upgrade.py"
    apply_plan = run([
        sys.executable, str(apply_script), "plan", "--repo-root", ".", "--migration-root", str(migration_root)
    ], cwd=apply_target)
    if "To: 0.43.2" not in apply_plan.stdout or (apply_target / ".forgekit" / "migration-proof.txt").exists():
        fail("plan must show the safe migration without applying it")
    run([
        sys.executable, str(apply_script), "apply", "--safe", "--repo-root", ".", "--migration-root", str(migration_root)
    ], cwd=apply_target)
    applied_state = json.loads((apply_target / ".forgekit" / "state.json").read_text(encoding="utf-8-sig"))
    if applied_state.get("forgekit_version") != "0.43.2":
        fail("safe migration did not update state version")
    if not (apply_target / ".forgekit" / "migration-proof.txt").is_file():
        fail("safe migration did not apply the declared safe action")


def assert_unified_project_entry(repo, current_target, temp_parent):
    script = repo / "scripts/forgekit-project.py"

    uninstalled = temp_parent / "unified-uninstalled"
    dry_run = run(
        [sys.executable, str(script), "--target", str(uninstalled), "--dry-run"],
        cwd=repo,
    )
    for marker in ["Detected action: init", "Check result: uninstalled", "No files were changed"]:
        if marker not in dry_run.stdout:
            fail(f"unified uninstalled dry-run missing marker: {marker}")
    if uninstalled.exists():
        fail("unified init dry-run must not create the target directory")

    preserved_init = temp_parent / "unified-existing-workspace"
    preserved_init.mkdir()
    existing_readme = preserved_init / "README.md"
    existing_readme.write_text("existing project file\n", encoding="utf-8")
    existing_before = existing_readme.read_bytes()
    initialized = run([
        sys.executable, str(script), "--target", str(preserved_init), "--force-init", "--yes",
    ], cwd=repo)
    if "ForgeKit initialization completed through the existing init entry point" not in initialized.stdout:
        fail("unified --force-init --yes did not delegate to the existing init script")
    if existing_readme.read_bytes() != existing_before:
        fail("unified --force-init must preserve existing target files")
    if not (preserved_init / ".forgekit/state.json").is_file():
        fail("unified initialization did not create state.json")
    if not (preserved_init / "unified-existing").is_dir():
        fail("unified initialization did not create the derived inner project directory")

    current_state = current_target / ".forgekit/state.json"
    current_before = current_state.read_bytes()
    current = run([sys.executable, str(script), "--target", str(current_target)], cwd=repo, input_text="\n")
    if "Detected action: up-to-date" not in current.stdout or "No files were changed" not in current.stdout:
        fail("unified entry must report an up-to-date project without writes")
    if current_state.read_bytes() != current_before:
        fail("unified up-to-date check must not rewrite state.json")
    zh_current = run([sys.executable, str(script), "--target", str(current_target), "--lang", "zh-CN"], cwd=repo)
    if "检查结果：current" not in zh_current.stdout or "请选择显示语言" in zh_current.stdout:
        fail("--lang zh-CN must use Chinese user-facing output without prompting")
    en_current = run([sys.executable, str(script), "--target", str(current_target), "--lang", "en-US"], cwd=repo)
    if "Check result: current" not in en_current.stdout or "请选择显示语言" in en_current.stdout:
        fail("--lang en-US must use English user-facing output without prompting")
    env_current = run([sys.executable, str(script), "--target", str(current_target)], cwd=repo, env_updates={"FORGEKIT_LANG": "zh-CN"})
    if "检查结果：current" not in env_current.stdout:
        fail("FORGEKIT_LANG=zh-CN must select Chinese output")
    precedence_current = run(
        [sys.executable, str(script), "--target", str(current_target), "--lang", "en-US"],
        cwd=repo,
        env_updates={"FORGEKIT_LANG": "zh-CN"},
    )
    if "Check result: current" not in precedence_current.stdout or "检查结果：current" in precedence_current.stdout:
        fail("--lang must take precedence over FORGEKIT_LANG")
    bad_lang = run([sys.executable, str(script), "--target", str(current_target), "--lang", "fr-FR"], cwd=repo, check=False)
    if bad_lang.returncode == 0 or "Allowed values: zh-CN, en-US" not in (bad_lang.stdout + bad_lang.stderr):
        fail("invalid --lang must fail with allowed values")

    def write_state(root, version):
        state_path = root / ".forgekit/state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state = json.loads((repo / "project-template/.forgekit/state.json").read_text(encoding="utf-8"))
        state["forgekit_version"] = version
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        return state_path

    same_target = temp_parent / "upgrade-same-existing"
    same_state = write_state(same_target, "0.40.1")
    same_maintenance = same_target / ".forgekit/docs/project-maintenance.md"
    same_maintenance.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(
        repo / "migrations/0.40.2/files/.forgekit/docs/project-maintenance.md",
        same_maintenance,
    )
    same_before = same_maintenance.read_bytes()
    upgrade_script = repo / "scripts/forgekit-upgrade.py"
    same_plan = run([sys.executable, str(upgrade_script), "plan", "--repo-root", str(same_target)], cwd=repo)
    if "ALREADY-PRESENT: install-current-project-maintenance-guide" not in same_plan.stdout:
        fail("plan must classify identical existing migration file as already-present")
    same_apply = run([sys.executable, str(upgrade_script), "apply", "--safe", "--repo-root", str(same_target), "--review-needed-policy", "replace-template"], cwd=repo)
    if "[already-present] install-current-project-maintenance-guide" not in same_apply.stdout:
        fail("safe apply must treat identical existing migration file as no-op")
    if same_maintenance.read_bytes() != same_before:
        fail("safe apply rewrote an identical existing managed doc")
    if json.loads(same_state.read_text(encoding="utf-8"))["forgekit_version"] != "0.43.2":
        fail("same-content idempotent migration did not reach v0.43.2")

    old = temp_parent / "unified-old-no-confirm"
    old_state = write_state(old, "0.38.0")
    business = old / "docs/business.md"
    business.parent.mkdir(parents=True)
    business.write_text("business truth\n", encoding="utf-8")
    old_state_before = old_state.read_bytes()
    business_before = business.read_bytes()
    old_plan = run([sys.executable, str(script), "--target", str(old)], cwd=repo, input_text="\n")
    for marker in [
        "Detected action: upgrade-sync", "Check result: update-available",
        "Status: report-only", "Safe actions count:", "Manual actions count:",
        "Safe apply was not executed",
    ]:
        if marker not in old_plan.stdout:
            fail(f"unified old-version plan missing marker: {marker}")
    if old_state.read_bytes() != old_state_before or business.read_bytes() != business_before:
        fail("unified upgrade without explicit yes must not modify project files")

    if os.name != "nt":
        ask_target = temp_parent / "unified-old-ask-review"
        ask_state = write_state(ask_target, "0.38.0")
        ask_maintenance = ask_target / ".forgekit/docs/project-maintenance.md"
        ask_maintenance.parent.mkdir(parents=True, exist_ok=True)
        ask_maintenance.write_text("# User-maintained project guide\n", encoding="utf-8")
        ask_before = ask_maintenance.read_bytes()
        ask_result = run_pty([sys.executable, str(script), "--target", str(ask_target)], cwd=repo, input_text="2\ny\nd\nm\n")
        for marker in [
            "ForgeKit found 1 file that cannot be safely overwritten automatically.",
            ".forgekit/docs/project-maintenance.md",
            "Reason:",
            "Impact:",
            "Recommendation:",
            "--- .forgekit/docs/project-maintenance.md",
            "Choose an action:",
            "[m] keep the local file and export the new template sample plus diff",
            "manual-merge item",
        ]:
            if marker not in ask_result.stdout:
                fail(f"interactive review-needed ask output missing marker: {marker}")
        if ask_maintenance.read_bytes() != ask_before:
            fail("show diff followed by manual-merge must not overwrite the review-needed file")
        ask_review = json.loads((ask_target / ".forgekit/reports/upgrade-review-needed.json").read_text(encoding="utf-8"))
        if not any(item["status"] == "resolved_manual_merge" for item in ask_review["items"]):
            fail("interactive manual-merge must record resolved_manual_merge")
        abort_target = temp_parent / "unified-old-ask-abort"
        abort_state = write_state(abort_target, "0.38.0")
        abort_maintenance = abort_target / ".forgekit/docs/project-maintenance.md"
        abort_maintenance.parent.mkdir(parents=True, exist_ok=True)
        abort_maintenance.write_text("# User-maintained project guide\n", encoding="utf-8")
        abort_state_before = abort_state.read_bytes()
        abort_file_before = abort_maintenance.read_bytes()
        abort_result = run_pty([sys.executable, str(script), "--target", str(abort_target)], cwd=repo, input_text="2\ny\na\n", check=False)
        if abort_result.returncode == 0 or "aborted" not in abort_result.stdout:
            fail("interactive abort must stop the migration")
        if abort_state.read_bytes() != abort_state_before or abort_maintenance.read_bytes() != abort_file_before:
            fail("interactive abort must not write migration state or targets")
        abort_review = json.loads((abort_target / ".forgekit/reports/upgrade-review-needed.json").read_text(encoding="utf-8"))
        if not any(item["status"] == "aborted" for item in abort_review["items"]):
            fail("interactive abort must record aborted status")
        zh_ask_target = temp_parent / "unified-old-ask-review-zh"
        write_state(zh_ask_target, "0.38.0")
        zh_maintenance = zh_ask_target / ".forgekit/docs/project-maintenance.md"
        zh_maintenance.parent.mkdir(parents=True, exist_ok=True)
        zh_maintenance.write_text("# User-maintained project guide\n", encoding="utf-8")
        zh_result = run_pty([sys.executable, str(script), "--target", str(zh_ask_target)], cwd=repo, input_text="1\ny\nm\n")
        for marker in [
            "请选择显示语言 / Select display language:",
            "[warning] ForgeKit 发现 1 个文件不能安全自动覆盖。",
            "原因：",
            "影响：",
            "建议：",
            "[m] 保留本地文件，并生成新版模板参考文件和差异文件",
            "项目已升级到 0.43.2",
        ]:
            if marker not in zh_result.stdout:
                fail(f"Chinese interactive review-needed output missing marker: {marker}")

    apply_target = temp_parent / "unified-old-apply"
    apply_state = write_state(apply_target, "0.38.0")
    existing_maintenance = apply_target / ".forgekit/docs/project-maintenance.md"
    existing_maintenance.parent.mkdir(parents=True, exist_ok=True)
    existing_maintenance.write_text("# User-maintained project guide\n", encoding="utf-8")
    existing_maintenance_before = existing_maintenance.read_bytes()
    apply_business = apply_target / "docs/business.md"
    apply_business.parent.mkdir(parents=True)
    apply_business.write_text("business truth\n", encoding="utf-8")
    apply_business_before = apply_business.read_bytes()
    apply_state_before_no_policy = apply_state.read_bytes()
    no_policy = run([sys.executable, str(script), "--target", str(apply_target), "--yes"], cwd=repo, check=False)
    if no_policy.returncode == 0 or "Review-needed item requires a policy in non-interactive mode" not in no_policy.stdout:
        fail("unified --yes without review-needed policy must stop before writing")
    for marker in ["--review-needed-policy manual-merge", "--review-needed-policy replace-template"]:
        if marker not in no_policy.stdout:
            fail(f"unified no-policy stop missing one-line command marker: {marker}")
    if apply_state.read_bytes() != apply_state_before_no_policy:
        fail("unified --yes without policy must not rewrite state")
    if existing_maintenance.read_bytes() != existing_maintenance_before or apply_business.read_bytes() != apply_business_before:
        fail("unified --yes without policy must not write migration targets")
    applied = run([
        sys.executable, str(script), "--target", str(apply_target), "--yes",
        "--review-needed-policy", "manual-merge",
    ], cwd=repo)
    if "Safe migration apply completed through forgekit-upgrade.py" not in applied.stdout:
        fail("unified --yes with manual-merge policy must delegate to forgekit-upgrade.py apply --safe")
    applied_state = json.loads(apply_state.read_text(encoding="utf-8"))
    if applied_state.get("forgekit_version") != "0.43.2":
        fail("unified --yes did not advance state through safe migrations")
    if "manual-merge item" not in applied.stdout or "fully updated" in applied.stdout:
        fail("manual-merge upgrade must report manual-merge item without claiming fully updated")
    if existing_maintenance.read_bytes() != existing_maintenance_before:
        fail("partial-upgrade rerun overwrote a user-modified managed doc")
    if apply_business.read_bytes() != apply_business_before:
        fail("unified safe apply must not modify business docs")
    keep_report = json.loads((apply_target / ".forgekit/reports/upgrade-review-needed.json").read_text(encoding="utf-8"))
    if not any(item["status"] == "resolved_manual_merge" for item in keep_report["items"]):
        fail("unified manual-merge must record resolved_manual_merge")
    alias_target = temp_parent / "unified-old-keep-local-alias"
    write_state(alias_target, "0.38.0")
    alias_maintenance = alias_target / ".forgekit/docs/project-maintenance.md"
    alias_maintenance.parent.mkdir(parents=True, exist_ok=True)
    alias_maintenance.write_text("# User-maintained project guide\n", encoding="utf-8")
    alias_result = run([
        sys.executable, str(script), "--target", str(alias_target), "--yes",
        "--review-needed-policy", "keep-local",
    ], cwd=repo)
    if "keep-local is treated as manual-merge" not in alias_result.stdout or "manual-merge item" not in alias_result.stdout:
        fail("keep-local policy alias must behave as manual-merge")
    applied_state_before = apply_state.read_bytes()
    rerun = run([sys.executable, str(script), "--target", str(apply_target), "--yes"], cwd=repo)
    if "Detected action: up-to-date" not in rerun.stdout or "No files were changed" not in rerun.stdout:
        fail("successful upgrade rerun must report up-to-date without writes")
    if apply_state.read_bytes() != applied_state_before:
        fail("up-to-date rerun rewrote state.json")

    replace_target = temp_parent / "unified-old-replace-template"
    write_state(replace_target, "0.38.0")
    replace_maintenance = replace_target / ".forgekit/docs/project-maintenance.md"
    replace_maintenance.parent.mkdir(parents=True, exist_ok=True)
    replace_maintenance.write_text("# User-maintained project guide\n", encoding="utf-8")
    replace_business = replace_target / "docs/business.md"
    replace_business.parent.mkdir(parents=True)
    replace_business.write_text("business truth\n", encoding="utf-8")
    replace_business_before = replace_business.read_bytes()
    replaced = run([
        sys.executable, str(script), "--target", str(replace_target), "--yes",
        "--review-needed-policy", "replace-template",
    ], cwd=repo)
    if "project is fully updated to 0.43.2" not in replaced.stdout:
        fail("replace-template upgrade must report fully updated")
    if replace_maintenance.read_bytes() == b"# User-maintained project guide\n":
        fail("replace-template policy did not replace the review-needed target file")
    if replace_business.read_bytes() != replace_business_before:
        fail("replace-template policy must not modify unrelated files")
    replace_report = json.loads((replace_target / ".forgekit/reports/upgrade-review-needed.json").read_text(encoding="utf-8"))
    if not any(item["status"] == "resolved_replace_template" for item in replace_report["items"]):
        fail("replace-template must record resolved_replace_template")

    legacy = temp_parent / "unified-legacy"
    (legacy / ".forgekit").mkdir(parents=True)
    legacy_result = run([sys.executable, str(script), "--target", str(legacy), "--yes"], cwd=repo)
    if "Detected action: legacy-adoption" not in legacy_result.stdout or "No automatic upgrade" not in legacy_result.stdout:
        fail("unified legacy project must receive adoption guidance")
    if (legacy / ".forgekit/state.json").exists():
        fail("unified legacy handling must not create state.json")
    force_legacy = run(
        [sys.executable, str(script), "--target", str(legacy), "--force-init", "--yes"],
        cwd=repo,
        check=False,
    )
    if force_legacy.returncode == 0 or "only valid when ForgeKit is not installed" not in (force_legacy.stdout + force_legacy.stderr):
        fail("--force-init must refuse legacy or installed ForgeKit projects")

    early_legacy = temp_parent / "unified-early-legacy"
    (early_legacy / "governance").mkdir(parents=True)
    (early_legacy / ".codex").mkdir()
    early_result = run([sys.executable, str(script), "--target", str(early_legacy)], cwd=repo)
    if "Detected action: legacy-adoption" not in early_result.stdout:
        fail("unified entry must recognize pre-boundary ForgeKit markers as legacy adoption")
    if (early_legacy / ".forgekit/state.json").exists():
        fail("early legacy detection must not create state.json")

    future = temp_parent / "unified-future"
    write_state(future, "0.44.0")
    future_result = run([sys.executable, str(script), "--target", str(future)], cwd=repo, check=False)
    if future_result.returncode == 0 or "Detected action: stop-toolkit-too-old" not in (future_result.stdout + future_result.stderr):
        fail("unified entry must stop when the project version is newer than ForgeKitRoot")


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
        ".forgekit/upgrade-export/0.43.0/.forgekit/docs/project-plan.md",
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
        ".forgekit/upgrade/candidates/0.43.0/.forgekit/docs/project-plan.md",
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


def assert_archive_capsule(target):
    script = target / "scripts/archive-capsule.py"
    change = target / ".forgekit/changes/capsule-phase"
    change.mkdir(parents=True, exist_ok=True)
    (change / "proposal.md").write_text("Status: done\nRisk: medium\n", encoding="utf-8")
    legacy = target / ".forgekit/archive/legacy-v1/keep.md"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("legacy archive stays in place\n", encoding="utf-8")
    business = target / "docs/business-capsule-marker.md"
    business.parent.mkdir(parents=True, exist_ok=True)
    business.write_text("business docs stay unchanged\n", encoding="utf-8")

    current_docs_before = {
        path.relative_to(target).as_posix(): path.read_bytes()
        for path in (target / ".forgekit/docs").rglob("*")
        if path.is_file()
    }
    protected_before = {
        "legacy": legacy.read_bytes(),
        "business": business.read_bytes(),
        "state": (target / ".forgekit/state.json").read_bytes(),
        "lock": (target / ".forgekit/template-lock.json").read_bytes(),
    }
    run([
        sys.executable, str(script), "plan", "--repo-root", ".",
        "--name", "phase-close", "--phase", "Phase Close", "--reason", "phase complete",
        "--item", ".forgekit/changes/capsule-phase",
    ], cwd=target)
    plan_path = target / ".forgekit/archive-capsule-plan.md"
    if not plan_path.is_file() or not change.is_dir():
        fail("archive capsule plan must exist without moving the source")
    plan_text = plan_path.read_text(encoding="utf-8")
    for marker in ["Status: report-only", "Mode: archive-capsule-plan", "Archive-Status: candidate"]:
        if marker not in plan_text:
            fail(f"archive capsule plan missing marker: {marker}")

    refused = run([
        sys.executable, str(script), "apply", "--repo-root", ".",
        "--plan", ".forgekit/archive-capsule-plan.md",
    ], cwd=target, check=False)
    if refused.returncode == 0 or "requires --confirm" not in (refused.stdout + refused.stderr):
        fail("archive capsule apply without --confirm must refuse")
    if not change.is_dir():
        fail("refused archive capsule apply must not move the source")

    run([
        sys.executable, str(script), "apply", "--repo-root", ".",
        "--plan", ".forgekit/archive-capsule-plan.md", "--confirm",
    ], cwd=target)
    target_match = re.search(r"(?m)^Archive-Target:\s*(.+)$", plan_text)
    if not target_match:
        fail("archive capsule plan missing Archive-Target")
    capsule = target / target_match.group(1).strip()
    if change.exists():
        fail("archive capsule apply must move the planned source")
    for relative in ["archive-summary.md", "archived-items.md", "items/changes/capsule-phase/proposal.md"]:
        if not (capsule / relative).is_file():
            fail(f"archive capsule output missing: {relative}")
    index = target / ".forgekit/archive/index.md"
    if not index.is_file() or "phase-close" not in index.read_text(encoding="utf-8"):
        fail("archive capsule apply must create/update archive index")
    summary = (capsule / "archive-summary.md").read_text(encoding="utf-8")
    for marker in ["Archive ID", "Verification Evidence", "Related Source IDs", "How to Find This Later"]:
        if marker not in summary:
            fail(f"archive summary missing marker: {marker}")
    if protected_before["legacy"] != legacy.read_bytes():
        fail("archive capsule must not rewrite legacy archive")
    if protected_before["business"] != business.read_bytes():
        fail("archive capsule must not modify business docs")
    if protected_before["state"] != (target / ".forgekit/state.json").read_bytes():
        fail("archive capsule must not modify state.json")
    if protected_before["lock"] != (target / ".forgekit/template-lock.json").read_bytes():
        fail("archive capsule must not modify template-lock.json")
    current_docs_after = {
        path.relative_to(target).as_posix(): path.read_bytes()
        for path in (target / ".forgekit/docs").rglob("*")
        if path.is_file()
    }
    if current_docs_before != current_docs_after:
        fail("archive capsule must not modify current docs")


def assert_current_docs_integrity(repo, target, temp_parent):
    checker = repo / "scripts/check-current-docs-integrity.py"

    def make_case(name, status="In Progress"):
        case = temp_parent / name
        shutil.copytree(target, case)
        docs = case / ".forgekit/docs"
        (docs / "task-board.md").write_text(
            "# 项目任务看板\n\n## 当前重点\n\n"
            "| Task ID | 标题 | 状态 | Source ID |\n| --- | --- | --- | --- |\n"
            f"| TASK-20260611-001 | 当前任务 | {status} | SRC-20260611-001 |\n",
            encoding="utf-8",
        )
        (docs / "task-intake.md").write_text(
            "# 工作来源台账\n\n## Current Source Records\n\n"
            "Source ID: SRC-20260611-001\nOriginal Text: 当前任务原文\nHuman Review: confirmed\n",
            encoding="utf-8",
        )
        (docs / "risk-register.md").write_text(
            "# 风险登记册\n\n| ID | 风险 | 状态 |\n| --- | --- | --- |\n"
            "| RISK-20260611-001 | 当前交付风险 | Open |\n",
            encoding="utf-8",
        )
        (docs / "traceability.md").write_text(
            "# 追踪矩阵\n\n| ID | 关联 ID | 状态 |\n| --- | --- | --- |\n"
            "| TASK-20260611-001 | SRC-20260611-001, TEST-20260611-001 | In Progress |\n",
            encoding="utf-8",
        )
        (docs / "testing.md").write_text(
            "# 测试文档\n\n## 当前验证基线\n\n"
            "| 场景 | 命令 | 通过标准 |\n| --- | --- | --- |\n| API smoke | pytest -q | exit 0 |\n",
            encoding="utf-8",
        )
        return case

    normal = make_case("integrity-pass", "Review")
    passed = run([sys.executable, str(checker), "--repo-root", str(normal)], cwd=repo)
    if "Status: passed" not in passed.stdout:
        fail("complete current docs fixture must pass integrity check")

    source_broken = make_case("integrity-source-broken")
    (source_broken / ".forgekit/docs/task-intake.md").write_text(
        "# 工作来源台账\n\nSource ID: SRC-EXAMPLE-001\nOriginal Text: 待补充\n",
        encoding="utf-8",
    )
    broken = run([sys.executable, str(checker), "--repo-root", str(source_broken)], cwd=repo, check=False)
    if broken.returncode != 1 or "missing-source-record" not in broken.stdout:
        fail("missing Source Record must be a blocking integrity failure")

    risk_broken = make_case("integrity-risk-placeholder")
    shutil.copyfile(repo / "project-template/docs/risk-register.md", risk_broken / ".forgekit/docs/risk-register.md")
    risk = run([sys.executable, str(checker), "--repo-root", str(risk_broken)], cwd=repo, check=False)
    if risk.returncode != 1 or "placeholder-only-risk-register" not in risk.stdout:
        fail("placeholder-only risk-register must block active work integrity")

    trace_broken = make_case("integrity-trace-placeholder")
    shutil.copyfile(repo / "project-template/docs/traceability.md", trace_broken / ".forgekit/docs/traceability.md")
    trace = run([sys.executable, str(checker), "--repo-root", str(trace_broken)], cwd=repo, check=False)
    if trace.returncode != 1 or "placeholder-only-traceability" not in trace.stdout:
        fail("placeholder-only traceability must block active work integrity")

    testing_broken = make_case("integrity-testing-placeholder", "Backend Ready")
    shutil.copyfile(repo / "project-template/docs/testing.md", testing_broken / ".forgekit/docs/testing.md")
    testing = run([sys.executable, str(checker), "--repo-root", str(testing_broken)], cwd=repo, check=False)
    if testing.returncode != 1 or "missing-testing-baseline" not in testing.stdout:
        fail("review-ready task without testing baseline must block integrity")

    examples = temp_parent / "integrity-examples"
    shutil.copytree(target, examples)
    examples_result = run([sys.executable, str(checker), "--repo-root", str(examples)], cwd=repo)
    if "Active tasks: 0" not in examples_result.stdout or "Status: passed" not in examples_result.stdout:
        fail("template example IDs must not be treated as real active tasks")

    archive_case = source_broken
    change = archive_case / ".forgekit/changes/blocked-capsule"
    change.mkdir(parents=True)
    (change / "proposal.md").write_text("Status: done\nRisk: medium\n", encoding="utf-8")
    capsule_script = archive_case / "scripts/archive-capsule.py"
    run([
        sys.executable, str(capsule_script), "plan", "--repo-root", ".",
        "--name", "evidence-snapshot", "--reason", "active-work evidence snapshot",
        "--item", ".forgekit/changes/blocked-capsule",
    ], cwd=archive_case)
    refused = run([
        sys.executable, str(capsule_script), "apply", "--repo-root", ".",
        "--plan", ".forgekit/archive-capsule-plan.md", "--confirm",
    ], cwd=archive_case, check=False)
    if refused.returncode == 0 or "blocked by current docs integrity" not in (refused.stdout + refused.stderr):
        fail("archive apply must stop on blocking current docs integrity failure")
    if not change.is_dir():
        fail("blocked archive apply must not move planned items")

    migration_case = temp_parent / "integrity-migration"
    shutil.copytree(target, migration_case)
    state_path = migration_case / ".forgekit/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8-sig"))
    state["forgekit_version"] = "0.40.1"
    state["features"].pop("active_current_docs_integrity_guard", None)
    state["features"].pop("multi_project_scoped_docs_available", None)
    state["features"].pop("multi_project_scoped_docs_enabled", None)
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    existing = migration_case / ".forgekit/docs/current-docs-integrity.md"
    existing.write_text("# User-owned integrity guidance\n", encoding="utf-8")
    before = existing.read_bytes()
    upgrade = repo / "scripts/forgekit-upgrade.py"
    first = run([
        sys.executable, str(upgrade), "apply", "--safe", "--repo-root", str(migration_case),
        "--review-needed-policy", "manual-merge",
    ], cwd=repo)
    if "resolved-manual-merge" not in first.stdout or existing.read_bytes() != before:
        fail("v0.40.2 migration must preserve a different existing integrity guide")
    migrated = json.loads(state_path.read_text(encoding="utf-8"))
    if migrated.get("forgekit_version") != "0.43.2" or migrated["features"].get("active_current_docs_integrity_guard") is not True:
        fail("migration chain did not update state through v0.43.2")
    second = run([sys.executable, str(upgrade), "apply", "--safe", "--repo-root", str(migration_case)], cwd=repo)
    if "No migration is required; no files were changed" not in second.stdout:
        fail("v0.40.2 migration rerun must be a no-op/current result")
    if existing.read_bytes() != before:
        fail("v0.40.2 migration rerun overwrote the user-owned guide")


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
    assert_manifest_checksum_stability(repo)
    assert_json(repo / "project-template" / ".forgekit" / "state.json")
    assert_json(repo / "migrations" / "0.36.0" / "migration.json")
    assert_json(repo / "project-template" / "migrations" / "0.36.0" / "migration.json")
    assert_json(repo / "migrations" / "0.37.0" / "migration.json")
    assert_json(repo / "project-template" / "migrations" / "0.37.0" / "migration.json")
    assert_json(repo / "migrations" / "0.38.0" / "migration.json")
    assert_json(repo / "project-template" / "migrations" / "0.38.0" / "migration.json")
    assert_json(repo / "migrations" / "0.39.0" / "migration.json")
    assert_json(repo / "project-template" / "migrations" / "0.39.0" / "migration.json")
    assert_json(repo / "migrations" / "0.40.0" / "migration.json")
    assert_json(repo / "project-template" / "migrations" / "0.40.0" / "migration.json")
    assert_json(repo / "migrations" / "0.40.1" / "migration.json")
    assert_json(repo / "project-template" / "migrations" / "0.40.1" / "migration.json")
    assert_json(repo / "migrations" / "0.40.2" / "migration.json")
    assert_json(repo / "project-template" / "migrations" / "0.40.2" / "migration.json")
    assert_json(repo / "migrations" / "0.41.0" / "migration.json")
    assert_json(repo / "project-template" / "migrations" / "0.41.0" / "migration.json")
    assert_json(repo / "migrations" / "0.41.1" / "migration.json")
    assert_json(repo / "project-template" / "migrations" / "0.41.1" / "migration.json")
    assert_json(repo / "migrations" / "0.42.0" / "migration.json")
    assert_json(repo / "project-template" / "migrations" / "0.42.0" / "migration.json")
    assert_json(repo / "migrations" / "0.43.0" / "migration.json")
    assert_json(repo / "project-template" / "migrations" / "0.43.0" / "migration.json")
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
    assert_independent_code_review(repo / "project-template")
    assert_context_continuity(repo / "project-template", "docs/context-continuity.md")
    assert_work_session_checkpoint(repo / "project-template", ".forgekit/docs")
    assert_reasoning_review(repo / "project-template", "docs/reasoning-review.md")
    assert_project_maintenance(repo / "project-template")
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
    assert_workflow_router(
        repo / "project-template",
        "docs/workflow-router.md",
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
        "scripts/context-continuity-runner.py",
        "project-template/scripts/context-continuity-runner.py",
        "scripts/token-monitor.py",
        "project-template/scripts/token-monitor.py",
        "scripts/auto-compact.py",
        "project-template/scripts/auto-compact.py",
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
        assert_generated_entry_checksums(repo, target)
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
        assert_independent_code_review(target)
        assert_context_continuity(target, ".forgekit/docs/context-continuity.md")
        assert_work_session_checkpoint(target, ".forgekit/docs")
        assert_reasoning_review(target, ".forgekit/docs/reasoning-review.md")
        assert_project_maintenance(target)
        assert_workspace_integrity(target, temp_parent)
        assert_project_capsule_bootstrap(target, temp_parent)
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
        assert_doc_health_report(target)
        assert_source_trace_report(target)
        assert_handoff_package(target)
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
        assert_workflow_router(
            target,
            ".forgekit/docs/workflow-router.md",
            ".forgekit/docs/document-responsibility.md",
            ".forgekit/docs/codebase-map.md",
            "AGENTS.md",
            "CLAUDE.md",
            ".codex/rules.md",
        )
        assert_absent_paths(target, [
            "scripts/forgekit-project.py",
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
        assert_versioned_migration_upgrade(repo, target, temp_parent)
        assert_unified_project_entry(repo, target, temp_parent)
        assert_no_escaped_filenames(target)
        assert_no_noise_files(target)
        assert_no_forbidden_text(target, FORBIDDEN_LEGACY_REFS, "Forbidden legacy path text found in generated project")
        run_generated_checks(target)
        assert_current_docs_integrity(repo, target, temp_parent)
        assert_archive_flow(target)
        assert_archive_capsule(target)
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
