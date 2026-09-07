#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    tomllib = None


EXPECTED_AGENTS = {
    "forgekit-planner": ".codex/agents/forgekit-planner.toml",
    "forgekit-reviewer": ".codex/agents/forgekit-reviewer.toml",
    "forgekit-verifier": ".codex/agents/forgekit-verifier.toml",
    "forgekit-code-reviewer": ".codex/agents/forgekit-code-reviewer.toml",
}


def fail(message):
    raise SystemExit(f"[fail] {message}")


def split_names(value):
    names = []
    for item in value or []:
        for part in item.split(","):
            name = part.strip()
            if name:
                names.append(name)
    return names


def load_toml(path):
    if tomllib is None:
        return load_toml_minimal(path)
    with path.open("rb") as fh:
        return tomllib.load(fh)


def load_toml_minimal(path):
    data = {}
    in_multiline = False
    key = None
    buffer = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("["):
            continue
        if in_multiline:
            if line.endswith('"""'):
                buffer.append(line[:-3])
                data[key] = "\n".join(buffer)
                in_multiline = False
                key = None
                buffer = []
            else:
                buffer.append(raw_line)
            continue
        if "=" not in line:
            continue
        key, value = [part.strip() for part in line.split("=", 1)]
        if value.startswith('"""'):
            value = value[3:]
            if value.endswith('"""'):
                data[key] = value[:-3]
            else:
                in_multiline = True
                buffer = [value] if value else []
            continue
        if value.startswith('"') and value.endswith('"'):
            data[key] = value[1:-1]
        else:
            data[key] = value
    return data


def resolve_root(path):
    root = Path(path).expanduser().resolve()
    if not root.exists():
        fail(f"repo-root does not exist: {root}")
    if not root.is_dir():
        fail(f"repo-root is not a directory: {root}")
    template_root = root / "project-template"
    if (root / ".codex-plugin").is_dir() and (template_root / ".codex").is_dir():
        return template_root, "project-template"
    if (root / ".codex").is_dir():
        return root, "project"
    if (template_root / ".codex").is_dir():
        return template_root, "project-template"
    fail("could not find .codex/ in repo-root or repo-root/project-template")


def ensure_inside(root, path):
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        fail(f"path escapes root: {path}")
    return resolved


def check_agent(project_root, name, rel_path):
    path = project_root / rel_path
    result = {
        "name": name,
        "path": rel_path,
        "exists": path.is_file(),
        "schema_status": "fail",
        "issues": [],
    }
    if not path.is_file():
        result["issues"].append("missing file")
        return result
    try:
        data = load_toml(path)
    except Exception as exc:
        result["issues"].append(f"invalid TOML: {exc}")
        return result
    for field in ("name", "description", "developer_instructions"):
        value = data.get(field)
        if value is None:
            result["issues"].append(f"missing {field}")
            continue
        if not isinstance(value, str):
            result["issues"].append(f"{field} must be string, got {type(value).__name__}")
            continue
        if not value.strip():
            result["issues"].append(f"empty {field}")
    if data.get("name") != name:
        result["issues"].append(f"name mismatch: expected {name}, got {data.get('name')}")
    if not result["issues"]:
        result["schema_status"] = "pass"
    return result


def runtime_status(observed_agents, invoked_agents):
    expected = set(EXPECTED_AGENTS)
    observed = set(observed_agents)
    invoked = set(invoked_agents)
    if invoked & expected:
        return "available", "invoked", "native agent invocation was observed"
    if observed and not (observed & expected):
        return "unavailable", "installed", "only non-ForgeKit agents were observed"
    if observed & expected:
        return "unverified", "registered", "ForgeKit agents were listed but not invoked"
    return "unverified", "installed", "no runtime agent list was provided"


def write_report(project_root, mode, checks, config_exists, observed, invoked):
    report_path = ensure_inside(project_root, project_root / ".forgekit" / "codex-native-agent-report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    schema_status = "pass" if config_exists and all(item["schema_status"] == "pass" for item in checks) else "fail"
    native_status, native_lifecycle, reason = runtime_status(observed, invoked)
    lines = [
        "# Codex Native Agent Report",
        "",
        "Status: report-only",
        "Mode: codex-native-agent-doctor",
        f"SourceMode: {mode}",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"ProjectRoot: {project_root}",
        f"SchemaStatus: {schema_status}",
        f"NativeAgentStatus: {native_status}",
        f"NativeAgentLifecycle: {native_lifecycle}",
        f"RuntimeRegistration: {native_lifecycle}",
        "RuntimeRegistrationDefault: unverified",
        "NativeAgentStatusAllowed: available | unavailable | unverified",
        "Schema pass does not mean runtime registered.",
        "Only observed invocation of a configured forgekit-* agent means native is usable.",
        "",
        "## Summary",
        "",
        f"- config.toml: {'present' if config_exists else 'missing'}",
        f"- observed agents: {', '.join(observed) if observed else 'not provided'}",
        f"- invoked agents: {', '.join(invoked) if invoked else 'not provided'}",
        f"- runtime reason: {reason}",
        "",
        "## Agent Schema Checks",
        "",
    ]
    for item in checks:
        issues = "; ".join(item["issues"]) if item["issues"] else "none"
        lines.extend(
            [
                f"### {item['name']}",
                "",
                f"Agent: {item['name']}",
                f"Path: {item['path']}",
                f"Schema-Status: {item['schema_status']}",
                f"Exists: {str(item['exists']).lower()}",
                f"Issues: {issues}",
                "",
            ]
        )
    lines.extend(
        [
            "## Policy",
            "",
            "- This doctor does not start Codex.",
            "- This doctor does not spawn agents.",
            "- This doctor does not modify task-intake.md, work-log.md, loop-state, current docs, business docs, or template-lock.",
            "- If Codex only exposes default, explorer, or worker, record native_agent_status=unavailable and do not call fallback native success.",
            "- If spawn fails because of thread limit, max_threads, or open completed agents, record capacity blocked instead of native unavailable.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path, schema_status, native_status, native_lifecycle


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Report-only ForgeKit Codex native agent schema and runtime-observation doctor."
    )
    parser.add_argument("--repo-root", default=".", help="Generated project root or ForgeKit repo root.")
    parser.add_argument(
        "--observed-agent",
        action="append",
        default=[],
        help="Agent name observed in Codex runtime. Repeat or pass comma-separated names.",
    )
    parser.add_argument(
        "--invoked-agent",
        action="append",
        default=[],
        help="ForgeKit agent name explicitly observed as invoked. Repeat or pass comma-separated names.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    project_root, mode = resolve_root(args.repo_root)
    observed = split_names(args.observed_agent)
    invoked = split_names(args.invoked_agent)
    checks = [check_agent(project_root, name, rel_path) for name, rel_path in EXPECTED_AGENTS.items()]
    config_exists = (project_root / ".codex" / "config.toml").is_file()
    report_path, schema_status, native_status, native_lifecycle = write_report(
        project_root, mode, checks, config_exists, observed, invoked
    )
    print("# ForgeKit Codex Native Agent Doctor")
    print(f"Report: {report_path}")
    print(f"SchemaStatus: {schema_status}")
    print(f"NativeAgentStatus: {native_status}")
    print(f"NativeAgentLifecycle: {native_lifecycle}")
    if schema_status != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
