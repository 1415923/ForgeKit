#!/usr/bin/env python3
import argparse
import datetime as _dt
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path, PurePosixPath


VALID_UPDATE_POLICIES = {"replace", "merge", "ask", "readonly"}
VALID_RENDER_MODES = {"copy", "render"}
VALID_ROLES = {
    "agent_entry",
    "boundary_config",
    "change_template",
    "codex_rule",
    "governance",
    "managed_doc",
    "metadata",
    "readme",
    "script",
    "skill",
}
EXCLUDED_SOURCE_PATHS = {
    ".forgekit/template-manifest.json",
    ".forgekit/template-lock.json",
    ".forgekit/upgrade-report.md",
    ".forgekit/archive-plan.md",
    ".forgekit/archive-apply-report.md",
}
EXCLUDED_SOURCE_PREFIXES = (
    ".forgekit/upgrade-export/",
)


def fail(message):
    raise SystemExit(f"[fail] {message}")


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Invalid JSON: {path}: {exc}")


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def normalize_posix(path):
    return str(PurePosixPath(str(path).replace("\\", "/")))


def is_relative_safe(path):
    posix = normalize_posix(path)
    pure = PurePosixPath(posix)
    return not pure.is_absolute() and ".." not in pure.parts and posix not in {"", "."}


def read_boundary(project_root):
    boundary = {
        "managed_docs_root": ".forgekit/docs",
        "change_root": ".forgekit/changes",
        "business_docs_roots": ["docs"],
    }
    path = project_root / ".forgekit" / "project-boundary.yml"
    if not path.exists():
        return boundary

    lines = path.read_text(encoding="utf-8").splitlines()
    current_key = None
    business = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("managed_docs_root:"):
            boundary["managed_docs_root"] = stripped.split(":", 1)[1].strip().strip('"')
            current_key = None
        elif stripped.startswith("change_root:"):
            boundary["change_root"] = stripped.split(":", 1)[1].strip().strip('"')
            current_key = None
        elif stripped.startswith("business_docs_roots:"):
            current_key = "business_docs_roots"
        elif current_key == "business_docs_roots" and stripped.startswith("- "):
            business.append(stripped[2:].strip().strip('"'))
        elif stripped and not stripped.startswith("#") and not stripped.startswith("- "):
            current_key = None
    if business:
        boundary["business_docs_roots"] = business
    return boundary


def expand_target_path(raw_target, boundary):
    target = raw_target.replace("${managed_docs_root}", boundary["managed_docs_root"])
    target = target.replace("${change_root}", boundary["change_root"])
    return normalize_posix(target)


def path_matches_root(path, root):
    path = normalize_posix(path).rstrip("/")
    root = normalize_posix(root).rstrip("/")
    return path == root or path.startswith(root + "/")


def validate_target_path(target_path, boundary):
    if not is_relative_safe(target_path):
        fail(f"Unsafe target_path: {target_path}")
    if path_matches_root(target_path, ".git"):
        fail(f"target_path cannot write .git: {target_path}")
    for business_root in boundary.get("business_docs_roots", []):
        if path_matches_root(target_path, business_root):
            fail(f"target_path cannot write business docs root by default: {target_path}")


def validate_manifest(manifest, template_root, check_checksums=False):
    if manifest.get("schema_version") != 1:
        fail("template-manifest schema_version must be 1")
    if not manifest.get("template_version"):
        fail("template-manifest requires template_version")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        fail("template-manifest requires non-empty files list")

    seen_sources = set()
    for index, item in enumerate(files):
        source_path = normalize_posix(item.get("source_path", ""))
        target_path = normalize_posix(item.get("target_path", ""))
        role = item.get("role")
        update_policy = item.get("update_policy")
        render_mode = item.get("render_mode")

        if not is_relative_safe(source_path):
            fail(f"Invalid source_path at files[{index}]: {source_path}")
        if source_path in EXCLUDED_SOURCE_PATHS or any(source_path.startswith(prefix) for prefix in EXCLUDED_SOURCE_PREFIXES):
            fail(f"Excluded source_path cannot be listed in manifest: {source_path}")
        if source_path in seen_sources:
            fail(f"Duplicate source_path in manifest: {source_path}")
        seen_sources.add(source_path)
        if not target_path:
            fail(f"Missing target_path for source_path: {source_path}")
        if role not in VALID_ROLES:
            fail(f"Invalid role for {source_path}: {role}")
        if update_policy not in VALID_UPDATE_POLICIES:
            fail(f"Invalid update_policy for {source_path}: {update_policy}")
        if render_mode not in VALID_RENDER_MODES:
            fail(f"Invalid render_mode for {source_path}: {render_mode}")
        if source_path.startswith("docs/") and not target_path.startswith("${managed_docs_root}/"):
            fail(f"docs source must target managed_docs_root: {source_path}")
        if source_path.startswith("changes/") and not target_path.startswith("${change_root}/"):
            fail(f"changes source must target change_root: {source_path}")

        source_file = template_root / Path(source_path)
        if not source_file.is_file():
            fail(f"Manifest source_path does not exist: {source_path}")
        actual_checksum = sha256_file(source_file)
        if check_checksums and item.get("checksum") != actual_checksum:
            fail(f"Checksum mismatch for {source_path}: manifest={item.get('checksum')} actual={actual_checksum}")


