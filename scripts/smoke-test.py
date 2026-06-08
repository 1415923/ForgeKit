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
    "docs/codebase-map.md",
    "docs/local-toolchain.md",
    "docs/version-roadmap.md",
    "docs/changelog.md",
    "governance/ai-engineering-loop.md",
    "changes/README.md",
    "changes/_template/proposal.md",
    "changes/_template/design.md",
    "changes/_template/tasks.md",
    "changes/_template/verification.md",
    "changes/_template/review.md",
    "changes/_template/ship.md",
    "changes/_template/retro.md",
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


def assert_json(path):
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Invalid JSON: {path}: {exc}")


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
    assert_skill_frontmatter(repo / "skills")
    assert_skill_frontmatter(repo / "project-template" / ".agents" / "skills")

    temp_parent = Path(tempfile.mkdtemp(prefix="forgekit-smoke-"))
    target = temp_parent / "generated"
    try:
        init_project(repo, target)
        assert_paths(target, REQUIRED_GENERATED_PATHS)
        assert_no_escaped_filenames(target)
        assert_no_forbidden_text(target, FORBIDDEN_LEGACY_REFS, "Forbidden legacy path text found in generated project")
        run_generated_checks(target)
    finally:
        if args.keep_temp:
            print(f"[info] temp kept: {temp_parent}")
        else:
            shutil.rmtree(temp_parent, ignore_errors=True)

    print("[ok] Smoke test passed")


if __name__ == "__main__":
    main()
