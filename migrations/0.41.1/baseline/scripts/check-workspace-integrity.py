#!/usr/bin/env python3
"""Report-only multi-project workspace and scoped-docs integrity check."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


STATE_PATH = Path(".forgekit/state.json")
MAP_PATH = Path(".forgekit/workspace-map.json")
ALLOWED_PROFILES = {"workspace-full", "project-capsule", "repo-lite"}
ALLOWED_READ_SCOPES = {"workspace", "project", "repo", "explicit"}
CAPSULE_FILES = {
    "project-card.md",
    "source-links.md",
    "task-board.md",
    "testing.md",
    "risk-register.md",
}
FORBIDDEN_CAPSULE_NAMES = {
    "AGENTS.md",
    "CLAUDE.md",
    "archive-capsule.md",
    "workflow-router.md",
    "document-responsibility.md",
    "scoped-docs.md",
    "project-maintenance.md",
    "current-docs-integrity.md",
    "reasoning-review.md",
    "bounded-auto-loop-policy.md",
    "loop-operations.md",
    "maker-checker-protocol.md",
    "native-agent-adapter.md",
}
FORBIDDEN_CAPSULE_DIRS = {"governance", "skills", "agents", ".agents", ".claude", ".codex", "archive"}
PLACEHOLDER_IDS = {"", "todo_review", "example", "workspace-example"}
SOURCE_PATTERN = re.compile(r"\bSRC-[A-Za-z0-9][A-Za-z0-9._-]*\b", re.IGNORECASE)
FIELD_PATTERNS = {
    "project": re.compile(r"(?:Project ID|Project):\s*`?([A-Za-z0-9._-]+)", re.IGNORECASE),
    "repo": re.compile(r"Repo ID:\s*`?([A-Za-z0-9._-]+)", re.IGNORECASE),
    "workspace_task": re.compile(r"Workspace Task ID:\s*`?([A-Za-z0-9._-]+)", re.IGNORECASE),
}


def finding(severity, code, message, path=None):
    item = {"severity": severity, "code": code, "message": message}
    if path:
        item["path"] = str(path).replace("\\", "/")
    return item


def is_placeholder_id(value):
    return str(value).strip().lower() in PLACEHOLDER_IDS


def load_json(path, label):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except FileNotFoundError:
        return None, f"{label} not found"
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"invalid {label}: {exc}"


def safe_relative(root, raw, label, findings):
    if not isinstance(raw, str) or not raw.strip():
        findings.append(finding("blocking", "invalid_path", f"{label} must be a non-empty relative path"))
        return None
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts or ".git" in path.parts:
        findings.append(finding("blocking", "unsafe_path", f"{label} is unsafe: {raw}"))
        return None
    resolved = (root / path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        findings.append(finding("blocking", "path_escape", f"{label} escapes WorkspaceRoot: {raw}"))
        return None
    return resolved


def feature_state(state):
    features = state.get("features", {}) if isinstance(state, dict) else {}
    return bool(features.get("multi_project_scoped_docs_available", False)), bool(
        features.get("multi_project_scoped_docs_enabled", False)
    )


def activation_status(root):
    state_path = root / STATE_PATH
    state, state_error = load_json(state_path, "state.json")
    if state_error:
        if state_path.exists():
            return "runtime-error", None, None, state_error
        return "not-enabled", None, None, state_error
    available, enabled = feature_state(state)
    if not available and not enabled:
        return "not-enabled", state, None, "multi-project scoped docs are not installed or enabled"
    map_data, map_error = load_json(root / MAP_PATH, "workspace-map.json")
    if enabled:
        if map_error:
            return "blocking", state, None, map_error
        if not map_data.get("enabled"):
            return "blocking", state, map_data, "state enables scoped docs but workspace map is disabled"
        return "enabled", state, map_data, None
    if map_error:
        return "not-enabled", state, None, "capability is available but workspace map is not configured"
    if map_data.get("enabled"):
        return "not-enabled", state, map_data, "workspace map requests enablement but state feature is disabled"
    return "not-enabled", state, map_data, "capability is available; configure the map and enable the state feature"


def validate_ids(items, kind, findings):
    seen = set()
    result = {}
    if not isinstance(items, list):
        findings.append(finding("blocking", "invalid_collection", f"{kind} must be an array"))
        return result
    for item in items:
        if not isinstance(item, dict):
            findings.append(finding("blocking", "invalid_entry", f"{kind} entry must be an object"))
            continue
        item_id = str(item.get("id", "")).strip()
        if is_placeholder_id(item_id):
            findings.append(finding("blocking", "invalid_id", f"{kind} entry requires a real id"))
            continue
        if item_id in seen:
            findings.append(finding("blocking", "duplicate_id", f"duplicate {kind} id: {item_id}"))
            continue
        seen.add(item_id)
        result[item_id] = item
    return result


def validate_profile_and_scope(item, label, findings):
    profile = item.get("docs_profile")
    if profile and profile not in ALLOWED_PROFILES:
        findings.append(finding("blocking", "invalid_docs_profile", f"{label} has invalid docs_profile: {profile}"))
    scope = item.get("default_read_scope")
    if scope and scope not in ALLOWED_READ_SCOPES:
        findings.append(finding("blocking", "invalid_read_scope", f"{label} has invalid default_read_scope: {scope}"))


def git_warning(repo_path, repo_id, findings):
    if not repo_path.exists():
        findings.append(finding("warning", "repo_missing", f"Repo {repo_id} is not checked out", repo_path))
        return
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "--show-toplevel"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        findings.append(finding("warning", "git_unavailable", "Git status could not be checked"))
        return
    if result.returncode != 0:
        findings.append(finding("warning", "repo_not_git", f"Repo {repo_id} path is not a Git repository", repo_path))


def capsule_files(project_path):
    if not project_path.is_dir():
        return []
    return [path for path in project_path.rglob("*") if path.is_file()]


def validate_capsule(project_id, project_path, findings):
    if not project_path.exists():
        findings.append(finding("blocking", "capsule_missing", f"Project capsule is missing: {project_id}", project_path))
        return
    for path in capsule_files(project_path):
        relative = path.relative_to(project_path)
        parts = set(relative.parts)
        if path.name in FORBIDDEN_CAPSULE_NAMES or parts & FORBIDDEN_CAPSULE_DIRS:
            findings.append(finding("blocking", "full_forgekit_copy", f"Project capsule contains a forbidden ForgeKit protocol or entry: {relative}", path))
            continue
        allowed = path.name in CAPSULE_FILES or (relative.parts[0] == "decisions" and path.suffix.lower() == ".md")
        if not allowed:
            findings.append(finding("warning", "extra_capsule_file", f"Project capsule contains an extra local file: {relative}", path))
        try:
            line_count = len(path.read_text(encoding="utf-8-sig").splitlines())
        except (OSError, UnicodeDecodeError):
            findings.append(finding("warning", "capsule_read_error", "Capsule file could not be read as UTF-8", path))
            continue
        if line_count > 400:
            findings.append(finding("warning", "capsule_too_long", f"Capsule file has {line_count} lines", path))


def read_text(path):
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return ""


def is_within(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def real_source_ids(text):
    return {
        item.upper()
        for item in SOURCE_PATTERN.findall(text)
        if "EXAMPLE" not in item.upper() and "YYYY" not in item.upper()
    }


def validate_references(root, workspace, projects, repos, findings):
    docs = safe_relative(root, workspace.get("docs_path", ".forgekit/docs"), "workspace.docs_path", findings)
    if docs is None:
        return
    archive = safe_relative(root, workspace.get("archive_root", ".forgekit/archive"), "workspace.archive_root", findings)
    projects_root = safe_relative(root, workspace.get("projects_path", ".forgekit/projects"), "workspace.projects_path", findings)
    if archive and ((docs and is_within(docs, archive)) or (projects_root and is_within(projects_root, archive))):
        findings.append(finding("blocking", "archive_as_current", "ArchiveRoot cannot be configured as current workspace or project docs"))

    workspace_sources = real_source_ids(read_text(docs / "task-intake.md"))
    workspace_task = read_text(docs / "task-board.md")
    project_refs = set(FIELD_PATTERNS["project"].findall(workspace_task))
    for project_id in project_refs:
        if project_id not in projects and project_id.upper() not in {"TODO_REVIEW", "EXAMPLE"}:
            findings.append(finding("blocking", "unknown_project_reference", f"Workspace task references unknown Project ID: {project_id}", docs / "task-board.md"))
    local_project_markers = len(re.findall(r"(?:Repo ID|Local Task ID):", workspace_task, re.IGNORECASE))
    if local_project_markers > 30:
        findings.append(finding("warning", "workspace_local_detail", "Workspace task-board carries excessive project-local detail", docs / "task-board.md"))

    for project_id, project in projects.items():
        project_path = safe_relative(root, project.get("docs_path", f".forgekit/projects/{project_id}"), f"project {project_id} docs_path", findings)
        if project_path is None:
            continue
        if archive and is_within(project_path, archive):
            findings.append(finding("blocking", "project_docs_in_archive", f"Project {project_id} docs cannot be located under ArchiveRoot"))
            continue
        validate_capsule(project_id, project_path, findings)
        task_text = read_text(project_path / "task-board.md")
        source_text = read_text(project_path / "source-links.md")
        local_sources = real_source_ids(source_text)
        standalone = str(project.get("scope", "")).strip().lower() == "standalone"
        if not standalone and re.search(r"^#{1,6}\s+Original Text\b|^Original Text:", source_text, re.IGNORECASE | re.MULTILINE):
            findings.append(finding("blocking", "duplicated_source_text", f"Project {project_id} is not standalone but source-links stores Original Text", project_path / "source-links.md"))
        for source_id in real_source_ids(task_text):
            if source_id not in workspace_sources and not (standalone and source_id in local_sources):
                findings.append(finding("blocking", "unresolved_source", f"Project {project_id} task references unresolved Source ID: {source_id}", project_path / "task-board.md"))
        for workspace_task_id in FIELD_PATTERNS["workspace_task"].findall(task_text):
            if workspace_task_id.upper() not in {"TODO_REVIEW", "EXAMPLE"} and workspace_task_id not in workspace_task:
                findings.append(finding("blocking", "unknown_workspace_task", f"Project {project_id} references unknown Workspace Task ID: {workspace_task_id}", project_path / "task-board.md"))
        for repo_id in FIELD_PATTERNS["repo"].findall(task_text):
            if repo_id not in repos and repo_id.upper() not in {"TODO_REVIEW", "EXAMPLE"}:
                findings.append(finding("blocking", "unknown_repo_reference", f"Project {project_id} task references unknown Repo ID: {repo_id}", project_path / "task-board.md"))


def run_check(root):
    activation, state, data, reason = activation_status(root)
    if activation == "not-enabled":
        return {
            "status": "not-enabled",
            "workspace_root": str(root),
            "summary": reason,
            "adoption_guidance": "Keep the legacy single-project flow, or configure workspace-map.json and explicitly enable scoped docs.",
            "findings": [],
        }
    if activation == "blocking":
        return {
            "status": "blocking",
            "workspace_root": str(root),
            "summary": reason,
            "findings": [finding("blocking", "activation_mismatch", reason)],
        }
    if activation == "runtime-error":
        return {
            "status": "runtime-error",
            "workspace_root": str(root),
            "summary": reason,
            "findings": [],
        }

    findings = []
    required = {"schema_version", "enabled", "workspace", "projects", "repos", "artifacts"}
    missing = sorted(required - set(data))
    if missing:
        findings.append(finding("blocking", "invalid_schema", f"workspace map is missing fields: {', '.join(missing)}", MAP_PATH))
    if data.get("schema_version") != 1:
        findings.append(finding("blocking", "unsupported_schema", "workspace map schema_version must be 1", MAP_PATH))
    workspace = data.get("workspace", {})
    if not isinstance(workspace, dict):
        findings.append(finding("blocking", "invalid_workspace", "workspace must be an object", MAP_PATH))
        workspace = {}
    workspace_id = str(workspace.get("id", "")).strip()
    if is_placeholder_id(workspace_id):
        findings.append(finding("blocking", "placeholder_workspace_id", "enabled workspace requires a real workspace.id", MAP_PATH))
    validate_profile_and_scope(workspace, "workspace", findings)

    projects = validate_ids(data.get("projects", []), "project", findings)
    repos = validate_ids(data.get("repos", []), "repo", findings)
    artifacts = validate_ids(data.get("artifacts", []), "artifact", findings)

    for project_id, project in projects.items():
        validate_profile_and_scope(project, f"project {project_id}", findings)
        if project.get("docs_profile") not in {None, "project-capsule"}:
            findings.append(finding("blocking", "project_profile_mismatch", f"Project {project_id} must use project-capsule"))
        for repo_id in project.get("repo_ids", []):
            if repo_id not in repos:
                findings.append(finding("blocking", "unknown_repo", f"Project {project_id} references unknown Repo ID: {repo_id}"))
        for dependency in project.get("depends_on", []):
            if dependency not in projects:
                findings.append(finding("blocking", "unknown_project_dependency", f"Project {project_id} depends on unknown Project ID: {dependency}"))

    repo_paths = {}
    for repo_id, repo in repos.items():
        validate_profile_and_scope(repo, f"repo {repo_id}", findings)
        if repo.get("docs_profile") not in {None, "repo-lite"}:
            findings.append(finding("blocking", "repo_profile_mismatch", f"Repo {repo_id} must use repo-lite"))
        if repo.get("project_id") not in projects:
            findings.append(finding("blocking", "unknown_repo_project", f"Repo {repo_id} references unknown Project ID: {repo.get('project_id')}"))
        repo_path = safe_relative(root, repo.get("repo_path", ""), f"repo {repo_id} repo_path", findings)
        if repo_path:
            repo_paths[repo_id] = repo_path
            git_warning(repo_path, repo_id, findings)

    artifact_paths = {}
    for artifact_id, artifact in artifacts.items():
        project_id = artifact.get("project_id")
        if project_id and project_id not in projects:
            findings.append(finding("blocking", "unknown_artifact_project", f"Artifact {artifact_id} references unknown Project ID: {project_id}"))
        artifact_path = safe_relative(root, artifact.get("path", ""), f"artifact {artifact_id} path", findings)
        if artifact_path:
            artifact_paths[artifact_id] = artifact_path
        evidence = artifact.get("evidence_index")
        if evidence:
            evidence_path = safe_relative(root, evidence, f"artifact {artifact_id} evidence_index", findings)
            if evidence_path and not evidence_path.exists():
                findings.append(finding("warning", "artifact_evidence_missing", f"Artifact {artifact_id} evidence index is missing", evidence_path))
        for repo_id in [artifact.get("produced_by_repo"), *artifact.get("consumed_by_repos", [])]:
            if repo_id and repo_id not in repos:
                findings.append(finding("blocking", "unknown_artifact_repo", f"Artifact {artifact_id} references unknown Repo ID: {repo_id}"))

    for repo_id, repo_path in repo_paths.items():
        archive_path = safe_relative(root, workspace.get("archive_root", ".forgekit/archive"), "workspace.archive_root", findings)
        if archive_path and is_within(repo_path, archive_path):
            findings.append(finding("blocking", "repo_in_archive", f"Repo {repo_id} cannot be located under ArchiveRoot"))
        for artifact_id, artifact_path in artifact_paths.items():
            if repo_path == artifact_path:
                findings.append(finding("blocking", "repo_artifact_collision", f"Repo {repo_id} and artifact {artifact_id} use the same path"))
    archive_path = safe_relative(root, workspace.get("archive_root", ".forgekit/archive"), "workspace.archive_root", findings)
    for artifact_id, artifact_path in artifact_paths.items():
        if archive_path and is_within(artifact_path, archive_path):
            findings.append(finding("blocking", "artifact_in_archive", f"Artifact {artifact_id} cannot be located under ArchiveRoot"))

    validate_references(root, workspace, projects, repos, findings)

    blocking = sum(item["severity"] == "blocking" for item in findings)
    warnings = sum(item["severity"] == "warning" for item in findings)
    status = "blocking" if blocking else "warning" if warnings else "passed"
    return {
        "status": status,
        "workspace_root": str(root),
        "summary": {"blocking": blocking, "warnings": warnings},
        "findings": findings,
    }


def print_text(report):
    print("ForgeKit Workspace Integrity")
    print(f"Status: {report['status']}")
    print(f"WorkspaceRoot: {report['workspace_root']}")
    if report["status"] == "not-enabled":
        print(f"Reason: {report['summary']}")
        print(f"Adoption: {report['adoption_guidance']}")
        return
    summary = report.get("summary", {})
    print(f"Blocking: {summary.get('blocking', 0)}")
    print(f"Warnings: {summary.get('warnings', 0)}")
    for item in report.get("findings", []):
        location = f" [{item['path']}]" if item.get("path") else ""
        print(f"[{item['severity']}] {item['code']}: {item['message']}{location}")
    print("Report-only: no project files were modified.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="WorkspaceRoot to inspect")
    parser.add_argument("--strict", action="store_true", help="Return 1 when warnings are present")
    parser.add_argument("--require-enabled", action="store_true", help="Return 1 when scoped docs are not enabled")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Print JSON report")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    if not root.is_dir():
        print(f"[fail] WorkspaceRoot does not exist: {root}", file=sys.stderr)
        return 2
    report = run_check(root)
    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_text(report)

    if report["status"] == "blocking":
        return 1
    if report["status"] == "runtime-error":
        return 2
    if report["status"] == "warning" and args.strict:
        return 1
    if report["status"] == "not-enabled" and args.require_enabled:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
