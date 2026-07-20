"""Fail-closed Codex CLI adapter for the isolated Skill behavior runner."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


CAPABILITY_KEYS = ("model", "tool_trace", "skill_source", "structured_output", "isolation")


def _empty_capabilities() -> dict[str, bool]:
    return {key: False for key in CAPABILITY_KEYS}


def probe() -> dict:
    executable = shutil.which("codex")
    if not executable:
        return {"available": False, "reason": "Codex CLI is not installed or not on PATH", "executable": None, "version": None}
    try:
        result = subprocess.run(
            [executable, "--version"], text=True, encoding="utf-8", errors="replace",
            capture_output=True, timeout=10, check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"available": False, "reason": f"Codex version probe failed: {exc}", "executable": executable, "version": None}
    return {
        "available": result.returncode == 0,
        "reason": None if result.returncode == 0 else "Codex version probe returned nonzero",
        "executable": executable,
        "command_prefix": [executable],
        "version": (result.stdout or result.stderr).strip(),
    }


def assess_isolation(availability: dict) -> dict[str, Any]:
    prefix = availability.get("command_prefix") or [availability["executable"]]
    try:
        result = subprocess.run(
            [*prefix, "exec", "--help"], text=True, encoding="utf-8", errors="replace",
            capture_output=True, timeout=10, check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ready": False, "reason": f"isolation capability unavailable: cannot inspect Codex help: {exc}"}
    help_text = result.stdout + result.stderr
    required = ("--ignore-user-config", "--ignore-rules", "--ephemeral", "--sandbox", "--json")
    missing = [flag for flag in required if flag not in help_text]
    reason = "isolation capability unavailable: Codex does not expose a verifiable fixture-only read boundary or network/external-action denial"
    if missing:
        reason += "; missing configuration isolation flags: " + ", ".join(missing)
    return {
        "ready": False,
        "reason": reason,
        "observed_flags": {flag: flag in help_text for flag in required},
        "fixture_read_boundary": False,
        "network_external_actions_denied": False,
    }


def _validate_context(workspace: Path, context: dict) -> None:
    marker = workspace / ".forgekit-skill-behavior-fixture"
    if not marker.is_file():
        raise ValueError("Codex adapter requires an isolated fixture marker")
    home = Path(context["home"]).resolve()
    try:
        home.relative_to(workspace.parent.resolve())
    except ValueError as exc:
        raise ValueError("Codex adapter HOME must be inside the disposable run root") from exc
    environment = context.get("environment")
    if not isinstance(environment, dict) or environment.get("HOME") != str(home) or environment.get("USERPROFILE") != str(home):
        raise ValueError("Codex adapter requires the runner-provided isolated environment")


def _parse_events(stdout: str) -> tuple[dict[str, Any], str | None]:
    events = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            return {}, f"Codex structured output parse failed: {exc}"
        if isinstance(event, dict):
            events.append(event)
    model = next((event.get("model") for event in events if isinstance(event.get("model"), str)), None)
    tools = [event for event in events if "tool" in str(event.get("type", "")).lower()]
    sources = [event.get("skill_source") for event in events if isinstance(event.get("skill_source"), dict)]
    return {
        "events": events,
        "model": model,
        "tool_trace": tools or None,
        "skill_source": sources or None,
    }, None


def _unavailable(availability: dict, reason: str, diagnostics: Any = None) -> dict:
    return {
        "available": False,
        "reason": reason,
        "diagnostics": diagnostics,
        "executable": availability.get("executable"),
        "version": availability.get("version"),
        "model": None,
        "tool_trace": None,
        "skill_source": None,
        "capabilities": _empty_capabilities(),
        "evidence_unavailable_reason": {key: reason for key in ("model", "tool_trace", "skill_source", "isolation")},
        "safe_command": None,
        "stdout": "",
        "stderr": "",
        "exit_code": None,
    }


def invoke(workspace: Path, prompt: str, invocation_mode: str, context: dict) -> dict:
    _validate_context(workspace, context)
    availability = probe()
    if not availability.get("available"):
        return _unavailable(availability, availability.get("reason", "Codex is unavailable"))
    isolation = assess_isolation(availability)
    if not isolation.get("ready"):
        return _unavailable(availability, isolation["reason"], isolation)
    prefix = availability.get("command_prefix") or [availability["executable"]]
    command = [
        *prefix, "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
        "--skip-git-repo-check", "--sandbox", "workspace-write", "--ask-for-approval", "never",
        "--json", "--cd", str(workspace), "-",
    ]
    safe_command = [
        "codex", "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
        "--skip-git-repo-check", "--sandbox", "workspace-write", "--ask-for-approval", "never",
        "--json", "--cd", "<fixture>", "-",
    ]
    try:
        result = subprocess.run(
            command, cwd=workspace, env=context["environment"], input=prompt,
            text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=300, check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            **_unavailable(availability, "Codex adapter invocation failed"),
            "available": True,
            "adapter_error": f"{type(exc).__name__}: {exc}",
            "safe_command": safe_command,
        }
    parsed, parse_error = _parse_events(result.stdout)
    if parse_error:
        return {
            "available": True, "adapter_error": parse_error, "executable": availability["executable"],
            "version": availability["version"], "model": None, "tool_trace": None, "skill_source": None,
            "capabilities": {**_empty_capabilities(), "isolation": True},
            "evidence_unavailable_reason": {"structured_output": parse_error}, "safe_command": safe_command,
            "stdout": result.stdout, "stderr": result.stderr, "exit_code": result.returncode,
            "diagnostics": {"invocation_mode": invocation_mode, "isolation": isolation},
        }
    capabilities = {
        "model": parsed["model"] is not None,
        "tool_trace": parsed["tool_trace"] is not None,
        "skill_source": parsed["skill_source"] is not None,
        "structured_output": True,
        "isolation": True,
    }
    missing = {key: f"Codex structured events did not expose {key}" for key in ("model", "tool_trace", "skill_source") if not capabilities[key]}
    return {
        "available": True, "executable": availability["executable"], "version": availability["version"],
        "model": parsed["model"], "tool_trace": parsed["tool_trace"], "skill_source": parsed["skill_source"],
        "capabilities": capabilities, "evidence_unavailable_reason": missing, "safe_command": safe_command,
        "stdout": result.stdout, "stderr": result.stderr, "exit_code": result.returncode,
        "diagnostics": {"invocation_mode": invocation_mode, "isolation": isolation},
    }
