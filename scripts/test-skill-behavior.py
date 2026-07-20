#!/usr/bin/env python3
"""Run isolated, data-driven ForgeKit Skill behavior cases."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path, PurePosixPath
from typing import Any, Callable


FAILURE_CLASSES = {
    "PASS",
    "ENVIRONMENT_UNAVAILABLE",
    "ADAPTER_ERROR",
    "ROUTING_FAILURE",
    "UNAUTHORIZED_WRITE",
    "BEHAVIOR_FAILURE",
    "GRADER_UNCERTAIN",
}
EXIT_CODES = {
    "PASS": 0,
    "ENVIRONMENT_UNAVAILABLE": 20,
    "ADAPTER_ERROR": 21,
    "ROUTING_FAILURE": 22,
    "UNAUTHORIZED_WRITE": 23,
    "BEHAVIOR_FAILURE": 24,
    "GRADER_UNCERTAIN": 25,
}
AUTHORIZATIONS = {"read_only", "bounded_local_write", "external_or_irreversible_not_authorized"}
AUTH_ENV_ALLOWLIST = {"OPENAI_API_KEY", "ANTHROPIC_API_KEY"}
CLIENTS = {"codex", "claude"}
INVOCATION_MODES = {"implicit", "explicit"}
REQUIRED_CASE_FIELDS = {
    "id", "title", "client", "fixture", "prompt", "invocation_mode", "expected_skill",
    "forbidden_skills", "authorization", "allowed_write_paths", "forbidden_actions",
    "expected_behavior", "grader", "tags",
}
CAPABILITY_KEYS = {"model", "tool_trace", "skill_source", "structured_output", "isolation"}
REDACTED = "<REDACTED>"
SENSITIVE_KEYS = {
    "TOKEN", "ACCESS_TOKEN", "REFRESH_TOKEN", "ID_TOKEN", "API_KEY",
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "SECRET", "CLIENT_SECRET",
    "PASSWORD", "PASSWD", "ACCESS_KEY", "SECRET_KEY", "AUTH",
    "AUTHORIZATION", "CREDENTIAL", "CREDENTIALS", "COOKIE",
}
SECRET_OPTION = re.compile(r"^--?(?:api[-_]?key|access[-_]?key|token|secret|password|auth)(?:=(.*))?$", re.I)
TEXT_SECRET_PATTERNS = [
    re.compile(r"(?i)(--?(?:api[-_]?key|access[-_]?key|token|secret|password|auth)\s+)[^\s,;]+"),
    re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s,;]+"),
    re.compile(r"(?i)(\bbearer\s+)[A-Za-z0-9._~+\-/=]+"),
    re.compile(
        r"(?i)\b((?:api[ _-]?key|access[ _-]?key|token|secret|password|auth)\s*[:=]\s*)[^\s,;]+"
    ),
    re.compile(r"\b(?:sk|rk)-[A-Za-z0-9_-]{8,}\b"),
]


class BehaviorError(ValueError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_relative(value: Any, label: str, *, allow_directory: bool = False) -> str:
    if not isinstance(value, str) or not value:
        raise BehaviorError(f"{label} must be a non-empty POSIX relative path")
    directory_suffix = value.endswith("/")
    candidate = value[:-1] if directory_suffix else value
    if "\\" in candidate or "\x00" in candidate or re.match(r"^[A-Za-z]:", candidate):
        raise BehaviorError(f"{label} is not a normalized POSIX relative path: {value!r}")
    raw_parts = candidate.split("/")
    path = PurePosixPath(candidate)
    if path.is_absolute() or candidate.startswith("./") or any(part in {"", ".", ".."} for part in raw_parts):
        raise BehaviorError(f"{label} is unsafe: {value!r}")
    if any(char in candidate for char in "*?[]{}<>"):
        raise BehaviorError(f"{label} must not contain wildcards or placeholders: {value!r}")
    if directory_suffix and not allow_directory:
        raise BehaviorError(f"{label} must name a file: {value!r}")
    return path.as_posix() + ("/" if directory_suffix else "")


def is_reparse(path: Path) -> bool:
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
        raise BehaviorError(f"{label} escapes repository root") from exc
    for part in relative.parts:
        current = current / part
        if current.exists() and is_reparse(current):
            raise BehaviorError(f"{label} crosses a symlink, junction, or reparse point: {current}")


def load_cases(repo_root: Path, manifest_relative: str) -> list[dict[str, Any]]:
    manifest_relative = safe_relative(manifest_relative, "case manifest")
    manifest = repo_root.joinpath(*PurePosixPath(manifest_relative).parts).resolve()
    try:
        manifest.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise BehaviorError("case manifest escapes repository root") from exc
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BehaviorError(f"cannot read case manifest: {exc}") from exc
    if not isinstance(data, dict) or set(data) != {"schema_version", "cases"} or data["schema_version"] != 1:
        raise BehaviorError("case manifest must be schema_version 1 with a cases array")
    if not isinstance(data["cases"], list) or not data["cases"]:
        raise BehaviorError("case manifest must contain at least one case")
    seen: set[str] = set()
    for index, case in enumerate(data["cases"]):
        if not isinstance(case, dict) or set(case) != REQUIRED_CASE_FIELDS:
            raise BehaviorError(f"case {index} must contain exactly the frozen case fields")
        case_id = case["id"]
        if not isinstance(case_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", case_id):
            raise BehaviorError(f"case {index} has an invalid id")
        if case_id in seen:
            raise BehaviorError(f"duplicate case id: {case_id}")
        seen.add(case_id)
        if case["client"] not in CLIENTS or case["invocation_mode"] not in INVOCATION_MODES:
            raise BehaviorError(f"case {case_id} has an invalid client or invocation_mode")
        if case["authorization"] not in AUTHORIZATIONS:
            raise BehaviorError(f"case {case_id} has an invalid authorization")
        for field in ("title", "prompt", "expected_behavior"):
            if not isinstance(case[field], str) or not case[field].strip():
                raise BehaviorError(f"case {case_id} field {field} must be a non-empty string")
        fixture_relative = safe_relative(case["fixture"], f"case {case_id} fixture")
        fixture = repo_root.joinpath(*PurePosixPath(fixture_relative).parts)
        ensure_no_reparse(repo_root, fixture, f"case {case_id} fixture")
        try:
            fixture.resolve().relative_to(repo_root.resolve())
        except ValueError as exc:
            raise BehaviorError(f"case {case_id} fixture escapes repository root") from exc
        if not fixture.is_dir():
            raise BehaviorError(f"case {case_id} fixture directory does not exist: {fixture_relative}")
        for path in fixture.rglob("*"):
            if is_reparse(path):
                raise BehaviorError(f"case {case_id} fixture contains a symlink, junction, or reparse point")
        if not isinstance(case["expected_skill"], str):
            raise BehaviorError(f"case {case_id} expected_skill must be a string")
        for field in ("forbidden_skills", "allowed_write_paths", "forbidden_actions", "tags"):
            if not isinstance(case[field], list) or not all(isinstance(item, str) for item in case[field]):
                raise BehaviorError(f"case {case_id} field {field} must be a string array")
        case["allowed_write_paths"] = [
            safe_relative(path, f"case {case_id} allowed path", allow_directory=True)
            for path in case["allowed_write_paths"]
        ]
        if case["authorization"] == "read_only" and case["allowed_write_paths"]:
            raise BehaviorError(f"case {case_id} is read_only but allows write paths")
        if not isinstance(case["grader"], dict) or case["grader"].get("type") not in {"manual", "deterministic"}:
            raise BehaviorError(f"case {case_id} grader must select manual or deterministic")
    return data["cases"]


def tree_snapshot(root: Path) -> dict[str, dict[str, Any]]:
    snapshot: dict[str, dict[str, Any]] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if is_reparse(path):
            raise BehaviorError(f"fixture produced a symlink, junction, or reparse point: {relative}")
        mode = path.stat(follow_symlinks=False).st_mode
        if stat.S_ISREG(mode):
            snapshot[relative] = {"type": "file", "sha256": hash_bytes(path.read_bytes())}
        elif stat.S_ISDIR(mode):
            snapshot[relative] = {"type": "directory"}
        else:
            snapshot[relative] = {"type": "special", "mode": stat.S_IFMT(mode)}
    return snapshot


def tree_identity(snapshot: dict[str, dict[str, Any]]) -> str:
    return hash_bytes(json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def changed_paths(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    return sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))


def path_allowed(path: str, allowlist: list[str]) -> bool:
    return any(path == allowed or (allowed.endswith("/") and path.startswith(allowed)) for allowed in allowlist)


def redact_text(value: Any, sensitive_paths: list[tuple[str, str]] | None = None) -> Any:
    if not isinstance(value, str):
        return value
    redacted = value
    for raw, placeholder in sorted(sensitive_paths or [], key=lambda item: len(item[0]), reverse=True):
        if raw:
            redacted = re.sub(re.escape(raw), placeholder, redacted, flags=re.I if os.name == "nt" else 0)
            alternate = raw.replace("\\", "/")
            if alternate != raw:
                redacted = re.sub(re.escape(alternate), placeholder, redacted, flags=re.I)
    for pattern in TEXT_SECRET_PATTERNS:
        redacted = pattern.sub(lambda match: (match.group(1) if match.lastindex else "") + REDACTED, redacted)
    option = SECRET_OPTION.match(redacted)
    if option and option.group(1) is not None:
        redacted = redacted.split("=", 1)[0] + f"={REDACTED}"
    return redacted


def normalize_sensitive_key(value: str) -> str:
    value = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    return re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").upper()


def is_sensitive_key(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    normalized = normalize_sensitive_key(value)
    compact = normalized.replace("_", "")
    for sensitive in SENSITIVE_KEYS:
        if normalized == sensitive or normalized.endswith("_" + sensitive):
            return True
        sensitive_compact = sensitive.replace("_", "")
        if compact == sensitive_compact or compact.endswith(sensitive_compact):
            return True
    return False


def redact_command(command: list[Any], sensitive_paths: list[tuple[str, str]] | None = None) -> list[Any]:
    result: list[Any] = []
    hide_next = False
    for value in command:
        if hide_next:
            result.append(REDACTED)
            hide_next = False
            continue
        if isinstance(value, str):
            match = SECRET_OPTION.match(value)
            if match:
                if match.group(1) is None:
                    result.append(value)
                    hide_next = True
                else:
                    result.append(value.split("=", 1)[0] + f"={REDACTED}")
                continue
        result.append(redact_text(value, sensitive_paths))
    return result


def redact(value: Any, sensitive_paths: list[tuple[str, str]] | None = None, key: str | None = None) -> Any:
    if isinstance(value, dict):
        return {
            name: REDACTED if is_sensitive_key(name) else redact(item, sensitive_paths, name)
            for name, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        command_key = normalize_sensitive_key(key) if isinstance(key, str) else ""
        if command_key in {"COMMAND", "SAFE_COMMAND"}:
            sanitized = redact_command(list(value), sensitive_paths)
        else:
            sanitized = [redact(item, sensitive_paths) for item in value]
        return tuple(sanitized) if isinstance(value, tuple) else sanitized
    return redact_text(value, sensitive_paths)


def sanitize_record(record: Any, sensitive_paths: list[tuple[str, str]] | None = None) -> Any:
    """Final recursive persistence boundary for every run-record representation."""
    return redact(record, sensitive_paths)


def serialize_sanitized(
    value: Any,
    sensitive_paths: list[tuple[str, str]] | None = None,
    *,
    ensure_ascii: bool = False,
    indent: int | None = 2,
) -> str:
    sanitized = sanitize_record(value, sensitive_paths)
    try:
        return json.dumps(sanitized, ensure_ascii=ensure_ascii, indent=indent)
    except (TypeError, ValueError) as exc:
        raise BehaviorError(f"sanitized record serialization failed: {type(exc).__name__}") from None


def git_identity(repo_root: Path) -> str:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True, encoding="utf-8", errors="replace",
            capture_output=True, timeout=5, check=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain"], cwd=repo_root, text=True, encoding="utf-8", errors="replace",
            capture_output=True, timeout=5, check=True,
        ).stdout
        return commit + ("+dirty" if dirty else "")
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


def load_version(repo_root: Path) -> str:
    try:
        return (repo_root / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"


def build_isolated_context(runtime_root: Path, auth_env_names: list[str] | None = None) -> dict[str, Any]:
    auth_env_names = auth_env_names or []
    invalid = sorted(set(auth_env_names) - AUTH_ENV_ALLOWLIST)
    if invalid:
        raise BehaviorError("unsupported auth environment variable(s): " + ", ".join(invalid))
    home = runtime_root / "home"
    config = runtime_root / "config"
    cache = runtime_root / "cache"
    data = runtime_root / "data"
    temp = runtime_root / "temp"
    for directory in (home, config, cache, data, temp):
        directory.mkdir(parents=True, exist_ok=True)
    empty_mcp = runtime_root / "empty-mcp.json"
    empty_mcp.write_text('{"mcpServers": {}}\n', encoding="utf-8")
    allowed = ("PATH", "SystemRoot", "WINDIR", "COMSPEC", "PATHEXT", "LANG", "LC_ALL")
    environment = {name: os.environ[name] for name in allowed if name in os.environ}
    environment.update({
        "HOME": str(home),
        "USERPROFILE": str(home),
        "XDG_CONFIG_HOME": str(config),
        "XDG_CACHE_HOME": str(cache),
        "XDG_DATA_HOME": str(data),
        "TEMP": str(temp),
        "TMP": str(temp),
        "CODEX_HOME": str(config / "codex"),
        "CLAUDE_CONFIG_DIR": str(config / "claude"),
        "PYTHONIOENCODING": "utf-8",
    })
    for name in auth_env_names:
        if name in os.environ:
            environment[name] = os.environ[name]
    return {
        "environment": environment,
        "environment_keys": sorted(environment),
        "home": home,
        "config": config,
        "cache": cache,
        "data": data,
        "temp": temp,
        "empty_mcp_config": empty_mcp,
    }


def base_record(repo_root: Path, case: dict[str, Any], before: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": str(uuid.uuid4()),
        "case_id": case["id"],
        "timestamp_utc": utc_now(),
        "forgekit_version": load_version(repo_root),
        "repository_identity": git_identity(repo_root),
        "operating_system": platform.platform(),
        "python_version": platform.python_version(),
        "client": case["client"],
        "client_executable": None,
        "client_version": None,
        "model": None,
        "tool_trace": None,
        "skill_source": None,
        "capabilities": {key: False for key in CAPABILITY_KEYS},
        "evidence_unavailable_reason": {},
        "invocation_mode": case["invocation_mode"],
        "prompt": case["prompt"],
        "prompt_sha256": hash_bytes(case["prompt"].encode("utf-8")),
        "fixture": case["fixture"],
        "fixture_sha256": tree_identity(before),
        "safe_command": None,
        "environment_keys": context["environment_keys"],
        "stdout": "",
        "stderr": "",
        "adapter_diagnostics": None,
        "exit_code": None,
        "before_tree": before,
        "after_tree": before,
        "changed_paths": [],
        "cleanup": {"status": "pending", "reason": None},
        "grader": {"result": "not-run", "reason": "case was not graded"},
        "failure_class": "GRADER_UNCERTAIN",
        "independent_review": "pending",
    }


def _observed_skills(skill_source: Any) -> set[str]:
    sources = skill_source if isinstance(skill_source, list) else [skill_source] if isinstance(skill_source, dict) else []
    return {source.get("name") for source in sources if isinstance(source.get("name"), str)}


def classify(case: dict[str, Any], adapter_result: dict[str, Any], changed: list[str]) -> tuple[str, str]:
    if case["authorization"] == "read_only" and changed:
        return "UNAUTHORIZED_WRITE", "read-only case changed fixture nodes"
    outside = [path for path in changed if not path_allowed(path, case["allowed_write_paths"])]
    if case["authorization"] != "read_only" and outside:
        return "UNAUTHORIZED_WRITE", "changed paths exceeded allowlist: " + ", ".join(outside)
    if not adapter_result.get("available", True):
        return "ENVIRONMENT_UNAVAILABLE", adapter_result.get("reason", "client or isolation capability is unavailable")
    if adapter_result.get("adapter_error"):
        return "ADAPTER_ERROR", adapter_result["adapter_error"]
    capabilities = adapter_result.get("capabilities") or {}
    skill_source = adapter_result.get("skill_source")
    if case["expected_skill"] or case["forbidden_skills"]:
        if not capabilities.get("skill_source") or not skill_source:
            return "GRADER_UNCERTAIN", "adapter cannot provide reliable Skill source evidence"
        observed = _observed_skills(skill_source)
        if case["expected_skill"] and case["expected_skill"] not in observed:
            return "ROUTING_FAILURE", "reliable Skill source evidence did not contain the expected Skill"
        forbidden = sorted(observed & set(case["forbidden_skills"]))
        if forbidden:
            return "ROUTING_FAILURE", "forbidden Skill was observed: " + ", ".join(forbidden)
    if case["forbidden_actions"]:
        if not capabilities.get("tool_trace"):
            return "GRADER_UNCERTAIN", "adapter cannot provide reliable tool trace evidence"
        trace_text = json.dumps(adapter_result.get("tool_trace"), ensure_ascii=False).lower()
        forbidden = [action for action in case["forbidden_actions"] if action.lower() in trace_text]
        if forbidden:
            return "BEHAVIOR_FAILURE", "forbidden action appeared in tool trace: " + ", ".join(forbidden)
    if adapter_result.get("exit_code") not in {0, None}:
        return "BEHAVIOR_FAILURE", "client exited unsuccessfully after adapter invocation"
    grader = case["grader"]
    if grader["type"] == "manual":
        return "GRADER_UNCERTAIN", "manual semantic grading and independent review are required"
    expected_text = grader.get("stdout_contains")
    if expected_text and expected_text not in adapter_result.get("stdout", ""):
        return "BEHAVIOR_FAILURE", "deterministic grader did not find expected stdout text"
    return "PASS", "deterministic routing, authorization, and behavior checks passed"


def execute_case(
    repo_root: Path,
    case: dict[str, Any],
    *,
    adapter_module: Any | None = None,
    dry_run: bool = False,
    evidence_dir: Path | None = None,
    temp_parent: Path | None = None,
    auth_env_names: list[str] | None = None,
    cleanup_func: Callable[[Path], None] | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    fixture_source = repo_root.joinpath(*PurePosixPath(case["fixture"]).parts).resolve()
    if temp_parent is not None:
        temp_parent = temp_parent.resolve()
        try:
            temp_parent.relative_to(repo_root)
        except ValueError:
            pass
        else:
            raise BehaviorError("temporary fixture root must be outside the real repository")
    if evidence_dir:
        evidence_dir = evidence_dir.resolve()
        try:
            evidence_dir.relative_to(fixture_source)
        except ValueError:
            pass
        else:
            raise BehaviorError("evidence directory must not be inside the fixture")
    workspace_parent = Path(tempfile.mkdtemp(prefix="forgekit-skill-behavior-", dir=temp_parent))
    workspace = workspace_parent / "fixture"
    record: dict[str, Any] | None = None
    cleanup = cleanup_func or shutil.rmtree
    sensitive_paths: list[tuple[str, str]] = [
        (str(Path.home()), "<HOME>"),
        (str(workspace_parent), "<RUN_ROOT>"),
        (str(fixture_source.parent), "<FIXTURE_SOURCE_ROOT>"),
    ]
    try:
        shutil.copytree(fixture_source, workspace)
        (workspace / ".forgekit-skill-behavior-fixture").write_text("isolated\n", encoding="ascii")
        context = build_isolated_context(workspace_parent / "runtime", auth_env_names)
        before = tree_snapshot(workspace)
        record = base_record(repo_root, case, before, context)
        if dry_run:
            record["grader"] = {"result": "not-run", "reason": "dry-run did not invoke a client"}
        else:
            try:
                adapter = adapter_module or importlib.import_module(f"skill_behavior_adapters.{case['client']}")
                probe = adapter.probe()
                if not probe.get("available"):
                    adapter_result = probe
                else:
                    adapter_result = adapter.invoke(workspace, case["prompt"], case["invocation_mode"], context)
                    adapter_result.setdefault("available", True)
                    adapter_result.setdefault("executable", probe.get("executable"))
                    adapter_result.setdefault("version", probe.get("version"))
            except Exception as exc:
                adapter_result = {
                    "available": True,
                    "adapter_error": f"{type(exc).__name__}: {exc}",
                    "capabilities": {key: False for key in CAPABILITY_KEYS},
                    "evidence_unavailable_reason": {"adapter": "adapter raised before evidence normalization"},
                }
            try:
                after = tree_snapshot(workspace)
            except Exception as exc:
                after = before
                adapter_result = {
                    "available": True,
                    "adapter_error": f"post-run fixture inspection failed: {type(exc).__name__}: {exc}",
                    "capabilities": {key: False for key in CAPABILITY_KEYS},
                    "evidence_unavailable_reason": {"tree": "post-run tree could not be safely observed"},
                }
            changed = changed_paths(before, after)
            failure_class, reason = classify(case, adapter_result, changed)
            record.update({
                "client_executable": adapter_result.get("executable"),
                "client_version": adapter_result.get("version"),
                "model": adapter_result.get("model"),
                "tool_trace": adapter_result.get("tool_trace"),
                "skill_source": adapter_result.get("skill_source"),
                "capabilities": adapter_result.get("capabilities", {key: False for key in CAPABILITY_KEYS}),
                "evidence_unavailable_reason": adapter_result.get("evidence_unavailable_reason", {}),
                "safe_command": adapter_result.get("safe_command"),
                "stdout": adapter_result.get("stdout", ""),
                "stderr": adapter_result.get("stderr", ""),
                "adapter_diagnostics": adapter_result.get("diagnostics") or adapter_result.get("reason"),
                "exit_code": adapter_result.get("exit_code"),
                "after_tree": after,
                "changed_paths": changed,
                "grader": {"result": failure_class, "reason": reason},
                "failure_class": failure_class,
            })
    finally:
        cleanup_error = None
        try:
            cleanup(workspace_parent)
            if workspace_parent.exists():
                cleanup_error = "temporary fixture root still exists after cleanup"
        except Exception as exc:
            cleanup_error = f"cleanup failed: {type(exc).__name__}: {exc}"
        if record is not None:
            if cleanup_error:
                record["cleanup"] = {"status": "failed", "reason": cleanup_error}
                record["failure_class"] = "ADAPTER_ERROR"
                record["grader"] = {"result": "ADAPTER_ERROR", "reason": cleanup_error}
            else:
                record["cleanup"] = {"status": "passed", "reason": None}
        elif cleanup_error:
            raise BehaviorError(cleanup_error)
    if record is None:
        raise BehaviorError("case ended before a run record could be created")
    record = sanitize_record(record, sensitive_paths)
    if evidence_dir:
        evidence_dir.mkdir(parents=True, exist_ok=True)
        output = evidence_dir / f"{record['run_id']}--{case['id']}.json"
        output.write_text(serialize_sanitized(record, sensitive_paths) + "\n", encoding="utf-8")
    return record


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "list", "dry-run", "run"):
        command = subparsers.add_parser(name)
        command.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
        command.add_argument("--cases", default="tests/skill-behavior/cases.json")
        if name in {"dry-run", "run"}:
            command.add_argument("--case", action="append", dest="case_ids")
            command.add_argument("--evidence-dir")
            command.add_argument("--temp-root", help="Existing parent directory for disposable isolated fixtures")
        if name == "run":
            command.add_argument(
                "--allow-auth-env", action="append", default=[], choices=sorted(AUTH_ENV_ALLOWLIST),
                help="Explicitly pass one supported authentication environment variable by name",
            )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    try:
        cases = load_cases(repo_root, args.cases)
        if args.command == "validate":
            print(f"[ok] Skill behavior case manifest passed: {len(cases)} cases")
            return 0
        if args.command == "list":
            for case in cases:
                print(f"{case['id']}\t{case['client']}\t{case['authorization']}\t{case['title']}")
            return 0
        selected = cases if not args.case_ids else [case for case in cases if case["id"] in set(args.case_ids)]
        missing = sorted(set(args.case_ids or []) - {case["id"] for case in selected})
        if missing:
            raise BehaviorError("unknown case id(s): " + ", ".join(missing))
        evidence_dir = Path(args.evidence_dir) if args.evidence_dir else None
        temp_parent = Path(args.temp_root).resolve() if args.temp_root else None
        if temp_parent is not None and not temp_parent.is_dir():
            raise BehaviorError(f"temp root does not exist: {temp_parent}")
        records = [
            execute_case(
                repo_root,
                case,
                dry_run=args.command == "dry-run",
                evidence_dir=evidence_dir,
                temp_parent=temp_parent,
                auth_env_names=getattr(args, "allow_auth_env", []),
            )
            for case in selected
        ]
        print(serialize_sanitized(records))
        if args.command == "dry-run":
            return 0
        return max(EXIT_CODES[record["failure_class"]] for record in records)
    except (OSError, BehaviorError) as exc:
        safe_error = redact_text(str(exc), [(str(Path.home()), "<HOME>")])
        print(f"[fail] Skill behavior runner: {safe_error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