def update_manifest(args):
    repo_root = Path(args.repo_root).resolve()
    template_root = repo_root / "project-template"
    manifest_path = template_root / ".forgekit" / "template-manifest.json"
    manifest = load_json(manifest_path)
    validate_manifest(manifest, template_root, check_checksums=False)

    changed = False
    for item in manifest["files"]:
        source_path = normalize_posix(item["source_path"])
        actual = sha256_file(template_root / Path(source_path))
        if item.get("checksum") != actual:
            if args.check:
                fail(f"Checksum mismatch for {source_path}: manifest={item.get('checksum')} actual={actual}")
            item["checksum"] = actual
            changed = True

    if not args.check and changed:
        save_json(manifest_path, manifest)
        print(f"[ok] Updated manifest checksums: {manifest_path}")
    else:
        print("[ok] Template manifest check passed")


def load_manifest(repo_root):
    template_root = repo_root / "project-template"
    manifest_path = template_root / ".forgekit" / "template-manifest.json"
    manifest = load_json(manifest_path)
    validate_manifest(manifest, template_root, check_checksums=True)
    return manifest


def write_lock(args):
    repo_root = Path(args.repo_root).resolve()
    project_root = Path(args.project_root).resolve()
    manifest = load_manifest(repo_root)
    boundary = read_boundary(project_root)
    lock_path = project_root / ".forgekit" / "template-lock.json"
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    files = []
    for item in manifest["files"]:
        target_path = expand_target_path(item["target_path"], boundary)
        validate_target_path(target_path, boundary)
        target_file = project_root / Path(target_path)
        if not target_file.is_file():
            continue
        files.append({
            "source_path": normalize_posix(item["source_path"]),
            "target_path": target_path,
            "role": item["role"],
            "update_policy": item["update_policy"],
            "render_mode": item["render_mode"],
            "source_checksum": item["checksum"],
            "installed_checksum": sha256_file(target_file),
        })

    lock = {
        "schema_version": 1,
        "installed_version": manifest["template_version"],
        "installed_at": _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "managed_docs_root": boundary["managed_docs_root"],
        "change_root": boundary["change_root"],
        "files": files,
    }
    save_json(lock_path, lock)
    print("[copy] .forgekit/template-lock.json")


def classify_entry(item, lock_by_target, target_file, current_checksum):
    target_path = item["target_path_expanded"]
    if item["update_policy"] == "readonly":
        return "report_only"
    if item["update_policy"] == "ask":
        return "ask_before_writing"
    old = lock_by_target.get(target_path)
    if old is None:
        if target_file.exists():
            return "needs_merge_report"
        return "can_restore"
    if not target_file.exists():
        return "can_restore"
    old_source = old.get("source_checksum")
    new_source = item.get("checksum")
    installed = old.get("installed_checksum")
    if old_source == new_source and current_checksum == installed:
        return "skip"
    if current_checksum == installed:
        return "can_replace"
    return "needs_merge_report"


def copy_candidate(template_root, project_root, item, target_path, export_root):
    export_file = export_root / Path(target_path)
    export_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template_root / Path(item["source_path"]), export_file)


