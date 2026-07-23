#!/usr/bin/env python3
"""Prove that the five frozen top-level gates propagate a Stage E failure."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


CHILD_ENV = "FORGEKIT_STAGE_E_RUNTIME_CANARY_CHILD"
MARKER_ENV = "FORGEKIT_STAGE_E_RUNTIME_CANARY_MARKER"
REQUIRED_RUNTIME_GATES = (
    "plugin",
    "template",
    "release-consistency",
    "smoke",
    "fresh-clone",
)
GATE_WORK_NAMES = {
    "plugin": "p", "template": "t", "release-consistency": "r",
    "smoke": "s", "fresh-clone": "f",
}
CANARY_MANIFEST = Path("project-template/.forgekit/template-manifest.json")
CANARY_VERSION = "0.44.1"
CANARY_DIAGNOSTIC = "version [template manifest]"


def powershell_executable() -> str:
    executable = shutil.which("pwsh") or shutil.which("powershell")
    if not executable:
        raise RuntimeError("PowerShell is required for the Stage E runtime canary")
    return executable


def gate_command(name: str, repo: Path) -> list[str]:
    powershell = powershell_executable()
    commands = {
        "plugin": [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ".\\scripts\\validate-plugin-assets.ps1"],
        "template": [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ".\\scripts\\validate-template.ps1"],
        "release-consistency": [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ".\\scripts\\test-release-consistency.ps1"],
        "smoke": [sys.executable, "-B", "scripts/smoke-test.py", "--repo-root", str(repo)],
        "fresh-clone": [sys.executable, "-B", "scripts/test-fresh-clone-crlf.py", "--repo-root", str(repo)],
    }
    return commands[name]


def load_fresh_clone_tool(repo: Path):
    path = repo / "scripts/test-fresh-clone-crlf.py"
    spec = importlib.util.spec_from_file_location("stage_e_runtime_fresh_clone", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_process(command: list[str], cwd: Path, env: dict[str, str], timeout: int = 1800) -> dict:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    rendered = (result.stdout or "") + (result.stderr or "")
    return {
        "exit_code": result.returncode,
        "command": [str(item) for item in command],
        "stage_e_diagnostic": CANARY_DIAGNOSTIC in rendered,
        "output_tail": rendered[-30000:],
    }


def clone_candidate(seed: Path, target: Path) -> None:
    result = subprocess.run(
        ["git", "-c", "core.autocrlf=false", "clone", "--no-local", str(seed), str(target)],
        cwd=seed.parent,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    if result.returncode:
        raise RuntimeError(f"candidate clone failed ({result.returncode}): {result.stdout}{result.stderr}")


def install_stage_e_observer(repo: Path) -> None:
    validator = repo / "scripts/validate-stage-e-release.py"
    source = validator.read_text(encoding="utf-8")
    needle = "from pathlib import Path\n"
    if needle not in source:
        raise RuntimeError(f"Stage E observer insertion point is absent: {validator}")
    observer = (
        "from pathlib import Path\n\n"
        "_runtime_canary_marker = __import__('os').environ.get("
        "'FORGEKIT_STAGE_E_RUNTIME_CANARY_MARKER')\n"
        "if _runtime_canary_marker:\n"
        "    Path(_runtime_canary_marker).write_text("
        "'stage-e-invoked\\n', encoding='utf-8', newline='\\n')\n"
    )
    validator.write_text(source.replace(needle, observer, 1), encoding="utf-8", newline="\n")


def inject_canary(repo: Path) -> None:
    path = repo / CANARY_MANIFEST
    data = json.loads(path.read_bytes().decode("utf-8"))
    if data.get("template_version") != "0.45.0":
        raise RuntimeError(
            f"runtime canary requires template_version=0.45.0 before mutation: {path}"
        )
    data["template_version"] = CANARY_VERSION
    path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def child_environment(temp_root: Path, marker: Path) -> dict[str, str]:
    temp_root.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment[CHILD_ENV] = "1"
    environment[MARKER_ENV] = str(marker)
    environment["TEMP"] = str(temp_root)
    environment["TMP"] = str(temp_root)
    if os.name == "nt":
        shim = temp_root / "powershell.cmd"
        shim.write_text(f'@"{powershell_executable()}" %*\n', encoding="ascii", newline="\r\n")
        environment["PATH"] = str(temp_root) + os.pathsep + environment.get("PATH", "")
    return environment


def evaluate_gate(name: str, seed: Path, work: Path) -> dict:
    baseline = work / "b"
    canary = work / "c"
    clone_candidate(seed, baseline)
    clone_candidate(seed, canary)
    install_stage_e_observer(baseline)
    install_stage_e_observer(canary)
    inject_canary(canary)
    baseline_marker = work / "baseline-stage-e-invoked"
    canary_marker = work / "canary-stage-e-invoked"
    baseline_result = run_process(
        gate_command(name, baseline), baseline,
        child_environment(work / "tb", baseline_marker),
    )
    canary_result = run_process(
        gate_command(name, canary), canary,
        child_environment(work / "tc", canary_marker),
    )
    baseline_result["stage_e_invoked"] = baseline_marker.is_file()
    canary_result["stage_e_invoked"] = canary_marker.is_file()
    passed = (
        baseline_result["exit_code"] == 0
        and baseline_result["stage_e_invoked"]
        and canary_result["exit_code"] != 0
        and canary_result["stage_e_invoked"]
        and canary_result["stage_e_diagnostic"]
    )
    return {
        "gate": name,
        "baseline": baseline_result,
        "canary": canary_result,
        "passed": passed,
    }


def candidate_seed(repo: Path, target: Path) -> str:
    tool = load_fresh_clone_tool(repo)
    return tool.construct_commit(repo, target)


def run_runtime_canary(repo: Path, selected: tuple[str, ...], temp_parent: Path | None = None) -> dict:
    if not (repo / ".git").exists():
        raise RuntimeError(f"runtime canary requires a Git worktree: {repo}")
    temp_root = Path(tempfile.mkdtemp(prefix="sr-", dir=temp_parent))
    evidence = {"candidate_commit": None, "canary": str(CANARY_MANIFEST), "gates": {}}
    try:
        seed = temp_root / "z"
        evidence["candidate_commit"] = candidate_seed(repo, seed)
        max_workers = min(len(selected), 5)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(evaluate_gate, name, seed, temp_root / GATE_WORK_NAMES[name]): name
                for name in selected
            }
            for future in as_completed(futures):
                name = futures[future]
                try:
                    evidence["gates"][name] = future.result()
                except Exception as exc:  # diagnostics belong in the evidence record
                    evidence["gates"][name] = {
                        "gate": name,
                        "passed": False,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
        evidence["passed"] = all(evidence["gates"].get(name, {}).get("passed") for name in selected)
        return evidence
    finally:
        tool = load_fresh_clone_tool(repo)
        tool.remove_tree(temp_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--gate", action="append", choices=REQUIRED_RUNTIME_GATES)
    parser.add_argument("--json-output")
    parser.add_argument("--temp-root")
    args = parser.parse_args(argv)
    selected = tuple(args.gate or REQUIRED_RUNTIME_GATES)
    if len(selected) != len(set(selected)):
        parser.error("--gate values must be unique")
    if args.temp_root:
        temp_parent = Path(args.temp_root).resolve()
    else:
        short_root = Path("D:/tmp")
        temp_parent = short_root if os.name == "nt" and short_root.is_dir() else None
    try:
        evidence = run_runtime_canary(
            Path(args.repo_root).resolve(),
            selected,
            temp_parent,
        )
    except Exception as exc:
        print(f"[fail] Stage E runtime canary setup: {type(exc).__name__}: {exc}")
        return 1
    for name in selected:
        result = evidence["gates"][name]
        if "error" in result:
            print(f"[fail] {name}: {result['error']}")
            continue
        baseline_exit = result["baseline"]["exit_code"]
        canary_exit = result["canary"]["exit_code"]
        label = "ok" if result["passed"] else "fail"
        print(
            f"[{label}] {name}: baseline_exit={baseline_exit} expected=0; "
            f"canary_exit={canary_exit} expected=nonzero; "
            f"baseline_stage_e={result['baseline']['stage_e_invoked']}; "
            f"canary_stage_e={result['canary']['stage_e_invoked']}; "
            f"diagnostic_propagated={result['canary']['stage_e_diagnostic']}; "
            f"command={' '.join(result['canary']['command'])}"
        )
    if args.json_output:
        Path(args.json_output).write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
    if not evidence["passed"]:
        print("[fail] Stage E runtime canary did not prove every selected gate")
        return 1
    print(f"[ok] Stage E runtime canary passed: gates={len(selected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
