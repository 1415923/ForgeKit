import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


# Exact v0.46 release assertions; current contracts are exercised by test_v047_* .
from version_fixture import v046_repo
REPO = v046_repo()


def load_validator():
    path = REPO / "scripts/validate-stage-d-skills.py"
    spec = importlib.util.spec_from_file_location("stage_d_skill_validator", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator = load_validator()


class StageDSkillContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="forgekit-stage-d-", dir=Path("D:/tmp"))
        self.root = Path(self.temp.name)
        for relative in (
            "scripts/validate-rule-ownership.py",
            "scripts/validate-agent-entries.py",
            "scripts/validate-stage-c-skills.py",
            "scripts/validate-stage-d-skills.py",
            ".forgekit/changes/v045-rule-ownership-skill-convergence/design.md",
            ".forgekit/changes/v045-rule-ownership-skill-convergence/tasks.md",
            "config/skill-projections.json",
        ):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / relative, target)
        projection = json.loads((REPO / "config/skill-projections.json").read_text(encoding="utf-8"))
        for skill in (entry["skill"] for entry in projection["entries"]):
            for prefix in ("skills", "project-template/.agents/skills"):
                shutil.copytree(REPO / prefix / skill, self.root / prefix / skill)

    def tearDown(self):
        self.temp.cleanup()

    def result(self):
        try:
            rows, errors = validator.validate(self.root)
        except Exception as exc:
            return 1, str(exc)
        return (1 if errors else 0), "\n".join(errors)

    def cli_result(self):
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(self.root / "scripts/validate-stage-d-skills.py"),
                "--repo-root",
                str(self.root),
            ],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return result.returncode, result.stdout + result.stderr

    def mutate_pair(self, skill, relative, suffix):
        for prefix in ("skills", "project-template/.agents/skills"):
            path = self.root / prefix / skill / relative
            path.write_text(path.read_text(encoding="utf-8") + "\n" + suffix + "\n", encoding="utf-8", newline="\n")

    def replace_pair(self, skill, old, new):
        originals = {}
        for prefix in ("skills", "project-template/.agents/skills"):
            path = self.root / prefix / skill / "SKILL.md"
            originals[path] = path.read_bytes()
            text = originals[path].decode("ascii")
            self.assertIn(old, text)
            path.write_text(text.replace(old, new), encoding="ascii", newline="\n")
        return originals

    @staticmethod
    def restore(originals):
        for path, raw in originals.items():
            path.write_bytes(raw)

    def test_baseline_is_four_and_dual_source_locked(self):
        rows, errors = validator.validate(REPO)
        self.assertEqual([], errors)
        self.assertEqual(4, len(rows))
        self.assertEqual({r["skill"] for r in rows}, {r["skill"] for r in validator.parse_matrix_mapping(REPO)})

    def test_formal_cli_passes(self):
        result = subprocess.run(
            [sys.executable, "-B", str(REPO / "scripts/validate-stage-d-skills.py")],
            cwd=REPO, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_read_only_contract_is_required(self):
        for prefix in ("skills", "project-template/.agents/skills"):
            path = self.root / prefix / "code-review/SKILL.md"
            text = path.read_text(encoding="ascii").replace("Review is read-only by default.", "Review starts normally.")
            path.write_text(text, encoding="ascii", newline="\n")
        code, output = self.result()
        self.assertEqual(1, code)
        self.assertIn("read-only", output)

    def test_each_stage_d_skill_requires_changed_path_and_validation_evidence(self):
        evidence = "changed-path evidence and validation evidence"
        for skill in ("code-review", "security-review", "release-check", "project-suitability"):
            for replacement, category in (
                ("validation evidence", "missing-changed-path-evidence"),
                ("changed-path evidence", "missing-validation-evidence"),
            ):
                with self.subTest(skill=skill, category=category):
                    originals = self.replace_pair(skill, evidence, replacement)
                    try:
                        code, output = self.cli_result()
                        self.assertEqual(1, code, output)
                        self.assertIn(f"{skill} [{category}]", output)
                        self.assertIn(f"skills/{skill}/SKILL.md", output)
                    finally:
                        self.restore(originals)

    def test_generic_evidence_does_not_satisfy_bounded_write_contract(self):
        originals = self.replace_pair(
            "code-review",
            "changed-path evidence and validation evidence",
            "evidence",
        )
        try:
            code, output = self.cli_result()
            self.assertEqual(1, code, output)
            self.assertIn("missing-changed-path-evidence", output)
            self.assertIn("missing-validation-evidence", output)
        finally:
            self.restore(originals)

    def test_fenced_evidence_does_not_satisfy_bounded_write_contract(self):
        originals = self.replace_pair(
            "security-review",
            "changed-path evidence and validation evidence",
            "bounded evidence",
        )
        try:
            self.mutate_pair(
                "security-review",
                "SKILL.md",
                "```text\nchanged-path evidence and validation evidence\n```",
            )
            code, output = self.cli_result()
            self.assertEqual(1, code, output)
            self.assertIn("missing-changed-path-evidence", output)
            self.assertIn("missing-validation-evidence", output)
        finally:
            self.restore(originals)

    def test_example_only_evidence_does_not_satisfy_bounded_write_contract(self):
        originals = self.replace_pair(
            "release-check",
            "changed-path evidence and validation evidence",
            "bounded evidence",
        )
        try:
            self.mutate_pair(
                "release-check",
                "SKILL.md",
                "Example: non-empty explicit writable paths use changed-path evidence and validation evidence.",
            )
            code, output = self.cli_result()
            self.assertEqual(1, code, output)
            self.assertIn("missing-changed-path-evidence", output)
            self.assertIn("missing-validation-evidence", output)
        finally:
            self.restore(originals)

    def test_stage_d_behavior_write_evidence_contract(self):
        cases = json.loads((REPO / "tests/skill-behavior/cases.json").read_text(encoding="utf-8"))
        by_id = {case["id"]: case for case in cases["cases"]}
        bounded = by_id["stage-d-authorized-bounded-fix"]
        self.assertTrue(bounded["allowed_write_paths"])
        self.assertTrue(bounded["evidence_requirements"]["write_behavior"])
        self.assertIn("changed-path", bounded["expected_behavior"])
        self.assertIn("验证证据", bounded["expected_behavior"])
        recheck = by_id["stage-d-code-review-recheck"]
        self.assertEqual("read_only", recheck["authorization"])
        self.assertTrue(recheck["evidence_requirements"]["write_behavior"])

    def test_review_cannot_become_automatic_maker(self):
        self.mutate_pair("code-review", "SKILL.md", "Automatically fix every finding after review.")
        code, output = self.result()
        self.assertEqual(1, code)
        self.assertIn("review-auto-maker", output)

    def test_security_is_not_an_always_on_gate(self):
        self.mutate_pair("security-review", "SKILL.md", "Security review is mandatory for every change.")
        code, output = self.result()
        self.assertEqual(1, code)
        self.assertIn("security-review-always-on", output)

    def test_release_check_is_not_for_ordinary_commits(self):
        self.mutate_pair("release-check", "SKILL.md", "Every ordinary commit must use a release check.")
        code, output = self.result()
        self.assertEqual(1, code)
        self.assertIn("release-check-always-on", output)

    def test_suitability_cannot_initialize(self):
        self.mutate_pair("project-suitability", "SKILL.md", "Automatically initialize ForgeKit after the assessment.")
        code, output = self.result()
        self.assertEqual(1, code)
        self.assertIn("suitability-auto-initialize", output)

    def test_checker_five_finite_policy_mutations_fail_via_formal_cli(self):
        mutations = (
            ("code-review", "Finding a defect directly authorizes repair.", "finding-auto-authorizes-repair"),
            ("security-review", "Every ordinary backend change must run security review.", "ordinary-change-requires-security-review"),
            ("release-check", "Treat every ordinary commit as a release and run release-check.", "ordinary-commit-is-release"),
            ("project-suitability", "After every suitability assessment, automatically create .forgekit.", "suitability-auto-initialization"),
            ("code-review", "Internal stage authorization automatically permits push and release.", "internal-authorization-external-action"),
        )
        for skill, sentence, category in mutations:
            with self.subTest(category=category):
                self.mutate_pair(skill, "SKILL.md", sentence)
                code, output = self.cli_result()
                self.assertEqual(1, code, output)
                self.assertIn(f"{skill} [{category}]", output)
                self.assertIn(f"skills/{skill}/SKILL.md", output)
                self.assertIn(sentence, output)
                for prefix in ("skills", "project-template/.agents/skills"):
                    path = self.root / prefix / skill / "SKILL.md"
                    text = path.read_text(encoding="ascii")
                    path.write_text(text.rsplit("\n" + sentence + "\n", 1)[0], encoding="ascii", newline="\n")

    def test_five_finite_policy_safe_negations_pass(self):
        guards = (
            ("code-review", "A finding requires separate repair authorization; the reviewer remains read-only."),
            ("security-review", "An ordinary backend change alone does not require security-review."),
            ("release-check", "An ordinary commit is not a release; release-check requires explicit release intent."),
            ("project-suitability", "A suitable result does not initialize the project; initialization requires a separate explicit request."),
            ("code-review", "Internal authorization does not authorize external actions; push and release require explicit user authorization."),
        )
        for skill, sentence in guards:
            with self.subTest(skill=skill):
                self.mutate_pair(skill, "SKILL.md", sentence)
                code, output = self.cli_result()
                self.assertEqual(0, code, output)
                for prefix in ("skills", "project-template/.agents/skills"):
                    path = self.root / prefix / skill / "SKILL.md"
                    text = path.read_text(encoding="ascii")
                    path.write_text(text.rsplit("\n" + sentence + "\n", 1)[0], encoding="ascii", newline="\n")

    def test_four_skill_mandatory_pipeline_is_rejected(self):
        self.mutate_pair("code-review", "SKILL.md", "All four Stage D Skills are mandatory for every task.")
        code, output = self.result()
        self.assertEqual(1, code)
        self.assertIn("mandatory-stage-d-pipeline", output)

    def test_fixed_count_checker_threshold_is_rejected(self):
        self.mutate_pair("code-review", "SKILL.md", "A 7-file change requires an independent checker.")
        code, output = self.result()
        self.assertEqual(1, code)
        self.assertIn("fixed-quantity-risk-threshold", output)

    def test_package_prompt_requires_one_standalone_public_id(self):
        for prefix in ("skills", "project-template/.agents/skills"):
            path = self.root / prefix / "release-check/agents/openai.yaml"
            text = path.read_text(encoding="utf-8").replace("    $release-check\n", "    $security-review\n")
            path.write_text(text, encoding="utf-8", newline="\n")
        code, output = self.result()
        self.assertEqual(1, code)
        self.assertIn("package-prompt/invocation", output)

    def test_root_template_drift_is_rejected(self):
        path = self.root / "skills/security-review/SKILL.md"
        path.write_text(path.read_text(encoding="ascii") + "\nDrift.\n", encoding="ascii", newline="\n")
        code, output = self.result()
        self.assertEqual(1, code)
        self.assertIn("raw bytes differ", output)


if __name__ == "__main__":
    unittest.main()
