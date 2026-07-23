#!/usr/bin/env python3
"""Validate the finite, structured ForgeKit v0.45.0 release-preparation contract."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


RELEASE_VERSION = "0.45.0"
PREVIOUS_VERSION = "0.44.1"
DRAFT = Path(".forgekit/changes/v045-rule-ownership-skill-convergence/stage-b-migration-draft/0.45.0")
FORMAL = Path("migrations/0.45.0")
TEMPLATE_FORMAL = Path("project-template/migrations/0.45.0")
PROMPTS = {
    "初始化项目.prompt.md": "$project-init",
    "初始化填充.prompt.md": "$project-bootstrap-fill",
    "代码审查.prompt.md": "$code-review",
    "版本发布.prompt.md": "$release-check",
    "架构设计.prompt.md": "$large-change-planning",
    "代码实现.prompt.md": "$large-change-planning",
    "需求分析.prompt.md": "$project-suitability",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def projected_targets(repo: Path) -> set[str]:
    config = load_json(repo / "config/skill-projections.json")
    targets = set()
    for entry in config.get("entries", []):
        skill = entry["skill"]
        for managed in entry.get("managed_files", []):
            target = f".agents/skills/{skill}/{managed}"
            if target in targets:
                raise ValueError(f"duplicate projection target: {target}")
            targets.add(target)
    return targets


def public_versions(repo: Path) -> dict[str, str]:
    return {
        "VERSION": (repo / "VERSION").read_text(encoding="utf-8").strip(),
        "codex plugin": load_json(repo / ".codex-plugin/plugin.json")["version"],
        "claude plugin": load_json(repo / ".claude-plugin/plugin.json")["version"],
        "agents marketplace": load_json(repo / ".agents/plugins/marketplace.json")["plugins"][0]["version"],
        "claude marketplace": load_json(repo / ".claude-plugin/marketplace.json")["version"],
        "claude marketplace plugin": load_json(repo / ".claude-plugin/marketplace.json")["plugins"][0]["version"],
        "template state": load_json(repo / "project-template/.forgekit/state.json")["forgekit_version"],
        "template manifest": load_json(repo / "project-template/.forgekit/template-manifest.json")["template_version"],
    }


def package_inventory(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}


def expected_template_migration_manifest_paths(repo: Path) -> set[str]:
    descriptor_path = repo / TEMPLATE_FORMAL / "migration.json"
    if not descriptor_path.is_file():
        return set()
    descriptor = load_json(descriptor_path)
    relative = {"migration.json"}
    for action in descriptor.get("actions", []):
        relative.add(action.get("baseline", ""))
        relative.add(action.get("source", ""))
    relative.discard("")
    return {f"migrations/{RELEASE_VERSION}/{item}" for item in relative}


def validate_template_migration_manifest(repo: Path, errors: list[str]) -> int:
    manifest_path = repo / "project-template/.forgekit/template-manifest.json"
    manifest = load_json(manifest_path)
    items = manifest.get("files", [])
    counts = {}
    by_path = {}
    for item in items:
        source = item.get("source_path", "")
        counts[source] = counts.get(source, 0) + 1
        by_path.setdefault(source, item)
    expected = expected_template_migration_manifest_paths(repo)
    actual_inventory = {
        f"migrations/{RELEASE_VERSION}/{relative}"
        for relative in package_inventory(repo / TEMPLATE_FORMAL)
    } if (repo / TEMPLATE_FORMAL).is_dir() else set()
    if expected != actual_inventory:
        errors.append(
            "template-migration-manifest-extra: formal descriptor/inventory mismatch: "
            f"missing={sorted(expected - actual_inventory)}, extra={sorted(actual_inventory - expected)}"
        )
    for relative in sorted(expected):
        if counts.get(relative, 0) != 1:
            errors.append(
                f"template-migration-manifest-missing: expected exactly one entry for {relative}, "
                f"actual={counts.get(relative, 0)}"
            )
            continue
        source = repo / "project-template" / relative
        if source.is_file():
            expected_checksum = "sha256:" + digest(source)
            if by_path[relative].get("checksum") != expected_checksum:
                errors.append(
                    f"template-migration-manifest-checksum: {relative}: "
                    f"manifest={by_path[relative].get('checksum')} actual={expected_checksum}"
                )
    prefix = f"migrations/{RELEASE_VERSION}/"
    extras = sorted(source for source in counts if source.startswith(prefix) and source not in expected)
    forbidden = sorted(
        source for source in counts
        if "stage-b-migration-draft" in source
        or source.startswith(".forgekit/changes/") and "/migration" in source
        or source.startswith("root/migrations/")
    )
    if extras or forbidden:
        errors.append(f"template-migration-manifest-extra: extra={sorted(set(extras + forbidden))}")
    return len(expected)


def validate_gate_wiring(repo: Path, errors: list[str]) -> None:
    path = repo / "scripts/validate-release-gate-wiring.py"
    if not path.is_file():
        errors.append("stage-e-gate-wiring-missing: scripts/validate-release-gate-wiring.py")
        return
    spec = importlib.util.spec_from_file_location("stage_e_gate_wiring", path)
    if spec is None or spec.loader is None:
        errors.append("stage-e-gate-wiring-invalid: cannot load wiring validator")
        return
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        errors.extend(module.validate_repo(repo))
    except Exception as exc:
        errors.append(f"stage-e-gate-wiring-invalid: {type(exc).__name__}: {exc}")


def validate_migration(repo: Path, errors: list[str]) -> int:
    draft_root = repo / DRAFT
    formal_root = repo / FORMAL
    template_root = repo / TEMPLATE_FORMAL
    for path in (draft_root, formal_root, template_root):
        if not path.is_dir():
            errors.append(f"migration [missing-package]: {path.relative_to(repo).as_posix()}")
            return 0

    formal_inventory = package_inventory(formal_root)
    if formal_inventory != package_inventory(template_root):
        errors.append("migration [root-template-inventory]: formal migration inventories differ")
    for relative in sorted(formal_inventory & package_inventory(template_root)):
        if (formal_root / relative).read_bytes() != (template_root / relative).read_bytes():
            errors.append(f"migration [root-template-bytes]: {relative}")

    descriptor = load_json(formal_root / "migration.json")
    template_descriptor = load_json(template_root / "migration.json")
    draft_descriptor = load_json(draft_root / "migration.json")
    if descriptor != template_descriptor:
        errors.append("migration [descriptor-mirror]: root/template descriptors differ")
    if descriptor.get("from") != PREVIOUS_VERSION or descriptor.get("to") != RELEASE_VERSION:
        errors.append("migration [version]: descriptor must be 0.44.1 -> 0.45.0")
    if descriptor.get("development_status") is not None:
        errors.append("migration [development-marker]: formal descriptor remains fixture-only")

    actions = descriptor.get("actions", [])
    draft_actions = draft_descriptor.get("actions", [])
    ids = [item.get("id") for item in actions]
    targets = [item.get("target") for item in actions]
    if len(ids) != len(set(ids)):
        errors.append("migration [duplicate-action-id]: action ids must be unique")
    if len(targets) != len(set(targets)):
        errors.append("migration [duplicate-target]: action targets must be unique")
    expected_targets = {"AGENTS.md", "CLAUDE.md"} | projected_targets(repo)
    if set(targets) != expected_targets:
        missing = sorted(expected_targets - set(targets))
        extra = sorted(set(targets) - expected_targets)
        errors.append(f"migration [action-set]: missing={missing}, extra={extra}")
    if actions != draft_actions:
        errors.append("migration [draft-provenance]: formal actions differ from approved development draft")

    for action in actions:
        action_id = action.get("id", "<unknown>")
        source = formal_root / action["source"]
        baseline = formal_root / action["baseline"]
        target = repo / "project-template" / action["target"]
        draft_source = draft_root / action["source"]
        draft_baseline = draft_root / action["baseline"]
        for kind, path in (("source", source), ("baseline", baseline), ("target", target)):
            if not path.is_file():
                errors.append(f"migration [{kind}-missing]: {action_id}: {path}")
        if not all(path.is_file() for path in (source, baseline, target, draft_source, draft_baseline)):
            continue
        if digest(source) != action.get("incoming_sha256"):
            errors.append(f"migration [incoming-checksum]: {action_id}")
        if digest(baseline) != action.get("baseline_sha256"):
            errors.append(f"migration [baseline-checksum]: {action_id}")
        if source.read_bytes() != target.read_bytes():
            errors.append(f"migration [incoming-template]: {action_id}: {action['target']}")
        if source.read_bytes() != draft_source.read_bytes() or baseline.read_bytes() != draft_baseline.read_bytes():
            errors.append(f"migration [payload-provenance]: {action_id}")

    discovered = []
    for migration in sorted((repo / "migrations").glob("*/migration.json")):
        item = load_json(migration)
        discovered.append((migration.parent.name, item.get("to")))
        if migration.parent.name != item.get("to"):
            errors.append(f"migration [directory-version]: {migration.parent.name}/{item.get('to')}")
    versions = [to for _, to in discovered]
    if versions.count(RELEASE_VERSION) != 1:
        errors.append(f"migration [production-discovery]: expected one {RELEASE_VERSION}, got {versions.count(RELEASE_VERSION)}")
    if len(versions) != len(set(versions)):
        errors.append("migration [duplicate-version]: production migration versions must be unique")
    return len(actions)


def validate_docs_and_prompts(repo: Path, errors: list[str]) -> None:
    for relative in ("README.md", "README.en.md", "CHANGELOG.md"):
        text = (repo / relative).read_text(encoding="utf-8")
        if RELEASE_VERSION not in text or "NEEDS_TEST" not in text:
            errors.append(f"docs [release-entry]: {relative} must contain {RELEASE_VERSION} and NEEDS_TEST")
    playbook = (repo / "project-template/.forgekit/docs/usage-playbook.md").read_text(encoding="utf-8")
    for skill in sorted(projected_targets(repo)):
        if not skill.endswith("/SKILL.md"):
            continue
        skill_id = skill.split("/")[2]
        if f"${skill_id}" not in playbook:
            errors.append(f"docs [usage-skill-entry]: missing ${skill_id}")
    for name, preferred in PROMPTS.items():
        text = (repo / "prompts" / name).read_text(encoding="utf-8")
        if "Deprecated compatibility prompt: v0.45-v0.46" not in text:
            errors.append(f"prompt [deprecation-window]: {name}")
        if preferred not in text:
            errors.append(f"prompt [preferred-entry]: {name}: missing {preferred}")
    manifest_paths = {entry.get("source_path") for entry in load_json(repo / "project-template/.forgekit/template-manifest.json").get("files", [])}
    if "usage.html" in manifest_paths:
        errors.append("release [usage-html]: deleted user file must not enter template manifest")


def validate_repo(repo: Path) -> tuple[list[str], dict]:
    repo = repo.resolve()
    errors: list[str] = []
    versions = public_versions(repo)
    for surface, value in versions.items():
        if value != RELEASE_VERSION:
            errors.append(f"version [{surface}]: expected {RELEASE_VERSION}, got {value}")
    action_count = validate_migration(repo, errors)
    manifest_migration_count = validate_template_migration_manifest(repo, errors)
    validate_gate_wiring(repo, errors)
    validate_docs_and_prompts(repo, errors)
    return errors, {
        "versions": versions,
        "actions": action_count,
        "template_migration_manifest": manifest_migration_count,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors, evidence = validate_repo(Path(args.repo_root))
    if errors:
        for error in errors:
            print(f"[fail] {error}")
        raise SystemExit(1)
    print(
        f"[ok] Stage E release structure passed: version={RELEASE_VERSION}, "
        f"actions={evidence['actions']}, template-migration-manifest={evidence['template_migration_manifest']}, "
        "real-model=NEEDS_TEST"
    )


if __name__ == "__main__":
    main()
