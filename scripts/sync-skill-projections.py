#!/usr/bin/env python3
"""Validate or apply the manifest-declared ForgeKit Skill projection."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


EXPECTED_SOURCE_ROOT = "skills"
EXPECTED_TARGET_ROOT = "project-template/.agents/skills"
EXPECTED_MANAGED_FILES = ["SKILL.md", "agents/openai.yaml"]
REQUIRED_REPO_MARKERS = ("VERSION", ".codex-plugin/plugin.json", "project-template", "skills")
WINDOWS_UNSAFE = re.compile(r"[<>:\"|?*\x00-\x1f]")


class ProjectionError(ValueError):
    pass


@dataclass(frozen=True)
class Projection:
    skill: str
    managed_file: str
    source_relative: str
    target_relative: str
    repo_root: Path
    source: Path
    target: Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_posix_relative(value: object, label: str, *, single_segment: bool = False) -> str:
    if not isinstance(value, str) or not value:
        raise ProjectionError(f"{label} must be a non-empty POSIX relative path")
    if "\\" in value or "\x00" in value or re.match(r"^[A-Za-z]:", value):
        raise ProjectionError(f"{label} is not a normalized POSIX relative path: {value!r}")
    raw_parts = value.split("/")
    path = PurePosixPath(value)
    if path.is_absolute() or value.startswith("./") or any(part in {"", ".", ".."} for part in raw_parts):
        raise ProjectionError(f"{label} is unsafe: {value!r}")
    if WINDOWS_UNSAFE.search(value) or any(char in value for char in "[]{}"):
        raise ProjectionError(f"{label} must not contain wildcards or placeholders: {value!r}")
    if single_segment and len(path.parts) != 1:
        raise ProjectionError(f"{label} must be one directory name: {value!r}")
    return path.as_posix()


def is_reparse_point(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    attributes = getattr(info, "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def ensure_no_reparse(root: Path, path: Path, label: str) -> None:
    root = root.resolve()
    current = root
    try:
        relative = path.absolute().relative_to(root.absolute())
    except ValueError as exc:
        raise ProjectionError(f"{label} escapes repository root: {path}") from exc
    for part in relative.parts:
        current = current / part
        if current.exists() and is_reparse_point(current):
            raise ProjectionError(f"{label} crosses a symlink, junction, or reparse point: {current}")


def resolve_inside(repo_root: Path, relative: str, allowed_root: str, label: str) -> Path:
    relative = safe_posix_relative(relative, label)
    allowed = (repo_root / Path(*PurePosixPath(allowed_root).parts)).resolve()
    candidate = repo_root / Path(*PurePosixPath(relative).parts)
    ensure_no_reparse(repo_root, candidate, label)
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(allowed)
    except ValueError as exc:
        raise ProjectionError(f"{label} escapes {allowed_root}: {relative}") from exc
    return resolved


def load_plan(repo_root: Path, manifest_relative: str) -> list[Projection]:
    repo_root = repo_root.resolve()
    missing_markers = [item for item in REQUIRED_REPO_MARKERS if not (repo_root / item).exists()]
    if missing_markers:
        raise ProjectionError(
            "apply/check root is not a ForgeKit source repository; missing: " + ", ".join(missing_markers)
        )
    manifest_relative = safe_posix_relative(manifest_relative, "manifest path")
    manifest_path = resolve_inside(repo_root, manifest_relative, "config", "manifest path")
    if not manifest_path.is_file():
        raise ProjectionError(f"manifest not found: {manifest_relative}")
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProjectionError(f"invalid manifest JSON: {exc}") from exc
    if not isinstance(data, dict) or set(data) != {"schema_version", "source_root", "target_root", "entries"}:
        raise ProjectionError("manifest must contain only schema_version, source_root, target_root, and entries")
    if data["schema_version"] != 1:
        raise ProjectionError("manifest schema_version must be 1")
    if data["source_root"] != EXPECTED_SOURCE_ROOT or data["target_root"] != EXPECTED_TARGET_ROOT:
        raise ProjectionError(
            f"manifest roots must be {EXPECTED_SOURCE_ROOT!r} and {EXPECTED_TARGET_ROOT!r}"
        )
    entries = data["entries"]
    if not isinstance(entries, list) or len(entries) != 9:
        raise ProjectionError("manifest entries must contain exactly nine Skills")
    plan: list[Projection] = []
    skills: set[str] = set()
    targets: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != {"skill", "managed_files"}:
            raise ProjectionError(f"entry {index} must contain only skill and managed_files")
        skill = safe_posix_relative(entry["skill"], f"entry {index} skill", single_segment=True)
        if skill in skills:
            raise ProjectionError(f"duplicate Skill entry: {skill}")
        skills.add(skill)
        managed_files = entry["managed_files"]
        if managed_files != EXPECTED_MANAGED_FILES:
            raise ProjectionError(
                f"Skill {skill} must manage exactly {EXPECTED_MANAGED_FILES!r}, actual {managed_files!r}"
            )
        for managed_file in managed_files:
            managed_file = safe_posix_relative(managed_file, f"Skill {skill} managed file")
            source_relative = f"{EXPECTED_SOURCE_ROOT}/{skill}/{managed_file}"
            target_relative = f"{EXPECTED_TARGET_ROOT}/{skill}/{managed_file}"
            if target_relative in targets:
                raise ProjectionError(f"duplicate managed target: {target_relative}")
            targets.add(target_relative)
            source = resolve_inside(repo_root, source_relative, EXPECTED_SOURCE_ROOT, "source")
            target = resolve_inside(repo_root, target_relative, EXPECTED_TARGET_ROOT, "target")
            if ".claude" in PurePosixPath(source_relative).parts or ".claude" in PurePosixPath(target_relative).parts:
                raise ProjectionError(f"Claude adapter path is outside the common projection: {target_relative}")
            plan.append(Projection(skill, managed_file, source_relative, target_relative, repo_root, source, target))
    return plan


def render_projection(item: Projection) -> tuple[str, str]:
    source_hash = sha256_file(item.source) if item.source.is_file() else "<missing>"
    target_hash = sha256_file(item.target) if item.target.is_file() else "<missing>"
    print(
        f"Skill={item.skill} source={item.source_relative} target={item.target_relative} "
        f"source SHA-256={source_hash} target SHA-256={target_hash}"
    )
    return source_hash, target_hash


def check(plan: list[Projection]) -> bool:
    valid = True
    for item in plan:
        source_hash, target_hash = render_projection(item)
        if source_hash == "<missing>" or target_hash == "<missing>" or source_hash != target_hash:
            valid = False
    return valid


def _regular_file(path: Path) -> bool:
    try:
        return stat.S_ISREG(path.stat(follow_symlinks=False).st_mode)
    except FileNotFoundError:
        return False


def _preflight_target(item: Projection) -> None:
    relative = item.target.absolute().relative_to(item.repo_root.absolute())
    current = item.repo_root
    for part in relative.parts[:-1]:
        current = current / part
        if is_reparse_point(current):
            raise ProjectionError(f"target parent is a symlink, junction, or reparse point: {current}")
        if current.exists() and not current.is_dir():
            raise ProjectionError(f"target parent is not a directory: {current}")
    if is_reparse_point(item.target):
        raise ProjectionError(f"target is a symlink, junction, or reparse point: {item.target_relative}")
    if item.target.exists() and not _regular_file(item.target):
        raise ProjectionError(f"target is not a regular file: {item.target_relative}")


def apply(plan: list[Projection]) -> bool:
    # Complete all predictable validation before the first target byte changes.
    for item in plan:
        ensure_no_reparse(item.repo_root, item.source, "source")
        ensure_no_reparse(item.repo_root, item.target, "target")
        if not _regular_file(item.source):
            raise ProjectionError(f"source is missing or not a regular file: {item.source_relative}")
        _preflight_target(item)
    print("Skill projection apply plan:")
    for item in plan:
        print(f"COPY {item.source_relative} -> {item.target_relative}")
    for item in plan:
        item.target.parent.mkdir(parents=True, exist_ok=True)
        temporary = item.target.parent / f".tmp-{item.target.name}-{uuid.uuid4().hex}"
        try:
            shutil.copyfile(item.source, temporary)
            temporary.replace(item.target)
        finally:
            temporary.unlink(missing_ok=True)
    print("Post-apply check:")
    return check(plan)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", nargs="?", choices=("check", "apply"), default=None)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--check", action="store_true", dest="check_flag")
    mode_group.add_argument("--apply", action="store_true", dest="apply_flag")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--manifest", default="config/skill-projections.json")
    args = parser.parse_args(argv)
    flag_mode = "apply" if args.apply_flag else "check" if args.check_flag else None
    if args.mode and flag_mode and args.mode != flag_mode:
        parser.error("positional mode conflicts with explicit mode flag")
    args.mode = args.mode or flag_mode or "check"
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        plan = load_plan(Path(args.repo_root), args.manifest)
        ok = apply(plan) if args.mode == "apply" else check(plan)
    except (OSError, ProjectionError) as exc:
        print(f"[fail] Skill projection {args.mode}: {exc}", file=sys.stderr)
        return 1
    if not ok:
        print(f"[fail] Skill projection {args.mode} detected missing files or content drift", file=sys.stderr)
        return 1
    print(f"[ok] Skill projection {args.mode} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