def upgrade_report(args):
    repo_root = Path(args.repo_root).resolve()
    template_root = repo_root / "project-template"
    project_root = Path(args.project_root).resolve()
    manifest = load_manifest(repo_root)
    boundary = read_boundary(project_root)
    version = manifest["template_version"]

    report_path = project_root / ".forgekit" / "upgrade-report.md"
    export_root = project_root / ".forgekit" / "upgrade-export" / version
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if export_root.exists():
        shutil.rmtree(export_root)
    export_root.mkdir(parents=True, exist_ok=True)

    lock_path = project_root / ".forgekit" / "template-lock.json"
    if not lock_path.exists():
        lines = [
            "# ForgeKit Upgrade Report",
            "",
            "Status: report-only",
            f"To: {version}",
            f"ManagedDocsRoot: {boundary['managed_docs_root']}",
            f"ChangeRoot: {boundary['change_root']}",
            "",
            "## Policy",
            "",
            "- No project files were overwritten.",
            "- No lock file was updated.",
            "- No business docs were modified.",
            "",
            "## Summary",
            "",
            "- legacy_no_lock: 1",
            "",
            f"This project does not have `.forgekit/template-lock.json`, so v{version} does not infer a baseline or create one automatically.",
        ]
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("[copy] .forgekit/upgrade-report.md")
        return

    lock = load_json(lock_path)
    lock_by_target = {normalize_posix(item.get("target_path", "")): item for item in lock.get("files", [])}
    rows = []
    summary = {
        "skip": 0,
        "can_replace": 0,
        "needs_merge_report": 0,
        "can_restore": 0,
        "ask_before_writing": 0,
        "report_only": 0,
        "read_mostly_excluded": 0,
    }

    for item in manifest["files"]:
        target_path = expand_target_path(item["target_path"], boundary)
        validate_target_path(target_path, boundary)
        item = dict(item)
        item["target_path_expanded"] = target_path
        target_file = project_root / Path(target_path)
        current_checksum = sha256_file(target_file) if target_file.is_file() else ""
        status = classify_entry(item, lock_by_target, target_file, current_checksum)
        summary[status] += 1
        copy_candidate(template_root, project_root, item, target_path, export_root)
        old = lock_by_target.get(target_path, {})
        rows.append({
            "status": status,
            "target_path": target_path,
            "role": item["role"],
            "update_policy": item["update_policy"],
            "render_mode": item["render_mode"],
            "old_source_checksum": old.get("source_checksum", ""),
            "new_source_checksum": item.get("checksum", ""),
            "installed_checksum": old.get("installed_checksum", ""),
            "current_checksum": current_checksum,
            "local_modified": bool(current_checksum and old.get("installed_checksum") and current_checksum != old.get("installed_checksum")),
        })

    lines = [
        "# ForgeKit Upgrade Report",
        "",
        "Status: report-only",
        f"From: {lock.get('installed_version', 'unknown')}",
        f"To: {version}",
        f"ManagedDocsRoot: {boundary['managed_docs_root']}",
        f"ChangeRoot: {boundary['change_root']}",
        "",
        "## Policy",
        "",
        "- No project files were overwritten.",
        "- No lock file was updated.",
        "- No business docs were modified.",
        "- `can_replace` means theoretically replaceable; it was not applied.",
        f"- Candidate templates were exported under `.forgekit/upgrade-export/{version}/`.",
        "",
        "## Summary",
        "",
    ]
    for key in ["skip", "can_replace", "needs_merge_report", "can_restore", "ask_before_writing", "report_only", "read_mostly_excluded"]:
        lines.append(f"- {key}: {summary[key]}")
    lines.extend([
        "",
        "## Files",
        "",
        "| status | target_path | role | policy | render | local_modified |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for row in rows:
        lines.append(
            f"| {row['status']} | `{row['target_path']}` | {row['role']} | {row['update_policy']} | {row['render_mode']} | {str(row['local_modified']).lower()} |"
        )
    lines.extend([
        "",
        "## Notes",
        "",
        "- `current_checksum` and `local_modified` are computed for this report only and are not written back to the lock file.",
        "- `.forgekit/upgrade-export/**` is comparison material, not current-state documentation or an active change.",
    ])
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("[copy] .forgekit/upgrade-report.md")
    print(f"[copy] .forgekit/upgrade-export/{version}")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")

    refresh = sub.add_parser("refresh")
    refresh.add_argument("--repo-root", default=Path(__file__).resolve().parents[1])
    refresh.add_argument("--check", action="store_true")

    check = sub.add_parser("check")
    check.add_argument("--repo-root", default=Path(__file__).resolve().parents[1])

    lock = sub.add_parser("install-lock")
    lock.add_argument("--repo-root", default=Path(__file__).resolve().parents[1])
    lock.add_argument("--project-root", required=True)

    upgrade = sub.add_parser("upgrade-report")
    upgrade.add_argument("--repo-root", default=Path(__file__).resolve().parents[1])
    upgrade.add_argument("--project-root", required=True)

    parser.add_argument("--check", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--repo-root", default=None, help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.command is None:
        args.command = "refresh"
        if args.repo_root is None:
            args.repo_root = Path(__file__).resolve().parents[1]

    if args.command == "check":
        args.command = "refresh"
        args.check = True
    if args.command == "refresh":
        update_manifest(args)
    elif args.command == "install-lock":
        write_lock(args)
    elif args.command == "upgrade-report":
        upgrade_report(args)
    else:
        fail(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
