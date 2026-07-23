import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "release_gate_wiring", REPO / "scripts/validate-release-gate-wiring.py"
)
WIRING = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(WIRING)


class ReleaseGateWiringTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fke-wiring-", dir=r"D:\tmp")
        self.repo = Path(self.temp.name) / "repo"
        (self.repo / ".git").mkdir(parents=True)
        for relative in (
            *WIRING.REQUIRED_PATHS,
            "scripts/validate-release-gate-wiring.py",
            WIRING.RUNTIME_CANARY_SCRIPT,
            WIRING.RUNTIME_CANARY_TEST,
        ):
            target = self.repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / relative, target)

    def tearDown(self):
        self.temp.cleanup()

    def errors(self):
        return WIRING.validate_repo(self.repo)

    def rewrite(self, relative, old, new):
        path = self.repo / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def test_baseline_wiring_passes(self):
        self.assertEqual([], self.errors())

    def test_plugin_stage_e_invocation_removal_fails(self):
        self.rewrite(
            "scripts/validate-plugin-assets.ps1",
            "$stageEOutput = & python -B $stageEValidator --repo-root $repoRoot 2>&1",
            "$stageEOutput = @()",
        )
        self.assertTrue(any("stage-e-gate-wiring-missing" in item and "validate-plugin-assets" in item for item in self.errors()))

    def test_plugin_ignored_exit_code_fails(self):
        self.rewrite(
            "scripts/validate-plugin-assets.ps1",
            "$stageEExitCode = $LASTEXITCODE",
            "$stageEExitCode = 0",
        )
        self.assertTrue(any("stage-e-gate-wiring-invalid" in item and "validate-plugin-assets" in item for item in self.errors()))

    def test_plugin_invalid_stage_e_path_fails(self):
        self.rewrite(
            "scripts/validate-plugin-assets.ps1",
            'scripts\\validate-stage-e-release.py',
            'scripts\\missing-stage-e-release.py',
        )
        self.assertTrue(any("stage-e-gate-wiring-missing" in item and "validate-plugin-assets" in item for item in self.errors()))

    def test_template_stage_e_wiring_removal_fails(self):
        path = self.repo / "scripts/validate-template.ps1"
        text = path.read_text(encoding="utf-8").replace("validate-stage-e-release.py", "removed-stage-e-release.py")
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("stage-e-gate-wiring-missing" in item and "validate-template" in item for item in self.errors()))

    def test_release_consistency_stage_e_wiring_removal_fails(self):
        path = self.repo / "scripts/test-release-consistency.ps1"
        text = path.read_text(encoding="utf-8").replace("validate-stage-e-release.py", "removed-stage-e-release.py")
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("stage-e-gate-wiring-missing" in item and "test-release-consistency" in item for item in self.errors()))

    def test_runtime_canary_script_is_required(self):
        (self.repo / WIRING.RUNTIME_CANARY_SCRIPT).unlink()
        self.assertTrue(any("stage-e-runtime-canary-missing" in item for item in self.errors()))

    def test_runtime_canary_test_is_required(self):
        (self.repo / WIRING.RUNTIME_CANARY_TEST).unlink()
        self.assertTrue(any("stage-e-runtime-canary-missing" in item for item in self.errors()))

    def test_release_consistency_runtime_canary_wiring_is_required(self):
        self.rewrite(
            "scripts/test-release-consistency.ps1",
            "$runtimeCanaryOutput = & python -B $runtimeCanary --repo-root $repoRoot 2>&1",
            "$runtimeCanaryOutput = @()",
        )
        self.assertTrue(any("stage-e-runtime-canary-wiring-missing" in item for item in self.errors()))

    def test_release_consistency_runtime_canary_exit_is_required(self):
        self.rewrite(
            "scripts/test-release-consistency.ps1",
            "$runtimeCanaryExitCode = $LASTEXITCODE",
            "$runtimeCanaryExitCode = 0",
        )
        self.assertTrue(any("stage-e-runtime-canary-wiring-invalid" in item for item in self.errors()))


if __name__ == "__main__":
    unittest.main()
