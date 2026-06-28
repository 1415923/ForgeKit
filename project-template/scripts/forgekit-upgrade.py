#!/usr/bin/env python3
"""Versioned, safe-only ForgeKit migration entry point."""

import argparse
import datetime as dt
import hashlib
import json
import shutil
from pathlib import Path


MIN_SUPPORTED_VERSION = (0, 36, 0)
STATE_RELATIVE_PATH = Path(".forgekit/state.json")
SAFE_ROOTS = {".forgekit", ".codex", ".agents", ".claude", "governance", "scripts", "migrations"}


def fail(message):
    raise SystemExit(f"[fail] {message}")


def parse_version(value):
    try:
        parts = tuple(int(part) for part in str(value).strip().lstrip("v").split("."))
    except ValueError:
        fail(f"Invalid ForgeKit version: {value}")
    if len(parts) != 3:
        fail(f"ForgeKit version must use major.minor.patch: {value}")
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


def state_status(project_root):
    state_path = project_root / STATE_RELATIVE_PATH
    if not state_path.is_file():
        return None, "missing_state"
    state = load_json(state_path, "state")
    required = {
        "schema_version",
        "forgekit_version",
        "managed_docs_root",
        "change_root",
        "mode",
        "features",
        "last_upgrade",
    }
    missing = sorted(required - set(state))
    if missing:
        return state, "invalid_state:" + ",".join(missing)
    if state.get("schema_version") != 1:
        return state, "unsupported_schema"
    if parse_version(state["forgekit_version"]) < MIN_SUPPORTED_VERSION:
        return state, "unsupported_version"
    return state, "supported"


def print_adoption_guidance(project_root, reason, state=None):
    detected = "none" if state is None else state.get("forgekit_version", "unknown")
    print("ForgeKit Upgrade Check")
    print("Status: adoption-required")
    print(f"Project: {project_root}")
    print(f"Detected version: {detected}")
    print(f"Reason: {reason}")
    print("")
    print("Pre-v0.36 projects are treated as existing projects for adoption.")
    print("1. Keep existing project and ForgeKit documents unchanged.")
    print("2. Build an adoption inventory; use handoff, doc-health, or source-trace reports when useful.")
    print("3. Review boundaries and current facts with the user.")
    print("4. Create .forgekit/state.json only after explicit user confirmation and a v0.36+ initialization/adoption step.")
    print("No automatic upgrade or migration was performed.")


def load_migrations(migration_root):
    if not migration_root.is_dir():
        fail(f"Migration directory not found: {migration_root}")
    migrations = []
    for path in sorted(migration_root.glob("*/migration.json")):
        item = load_json(path, "migration")
        required = {"id", "title", "from", "to", "risk", "actions", "manual_review", "non_goals"}
        missing = sorted(required - set(item))
        if missing:
            fail(f"Migration {path} missing fields: {', '.join(missing)}")
        item["_path"] = path
        item["_from_versions"] = item["from"] if isinstance(item["from"], list) else [item["from"]]
        item["_to_version"] = parse_version(item["to"])
        migrations.append(item)
    return sorted(migrations, key=lambda item: item["_to_version"])


def migration_matches(item, current):
    return any(value == "*" or parse_version(value) == current for value in item["_from_versions"])


def pending_migrations(current, migrations):
    pending = []
    cursor = current
    for item in migrations:
        if item["_to_version"] <= cursor:
            continue
        if migration_matches(item, cursor):
            pending.append(item)
            cursor = item["_to_version"]
    return pending, cursor


def latest_available(migrations, current):
    return max([current] + [item["_to_version"] for item in migrations])


def command_check(project_root, migration_root):
    state, status = state_status(project_root)
    if status != "supported":
        print_adoption_guidance(project_root, status, state)
        return
    current = parse_version(state["forgekit_version"])
    migrations = load_migrations(migration_root)
    pending, target = pending_migrations(current, migrations)
    print("ForgeKit Upgrade Check")
    print(f"Status: {'update-available' if pending else 'current'}")
    print(f"Project: {project_root}")
    print(f"Current version: {version_text(current)}")
    print(f"Latest available: {version_text(latest_available(migrations, current))}")
    print(f"Planned target: {version_text(target)}")
    print(f"Pending migrations: {len(pending)}")
    print("Next: run `plan` to review the migration plan." if pending else "No migration is required.")


def render_plan(project_root, state, migrations):
    current = parse_version(state["forgekit_version"])
    pending, target = pending_migrations(current, migrations)
    lines = [
        "ForgeKit Versioned Migration Plan",
        "Status: report-only",
        "Mode: versioned-migration-plan",
        f"Project: {project_root}",
        f"From: {version_text(current)}",
        f"To: {version_text(target)}",
        f"Migrations: {len(pending)}",
        "",
    ]
    if not pending:
        lines.extend(["No migration is required.", "No files were changed."])
        return "\n".join(lines), pending
    for item in pending:
        safe_actions = [action for action in item["actions"] if action.get("safety") == "safe"]
        non_safe = [action for action in item["actions"] if action.get("safety") != "safe"]
        lines.extend([
            f"## {item['to']} - {item['title']}",
            f"Risk: {item['risk']}",
            f"Safe actions: {len(safe_actions)}",
            f"Manual actions: {len(non_safe)}",
        ])
        for action in safe_actions:
            lines.append(f"- SAFE: {action.get('description', action.get('id', action.get('type', 'action')))}")
        for review in item["manual_review"]:
            lines.append(f"- REVIEW: {review}")
        lines.append("")
    lines.extend([
        "Apply command: python scripts/forgekit-upgrade.py apply --safe --repo-root <project>",
        "No files were changed by plan.",
    ])
    return "\n".join(lines), pending


