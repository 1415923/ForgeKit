#!/usr/bin/env python3
"""Validate the finite Stage E release-gate wiring contract."""

from __future__ import annotations

import argparse
import ast
import importlib.util
import re
from pathlib import Path


STAGE_E_SCRIPT = "scripts/validate-stage-e-release.py"
REQUIRED_PATHS = (
    "scripts/validate-plugin-assets.ps1",
    "scripts/validate-template.ps1",
    "scripts/test-release-consistency.ps1",
    "scripts/smoke-test.py",
    "scripts/test-fresh-clone-crlf.py",
)
RUNTIME_CANARY_SCRIPT = "scripts/test-stage-e-gate-runtime.py"
RUNTIME_CANARY_TEST = "tests/test_stage_e_gate_runtime.py"
RUNTIME_CANARY_CHILD_ENV = "FORGEKIT_STAGE_E_RUNTIME_CANARY_CHILD"
EXPECTED_RUNTIME_GATES = (
    "plugin", "template", "release-consistency", "smoke", "fresh-clone",
)


def normalized(text: str) -> str:
    return text.replace("\\", "/")


def powershell_stage_e_wiring(relative: str, text: str) -> list[str]:
    errors = []
    value = normalized(text)
    assignment = re.search(
        r"\$stageEValidator\s*=\s*Join-Path\s+\$(?:repoRoot|scriptRoot)\s+[\"'](?:scripts/)?validate-stage-e-release\.py[\"']",
        value,
        re.IGNORECASE,
    )
    invocation = re.search(
        r"&\s*python\s+-B\s+\$stageEValidator\s+--repo-root\s+\$repoRoot\s+2>&1",
        value,
        re.IGNORECASE,
    )
    if relative.endswith("validate-plugin-assets.ps1"):
        capture = re.search(r"\$stageEExitCode\s*=\s*\$LASTEXITCODE", value, re.IGNORECASE)
        guard = re.search(r"if\s*\(\s*\$stageEExitCode\s+-ne\s+0\s*\)", value, re.IGNORECASE)
    elif relative.endswith("validate-template.ps1"):
        capture = re.search(r"\$(?:stageEExitCode|LASTEXITCODE)\s*(?:=\s*\$LASTEXITCODE)?", value, re.IGNORECASE)
        guard = re.search(r"if\s*\(\s*\$(?:stageEExitCode|LASTEXITCODE)\s+-ne\s+0\s*\)", value, re.IGNORECASE)
    else:
        capture = re.search(r"\$exitCode\s*=\s*\$LASTEXITCODE", value, re.IGNORECASE)
        guard = (
            re.search(r"ExitCode\s*=\s*\$exitCode", value, re.IGNORECASE)
            and len(re.findall(r"Invoke-StageEReleaseValidator", value, re.IGNORECASE)) > 1
        )
    if not assignment or not invocation:
        errors.append(f"stage-e-gate-wiring-missing: {relative}: direct Stage E invocation")
    if not capture or not guard:
        errors.append(f"stage-e-gate-wiring-invalid: {relative}: Stage E exit code is not propagated")
    return errors


def validate_python_wiring(relative: str, text: str) -> list[str]:
    errors = []
    if relative.endswith("smoke-test.py"):
        try:
            tree = ast.parse(text)
        except SyntaxError:
            tree = None
        valid = False
        if tree is not None:
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                function = node.func
                if not isinstance(function, ast.Name) or function.id != "run":
                    continue
                constants = {
                    item.value
                    for item in ast.walk(node)
                    if isinstance(item, ast.Constant) and isinstance(item.value, str)
                }
                if "scripts/validate-stage-e-release.py" in constants and "--repo-root" in constants:
                    valid = True
                    break
    else:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            tree = None
        valid = False
        if tree is not None:
            for node in ast.walk(tree):
                if not isinstance(node, (ast.Tuple, ast.List)):
                    continue
                constants = {item.value for item in ast.walk(node) if isinstance(item, ast.Constant) and isinstance(item.value, str)}
                if "stage_e" in constants and STAGE_E_SCRIPT in constants:
                    valid = True
                    break
    if not valid:
        errors.append(f"stage-e-gate-wiring-missing: {relative}: Stage E command is not in the executable command structure")
    return errors


