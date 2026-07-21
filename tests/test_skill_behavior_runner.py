import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import types
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


behavior = load_module("skill_behavior", REPO / "scripts/test-skill-behavior.py")


class FakeAdapter:
    def __init__(self, *, available=True, error=None, write_path=None, stdout="ok", action=None, result=None):
        self.available = available
        self.error = error
        self.write_path = write_path
        self.stdout = stdout
        self.action = action
        self.result = result
        self.observed_workspace = None
        self.observed_context = None
        self.observed_prompt = None

    def probe(self):
        return {"available": self.available, "reason": "not installed", "executable": "fake", "version": "1"}

    def invoke(self, workspace, prompt, invocation_mode, context):
        self.observed_workspace = workspace.resolve()
        self.observed_context = context
        self.observed_prompt = prompt
        if self.error:
            raise RuntimeError(self.error)
        if self.write_path:
            path = workspace / self.write_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("changed\n", encoding="utf-8")
        if self.action:
            self.action(workspace)
        response = {
            "available": True,
            "executable": "fake",
            "version": "1",
            "model": "fake-model",
            "safe_command": ["fake", "<fixture>", "<prompt>"],
            "stdout": self.stdout,
            "stderr": "",
            "exit_code": 0,
            "tool_trace": [],
            "skill_source": None,
            "capabilities": {
                "model": True,
                "tool_trace": True,
                "skill_source": False,
                "structured_output": True,
                "isolation": True,
            },
            "evidence_unavailable_reason": {"skill_source": "fake did not provide routing"},
            "diagnostics": "fake adapter",
        }
        response.update(self.result or {})
        return response


