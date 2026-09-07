import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


# Exact v0.46 release assertions; current contracts are exercised by test_v047_* .
from version_fixture import v046_repo
REPO = v046_repo()
SCRIPT = REPO / "scripts/test-stage-e-gate-runtime.py"
SPEC = importlib.util.spec_from_file_location("stage_e_gate_runtime", SCRIPT)
RUNTIME = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(RUNTIME)
NESTED = os.environ.get(RUNTIME.CHILD_ENV) == "1"


@unittest.skipIf(NESTED, "nested top-level gate skips only runtime-canary orchestration tests")
class StageEGateRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent = Path("D:/tmp") if os.name == "nt" and Path("D:/tmp").is_dir() else None
        cls.temp_root = Path(tempfile.mkdtemp(prefix="segr-test-", dir=parent))
        cls.seed = cls.temp_root / "candidate"
        RUNTIME.candidate_seed(REPO, cls.seed)

    @classmethod
    def tearDownClass(cls):
        tool = RUNTIME.load_fresh_clone_tool(REPO)
        tool.remove_tree(cls.temp_root)

    def clone_case(self, name):
        target = self.temp_root / name
        if target.exists():
            RUNTIME.load_fresh_clone_tool(REPO).remove_tree(target)
        RUNTIME.clone_candidate(self.seed, target)
        return target

    def run_runtime(self, repo, *gates):
        evidence_path = self.temp_root / f"{repo.name}-evidence.json"
        command = [
            sys.executable, "-B", str(repo / "scripts/test-stage-e-gate-runtime.py"),
            "--repo-root", str(repo), "--json-output", str(evidence_path),
        ]
        for gate in gates:
            command.extend(["--gate", gate])
        result = subprocess.run(
            command, cwd=repo, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace", timeout=2400,
        )
        evidence = json.loads(evidence_path.read_text(encoding="utf-8")) if evidence_path.is_file() else {}
        return result, evidence

    def plugin_block(self, repo):
        path = repo / "scripts/validate-plugin-assets.ps1"
        text = path.read_text(encoding="utf-8")
        start = text.index("    $stageEValidator = Join-Path $repoRoot")
        end_marker = '        Add-Error "Stage E release structure check failed:'
        end = text.index("\n    }", text.index(end_marker, start)) + len("\n    }")
        return path, text, start, end

    def assert_plugin_break_is_caught(self, name, mutate):
        repo = self.clone_case(name)
        path, text, start, end = self.plugin_block(repo)
        path.write_text(mutate(text, start, end), encoding="utf-8", newline="\n")
        result, evidence = self.run_runtime(repo, "plugin")
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        plugin = evidence.get("gates", {}).get("plugin", {})
        self.assertFalse(plugin.get("passed", True), evidence)
        if "canary" in plugin:
            self.assertTrue(
                not plugin["canary"].get("stage_e_invoked")
                or not plugin["canary"].get("stage_e_diagnostic"),
                evidence,
            )

    def test_fixed_five_gate_runtime_canary(self):
        result, evidence = self.run_runtime(REPO)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(set(RUNTIME.REQUIRED_RUNTIME_GATES), set(evidence["gates"]))
        for name in RUNTIME.REQUIRED_RUNTIME_GATES:
            with self.subTest(gate=name):
                self.assertEqual(0, evidence["gates"][name]["baseline"]["exit_code"])
                self.assertTrue(evidence["gates"][name]["baseline"]["stage_e_invoked"])
                self.assertNotEqual(0, evidence["gates"][name]["canary"]["exit_code"])
                self.assertTrue(evidence["gates"][name]["canary"]["stage_e_invoked"])
                self.assertTrue(evidence["gates"][name]["canary"]["stage_e_diagnostic"])

    def test_commented_plugin_stage_e_block_is_caught(self):
        def mutate(text, start, end):
            block = text[start:end]
            commented = "\n".join("# " + line if line.strip() else line for line in block.splitlines())
            return text[:start] + commented + text[end:]
        self.assert_plugin_break_is_caught("commented", mutate)

    def test_false_branch_plugin_stage_e_block_is_caught(self):
        def mutate(text, start, end):
            block = text[start:end]
            indented = "\n".join("    " + line for line in block.splitlines())
            return text[:start] + "    if ($false) {\n" + indented + "\n    }" + text[end:]
        self.assert_plugin_break_is_caught("false-branch", mutate)

    def test_deleted_plugin_stage_e_block_is_caught(self):
        self.assert_plugin_break_is_caught("deleted", lambda text, start, end: text[:start] + text[end:])

    def test_missing_validator_path_is_caught(self):
        def mutate(text, _start, _end):
            return text.replace("scripts\\validate-stage-e-release.py", "scripts\\missing-stage-e-release.py", 1)
        self.assert_plugin_break_is_caught("missing-path", mutate)

    def test_swallowed_stage_e_exit_is_caught(self):
        def mutate(text, _start, _end):
            return text.replace("$stageEExitCode = $LASTEXITCODE", "$stageEExitCode = 0", 1)
        self.assert_plugin_break_is_caught("swallowed-exit", mutate)

    def test_child_marker_does_not_bypass_stage_e(self):
        repo = self.clone_case("child-marker")
        RUNTIME.inject_canary(repo)
        environment = os.environ.copy()
        environment[RUNTIME.CHILD_ENV] = "1"
        command = RUNTIME.gate_command("release-consistency", repo)
        result = subprocess.run(
            command, cwd=repo, env=environment, check=False, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", timeout=600,
        )
        rendered = result.stdout + result.stderr
        self.assertNotEqual(0, result.returncode, rendered)
        self.assertIn("nested Stage E runtime-canary orchestration skipped", rendered)
        self.assertIn("template-manifest", rendered)


if __name__ == "__main__":
    unittest.main()
