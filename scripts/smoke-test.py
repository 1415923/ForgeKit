#!/usr/bin/env python3
import argparse
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
REQUIRED_REPO_PATHS = [
    "usage.html",
    "project-template/.forgekit/project-boundary.yml",
    "project-template/.forgekit/docs/document-responsibility.md",
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
    "project-template/docs/local-toolchain.md",
    "project-template/docs/version-roadmap.md",
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
]
REQUIRED_GENERATED_PATHS = [
    "AGENTS.md",
    "CLAUDE.md",
    ".forgekit/project-boundary.yml",
    ".forgekit/template-lock.json",
    ".forgekit/docs/document-responsibility.md",
    ".forgekit/docs/codebase-map.md",
    ".forgekit/docs/local-toolchain.md",
    ".forgekit/docs/version-roadmap.md",
    ".forgekit/docs/changelog.md",
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


def assert_json(path):
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Invalid JSON: {path}: {exc}")


def assert_manifest_lock(target):
    lock_path = target / ".forgekit" / "template-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if lock.get("installed_version") != "0.17.0":
        fail("template-lock installed_version must be 0.17.0")
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
        ".forgekit/upgrade-export/0.17.0/.forgekit/docs/project-plan.md",
    ])


def assert_legacy_upgrade_no_lock(repo, target):
    target.mkdir(parents=True, exist_ok=True)
    (target / ".forgekit").mkdir(parents=True, exist_ok=True)
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
            "forgekit-legacy",
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
            "forgekit-legacy",
            "--mode",
            "Standard",
            "--upgrade",
            "--export-upgrade-templates",
        ], cwd=repo)
    report = target / ".forgekit" / "upgrade-report.md"
    if not report.is_file():
        fail("legacy upgrade must write .forgekit/upgrade-report.md")
    if (target / ".forgekit" / "template-lock.json").exists():
        fail("legacy upgrade must not create template-lock.json")
    if "legacy_no_lock" not in report.read_text(encoding="utf-8"):
        fail("legacy upgrade report must mention legacy_no_lock")


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
    assert_no_forbidden_text(repo, FORBIDDEN_LEGACY_REFS, "Forbidden legacy path text found", LEGACY_REF_ALLOWLIST)
    assert_no_forbidden_text(repo / "templates", FORBIDDEN_PRIVATE_PATHS, "Private machine paths found in templates")
    assert_json(repo / ".codex-plugin" / "plugin.json")
    assert_json(repo / ".claude-plugin" / "plugin.json")
    assert_json(repo / "project-template" / ".forgekit" / "template-manifest.json")
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
            ".forgekit/archive",
            "archive",
        ])
        assert_boundary_config(target / ".forgekit" / "project-boundary.yml")
        assert_manifest_lock(target)
        assert_no_escaped_filenames(target)
        assert_no_forbidden_text(target, FORBIDDEN_LEGACY_REFS, "Forbidden legacy path text found in generated project")
        run_generated_checks(target)
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