def validate_repo(repo: Path) -> list[str]:
    repo = repo.resolve()
    errors = []
    for relative in REQUIRED_PATHS:
        path = repo / relative
        if not path.is_file():
            errors.append(f"stage-e-gate-wiring-missing: {relative}: required gate file is absent")
            continue
        text = path.read_text(encoding="utf-8")
        if relative.endswith(".ps1"):
            errors.extend(powershell_stage_e_wiring(relative, text))
        else:
            errors.extend(validate_python_wiring(relative, text))

    plugin = repo / "scripts/validate-plugin-assets.ps1"
    if plugin.is_file():
        value = normalized(plugin.read_text(encoding="utf-8"))
        wiring_assignment = re.search(
            r"\$wiringValidator\s*=\s*Join-Path\s+\$repoRoot\s+[\"']scripts/validate-release-gate-wiring\.py[\"']",
            value,
            re.IGNORECASE,
        )
        wiring_invocation = re.search(
            r"&\s*python\s+-B\s+\$wiringValidator\s+--repo-root\s+\$repoRoot\s+2>&1",
            value,
            re.IGNORECASE,
        )
        wiring_capture = re.search(r"\$wiringExitCode\s*=\s*\$LASTEXITCODE", value, re.IGNORECASE)
        wiring_guard = re.search(r"if\s*\(\s*\$wiringExitCode\s+-ne\s+0\s*\)", value, re.IGNORECASE)
        if not wiring_assignment or not wiring_invocation:
            errors.append("stage-e-gate-wiring-missing: scripts/validate-plugin-assets.ps1: independent wiring validator invocation")
        if not wiring_capture or not wiring_guard:
            errors.append("stage-e-gate-wiring-invalid: scripts/validate-plugin-assets.ps1: wiring validator exit code is not propagated")

    # Runtime artifacts are a release-worktree contract. Lightweight validator
    # fixtures without .git continue to exercise the pre-existing direct wiring.
    if (repo / ".git").exists():
        for relative in (RUNTIME_CANARY_SCRIPT, RUNTIME_CANARY_TEST):
            if not (repo / relative).is_file():
                errors.append(f"stage-e-runtime-canary-missing: {relative}")
        runtime_path = repo / RUNTIME_CANARY_SCRIPT
        if runtime_path.is_file():
            try:
                spec = importlib.util.spec_from_file_location("stage_e_gate_runtime", runtime_path)
                module = importlib.util.module_from_spec(spec)
                assert spec.loader is not None
                spec.loader.exec_module(module)
                gates = tuple(module.REQUIRED_RUNTIME_GATES)
            except Exception as exc:
                errors.append(f"stage-e-runtime-canary-invalid: {RUNTIME_CANARY_SCRIPT}: {exc}")
            else:
                if gates != EXPECTED_RUNTIME_GATES:
                    errors.append(
                        "stage-e-runtime-canary-invalid: fixed gate registration mismatch: "
                        f"expected={EXPECTED_RUNTIME_GATES} actual={gates}"
                    )
        release = repo / "scripts/test-release-consistency.ps1"
        if release.is_file():
            release_text = normalized(release.read_text(encoding="utf-8"))
            runtime_assignment = re.search(
                r"\$runtimeCanary\s*=\s*Join-Path\s+\$scriptRoot\s+[\"']test-stage-e-gate-runtime\.py[\"']",
                release_text,
                re.IGNORECASE,
            )
            runtime_invocation = re.search(
                r"&\s*python\s+-B\s+\$runtimeCanary\s+--repo-root\s+\$repoRoot\s+2>&1",
                release_text,
                re.IGNORECASE,
            )
            runtime_capture = re.search(
                r"\$runtimeCanaryExitCode\s*=\s*\$LASTEXITCODE", release_text, re.IGNORECASE
            )
            runtime_guard = re.search(
                r"if\s*\(\s*\$runtimeCanaryExitCode\s+-ne\s+0\s*\)", release_text, re.IGNORECASE
            )
            if not runtime_assignment or not runtime_invocation:
                errors.append(
                    "stage-e-runtime-canary-wiring-missing: scripts/test-release-consistency.ps1"
                )
            if not runtime_capture or not runtime_guard:
                errors.append(
                    "stage-e-runtime-canary-wiring-invalid: scripts/test-release-consistency.ps1: exit code is not propagated"
                )
            if RUNTIME_CANARY_CHILD_ENV not in release_text:
                errors.append(
                    "stage-e-runtime-canary-wiring-invalid: scripts/test-release-consistency.ps1: child recursion marker is absent"
                )
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate_repo(Path(args.repo_root))
    if errors:
        for error in errors:
            print(f"[fail] {error}")
        raise SystemExit(1)
    print(f"[ok] Stage E gate wiring passed: required_paths={len(REQUIRED_PATHS)}")


if __name__ == "__main__":
    main()