def command_plan(project_root, migration_root):
    state, status = state_status(project_root)
    if status != "supported":
        print_adoption_guidance(project_root, status, state)
        return
    plan, _ = render_plan(project_root, state, load_migrations(migration_root))
    print(plan)


def safe_target(project_root, relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        fail(f"Unsafe migration target: {relative}")
    if path.parts[0] not in SAFE_ROOTS:
        fail(f"Safe migration target is outside ForgeKit governance roots: {relative}")
    target = (project_root / path).resolve()
    try:
        target.relative_to(project_root)
    except ValueError:
        fail(f"Migration target escapes project root: {relative}")
    return target


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def apply_action(project_root, migration, action, state):
    action_type = action.get("type")
    if action.get("safety") != "safe":
        return "manual"
    if action_type == "ensure_directory":
        safe_target(project_root, action["target"]).mkdir(parents=True, exist_ok=True)
        return "applied"
    if action_type == "copy_file_if_missing":
        source = (migration["_path"].parent / action["source"]).resolve()
        try:
            source.relative_to(migration["_path"].parent.resolve())
        except ValueError:
            fail(f"Migration source escapes package: {action['source']}")
        if not source.is_file():
            fail(f"Migration source not found: {source}")
        target = safe_target(project_root, action["target"])
        if target.exists():
            if target.is_file() and sha256(target) == sha256(source):
                return "unchanged"
            fail(f"Conflict: target already exists and was not overwritten: {action['target']}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        return "applied"
    if action_type == "set_state_feature":
        state.setdefault("features", {})[action["name"]] = action["value"]
        return "applied"
    fail(f"Unsupported safe migration action: {action_type}")


def preflight_action(project_root, migration, action):
    if action.get("safety") != "safe":
        fail(f"Migration {migration['id']} contains a non-safe action: {action.get('id', action.get('type'))}")
    action_type = action.get("type")
    if action_type == "ensure_directory":
        safe_target(project_root, action["target"])
        return
    if action_type == "copy_file_if_missing":
        source = (migration["_path"].parent / action["source"]).resolve()
        try:
            source.relative_to(migration["_path"].parent.resolve())
        except ValueError:
            fail(f"Migration source escapes package: {action['source']}")
        if not source.is_file():
            fail(f"Migration source not found: {source}")
        target = safe_target(project_root, action["target"])
        if target.exists() and (not target.is_file() or sha256(target) != sha256(source)):
            fail(f"Conflict: target already exists and was not overwritten: {action['target']}")
        return
    if action_type == "set_state_feature":
        if not action.get("name"):
            fail(f"Migration {migration['id']} has a state feature without a name")
        return
    fail(f"Unsupported safe migration action: {action_type}")


def write_state(path, state):
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def command_apply(project_root, migration_root, safe):
    if not safe:
        fail("apply requires --safe")
    state, status = state_status(project_root)
    if status != "supported":
        print_adoption_guidance(project_root, status, state)
        return
    migrations = load_migrations(migration_root)
    current = parse_version(state["forgekit_version"])
    pending, _ = pending_migrations(current, migrations)
    if not pending:
        print("[ok] No migration is required; no files were changed.")
        return
    for migration in pending:
        for action in migration["actions"]:
            preflight_action(project_root, migration, action)
    applied_ids = []
    start = state["forgekit_version"]
    for migration in pending:
        for action in migration["actions"]:
            result = apply_action(project_root, migration, action, state)
            print(f"[{result}] {action.get('id', action.get('type'))}")
        state["forgekit_version"] = migration["to"]
        applied_ids.append(migration["id"])
    state["last_upgrade"] = {
        "from": start,
        "to": state["forgekit_version"],
        "applied_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "migrations": applied_ids,
        "mode": "safe",
    }
    write_state(project_root / STATE_RELATIVE_PATH, state)
    print(f"[ok] Applied {len(applied_ids)} safe migration(s); state is now {state['forgekit_version']}")


def main():
    parser = argparse.ArgumentParser(description="ForgeKit versioned migration upgrade")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "plan"):
        command = subparsers.add_parser(name)
        command.add_argument("--repo-root", default=".", help="Target project root")
        command.add_argument("--migration-root", help="Migration package directory")
    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--repo-root", default=".", help="Target project root")
    apply_parser.add_argument("--migration-root", help="Migration package directory")
    apply_parser.add_argument("--safe", action="store_true", help="Apply safe actions only")
    args = parser.parse_args()

    project_root = Path(args.repo_root).resolve()
    if not project_root.is_dir():
        fail(f"Project root does not exist: {project_root}")
    migration_root = Path(args.migration_root).resolve() if args.migration_root else Path(__file__).resolve().parents[1] / "migrations"
    if args.command == "check":
        command_check(project_root, migration_root)
    elif args.command == "plan":
        command_plan(project_root, migration_root)
    else:
        command_apply(project_root, migration_root, args.safe)


if __name__ == "__main__":
    main()
