#!/usr/bin/env python3
"""Build a temporary Stage C commit and verify LF/CRLF fresh clones without overlays."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath


class FreshCloneError(RuntimeError):
    pass


def short_temp_environment(temp_root):
    temp_root.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["TEMP"] = str(temp_root)
    environment["TMP"] = str(temp_root)
    return environment


def run(command, cwd, *, capture=True, env=None):
    result = subprocess.run(
        [str(item) for item in command], cwd=cwd, check=False,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        text=True, encoding="utf-8", errors="replace", timeout=600,
        env=env,
    )
    if result.returncode:
        rendered = (result.stdout or "") + (result.stderr or "")
        raise FreshCloneError(f"command failed ({result.returncode}): {' '.join(map(str, command))}\n{rendered}")
    return result


def nul_paths(command, cwd):
    result = subprocess.run(
        command, cwd=cwd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60
    )
    if result.returncode:
        raise FreshCloneError(result.stderr.decode("utf-8", errors="replace"))
    return [Path(item.decode("utf-8")) for item in result.stdout.split(b"\0") if item]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def remove_tree(path):
    def make_writable(function, target, _exc):
        os.chmod(target, 0o700)
        function(target)
    shutil.rmtree(path, onexc=make_writable)


def construct_commit(repo, staging):
    run(["git", "-c", "core.autocrlf=false", "clone", "--no-local", str(repo), str(staging)], repo)
    deleted = nul_paths(["git", "diff", "--name-only", "--diff-filter=D", "-z"], repo)
    unexpected = [path for path in deleted if path.as_posix() != "usage.html"]
    if unexpected:
        raise FreshCloneError(f"fresh-clone fixture has unexpected tracked deletions: {unexpected}")
    changed = nul_paths(["git", "diff", "--name-only", "--diff-filter=ACMRTUXB", "-z"], repo)
    staged = nul_paths(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB", "-z"], repo)
    untracked = nul_paths(["git", "ls-files", "--others", "--exclude-standard", "-z"], repo)
    paths = sorted(set(changed + staged + untracked), key=lambda path: path.as_posix())
    for relative in paths:
        if relative.as_posix() == "usage.html":
            continue
        source = repo / relative
        target = staging / relative
        if not source.is_file():
            raise FreshCloneError(f"fresh-clone fixture only accepts files: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    add_paths = [path.as_posix() for path in paths if path.as_posix() != "usage.html"]
    if add_paths:
        run(["git", "add", "--", *add_paths], staging)
    run([
        "git", "-c", "user.name=ForgeKit Fresh Clone Gate",
        "-c", "user.email=forgekit-fresh-clone@example.invalid",
        "commit", "-m", "temporary Stage C fresh-clone fixture",
    ], staging)
    status = run(["git", "status", "--porcelain"], staging).stdout.strip()
    if status:
        raise FreshCloneError(f"temporary commit is not clean: {status}")
    usage_status = run(["git", "show", "--format=", "--name-status", "HEAD"], staging).stdout
    if "D\tusage.html" in usage_status:
        raise FreshCloneError("temporary commit included the user-owned usage.html deletion")
    return run(["git", "rev-parse", "HEAD"], staging).stdout.strip()


def stage_c_byte_paths(repo):
    sys.path.insert(0, str(repo / "scripts"))
    import importlib.util
    validator_path = repo / "scripts/validate-stage-c-skills.py"
    spec = importlib.util.spec_from_file_location("fresh_clone_stage_c", validator_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    paths = {Path(".gitattributes"), Path("project-template/.gitattributes")}
    for source, target, _ in module.projection_managed_paths(repo):
        paths.add(source)
        paths.add(target)
    manifest = json.loads(
        (repo / "project-template/.forgekit/template-manifest.json").read_text(encoding="utf-8")
    )
    for item in manifest["files"]:
        paths.add(Path("project-template") / item["source_path"])
    draft = repo / ".forgekit/changes/v045-rule-ownership-skill-convergence/stage-b-migration-draft/0.45.0"
    for branch in ("baseline", "files"):
        for item in (draft / branch).rglob("*"):
            if item.is_file():
                paths.add(item.relative_to(repo))
    paths.update({
        Path("project-template/.forgekit/template-manifest.json"),
        Path(".forgekit/changes/v045-rule-ownership-skill-convergence/stage-b-migration-draft/0.45.0/migration.json"),
    })
    return sorted(paths, key=lambda path: path.as_posix())


def verify_clone(clone, mode, full, temp_root):
    evidence = {"mode": mode, "paths": {}, "commands": {}}
    environment = short_temp_environment(temp_root)
    status = run(["git", "status", "--porcelain"], clone).stdout.strip()
    if status:
        raise FreshCloneError(f"{mode} fresh clone is dirty: {status}")
    for relative in stage_c_byte_paths(clone):
        posix = relative.as_posix()
        blob = subprocess.run(
            ["git", "show", f"HEAD:{posix}"], cwd=clone, check=False,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60,
        )
        if blob.returncode:
            raise FreshCloneError(f"{mode}: missing Git blob for {posix}")
        working = (clone / relative).read_bytes()
        if blob.stdout != working:
            raise FreshCloneError(
                f"{mode}: byte-exact checkout mismatch for {posix}; "
                f"blob={sha256(blob.stdout)} working={sha256(working)}"
            )
        attr = run(["git", "check-attr", "text", "eol", "--", posix], clone).stdout.strip()
        if "text: set" not in attr or "eol: lf" not in attr:
            raise FreshCloneError(f"{mode}: checkout attributes are not text/eol=lf for {posix}: {attr}")
        evidence["paths"][posix] = {
            "blob_sha256": sha256(blob.stdout),
            "working_sha256": sha256(working),
            "attributes": attr,
        }
    commands = [
        ("stage_c", [sys.executable, "-B", "scripts/validate-stage-c-skills.py"]),
        ("migration", [sys.executable, "-B", "scripts/validate-stage-b-entry-migration.py"]),
        ("projection", [sys.executable, "-B", "scripts/sync-skill-projections.py", "check"]),
        ("template", [shutil.which("pwsh") or "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ".\\scripts\\validate-template.ps1"]),
    ]
    if full:
        commands.append(("smoke", [sys.executable, "-B", "scripts/smoke-test.py", "--repo-root", str(clone)]))
    for label, command in commands:
        run(command, clone, env=environment)
        evidence["commands"][label] = "PASS"
    return evidence


def verify_missing_attribute_mutation(staging, temp):
    attributes = staging / ".gitattributes"
    text = attributes.read_text(encoding="utf-8")
    needle = "*.md text eol=lf\n"
    if needle not in text:
        raise FreshCloneError("mutation setup could not find the root Markdown LF rule")
    attributes.write_text(text.replace(needle, "", 1), encoding="utf-8", newline="\n")
    run(["git", "add", "--", ".gitattributes"], staging)
    run([
        "git", "-c", "user.name=ForgeKit Fresh Clone Gate",
        "-c", "user.email=forgekit-fresh-clone@example.invalid",
        "commit", "-m", "temporary missing LF rule mutation",
    ], staging)
    clone = temp / "bad"
    run(["git", "-c", "core.autocrlf=true", "clone", "--no-local", str(staging), str(clone)], temp)
    result = subprocess.run(
        [sys.executable, "-B", "scripts/validate-stage-c-skills.py"], cwd=clone,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
        errors="replace", check=False, timeout=60,
    )
    rendered = result.stdout + result.stderr
    if result.returncode == 0 or "checkout-contract" not in rendered:
        raise FreshCloneError("missing Markdown LF rule mutation did not fail the formal checkout contract")
    relative = "skills/project-init/SKILL.md"
    blob = subprocess.run(
        ["git", "show", f"HEAD:{relative}"], cwd=clone, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60,
    ).stdout
    working = (clone / relative).read_bytes()
    if blob == working:
        raise FreshCloneError("missing Markdown LF rule mutation did not expose an autocrlf=true byte mismatch")
    return {
        "validator_exit_code": result.returncode,
        "diagnostic": "checkout-contract",
        "path": relative,
        "blob_sha256": sha256(blob),
        "working_sha256": sha256(working),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--full", action="store_true", help="also run complete smoke in both clones")
    parser.add_argument("--mutation-check", action="store_true", help="prove removal of the Markdown LF rule fails")
    parser.add_argument("--temp-root", default=None)
    args = parser.parse_args(argv)
    repo = Path(args.repo_root).resolve()
    if args.temp_root:
        parent = Path(args.temp_root).resolve()
    else:
        windows_short_root = Path("D:/tmp")
        parent = windows_short_root if os.name == "nt" and windows_short_root.is_dir() else None
    temp = Path(tempfile.mkdtemp(prefix="fc-", dir=parent))
    evidence = {"temporary_commit": None, "clones": {}}
    try:
        staging = temp / "s"
        evidence["temporary_commit"] = construct_commit(repo, staging)
        if args.full:
            snapshot_temp = temp / "t"
            run(
                [sys.executable, "-B", "scripts/smoke-test.py", "--repo-root", str(staging)],
                staging,
                env=short_temp_environment(snapshot_temp),
            )
            evidence["working_tree_snapshot"] = {
                "smoke": "PASS",
                "git_directory": ".git",
                "usage_html": "HEAD materialized; user deletion excluded",
            }
        for mode in ("false", "true"):
            clone = temp / ("lf" if mode == "false" else "cr")
            run(["git", "-c", f"core.autocrlf={mode}", "clone", "--no-local", str(staging), str(clone)], temp)
            evidence["clones"][mode] = verify_clone(clone, mode, args.full, temp / "t")
        if args.mutation_check:
            evidence["missing_lf_rule_mutation"] = verify_missing_attribute_mutation(staging, temp)
        print(json.dumps(evidence, indent=2, ensure_ascii=False))
        print("[ok] fresh-clone LF/CRLF gate passed without post-clone overlays")
        return 0
    except (OSError, subprocess.SubprocessError, FreshCloneError) as exc:
        print(f"[fail] fresh-clone LF/CRLF gate: {exc}", file=sys.stderr)
        return 1
    finally:
        remove_tree(temp)


if __name__ == "__main__":
    raise SystemExit(main())
