#!/usr/bin/env python3
"""Plan or create one minimal ForgeKit Project Capsule."""

import argparse
import json
import shutil
import sys
from pathlib import Path


STATE_PATH = Path(".forgekit/state.json")
MAP_PATH = Path(".forgekit/workspace-map.json")
TEMPLATE_PATH = Path(".forgekit/projects/_template")
CAPSULE_FILES = (
    Path("project-card.md"),
    Path("source-links.md"),
    Path("task-board.md"),
    Path("testing.md"),
    Path("risk-register.md"),
    Path("decisions/0001-example.md"),
)
FORBIDDEN_FILES = {
    "AGENTS.md",
    "CLAUDE.md",
    "workflow-router.md",
    "document-responsibility.md",
    "archive-capsule.md",
}
FORBIDDEN_DIRS = {"governance", "skills", "agents", "docs"}


class BootstrapError(Exception):
    """A blocking configuration or safety failure."""


def load_json(path, label):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise BootstrapError(f"{label} not found: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise BootstrapError(f"invalid {label}: {exc}") from exc


def safe_relative(root, raw, label):
    if not isinstance(raw, str) or not raw.strip():
        raise BootstrapError(f"{label} must be a non-empty relative path")
    relative = Path(raw)
    if relative.is_absolute() or ".." in relative.parts or ".git" in relative.parts:
        raise BootstrapError(f"unsafe {label}: {raw}")
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise BootstrapError(f"{label} escapes WorkspaceRoot: {raw}") from exc
    return relative, resolved


def is_within(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def activation(root):
    state_path = root / STATE_PATH
    if not state_path.is_file():
        raise BootstrapError("state.json is required; this project does not support multi-project scoped docs")
    state = load_json(state_path, "state.json")
    features = state.get("features", {}) if isinstance(state, dict) else {}
    available = features.get("multi_project_scoped_docs_available") is True
    enabled = features.get("multi_project_scoped_docs_enabled") is True
    if not available:
        raise BootstrapError("multi-project scoped docs are unsupported by this project state")
    map_path = root / MAP_PATH
    if not enabled or not map_path.is_file():
        return "not-enabled", None
    workspace_map = load_json(map_path, "workspace-map.json")
    if workspace_map.get("enabled") is not True:
        return "not-enabled", workspace_map
    return "enabled", workspace_map


def project_by_id(workspace_map, project_id):
    projects = workspace_map.get("projects", [])
    if not isinstance(projects, list):
        raise BootstrapError("workspace-map projects must be an array")
    matches = [item for item in projects if isinstance(item, dict) and item.get("id") == project_id]
    if not matches:
        raise BootstrapError(f"project is not listed in workspace-map.json: {project_id}")
    if len(matches) > 1:
        raise BootstrapError(f"duplicate project id in workspace-map.json: {project_id}")
    return matches[0]


def validate_target(root, workspace_map, project_id, project):
    workspace = workspace_map.get("workspace", {})
    if not isinstance(workspace, dict):
        raise BootstrapError("workspace-map workspace must be an object")
    projects_raw = workspace.get("projects_path", ".forgekit/projects")
    _, projects_root = safe_relative(root, projects_raw, "workspace.projects_path")
    expected = projects_root / project_id
    docs_raw = project.get("docs_path", f"{projects_raw}/{project_id}")
    docs_relative, docs_path = safe_relative(root, docs_raw, f"project {project_id} docs_path")
    if docs_path != expected:
        raise BootstrapError(
            f"project {project_id} docs_path must be {expected.relative_to(root).as_posix()} for minimal bootstrap"
        )

    protected = []
    for label, raw in (
        ("workspace docs", workspace.get("docs_path", ".forgekit/docs")),
        ("archive", workspace.get("archive_root", ".forgekit/archive")),
    ):
        _, path = safe_relative(root, raw, label)
        protected.append((label, path))
    for repo in workspace_map.get("repos", []):
        if isinstance(repo, dict) and repo.get("repo_path"):
            _, path = safe_relative(root, repo["repo_path"], f"repo {repo.get('id', 'unknown')} repo_path")
            protected.append((f"repo {repo.get('id', 'unknown')}", path))
    for artifact in workspace_map.get("artifacts", []):
        if isinstance(artifact, dict) and artifact.get("path"):
            _, path = safe_relative(root, artifact["path"], f"artifact {artifact.get('id', 'unknown')} path")
            protected.append((f"artifact {artifact.get('id', 'unknown')}", path))
    for label, path in protected:
        if docs_path == path or is_within(docs_path, path) or is_within(path, docs_path):
            raise BootstrapError(f"project capsule path conflicts with {label}: {docs_relative.as_posix()}")
    return docs_relative, docs_path


def validate_existing_capsule(target):
    if not target.exists():
        return
    if not target.is_dir():
        raise BootstrapError(f"project capsule target is not a directory: {target}")
    for path in target.rglob("*"):
        relative = path.relative_to(target)
        if path.is_file() and path.name in FORBIDDEN_FILES:
            raise BootstrapError(f"capsule contains forbidden ForgeKit entry: {relative.as_posix()}")
        if path.is_dir() and any(part in FORBIDDEN_DIRS for part in relative.parts):
            raise BootstrapError(f"capsule contains forbidden ForgeKit protocol directory: {relative.as_posix()}")


def classify_files(template, target):
    actions = []
    for relative in CAPSULE_FILES:
        source = template / relative
        destination = target / relative
        if not source.is_file():
            raise BootstrapError(f"capsule template file is missing: {source}")
        if not destination.exists():
            status = "create"
        elif not destination.is_file():
            raise BootstrapError(f"capsule target is not a file: {destination}")
        elif destination.read_bytes() == source.read_bytes():
            status = "already-present"
        else:
            status = "review-needed"
        actions.append({"status": status, "source": source, "target": destination, "relative": relative})
    return actions


def print_summary(mode, status, project_id, profile, docs_path, actions, blocking=None, will_write=False):
    counts = {name: 0 for name in ("create", "already-present", "review-needed", "blocking")}
    for action in actions:
        counts[action["status"]] += 1
    if blocking:
        counts["blocking"] += 1
    print("ForgeKit Minimal Project Capsule Bootstrap")
    print(f"Mode: {mode}")
    print(f"Status: {status}")
    print(f"project_id: {project_id}")
    print(f"docs_profile: {profile}")
    print(f"docs_path: {docs_path or 'not-applicable'}")
    for name in ("create", "already-present", "review-needed", "blocking"):
        print(f"{name}: {counts[name]}")
    print(f"will_write: {'yes' if will_write else 'no'}")
    print("write_scope: only the six minimal files under .forgekit/projects/<project-id>/")
    print("untouched: workspace-map, workspace docs, repos, artifacts, archive, and Git state")
    for action in actions:
        print(f"[{action['status']}] {action['relative'].as_posix()}")
    if blocking:
        print(f"[blocking] {blocking}")


def inspect(root, project_id):
    activation_status, workspace_map = activation(root)
    if activation_status == "not-enabled":
        return {
            "status": "not-enabled",
            "project": project_id,
            "profile": "unknown",
            "docs_path": None,
            "actions": [],
        }
    project = project_by_id(workspace_map, project_id)
    profile = project.get("docs_profile")
    if profile == "workspace-only":
        return {
            "status": "skipped_workspace_only",
            "project": project_id,
            "profile": profile,
            "docs_path": project.get("docs_path"),
            "actions": [],
        }
    if profile != "project-capsule":
        raise BootstrapError(f"project {project_id} has invalid docs_profile: {profile}")
    docs_relative, target = validate_target(root, workspace_map, project_id, project)
    template = root / TEMPLATE_PATH
    if not template.is_dir():
        raise BootstrapError(f"project capsule template is missing: {TEMPLATE_PATH.as_posix()}")
    validate_existing_capsule(target)
    actions = classify_files(template, target)
    return {
        "status": "ready",
        "project": project_id,
        "profile": profile,
        "docs_path": docs_relative.as_posix(),
        "target": target,
        "actions": actions,
    }


def run(args):
    root = Path(args.repo_root).resolve()
    if not root.is_dir():
        raise BootstrapError(f"WorkspaceRoot does not exist: {root}")
    result = inspect(root, args.project)
    if result["status"] in {"not-enabled", "skipped_workspace_only"}:
        print_summary(
            args.command, result["status"], result["project"], result["profile"],
            result["docs_path"], result["actions"], will_write=False,
        )
        if result["status"] == "not-enabled":
            print("Adoption: configure and explicitly enable scoped docs before creating a capsule.")
        return 0

    actions = result["actions"]
    create_actions = [item for item in actions if item["status"] == "create"]
    review_needed = any(item["status"] == "review-needed" for item in actions)
    if args.command == "plan":
        print_summary(
            "plan", "planned", result["project"], result["profile"], result["docs_path"],
            actions, will_write=False,
        )
        return 0
    if not args.confirm:
        print_summary(
            "apply", "confirmation-required", result["project"], result["profile"], result["docs_path"],
            actions, blocking="apply requires --confirm after reviewing the plan", will_write=False,
        )
        return 1

    for action in create_actions:
        action["target"].parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(action["source"], action["target"])
    status = "completed_with_review_needed" if review_needed else "completed"
    print_summary(
        "apply", status, result["project"], result["profile"], result["docs_path"],
        actions, will_write=bool(create_actions),
    )
    print("Next: run scripts/check-workspace-integrity.py to verify cross-scope relationships.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("plan", "apply"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--repo-root", default=".", help="WorkspaceRoot containing .forgekit")
        subparser.add_argument("--project", required=True, help="One project id from workspace-map.json")
        if command == "apply":
            subparser.add_argument("--confirm", action="store_true", help="Confirm minimal capsule file creation")
    args = parser.parse_args()
    try:
        return run(args)
    except BootstrapError as exc:
        print_summary(
            args.command, "blocking", getattr(args, "project", "unknown"), "unknown", None, [],
            blocking=str(exc), will_write=False,
        )
        return 1
    except OSError as exc:
        print(f"[runtime-error] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
