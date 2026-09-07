import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


# Exact v0.46 release assertions; current contracts are exercised by test_v047_* .
from version_fixture import v046_repo
REPO = v046_repo()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validator = load_module("stage_c_skill_validator", REPO / "scripts/validate-stage-c-skills.py")
policy = load_module("stage_c_policy_helper", REPO / "scripts/validate-agent-entries.py")


class StageCSkillContractTests(unittest.TestCase):
    def setUp(self):
        if self._testMethodName in {
            "test_fixed_quantity_factor_families_are_data_driven",
            "test_init_action_matcher_positive_negative_symmetry",
            "test_reinitialize_factor_families_and_safe_scope",
            "test_mandatory_pipeline_factor_families_and_safe_scope",
        }:
            self.temp = None
            self.skills = [row["skill"] for row in validator.stage_c_rows(REPO)]
            return
        self.temp = tempfile.TemporaryDirectory(prefix="forgekit-stage-c-skills-", dir=Path("D:/tmp"))
        self.root = Path(self.temp.name)
        for relative in (
            "scripts/validate-rule-ownership.py",
            "scripts/validate-agent-entries.py",
            "scripts/validate-stage-c-skills.py",
            "scripts/update-template-manifest.py",
            ".forgekit/changes/v045-rule-ownership-skill-convergence/design.md",
            ".forgekit/changes/v045-rule-ownership-skill-convergence/tasks.md",
            "config/skill-projections.json",
            "project-template/.forgekit/template-manifest.json",
            ".gitattributes",
            "project-template/.gitattributes",
            "VERSION",
        ):
            source = REPO / relative
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        self.rows = validator.stage_c_rows(REPO)
        self.skills = [row["skill"] for row in self.rows]
        projection = json.loads((REPO / "config/skill-projections.json").read_text(encoding="utf-8"))
        for skill in (entry["skill"] for entry in projection["entries"]):
            for prefix in ("skills", "project-template/.agents/skills"):
                source = REPO / prefix / skill
                target = self.root / prefix / skill
                shutil.copytree(source, target, copy_function=shutil.copyfile)

    def tearDown(self):
        if self.temp is not None:
            self.temp.cleanup()

    def run_cli(self):
        try:
            _, errors = validator.validate(self.root)
        except (OSError, UnicodeError, json.JSONDecodeError, validator.StageCSkillError) as exc:
            errors = [str(exc)]
        rendered = "\n".join(errors)
        return SimpleNamespace(returncode=1 if errors else 0, stdout="", stderr=rendered)

    def assert_fails(self, expected):
        result = self.run_cli()
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(expected, result.stdout + result.stderr)

    def mutate_package_pair(self, skill, relative, old, new):
        for prefix in ("skills", "project-template/.agents/skills"):
            path = self.root / prefix / skill / relative
            text = path.read_text(encoding="utf-8")
            self.assertIn(old, text)
            path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
        source = f".agents/skills/{skill}/{Path(relative).as_posix()}"
        manifest_path = self.root / "project-template/.forgekit/template-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entry = next((item for item in manifest["files"] if item["source_path"] == source), None)
        if entry is not None:
            entry["checksum"] = validator.canonical_checksum(self.root / "project-template" / source)
            manifest_path.write_bytes(
                (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            )

    def materialize_manifest_sources(self):
        manifest = json.loads(
            (REPO / "project-template/.forgekit/template-manifest.json").read_text(encoding="utf-8")
        )
        for item in manifest["files"]:
            source = REPO / "project-template" / item["source_path"]
            target = self.root / "project-template" / item["source_path"]
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)

    def test_baseline_is_five_and_dual_source_locked(self):
        rows, errors = validator.validate(REPO)
        self.assertEqual([], errors)
        self.assertEqual(5, len(rows))
        self.assertEqual(set(self.skills), {row["skill"] for row in validator.parse_matrix_sources(REPO)[0]})

    def test_current_version_lifecycle_requires_manifest_consistency(self):
        cases = (
            ("0.45.0", "0.45.0", 0),
            ("0.45.0", "0.44.1", 1),
            ("0.44.1", "0.44.1", 0),
            ("0.44.1", "0.45.0", 1),
        )
        for version, manifest_version, expected_exit in cases:
            with self.subTest(version=version, manifest=manifest_version):
                (self.root / "VERSION").write_text(version + "\n", encoding="ascii", newline="\n")
                manifest_path = self.root / "project-template/.forgekit/template-manifest.json"
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest["template_version"] = manifest_version
                manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
                result = self.run_cli()
                self.assertEqual(expected_exit, result.returncode, result.stderr)
                if expected_exit:
                    self.assertIn("current-version-mismatch", result.stderr)
                    self.assertIn("VERSION", result.stderr)
                    self.assertIn("template-manifest.json", result.stderr)

    def test_formal_cli_propagates_success_exit_code(self):
        result = subprocess.run(
            [sys.executable, "-B", str(REPO / "scripts/validate-stage-c-skills.py")], cwd=REPO,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, timeout=30,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_frontmatter_implicit_policy_is_rejected(self):
        self.mutate_package_pair(
            "project-bootstrap-fill", "SKILL.md", "name: project-bootstrap-fill\n",
            "name: project-bootstrap-fill\nmetadata:\n  allow_implicit_invocation: false\n",
        )
        self.assert_fails("unsupported in SKILL.md frontmatter")

    def test_explicit_policy_missing_wrong_level_and_string_are_rejected(self):
        old = "\npolicy:\n  allow_implicit_invocation: false\n"
        self.mutate_package_pair("project-bootstrap-fill", "agents/openai.yaml", old, "\n")
        self.assert_fails("missing policy.allow_implicit_invocation")

        self.setUp_from_repo()
        self.mutate_package_pair(
            "project-bootstrap-fill", "agents/openai.yaml", old,
            "\nmetadata:\n  allow_implicit_invocation: false\n",
        )
        self.assert_fails("missing policy.allow_implicit_invocation")

        self.setUp_from_repo()
        self.mutate_package_pair(
            "project-bootstrap-fill", "agents/openai.yaml", "allow_implicit_invocation: false",
            'allow_implicit_invocation: "false"',
        )
        self.assert_fails("must be boolean")

    def setUp_from_repo(self):
        self.temp.cleanup()
        self.setUp()

    def test_old_package_prompts_are_rejected(self):
        self.mutate_package_pair(
            "project-init", "agents/openai.yaml", "Initialize only this uninitialized project from existing evidence.",
            "Run a questionnaire and selected stack templates. Initialize only this uninitialized project from existing evidence.",
        )
        self.assert_fails("questionnaire")
        self.setUp_from_repo()
        self.mutate_package_pair(
            "document-backfill", "agents/openai.yaml", "Backfill only verified facts",
            "Backfill one source document at a time. Backfill only verified facts",
        )
        self.assert_fails("one source document at a time")

    def test_default_prompts_have_one_exact_public_invocation(self):
        for skill in self.skills:
            package = validator.yaml.safe_load(
                (REPO / "skills" / skill / "agents/openai.yaml").read_text(encoding="utf-8")
            )
            prompt = package["interface"]["default_prompt"]
            formal, tokens = validator.prompt_invocations(prompt)
            self.assertEqual([skill], formal, skill)
            self.assertEqual([skill], tokens, skill)

    def test_default_prompt_missing_duplicate_wrong_and_fenced_invocations_fail(self):
        cases = (
            (r"$project-init\n\n", "", "missing standalone"),
            (r"$project-init\n\n", r"$project-init\n$project-init\n\n", "duplicate standalone"),
            (r"$project-init\n\n", r"$handover-review\n\n", "wrong standalone"),
            (r"$project-init\n\n", r"~~~text\n$project-init\n~~~\n\n", "missing standalone"),
        )
        for old, new, expected in cases:
            self.setUp_from_repo()
            self.mutate_package_pair("project-init", "agents/openai.yaml", old, new)
            self.assert_fails(expected)

    def test_fixed_quantity_thresholds_in_default_prompt_fail_but_safe_examples_pass(self):
        unsafe = (
            "Treat changes touching 5 files as large changes.",
            "More than 17 files requires large-change planning.",
            "Use this Skill whenever three modules are modified.",
            "A change over 900 lines must use the large-change workflow.",
            "Seven components is the threshold for independent planning.",
        )
        for sentence in unsafe:
            self.setUp_from_repo()
            self.mutate_package_pair(
                "large-change-planning", "agents/openai.yaml",
                "Plan this change only when impact warrants staged planning.",
                f"Plan this change only when impact warrants staged planning. {sentence}",
            )
            self.assert_fails("package-prompt/fixed-quantity-risk-threshold")
        safe = (
            "Do not use 5 files as a risk threshold.",
            "A five-file deterministic projection can remain low risk.",
            "File count alone does not trigger large-change planning.",
            "For example, 5 files may still be low risk.",
        )
        for sentence in safe:
            self.setUp_from_repo()
            self.mutate_package_pair(
                "large-change-planning", "agents/openai.yaml",
                "Plan this change only when impact warrants staged planning.",
                f"Plan this change only when impact warrants staged planning. {sentence}",
            )
            self.assertEqual(0, self.run_cli().returncode, sentence)

    def test_yaml_projection_drift_is_rejected(self):
        path = self.root / "project-template/.agents/skills/project-init/agents/openai.yaml"
        path.write_bytes(path.read_bytes() + b"\n# drift\n")
        self.assert_fails("root and .agents bytes differ")

    def test_manifest_missing_checksum_and_duplicate_are_rejected(self):
        path = self.root / "project-template/.forgekit/template-manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        required = ".agents/skills/handover-review/SKILL.md"
        data["files"] = [item for item in data["files"] if item["source_path"] != required]
        path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        self.assert_fails("Stage C completeness")

        self.setUp_from_repo()
        path = self.root / "project-template/.forgekit/template-manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        yaml_path = ".agents/skills/project-init/agents/openai.yaml"
        next(item for item in data["files"] if item["source_path"] == yaml_path)["checksum"] = "sha256:" + "0" * 64
        path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        self.assert_fails("checksum")

        self.setUp_from_repo()
        path = self.root / "project-template/.forgekit/template-manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["files"].append(dict(next(item for item in data["files"] if item["source_path"] == yaml_path)))
        path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        self.assert_fails("duplicate")

    def test_manifest_contains_all_eighteen_projection_targets_and_ten_stage_c_files(self):
        manifest = json.loads(
            (REPO / "project-template/.forgekit/template-manifest.json").read_text(encoding="utf-8")
        )
        sources = [item["source_path"] for item in manifest["files"]]
        projected = {path for _, _, path in validator.projection_managed_paths(REPO)}
        self.assertEqual(18, len(projected))
        self.assertTrue(projected <= set(sources))
        stage_c = {
            f".agents/skills/{skill}/{relative}"
            for skill in self.skills for relative in ("SKILL.md", "agents/openai.yaml")
        }
        self.assertEqual(10, len(stage_c))
        self.assertTrue(stage_c <= set(sources))
        for missing in (
            ".agents/skills/handover-review/agents/openai.yaml",
            ".agents/skills/large-change-planning/agents/openai.yaml",
            ".agents/skills/code-review/agents/openai.yaml",
        ):
            self.setUp_from_repo()
            path = self.root / "project-template/.forgekit/template-manifest.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["files"] = [item for item in data["files"] if item["source_path"] != missing]
            path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
            self.assert_fails(missing)

    def test_manifest_generator_rejects_missing_target_and_restores_complete_set(self):
        self.materialize_manifest_sources()
        manifest_path = self.root / "project-template/.forgekit/template-manifest.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        missing = ".agents/skills/handover-review/agents/openai.yaml"
        data["files"] = [item for item in data["files"] if item["source_path"] != missing]
        manifest_path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        command = [
            sys.executable, "-B", str(self.root / "scripts/update-template-manifest.py"),
            "--repo-root", str(self.root),
        ]
        checked = subprocess.run(
            command + ["--check"], cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, check=False, timeout=30,
        )
        self.assertNotEqual(0, checked.returncode)
        self.assertIn(missing, checked.stdout + checked.stderr)
        refreshed = subprocess.run(
            command, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, check=False, timeout=30,
        )
        self.assertEqual(0, refreshed.returncode, refreshed.stdout + refreshed.stderr)
        restored = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(1, [item["source_path"] for item in restored["files"]].count(missing))

    def test_projection_config_new_target_without_manifest_update_fails_generator(self):
        self.materialize_manifest_sources()
        config_path = self.root / "config/skill-projections.json"
        data = json.loads(config_path.read_text(encoding="utf-8"))
        data["entries"][0]["managed_files"].append("EXTRA.md")
        config_path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        extra = self.root / "project-template/.agents/skills" / data["entries"][0]["skill"] / "EXTRA.md"
        extra.write_bytes(b"extra\n")
        result = subprocess.run(
            [sys.executable, "-B", str(self.root / "scripts/update-template-manifest.py"),
             "--repo-root", str(self.root), "--check"],
            cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, check=False, timeout=30,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("exactly 18", result.stdout + result.stderr)

    def test_existing_project_reinitialization_examples_fail_and_safe_negation_passes(self):
        unsafe = (
            "Existing projects should be initialized again from scratch.",
            "Project initialization also applies to already initialized projects.",
            "Reinitialize an existing ForgeKit project before handover review.",
        )
        for sentence in unsafe:
            self.setUp_from_repo()
            self.mutate_package_pair("project-init", "SKILL.md", "Use only when all of these are true:", f"Use only when all of these are true:\n\n{sentence}")
            self.assert_fails("existing-project-reinitialize")
        for sentence in (
            "Existing projects must not be reinitialized.",
            "Route an existing project to handover-review or project-bootstrap-fill.",
        ):
            self.setUp_from_repo()
            self.mutate_package_pair("project-init", "SKILL.md", "Use only when all of these are true:", f"Use only when all of these are true:\n\n{sentence}")
            self.assertEqual(0, self.run_cli().returncode)

    def test_mandatory_pipeline_examples_fail_and_safe_negation_passes(self):
        unsafe = (
            "Always run all five Stage C Skills in sequence.",
            "Every task must execute project-init, project-bootstrap-fill, handover-review, document-backfill, and large-change-planning in order.",
            "These five Skills form a mandatory pipeline for every project task.",
        )
        for sentence in unsafe:
            self.setUp_from_repo()
            self.mutate_package_pair("project-init", "SKILL.md", "Use only when all of these are true:", f"Use only when all of these are true:\n\n{sentence}")
            self.assert_fails("mandatory-five-skill-pipeline")
        self.setUp_from_repo()
        self.mutate_package_pair("project-init", "SKILL.md", "Use only when all of these are true:", "Use only when all of these are true:\n\nDo not run all five Skills in sequence. Select only the Skill that matches the current task.")
        self.assertEqual(0, self.run_cli().returncode)

    def test_checker_c_m01_regression_and_c_m03_nine_cases_via_formal_cli(self):
        unsafe = (
            (
                "large-change-planning", "agents/openai.yaml",
                "Plan this change only when impact warrants staged planning.",
                "A 42-directory change requires independent planning.",
                "package-prompt/fixed-quantity-risk-threshold",
                ("quantity='42'", "unit='directory'"),
            ),
            (
                "project-init", "SKILL.md", "Use only when all of these are true:",
                "Run the bootstrap process once more for repositories that are already initialized.",
                "existing-project-reinitialize",
                ("features=existing_subject,init_action,repeat_action,positive_requirement",),
            ),
            (
                "project-init", "SKILL.md", "Use only when all of these are true:",
                "For each project that has already been initialized, run project setup again.",
                "existing-project-reinitialize",
                ("features=existing_subject,init_action,repeat_action,positive_requirement",),
            ),
            (
                "project-init", "SKILL.md", "Use only when all of these are true:",
                "Bootstrap an already initialized repository again.",
                "existing-project-reinitialize",
                ("features=existing_subject,init_action,repeat_action,positive_requirement",),
            ),
            (
                "project-init", "SKILL.md", "Use only when all of these are true:",
                "Set up each existing workspace from scratch.",
                "existing-project-reinitialize",
                ("features=existing_subject,init_action,repeat_action,positive_requirement",),
            ),
            (
                "project-init", "SKILL.md", "Use only when all of these are true:",
                "Every request must complete each Stage C Skill before finishing.",
                "mandatory-five-skill-pipeline",
                ("features=full_skill_set,universal_scope,mandatory,sequence",),
            ),
            (
                "project-init", "SKILL.md", "Use only when all of these are true:",
                "The complete Stage C Skill set is a required chain for any change.",
                "mandatory-five-skill-pipeline",
                ("features=full_skill_set,universal_scope,mandatory,sequence",),
            ),
            (
                "project-init", "SKILL.md", "Use only when all of these are true:",
                "Every Stage C Skill is compulsory for every project request.",
                "mandatory-five-skill-pipeline",
                ("features=full_skill_set,universal_scope,mandatory",),
            ),
            (
                "project-init", "SKILL.md", "Use only when all of these are true:",
                "Each of the five Skills is mandatory for every task.",
                "mandatory-five-skill-pipeline",
                ("features=full_skill_set,universal_scope,mandatory",),
            ),
            (
                "project-init", "SKILL.md", "Use only when all of these are true:",
                "The complete set of five forms a prerequisite chain for each change.",
                "mandatory-five-skill-pipeline",
                ("features=full_skill_set,universal_scope,mandatory,sequence",),
            ),
            (
                "project-init", "SKILL.md", "Use only when all of these are true:",
                "All five Skills are required one at a time for any project request.",
                "mandatory-five-skill-pipeline",
                ("features=full_skill_set,universal_scope,mandatory,sequence",),
            ),
        )
        for skill, relative, marker, sentence, category, details in unsafe:
            affected = (
                self.root / "skills" / skill / relative,
                self.root / "project-template/.agents/skills" / skill / relative,
                self.root / "project-template/.forgekit/template-manifest.json",
            )
            originals = {path: path.read_bytes() for path in affected}
            try:
                self.mutate_package_pair(
                    skill, relative, marker, f"{marker}\n\n{sentence}",
                )
                result = subprocess.run(
                    [sys.executable, "-B", str(self.root / "scripts/validate-stage-c-skills.py"),
                     "--repo-root", str(self.root)],
                    cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, check=False, timeout=30,
                )
            finally:
                for path, original in originals.items():
                    path.write_bytes(original)
            output = result.stdout + result.stderr
            self.assertEqual(1, result.returncode, sentence)
            self.assertIn(skill, output)
            self.assertIn(category, output)
            self.assertIn(sentence, output)
            for detail in details:
                self.assertIn(detail, output)

        safe_sentences = (
            "Existing repositories may continue to handover-review without repeating setup.",
            "An already initialized project must not be bootstrapped again.",
            "An existing repository should not be bootstrapped again.",
            "Previously initialized workspaces cannot be bootstrapped anew.",
            "Existing projects continue without bootstrapping again.",
            "An initialized workspace must not be set up again.",
            "Bootstrapping an initialized project again is not required.",
        )
        for sentence in safe_sentences:
            skill = "project-init"
            relative = "SKILL.md"
            marker = "Use only when all of these are true:"
            affected = (
                self.root / "skills" / skill / relative,
                self.root / "project-template/.agents/skills" / skill / relative,
                self.root / "project-template/.forgekit/template-manifest.json",
            )
            originals = {path: path.read_bytes() for path in affected}
            try:
                self.mutate_package_pair(skill, relative, marker, f"{marker}\n\n{sentence}")
                result = subprocess.run(
                    [sys.executable, "-B", str(self.root / "scripts/validate-stage-c-skills.py"),
                     "--repo-root", str(self.root)],
                    cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, check=False, timeout=30,
                )
            finally:
                for path, original in originals.items():
                    path.write_bytes(original)
            output = result.stdout + result.stderr
            self.assertEqual(0, result.returncode, f"expected=0 actual={result.returncode}: {output}")
            self.assertNotIn("existing-project-reinitialize", output)
            self.assertNotIn("features=existing_subject", output)

    def test_fixed_quantity_factor_families_are_data_driven(self):
        unsafe = (
            ("A 42-directory change requires independent planning.", "42", "directory"),
            ("More than 11 folders must use the staged workflow.", "More than 11", "folders"),
            ("Changing three services automatically becomes a large change.", "Changing three", "services"),
            ("Twenty-eight is not needed; 28 packages is the threshold for formal review.", "28", "packages"),
            ("A change over 700 lines mandates heavy planning.", "over 700", "lines"),
            ("Changes affecting nine endpoints require an independent checker.", "affecting nine", "endpoints"),
            ("Dozens of classes triggers escalation.", "Dozens", "classes"),
        )
        for sentence, quantity, unit in unsafe:
            with self.subTest(sentence=sentence):
                matches = validator.fixed_quantity_thresholds(sentence, policy)
                self.assertEqual(1, len(matches))
                self.assertEqual(quantity.casefold(), matches[0]["quantity"].casefold())
                self.assertEqual(unit, matches[0]["unit"].casefold())
                self.assertTrue(matches[0]["trigger"])
                self.assertTrue(matches[0]["target"])

        safe = (
            "A 42-directory change does not automatically require independent planning.",
            "Directory count alone is not a risk threshold.",
            "Even changes across ten services may remain low risk.",
            "Three modules are mentioned here only as an example.",
            "Do not classify work by file, directory, or module count.",
            "A 42-directory deterministic projection can remain low risk.",
        )
        for sentence in safe:
            with self.subTest(sentence=sentence):
                self.assertEqual([], validator.fixed_quantity_thresholds(sentence, policy))

    def test_reinitialize_factor_families_and_safe_scope(self):
        unsafe = (
            "Bootstrap an already initialized repository again.",
            "Set up each existing workspace from scratch.",
            "Bootstrap every previously initialized workspace once more.",
            "Set the existing repository up again before review.",
            "For each initialized project, set it up from scratch.",
            "Before handover, bootstrap the existing project anew.",
            "Setting up an already initialized workspace again is required.",
            "An existing repository must be bootstrapped again.",
            "Bootstrapping an existing workspace from scratch is required.",
            "Run the bootstrap process once more for repositories that are already initialized.",
            "For each project that has already been initialized, run project setup again.",
            "An initialized project is required to go through project setup again before review.",
            "Before review, reinitialize every previously initialized repository.",
            "Previously initialized workspaces must repeat the setup process.",
            "Restart project initialization for an existing repository.",
            "A project that has already been initialized should bootstrap again before continuing.",
            "Project setup must be performed anew for every initialized workspace.",
            "Reinitialize repositories that have already been initialized before audit.",
            "Any workspace that is already initialized must run bootstrap again.",
            "Bootstrap is required once more for each previously initialized repository.",
        )
        safe = (
            "An already initialized project must not be bootstrapped again.",
            "An existing repository should not be bootstrapped again.",
            "Previously initialized workspaces cannot be bootstrapped anew.",
            "Do not bootstrap an initialized project again.",
            "Never bootstrap an existing repository from scratch.",
            "An initialized workspace must not be set up again.",
            "Do not set the existing repository up again.",
            "Existing projects continue without bootstrapping again.",
            "Use handover-review instead of bootstrapping the project again.",
            "Bootstrapping an initialized project again is not required.",
            "Do not bootstrap an already initialized repository again.",
            "Never set up an existing workspace from scratch.",
            "Existing repositories continue without bootstrapping again.",
            "Use handover-review instead of setting the workspace up again.",
            "The documentation explains the term bootstrap.",
            "The phrase set up appears only as an example.",
            "Bootstrap files are present in the repository.",
            "An existing workspace may continue without setup.",
            "An existing project must document bootstrappable helpers again.",
            "An existing repository must document bootstrapper roles again.",
            "An existing workspace must document setup-like labels again.",
            "An existing project must discuss upset again.",
            "Existing repositories may continue to handover-review without repeating setup.",
            "Previously initialized workspaces continue without rerunning bootstrap.",
            "An initialized project must not go through setup again.",
            "Do not reinitialize previously initialized repositories.",
            "Existing projects go to handover-review instead of project setup.",
            "Project setup is not required again before review.",
            "Reinitialization should never be used for an existing workspace.",
            "The text explains why initialized projects are not bootstrapped again.",
            "Use project-bootstrap-fill rather than reinitializing an existing project.",
            "Skip initialization and continue to handover-review for an existing workspace.",
        )
        for sentence in unsafe:
            with self.subTest(sentence=sentence):
                self.assertIn(
                    "existing-project-reinitialize",
                    [match["category"] for match in validator.semantic_reversals(sentence, policy, set(self.skills))],
                )
        for sentence in safe:
            with self.subTest(sentence=sentence):
                self.assertEqual([], validator.semantic_reversals(sentence, policy, set(self.skills)))

    def test_init_action_matcher_positive_negative_symmetry(self):
        cases = (
            (
                "bootstrap",
                "An existing project must bootstrap again.",
                "An existing project must not bootstrap again.",
            ),
            (
                "bootstrap",
                "An already initialized project must be bootstrapped again.",
                "An already initialized project must not be bootstrapped again.",
            ),
            (
                "bootstrap",
                "An initialized project requires bootstrapping again.",
                "Bootstrapping an initialized project again is not required.",
            ),
            (
                "set-up",
                "An existing workspace must set up again.",
                "An existing workspace must not set up again.",
            ),
            (
                "set-up",
                "An existing repository must set it up again.",
                "An existing repository must not set it up again.",
            ),
            (
                "initialize",
                "An existing project must be initialized again.",
                "An existing project must not be initialized again.",
            ),
            (
                "reinitialize",
                "An existing project must reinitialize.",
                "An existing project must not reinitialize.",
            ),
        )
        for family, positive, negative in cases:
            with self.subTest(family=family, positive=positive):
                positive_actions = validator.directive_init_action_matches(positive)
                negative_actions = validator.directive_init_action_matches(negative)
                self.assertTrue(any(action.family == family for action in positive_actions))
                self.assertTrue(any(action.family == family for action in negative_actions))
                for sentence, actions in ((positive, positive_actions), (negative, negative_actions)):
                    for action in actions:
                        self.assertEqual(sentence[action.start:action.end], action.text)
                self.assertTrue(all(not validator.init_action_is_negated(positive, action) for action in positive_actions))
                self.assertTrue(all(validator.init_action_is_negated(negative, action) for action in negative_actions))
                self.assertIn(
                    "existing-project-reinitialize",
                    [match["category"] for match in validator.semantic_reversals(positive, policy, set(self.skills))],
                )
                self.assertEqual([], validator.semantic_reversals(negative, policy, set(self.skills)))

    def test_mandatory_pipeline_factor_families_and_safe_scope(self):
        unsafe = (
            "Every request must complete each Stage C Skill before finishing.",
            "The complete Stage C Skill set is a required chain for any change.",
            "Every Stage C Skill is compulsory for every project request.",
            "Each of the five Skills is mandatory for every task.",
            "The complete set of five forms a prerequisite chain for each change.",
            "All five Skills are required one at a time for any project request.",
            "All Stage C Skills form a mandatory one-by-one workflow for each project.",
            "For every project request, all five Skills have to be processed sequentially as one required workflow.",
            "Always take each task through every Stage C Skill in a fixed order.",
            "Each request must pass through the complete set of Stage C Skills.",
            "Every change runs every Skill one after another.",
            "The full set of five is a prerequisite pipeline for all work.",
            "No Stage C Skill may be skipped for any task.",
            "All Stage C Skills are required for each request.",
            "The complete Stage C Skill set is mandatory for any task.",
            "Each task has to complete every Stage C Skill before finishing.",
            "No Stage C Skill may be skipped for every project request.",
        )
        safe = (
            "All Stage C Skills are documented, but they are alternatives.",
            "For each request, all Stage C Skills are alternatives rather than a mandatory set.",
            "Not every request uses every Stage C Skill.",
            "Not every task requires each Stage C Skill.",
            "Choose one matching Skill rather than processing all of them.",
            "The five Skills do not form a sequential workflow.",
            "There is no fixed order among the Stage C Skills.",
            "A task may use more than one Skill, but it need not use all five.",
            "No task is required to pass through every Skill.",
            "Every Stage C Skill is available, but only the matching one is required.",
            "Every request uses only the matching Skill; all Stage C Skills remain alternatives.",
        )
        for sentence in unsafe:
            with self.subTest(sentence=sentence):
                self.assertIn(
                    "mandatory-five-skill-pipeline",
                    [match["category"] for match in validator.semantic_reversals(sentence, policy, set(self.skills))],
                )
        for sentence in safe:
            with self.subTest(sentence=sentence):
                self.assertEqual([], validator.semantic_reversals(sentence, policy, set(self.skills)))

    def test_extended_safe_negations_pass(self):
        safe = (
            "Existing projects must not be initialized from scratch again.",
            "Do not repeat project initialization for an already initialized project.",
            "Reinitialization is not required before handover for an existing project.",
            "The five Skills are alternatives, not a sequential workflow.",
            "Not every task goes through all five Skills in sequence.",
            "All five are documented here, but they are not a mandatory pipeline.",
        )
        for sentence in safe:
            self.setUp_from_repo()
            self.mutate_package_pair(
                "project-init", "SKILL.md", "Use only when all of these are true:",
                f"Use only when all of these are true:\n\n{sentence}",
            )
            self.assertEqual(0, self.run_cli().returncode, sentence)

    def test_fenced_and_heading_required_markers_cannot_fake_contract(self):
        self.mutate_package_pair(
            "handover-review", "SKILL.md", "Handover review is read-only by default.",
            "```text\nHandover review is read-only by default.\n```",
        )
        self.assert_fails("missing prose contract")
        self.setUp_from_repo()
        self.mutate_package_pair(
            "handover-review", "SKILL.md", "Handover review is read-only by default.",
            "### Handover review is read-only by default.",
        )
        self.assert_fails("missing prose contract")

    def test_fenced_heading_and_navigation_legacy_text_do_not_false_positive(self):
        additions = (
            "\n```text\nAutomatically repair every finding.\n```\n",
            "\n### Automatically repair every finding.\n",
            "\nSee `skills/handover-review/SKILL.md` and [handover-review](skills/handover-review/SKILL.md).\n",
            "\n```text\nSet up each existing workspace from scratch.\n```\n",
            "\nThe example is `Set up each existing workspace from scratch.`\n",
        )
        for addition in additions:
            self.setUp_from_repo()
            self.mutate_package_pair("handover-review", "SKILL.md", "# Handover Review", "# Handover Review" + addition)
            self.assertEqual(0, self.run_cli().returncode)

    def test_plain_list_table_and_link_followed_contradictions_fail(self):
        additions = (
            "\n- The handover review automatically repairs defects.\n",
            "\n| policy | behavior |\n| --- | --- |\n| handover review | automatically repair defects |\n",
            "\nSee [audit guide](docs/audit.md). The handover review automatically repairs defects.\n",
        )
        for addition in additions:
            self.setUp_from_repo()
            self.mutate_package_pair("handover-review", "SKILL.md", "# Handover Review", "# Handover Review" + addition)
            self.assert_fails("forbidden regression")

    def test_existing_stage_c_regression_mutations(self):
        cases = (
            ("project-init", "Ask only for information", "Ask exactly 4 questions. Ask only for information", "forbidden regression"),
            ("project-bootstrap-fill", "Preserve existing customization and confirmed content.", "Overwrite existing customization and confirmed content.", "forbidden regression"),
            ("handover-review", "Findings may recommend another Skill", "Findings may automatically repair defects. Findings may recommend another Skill", "forbidden regression"),
            ("document-backfill", "Evidence gaps remain `UNKNOWN` or `TODO_REVIEW`", "When evidence is insufficient, infer plausible completion. Evidence gaps remain `UNKNOWN` or `TODO_REVIEW`", "forbidden regression"),
            ("large-change-planning", "Use when objective impact requires a staged plan:", "Use when work touches more than 5 files or more than 2 modules. Use when objective impact requires a staged plan:", "fixed-quantity-risk-threshold"),
            ("large-change-planning", "Self-review does not satisfy an independent gate.", "All code changes must require an independent checker. Self-review does not satisfy an independent gate.", "forbidden regression"),
        )
        for skill, old, new, expected in cases:
            self.setUp_from_repo()
            self.mutate_package_pair(skill, "SKILL.md", old, new)
            self.assert_fails(expected)

    def test_matrix_and_tasks_cardinality_mutations_fail(self):
        design = self.root / ".forgekit/changes/v045-rule-ownership-skill-convergence/design.md"
        text = design.read_text(encoding="utf-8")
        design.write_text(text.replace("阶段 C 收敛具体触发", "后续收敛具体触发", 1), encoding="utf-8")
        self.assert_fails("Source B must contain exactly five")

        self.setUp_from_repo()
        tasks = self.root / ".forgekit/changes/v045-rule-ownership-skill-convergence/tasks.md"
        text = tasks.read_text(encoding="utf-8")
        tasks.write_text("\n".join(line for line in text.splitlines() if not line.startswith("| SC-05 ")) + "\n", encoding="utf-8")
        self.assert_fails("Source A must contain exactly")

    def test_dual_sources_different_stage_d_and_duplicates_fail(self):
        tasks = self.root / ".forgekit/changes/v045-rule-ownership-skill-convergence/tasks.md"
        text = tasks.read_text(encoding="utf-8")
        tasks.write_text(text.replace("skills/project-init/SKILL.md", "skills/code-review/SKILL.md", 1), encoding="utf-8")
        self.assert_fails("sources disagree")

        self.setUp_from_repo()
        tasks = self.root / ".forgekit/changes/v045-rule-ownership-skill-convergence/tasks.md"
        tasks.write_text(tasks.read_text(encoding="utf-8").replace("skills/project-init/SKILL.md", "skills/code-review/SKILL.md", 1), encoding="utf-8")
        design = self.root / ".forgekit/changes/v045-rule-ownership-skill-convergence/design.md"
        design.write_text(
            design.read_text(encoding="utf-8").replace(
                "`skills/project-init/SKILL.md` | `.agents` 投影",
                "`skills/code-review/SKILL.md` | `.agents` 投影", 1,
            ), encoding="utf-8",
        )
        self.assert_fails("Stage D Skill owner")

        self.setUp_from_repo()
        tasks = self.root / ".forgekit/changes/v045-rule-ownership-skill-convergence/tasks.md"
        tasks.write_text(tasks.read_text(encoding="utf-8").replace("skills/project-bootstrap-fill/SKILL.md", "skills/project-init/SKILL.md", 1), encoding="utf-8")
        self.assert_fails("five distinct Skills")

    def test_lf_contract_mutation_fails(self):
        path = self.root / ".gitattributes"
        path.write_text(path.read_text(encoding="utf-8").replace("*.md text eol=lf", "*.md text"), encoding="utf-8")
        self.assert_fails("checkout-contract")

    def test_raw_byte_projection_and_lf_contract_reject_crlf_mutations(self):
        relative = Path("project-init/SKILL.md")
        root = self.root / "skills" / relative
        target = self.root / "project-template/.agents/skills" / relative
        root.write_bytes(root.read_bytes().replace(b"\n", b"\r\n"))
        self.assert_fails("root and .agents bytes differ")

        self.setUp_from_repo()
        root = self.root / "skills" / relative
        target = self.root / "project-template/.agents/skills" / relative
        crlf = root.read_bytes().replace(b"\n", b"\r\n")
        root.write_bytes(crlf)
        target.write_bytes(crlf)
        self.assert_fails("LF content")

        manifest_path = self.root / "project-template/.forgekit/template-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entry = next(item for item in manifest["files"] if item["source_path"] == ".agents/skills/project-init/SKILL.md")
        entry["checksum"] = validator.canonical_checksum(target)
        manifest_path.write_bytes(
            (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        )
        self.assert_fails("LF content")

        self.setUp_from_repo()
        relative = Path("project-init/agents/openai.yaml")
        for prefix in ("skills", "project-template/.agents/skills"):
            path = self.root / prefix / relative
            path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        self.assert_fails("LF content")


if __name__ == "__main__":
    unittest.main()
