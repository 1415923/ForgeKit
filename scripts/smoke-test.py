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
    ".forgekit/docs/document-lifecycle.md",
    ".forgekit/archive/README.md",
    ".forgekit/archive/changes/README.md",
    ".forgekit/archive/releases/README.md",
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
    if lock.get("installed_version") != "0.21.0":
        fail("template-lock installed_version must be 0.21.0")
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
        ".forgekit/upgrade-export/0.21.0/.forgekit/docs/project-plan.md",
    ])


def write_change(root, change_id, metadata, files):
    change_dir = root / ".forgekit" / "changes" / change_id
    change_dir.mkdir(parents=True, exist_ok=True)
    if metadata is not None:
        (change_dir / "proposal.md").write_text(metadata, encoding="utf-8")
    for name in files:
        (change_dir / name).write_text(f"# {name}\n", encoding="utf-8")


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
    reference_report_path.unlink()
    run([sys.executable, "scripts/archive-changes.py", "--dry-run"], cwd=target)

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
            "archive",
        ])
        assert_boundary_config(target / ".forgekit" / "project-boundary.yml")
        assert_manifest_lock(target)
        assert_no_escaped_filenames(target)
        assert_no_forbidden_text(target, FORBIDDEN_LEGACY_REFS, "Forbidden legacy path text found in generated project")
        run_generated_checks(target)
        assert_archive_flow(target)
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