class SkillBehaviorRunnerTests(unittest.TestCase):
    def setUp(self):
        self.cases = behavior.load_cases(REPO, "tests/skill-behavior/cases.json")
        self.temp = tempfile.TemporaryDirectory(prefix="forgekit-behavior-tests-", dir=Path("D:/tmp"))
        self.temp_root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def case(self, case_id):
        return next(case.copy() for case in self.cases if case["id"] == case_id)

    def run_case(self, case, adapter):
        return behavior.execute_case(REPO, case, adapter_module=adapter, temp_parent=self.temp_root)

    def load_mutated_case(self, case, name="mutated"):
        root = self.temp_root / name
        shutil.copytree(REPO / "tests/skill-behavior/fixtures/minimal-project", root / "fixture")
        shutil.copytree(REPO / "config", root / "config")
        shutil.copytree(REPO / "skills", root / "skills")
        case = json.loads(json.dumps(case))
        case["fixture"] = "fixture"
        (root / "cases.json").write_text(
            json.dumps({"schema_version": 1, "cases": [case]}), encoding="utf-8"
        )
        return behavior.load_cases(root, "cases.json")

    def test_real_manifest_schema(self):
        self.assertEqual(13, len(self.cases))

    def test_duplicate_id_invalid_authorization_and_path_fail(self):
        manifest = json.loads((REPO / "tests/skill-behavior/cases.json").read_text(encoding="utf-8"))
        manifest_root = self.temp_root / "manifest-root"
        fixture = manifest_root / "fixture"
        shutil.copytree(REPO / "tests/skill-behavior/fixtures/minimal-project", fixture)
        shutil.copytree(REPO / "config", manifest_root / "config")
        shutil.copytree(REPO / "skills", manifest_root / "skills")
        for case in manifest["cases"]:
            case["fixture"] = "fixture"
        mutations = []
        duplicate = json.loads(json.dumps(manifest))
        duplicate["cases"].append(duplicate["cases"][0])
        mutations.append(duplicate)
        invalid_auth = json.loads(json.dumps(manifest))
        invalid_auth["cases"][0]["authorization"] = "write_anywhere"
        mutations.append(invalid_auth)
        invalid_path = json.loads(json.dumps(manifest))
        invalid_path["cases"][1]["allowed_write_paths"] = ["../escape"]
        mutations.append(invalid_path)
        for index, data in enumerate(mutations):
            path = manifest_root / f"cases-{index}.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.subTest(index=index), self.assertRaises(behavior.BehaviorError):
                behavior.load_cases(manifest_root, path.name)

    def test_fixture_reparse_and_in_repository_temp_root_are_rejected(self):
        with self.assertRaisesRegex(behavior.BehaviorError, "outside the real repository"):
            behavior.execute_case(
                REPO,
                self.case("stage-a-read-only-audit"),
                dry_run=True,
                temp_parent=REPO / "tests",
            )

        manifest_root = self.temp_root / "reparse-root"
        fixture = manifest_root / "fixture"
        fixture.mkdir(parents=True)
        shutil.copytree(REPO / "config", manifest_root / "config")
        shutil.copytree(REPO / "skills", manifest_root / "skills")
        outside = self.temp_root / "outside"
        outside.mkdir()
        link = fixture / "linked"
        try:
            if os.name == "nt":
                result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)], capture_output=True)
                if result.returncode != 0:
                    self.skipTest("directory junction is unavailable")
            else:
                link.symlink_to(outside, target_is_directory=True)
            manifest = json.loads((REPO / "tests/skill-behavior/cases.json").read_text(encoding="utf-8"))
            manifest["cases"] = [manifest["cases"][0]]
            manifest["cases"][0]["fixture"] = "fixture"
            (manifest_root / "cases.json").write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(behavior.BehaviorError):
                behavior.load_cases(manifest_root, "cases.json")
        finally:
            if link.exists():
                if link.is_symlink():
                    link.unlink()
                else:
                    link.rmdir()

    def test_read_only_change_is_unauthorized(self):
        record = self.run_case(self.case("stage-a-read-only-audit"), FakeAdapter(write_path="unexpected.txt"))
        self.assertEqual("UNAUTHORIZED_WRITE", record["failure_class"])

    def test_directory_only_changes_and_type_changes_are_observed(self):
        case = self.case("stage-a-read-only-audit")

        def add_empty(workspace):
            (workspace / "empty-added").mkdir()

        empty = self.run_case(case, FakeAdapter(action=add_empty))
        self.assertEqual("UNAUTHORIZED_WRITE", empty["failure_class"])
        self.assertIn("empty-added", empty["changed_paths"])

        def delete_directory(workspace):
            for child in (workspace / "src").iterdir():
                child.unlink()
            (workspace / "src").rmdir()

        deleted = self.run_case(case, FakeAdapter(action=delete_directory))
        self.assertEqual("UNAUTHORIZED_WRITE", deleted["failure_class"])
        self.assertIn("src", deleted["changed_paths"])

        def file_to_directory(workspace):
            path = workspace / "src/note.txt"
            path.unlink()
            path.mkdir()

        changed_type = self.run_case(case, FakeAdapter(action=file_to_directory))
        self.assertEqual("UNAUTHORIZED_WRITE", changed_type["failure_class"])
        self.assertIn("src/note.txt", changed_type["changed_paths"])
        self.assertEqual("directory", changed_type["after_tree"]["src/note.txt"]["type"])

        def rename_directory(workspace):
            (workspace / "src").rename(workspace / "renamed-src")

        renamed = self.run_case(case, FakeAdapter(action=rename_directory))
        self.assertEqual("UNAUTHORIZED_WRITE", renamed["failure_class"])
        self.assertIn("src", renamed["changed_paths"])
        self.assertIn("renamed-src", renamed["changed_paths"])

    def test_bounded_write_outside_allowlist_is_unauthorized(self):
        record = self.run_case(self.case("stage-a-bounded-local-write"), FakeAdapter(write_path="outside.txt"))
        self.assertEqual("UNAUTHORIZED_WRITE", record["failure_class"])

        def add_outside_directory(workspace):
            (workspace / "outside-empty").mkdir()

        directory_record = self.run_case(
            self.case("stage-a-bounded-local-write"), FakeAdapter(action=add_outside_directory)
        )
        self.assertEqual("UNAUTHORIZED_WRITE", directory_record["failure_class"])
        self.assertIn("outside-empty", directory_record["changed_paths"])

    def test_bounded_write_inside_allowlist_is_not_unauthorized(self):
        record = self.run_case(
            self.case("stage-a-bounded-local-write"),
            FakeAdapter(write_path="src/note.txt"),
        )
        self.assertEqual("GRADER_UNCERTAIN", record["failure_class"])

    def test_environment_and_adapter_failures_are_distinct(self):
        case = self.case("stage-a-read-only-audit")
        unavailable = self.run_case(case, FakeAdapter(available=False))
        adapter_error = self.run_case(case, FakeAdapter(error="protocol broke"))
        self.assertEqual("ENVIRONMENT_UNAVAILABLE", unavailable["failure_class"])
        self.assertEqual("ADAPTER_ERROR", adapter_error["failure_class"])

    def test_normal_and_exceptional_runs_cleanup(self):
        adapter = FakeAdapter()
        self.run_case(self.case("stage-a-read-only-audit"), adapter)
        self.assertIsNotNone(adapter.observed_workspace)
        self.assertNotEqual(REPO, adapter.observed_workspace)
        self.assertNotIn(REPO, adapter.observed_workspace.parents)
        self.run_case(self.case("stage-a-read-only-audit"), FakeAdapter(error="boom"))
        self.assertEqual([], list(self.temp_root.iterdir()))

    def test_cleanup_failure_is_recorded_as_non_pass(self):
        def fail_cleanup(_path):
            raise PermissionError("simulated cleanup denial")

        record = behavior.execute_case(
            REPO,
            self.case("stage-a-read-only-audit"),
            adapter_module=FakeAdapter(),
            temp_parent=self.temp_root,
            cleanup_func=fail_cleanup,
        )
        self.assertEqual("ADAPTER_ERROR", record["failure_class"])
        self.assertEqual("failed", record["cleanup"]["status"])
        self.assertIn("simulated cleanup denial", record["cleanup"]["reason"])
        for child in list(self.temp_root.iterdir()):
            shutil.rmtree(child)

    def test_run_record_redacts_fixed_secret_forms_and_home(self):
        values = ["maker-token-731", "maker-api-924", "maker-password-583", "maker-bearer-417"]
        output = (
            f"--token {values[0]} --api-key={values[1]} PASSWORD: {values[2]} "
            f"Bearer {values[3]} home={Path.home()}"
        )
        result = {
            "safe_command": ["fake", "--token", values[0], "--api_key", values[1], "--password=" + values[2]],
            "stderr": "API KEY: " + values[1],
            "tool_trace": [{"authorization": "Bearer " + values[3]}],
            "diagnostics": "ACCESS_KEY=" + values[0] + " " + str(Path.home()),
        }
        record = self.run_case(
            self.case("stage-a-read-only-audit"),
            FakeAdapter(stdout=output, result=result),
        )
        rendered = json.dumps(record, ensure_ascii=False)
        for value in values:
            self.assertNotIn(value, rendered)
        self.assertNotIn(str(Path.home()), rendered)
        self.assertIn("<REDACTED>", rendered)

    def test_final_recursive_sanitization_redacts_nested_auth_values_and_evidence(self):
        secrets = [f"independent-secret-{index}-947" for index in range(1, 13)]
        protected = self.temp_root / "protected-outside-fixture"
        raw = {
            "adapter_diagnostics": {
                "environment": {
                    "OPENAI_API_KEY": secrets[0],
                    "awsSecretAccessKey": {"nested": [secrets[1], {"deeper": secrets[2]}]},
                    "ordinary": "preserved-value",
                },
                "third_level": {"items": [{"clientSecret": secrets[3]}]},
            },
            "tool_trace": [{"environment": {"ANTHROPIC_API_KEY": secrets[4]}}],
            "command": ("fake", "--token", secrets[5], "--api-key=" + secrets[6]),
            "stdout": "Bearer " + secrets[7],
            "stderr": "API KEY: " + secrets[8],
            "grader": {"reason": "PASSWORD=" + secrets[9]},
            "exception_diagnostics": {"credentials": [secrets[10], {"raw": secrets[11]}]},
            "paths": [str(Path.home()), str(protected)],
            "normal": {"tuple": ("alpha", 7, True)},
        }
        serialized = behavior.serialize_sanitized(
            raw,
            [(str(Path.home()), "<HOME>"), (str(protected), "<PROTECTED>")],
        )
        for secret in secrets:
            self.assertNotIn(secret, serialized)
        self.assertIn("<REDACTED>", serialized)
        self.assertIn("<HOME>", serialized)
        self.assertIn("<PROTECTED>", serialized)
        self.assertIn("preserved-value", serialized)
        self.assertIn("alpha", serialized)

        evidence_secret = "adapter-environment-secret-63819"
        evidence_dir = self.temp_root / "evidence"
        adapter = FakeAdapter(result={
            "diagnostics": {"environment": {"OPENAI_API_KEY": evidence_secret}, "ordinary": "visible"},
            "tool_trace": [{"environment": {"refreshToken": "refresh-value-862"}}],
        })
        record = behavior.execute_case(
            REPO,
            self.case("stage-a-read-only-audit"),
            adapter_module=adapter,
            temp_parent=self.temp_root,
            evidence_dir=evidence_dir,
        )
        files = list(evidence_dir.rglob("*"))
        evidence_files = [path for path in files if path.is_file()]
        self.assertEqual(1, len(evidence_files))
        persisted = evidence_files[0].read_text(encoding="utf-8")
        self.assertNotIn(evidence_secret, persisted)
        self.assertNotIn("refresh-value-862", persisted)
        self.assertNotIn(evidence_secret, json.dumps(record, ensure_ascii=False))
        self.assertEqual("<REDACTED>", record["adapter_diagnostics"]["environment"]["OPENAI_API_KEY"])
        self.assertEqual("visible", record["adapter_diagnostics"]["ordinary"])

    def test_routing_evidence_capability_is_honest(self):
        case = self.case("stage-a-read-only-audit")
        case["expected_skill"] = "code-review"
        complete = FakeAdapter(result={
            "skill_source": [{"name": "code-review", "path": "skills/code-review/SKILL.md"}],
            "capabilities": {
                "model": True, "tool_trace": True, "skill_source": True,
                "structured_output": True, "isolation": True,
            },
        })
        record = self.run_case(case, complete)
        self.assertEqual("GRADER_UNCERTAIN", record["failure_class"])
        self.assertNotIn("Skill source", record["grader"]["reason"])
        missing = self.run_case(case, FakeAdapter())
        self.assertEqual("GRADER_UNCERTAIN", missing["failure_class"])
        self.assertIn("Skill source evidence", missing["grader"]["reason"])

    def test_dry_run_needs_no_real_client(self):
        record = behavior.execute_case(
            REPO,
            self.case("stage-a-read-only-audit"),
            dry_run=True,
            temp_parent=self.temp_root,
        )
        self.assertEqual("GRADER_UNCERTAIN", record["failure_class"])
        self.assertEqual([], list(self.temp_root.iterdir()))

    def test_stage_c_fixture_materializes_authoritative_skill_packages(self):
        case = self.case("stage-c-bootstrap-placeholder")
        captured = {}

        def inspect_materialized(workspace):
            for relative in ("SKILL.md", "agents/openai.yaml"):
                target = workspace / ".agents/skills/project-bootstrap-fill" / relative
                source = REPO / "skills/project-bootstrap-fill" / relative
                captured[relative] = target.read_bytes()
                self.assertEqual(source.read_bytes(), captured[relative])

        adapter = FakeAdapter(action=inspect_materialized)
        record = self.run_case(case, adapter)
        self.assertEqual({"SKILL.md", "agents/openai.yaml"}, set(captured))
        self.assertTrue(record["client_skill_capability"])
        self.assertEqual(".agents/skills", record["materialization"]["location"])
        self.assertEqual("skills/project-bootstrap-fill/SKILL.md", record["expected_skill_source"])
        self.assertEqual([], list(self.temp_root.iterdir()))

    def test_explicit_and_implicit_prompts_render_real_invocation_syntax(self):
        explicit_adapter = FakeAdapter()
        explicit = self.run_case(self.case("stage-c-bootstrap-placeholder"), explicit_adapter)
        self.assertTrue(explicit_adapter.observed_context)
        self.assertEqual("project-bootstrap-fill", explicit["explicit_skill_id"])
        self.assertTrue(explicit["rendered_prompt"].startswith("$project-bootstrap-fill\n\n"))
        self.assertEqual(1, explicit["invocation_marker_count"])
        self.assertTrue(explicit["invocation_inserted"])
        self.assertEqual(explicit["rendered_prompt"], explicit_adapter.observed_prompt)

        implicit_adapter = FakeAdapter()
        implicit = self.run_case(self.case("stage-c-handover-read-only"), implicit_adapter)
        self.assertIsNone(implicit["explicit_skill_id"])
        self.assertNotIn("$handover-review", implicit["rendered_prompt"])
        self.assertEqual(implicit["original_prompt"], implicit["rendered_prompt"])
        self.assertEqual(0, implicit["invocation_marker_count"])
        self.assertFalse(implicit["invocation_inserted"])

    def test_bounded_write_and_read_only_cases_require_write_evidence(self):
        bounded = self.case("stage-a-bounded-local-write")
        bounded["evidence_requirements"]["write_behavior"] = False
        with self.assertRaisesRegex(behavior.BehaviorError, "bounded local write requires write behavior evidence"):
            self.load_mutated_case(bounded, "bounded-no-evidence")

        bounded = self.case("stage-a-bounded-local-write")
        bounded["allowed_write_paths"] = []
        with self.assertRaisesRegex(behavior.BehaviorError, "non-empty allowed_write_paths"):
            self.load_mutated_case(bounded, "bounded-no-path")

        read_only = self.case("stage-c-handover-read-only")
        read_only["evidence_requirements"]["write_behavior"] = False
        with self.assertRaisesRegex(behavior.BehaviorError, "read_only requires write behavior evidence"):
            self.load_mutated_case(read_only, "readonly-no-oracle")

    def test_explicit_prompt_rendering_is_idempotent_and_rejects_bad_markers(self):
        case = self.case("stage-c-bootstrap-placeholder")
        case["prompt"] = "$project-bootstrap-fill\n\n" + case["prompt"]
        loaded = self.load_mutated_case(case, "existing-marker")[0]
        rendered, skill, count, inserted = behavior.render_prompt(loaded)
        self.assertEqual(case["prompt"], rendered)
        self.assertEqual("project-bootstrap-fill", skill)
        self.assertEqual(1, count)
        self.assertFalse(inserted)

        duplicate = self.case("stage-c-bootstrap-placeholder")
        duplicate["prompt"] = "$project-bootstrap-fill\n$project-bootstrap-fill\n\n" + duplicate["prompt"]
        with self.assertRaisesRegex(behavior.BehaviorError, "duplicate formal invocation"):
            self.load_mutated_case(duplicate, "duplicate-marker")

        wrong = self.case("stage-c-bootstrap-placeholder")
        wrong["prompt"] = "$document-backfill\n\n" + wrong["prompt"]
        with self.assertRaisesRegex(behavior.BehaviorError, "wrong Skill marker"):
            self.load_mutated_case(wrong, "wrong-marker")

        inline = self.case("stage-c-bootstrap-placeholder")
        inline["prompt"] = "Use $project-bootstrap-fill as an example.\n" + inline["prompt"]
        loaded = self.load_mutated_case(inline, "inline-marker")[0]
        rendered, _, count, inserted = behavior.render_prompt(loaded)
        self.assertTrue(rendered.startswith("$project-bootstrap-fill\n\n"))
        self.assertEqual(1, count)
        self.assertTrue(inserted)

        implicit = self.case("stage-c-handover-read-only")
        rendered, skill, count, inserted = behavior.render_prompt(implicit)
        self.assertNotIn("$handover-review", rendered)
        self.assertIsNone(skill)
        self.assertEqual(0, count)
        self.assertFalse(inserted)

    def test_case_evidence_requirements_and_dry_run_plan_are_explicit(self):
        for case in self.cases:
            self.assertEqual(behavior.EVIDENCE_REQUIREMENT_KEYS, set(case["evidence_requirements"]))
            self.assertTrue(any(case["evidence_requirements"].values()))
        record = behavior.execute_case(
            REPO, self.case("stage-c-document-backfill-fact"), dry_run=True,
            temp_parent=self.temp_root,
        )
        self.assertEqual("not-obtained", record["evidence_status"]["routing"])
        self.assertEqual("not-obtained", record["evidence_status"]["skill_source"])
        self.assertEqual("not-run", record["grader"]["result"])
        paths = {
            item["source_path"]
            for skill in record["materialization"]["skills"] for item in skill["files"]
        }
        self.assertIn("skills/document-backfill/SKILL.md", paths)

    def test_missing_or_invalid_evidence_and_implicit_explicit_only_positive_fail(self):
        manifest_root = self.temp_root / "evidence-schema"
        shutil.copytree(REPO / "tests/skill-behavior/fixtures/minimal-project", manifest_root / "fixture")
        shutil.copytree(REPO / "config", manifest_root / "config")
        shutil.copytree(REPO / "skills", manifest_root / "skills")
        manifest = json.loads((REPO / "tests/skill-behavior/cases.json").read_text(encoding="utf-8"))
        manifest["cases"] = [manifest["cases"][4]]
        manifest["cases"][0]["fixture"] = "fixture"

        missing = json.loads(json.dumps(manifest))
        del missing["cases"][0]["evidence_requirements"]
        (manifest_root / "missing.json").write_text(json.dumps(missing), encoding="utf-8")
        with self.assertRaises(behavior.BehaviorError):
            behavior.load_cases(manifest_root, "missing.json")

        wrong_type = json.loads(json.dumps(manifest))
        wrong_type["cases"][0]["evidence_requirements"]["routing"] = "true"
        (manifest_root / "wrong-type.json").write_text(json.dumps(wrong_type), encoding="utf-8")
        with self.assertRaises(behavior.BehaviorError):
            behavior.load_cases(manifest_root, "wrong-type.json")

        implicit = json.loads(json.dumps(manifest))
        implicit["cases"][0]["invocation_mode"] = "implicit"
        (manifest_root / "implicit.json").write_text(json.dumps(implicit), encoding="utf-8")
        with self.assertRaisesRegex(behavior.BehaviorError, "explicit-only"):
            behavior.load_cases(manifest_root, "implicit.json")

    def test_adapter_modules_expose_only_runner_interface(self):
        for client in ("codex", "claude"):
            adapter = load_module(client + "_adapter", REPO / f"scripts/skill_behavior_adapters/{client}.py")
            self.assertTrue(callable(adapter.probe))
            self.assertTrue(callable(adapter.invoke))


if __name__ == "__main__":
    unittest.main()
