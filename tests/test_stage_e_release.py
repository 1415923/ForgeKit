import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("stage_e_release", REPO / "scripts/validate-stage-e-release.py")
STAGE_E = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(STAGE_E)


class StageEReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fke-test-", dir=r"D:\tmp")
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        files = [
            "VERSION", "config/skill-projections.json", ".codex-plugin/plugin.json",
            ".claude-plugin/plugin.json", ".agents/plugins/marketplace.json",
            ".claude-plugin/marketplace.json", "project-template/.forgekit/state.json",
            "project-template/.forgekit/template-manifest.json", "README.md", "README.en.md",
            "CHANGELOG.md", "project-template/.forgekit/docs/usage-playbook.md",
            "scripts/validate-release-gate-wiring.py", "scripts/validate-plugin-assets.ps1",
            "scripts/validate-template.ps1", "scripts/test-release-consistency.ps1",
            "scripts/smoke-test.py", "scripts/test-fresh-clone-crlf.py",
            "migrations/0.45.0/migration.json",
        ]
        for relative in files:
            target = self.repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / relative, target)
        for relative in (STAGE_E.FORMAL, STAGE_E.TEMPLATE_FORMAL, Path("prompts")):
            target = self.repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(REPO / relative, target)
        descriptor = json.loads((self.repo / STAGE_E.FORMAL / "migration.json").read_text(encoding="utf-8"))
        manifest = json.loads((self.repo / "project-template/.forgekit/template-manifest.json").read_text(encoding="utf-8"))
        target_sources = {}
        for item in manifest["files"]:
            target_name = item["target_path"].replace("${managed_docs_root}", ".forgekit/docs")
            target_name = target_name.replace("${change_root}", ".forgekit/changes")
            target_sources[target_name] = item["source_path"]
        for action in descriptor["actions"]:
            if action["type"] != "replace_file_if_baseline_matches":
                continue
            source_name = target_sources.get(action["target"], action["target"])
            source = REPO / "project-template" / source_name
            target = self.repo / "project-template" / source_name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    def tearDown(self):
        self.temp.cleanup()

    def errors(self):
        return STAGE_E.validate_repo(self.repo)[0]

    def rewrite_descriptor(self, mutate):
        for relative in (STAGE_E.FORMAL, STAGE_E.TEMPLATE_FORMAL):
            path = self.repo / relative / "migration.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            mutate(data)
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def rewrite_manifest(self, mutate):
        path = self.repo / "project-template/.forgekit/template-manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        mutate(data)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def migration_manifest_entry(self, suffix):
        data = json.loads(
            (self.repo / "project-template/.forgekit/template-manifest.json").read_text(encoding="utf-8")
        )
        return next(
            item for item in data["files"]
            if item["source_path"].startswith("migrations/0.46.0/")
            and item["source_path"].endswith(suffix)
        )

    def test_baseline_passes(self):
        self.assertEqual([], self.errors())

    def test_version_surface_mismatch_fails(self):
        (self.repo / "VERSION").write_text("0.44.1\n", encoding="utf-8")
        self.assertTrue(any("version [VERSION]" in item for item in self.errors()))

    def test_missing_action_fails(self):
        self.rewrite_descriptor(lambda data: data["actions"].pop())
        self.assertTrue(any("migration [action-set]" in item for item in self.errors()))

    def test_duplicate_action_fails(self):
        self.rewrite_descriptor(lambda data: data["actions"].append(dict(data["actions"][0])))
        errors = self.errors()
        self.assertTrue(any("duplicate-action-id" in item for item in errors))
        self.assertTrue(any("duplicate-target" in item for item in errors))

    def test_incoming_template_drift_fails(self):
        descriptor = json.loads((self.repo / STAGE_E.FORMAL / "migration.json").read_text(encoding="utf-8"))
        action = next(item for item in descriptor["actions"] if item["type"] == "replace_file_if_baseline_matches")
        for relative in (STAGE_E.FORMAL, STAGE_E.TEMPLATE_FORMAL):
            path = self.repo / relative / action["source"]
            path.write_bytes(path.read_bytes() + b"drift\n")
        self.assertTrue(any("incoming-template" in item for item in self.errors()))

    def test_missing_baseline_fails(self):
        descriptor = json.loads((self.repo / STAGE_E.FORMAL / "migration.json").read_text(encoding="utf-8"))
        action = descriptor["actions"][0]
        for relative in (STAGE_E.FORMAL, STAGE_E.TEMPLATE_FORMAL):
            (self.repo / relative / action["baseline"]).unlink()
        self.assertTrue(any("baseline-missing" in item for item in self.errors()))

    def test_root_template_drift_fails(self):
        descriptor = json.loads((self.repo / STAGE_E.FORMAL / "migration.json").read_text(encoding="utf-8"))
        source = next(item["source"] for item in descriptor["actions"] if item["type"] == "replace_file_if_baseline_matches")
        path = self.repo / STAGE_E.TEMPLATE_FORMAL / source
        path.write_bytes(path.read_bytes() + b"drift\n")
        self.assertTrue(any("root-template-bytes" in item for item in self.errors()))

    def test_duplicate_production_version_fails(self):
        duplicate = self.repo / "migrations/0.46.0-copy"
        shutil.copytree(self.repo / STAGE_E.FORMAL, duplicate)
        errors = self.errors()
        self.assertTrue(any("production-discovery" in item for item in errors))
        self.assertTrue(any("duplicate-version" in item for item in errors))

    def test_release_payload_is_finite(self):
        errors, evidence = STAGE_E.validate_repo(self.repo)
        self.assertEqual([], errors)
        self.assertEqual(38, evidence["actions"])

    def test_release_doc_marker_is_required(self):
        path = self.repo / "README.en.md"
        path.write_text(path.read_text(encoding="utf-8").replace("NEEDS_TEST", "pending evidence"), encoding="utf-8")
        self.assertTrue(any("docs [release-entry]" in item for item in self.errors()))

    def test_prompt_deprecation_marker_is_required(self):
        path = self.repo / "prompts/代码审查.prompt.md"
        path.write_text(path.read_text(encoding="utf-8").replace("Deprecated compatibility prompt for v0.46", "compatibility"), encoding="utf-8")
        self.assertTrue(any("prompt [deprecation-window]" in item for item in self.errors()))

    def test_formal_template_migration_manifest_is_complete(self):
        expected = STAGE_E.expected_template_migration_manifest_paths(self.repo)
        manifest = json.loads(
            (self.repo / "project-template/.forgekit/template-manifest.json").read_text(encoding="utf-8")
        )
        actual = {
            item["source_path"] for item in manifest["files"]
            if item["source_path"].startswith("migrations/0.46.0/")
        }
        self.assertEqual(expected, actual)
        self.assertEqual(len(expected), len(actual))

    def test_missing_formal_descriptor_manifest_entry_fails(self):
        target = "migrations/0.46.0/migration.json"
        self.rewrite_manifest(lambda data: data.update(files=[item for item in data["files"] if item["source_path"] != target]))
        self.assertTrue(any("template-migration-manifest-missing" in item and target in item for item in self.errors()))

    def test_missing_formal_baseline_manifest_entry_fails(self):
        target = next(
            item["source_path"] for item in json.loads(
                (self.repo / "project-template/.forgekit/template-manifest.json").read_text(encoding="utf-8")
            )["files"] if item["source_path"].startswith("migrations/0.46.0/baseline/")
        )
        self.rewrite_manifest(lambda data: data.update(files=[item for item in data["files"] if item["source_path"] != target]))
        self.assertTrue(any("template-migration-manifest-missing" in item and target in item for item in self.errors()))

    def test_missing_formal_incoming_manifest_entry_fails(self):
        target = next(
            item["source_path"] for item in json.loads(
                (self.repo / "project-template/.forgekit/template-manifest.json").read_text(encoding="utf-8")
            )["files"] if item["source_path"].startswith("migrations/0.46.0/files/")
        )
        self.rewrite_manifest(lambda data: data.update(files=[item for item in data["files"] if item["source_path"] != target]))
        self.assertTrue(any("template-migration-manifest-missing" in item and target in item for item in self.errors()))

    def test_duplicate_formal_manifest_entry_fails(self):
        entry = self.migration_manifest_entry("migration.json")
        self.rewrite_manifest(lambda data: data["files"].append(dict(entry)))
        self.assertTrue(any("template-migration-manifest-missing" in item and "actual=2" in item for item in self.errors()))

    def test_formal_manifest_checksum_fails(self):
        target = self.migration_manifest_entry("migration.json")["source_path"]
        def mutate(data):
            next(item for item in data["files"] if item["source_path"] == target)["checksum"] = "sha256:" + "0" * 64
        self.rewrite_manifest(mutate)
        self.assertTrue(any("template-migration-manifest-checksum" in item and target in item for item in self.errors()))

    def test_change_local_draft_manifest_entry_fails(self):
        entry = dict(self.migration_manifest_entry("migration.json"))
        entry["source_path"] = ".forgekit/changes/v046-semantic-freeze/stage-b-migration-draft/0.46.0/migration.json"
        entry["target_path"] = entry["source_path"]
        self.rewrite_manifest(lambda data: data["files"].append(entry))
        self.assertTrue(any("template-migration-manifest-extra" in item and "stage-b-migration-draft" in item for item in self.errors()))

    def test_root_migration_manifest_entry_fails(self):
        entry = dict(self.migration_manifest_entry("migration.json"))
        entry["source_path"] = "root/migrations/0.46.0/migration.json"
        entry["target_path"] = entry["source_path"]
        self.rewrite_manifest(lambda data: data["files"].append(entry))
        self.assertTrue(any("template-migration-manifest-extra" in item and "root/migrations" in item for item in self.errors()))


if __name__ == "__main__":
    unittest.main()
