import hashlib
import importlib.util
import json
import shutil
import unittest
import uuid
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
DRAFT = REPO / ".forgekit/changes/v045-rule-ownership-skill-convergence/stage-b-migration-draft/0.45.0"


def load_validator():
    path = REPO / "scripts" / "validate-stage-b-entry-migration.py"
    spec = importlib.util.spec_from_file_location("stage_b_migration_validator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_validator()


class ExplicitTempMixin:
    def make_root(self, prefix):
        root = REPO / f".{prefix}-{uuid.uuid4().hex[:8]}"
        root.mkdir()
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root


class StageBMigrationIdentityTests(ExplicitTempMixin, unittest.TestCase):
    def setUp(self):
        self.root = self.make_root("stage-b-static")
        self.package = self.root / "0.45.0"
        shutil.copytree(DRAFT, self.package)

    def descriptor(self):
        return json.loads((self.package / "migration.json").read_text(encoding="utf-8"))

    def write_descriptor(self, descriptor):
        (self.package / "migration.json").write_text(
            json.dumps(descriptor, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def test_repository_draft_passes_independent_identity_gate(self):
        self.assertEqual([], validator.validate_draft(REPO))

    def test_baseline_byte_mutation_without_descriptor_change_fails(self):
        path = self.package / "baseline/AGENTS.md"
        path.write_bytes(path.read_bytes() + b"\nmutated baseline\n")
        errors = validator.validate_draft(REPO, self.package)
        self.assertTrue(any("AGENTS.md: approved baseline mismatch" in item for item in errors), errors)

    def test_baseline_and_checksum_synchronized_mutation_still_fails_git_anchor(self):
        path = self.package / "baseline/AGENTS.md"
        mutated = path.read_bytes() + b"\ncoherent but unapproved baseline\n"
        path.write_bytes(mutated)
        descriptor = self.descriptor()
        action = next(item for item in descriptor["actions"] if item["target"] == "AGENTS.md")
        action["baseline_sha256"] = hashlib.sha256(mutated).hexdigest()
        self.write_descriptor(descriptor)
        errors = validator.validate_draft(REPO, self.package)
        joined = "\n".join(errors)
        self.assertIn("AGENTS.md: approved baseline mismatch", joined)
        self.assertIn(validator.APPROVED_STAGE_A_COMMIT, joined)
        self.assertIn("expected Git SHA-256=", joined)
        self.assertIn("draft baseline SHA-256=", joined)
        self.assertIn("descriptor SHA-256=", joined)

    def test_descriptor_source_commit_mutation_fails(self):
        descriptor = self.descriptor()
        descriptor["source_commit"] = "077fcfa000000000000000000000000000000000"
        self.write_descriptor(descriptor)
        errors = validator.validate_draft(REPO, self.package)
        self.assertTrue(any("source_commit must equal approved Stage A commit" in item for item in errors), errors)

    def test_incoming_and_checksum_synchronized_mutation_still_fails_current_template_anchor(self):
        path = self.package / "files/CLAUDE.md"
        mutated = path.read_bytes() + b"\ncoherent but stale incoming\n"
        path.write_bytes(mutated)
        descriptor = self.descriptor()
        action = next(item for item in descriptor["actions"] if item["target"] == "CLAUDE.md")
        action["incoming_sha256"] = hashlib.sha256(mutated).hexdigest()
        self.write_descriptor(descriptor)
        errors = validator.validate_draft(REPO, self.package)
        self.assertTrue(any("CLAUDE.md: current incoming mismatch" in item for item in errors), errors)

    def test_stage_c_skill_baseline_is_anchored_to_approved_stage_b_commit(self):
        target = validator.stage_c_skill_targets(REPO)[0]
        path = self.package / "baseline" / target
        mutated = path.read_bytes() + b"\ncoherent but unapproved skill baseline\n"
        path.write_bytes(mutated)
        descriptor = self.descriptor()
        action = next(item for item in descriptor["actions"] if item["target"] == target)
        action["baseline_sha256"] = hashlib.sha256(mutated).hexdigest()
        self.write_descriptor(descriptor)
        errors = validator.validate_draft(REPO, self.package)
        joined = "\n".join(errors)
        self.assertIn(f"{target}: approved baseline mismatch", joined)
        self.assertIn(validator.APPROVED_STAGE_B_COMMIT, joined)

    def test_stage_c_skill_baseline_commit_field_is_frozen(self):
        target = validator.stage_c_skill_targets(REPO)[0]
        descriptor = self.descriptor()
        action = next(item for item in descriptor["actions"] if item["target"] == target)
        action["baseline_commit"] = validator.APPROVED_STAGE_A_COMMIT
        self.write_descriptor(descriptor)
        errors = validator.validate_draft(REPO, self.package)
        self.assertTrue(any(f"{target}: baseline_commit must equal approved Stage B commit" in item for item in errors), errors)

    def test_stage_c_skill_incoming_is_anchored_to_current_projection(self):
        target = validator.stage_c_skill_targets(REPO)[-1]
        path = self.package / "files" / target
        mutated = path.read_bytes() + b"\ncoherent but stale skill incoming\n"
        path.write_bytes(mutated)
        descriptor = self.descriptor()
        action = next(item for item in descriptor["actions"] if item["target"] == target)
        action["incoming_sha256"] = hashlib.sha256(mutated).hexdigest()
        self.write_descriptor(descriptor)
        errors = validator.validate_draft(REPO, self.package)
        self.assertTrue(any(f"{target}: current incoming mismatch" in item for item in errors), errors)

    def test_all_five_stage_c_yaml_packages_are_managed(self):
        yaml_targets = [
            target for target in validator.stage_c_skill_targets(REPO)
            if target.endswith("/agents/openai.yaml")
        ]
        self.assertEqual(5, len(yaml_targets))
        descriptor_targets = {item["target"] for item in self.descriptor()["actions"]}
        self.assertTrue(set(yaml_targets) <= descriptor_targets)

    def test_all_four_stage_d_packages_use_stage_c_baseline(self):
        targets = validator.stage_d_skill_targets(REPO)
        self.assertEqual(8, len(targets))
        self.assertEqual(4, len([target for target in targets if target.endswith("/agents/openai.yaml")]))
        descriptor = self.descriptor()
        actions = {item["target"]: item for item in descriptor["actions"]}
        for target in targets:
            self.assertIn(target, actions)
            self.assertEqual(validator.APPROVED_STAGE_C_COMMIT, actions[target]["baseline_commit"])

    def test_stage_d_baseline_commit_field_is_frozen(self):
        target = validator.stage_d_skill_targets(REPO)[0]
        descriptor = self.descriptor()
        action = next(item for item in descriptor["actions"] if item["target"] == target)
        action["baseline_commit"] = validator.APPROVED_STAGE_B_COMMIT
        self.write_descriptor(descriptor)
        errors = validator.validate_draft(REPO, self.package)
        self.assertTrue(any(f"{target}: baseline_commit must equal approved Stage C commit" in item for item in errors), errors)

    def test_migration_crlf_with_synchronized_checksum_still_fails_lf_contract(self):
        target = next(
            target for target in validator.stage_c_skill_targets(REPO)
            if target.endswith("/agents/openai.yaml")
        )
        path = self.package / "files" / target
        mutated = path.read_bytes().replace(b"\n", b"\r\n")
        path.write_bytes(mutated)
        descriptor = self.descriptor()
        action = next(item for item in descriptor["actions"] if item["target"] == target)
        action["incoming_sha256"] = hashlib.sha256(mutated).hexdigest()
        self.write_descriptor(descriptor)
        errors = validator.validate_draft(REPO, self.package)
        self.assertTrue(any(f"{target}: incoming fixture violates the LF checkout contract" in item for item in errors), errors)


class StageBProductionDiscoveryTests(ExplicitTempMixin, unittest.TestCase):
    def candidate_repo(self):
        root = self.make_root("stage-b-discovery")
        (root / "scripts").mkdir()
        for name in ("forgekit-upgrade.py", "upgrade_review_packets.py"):
            shutil.copy2(REPO / "scripts" / name, root / "scripts" / name)
        shutil.copytree(REPO / "migrations", root / "migrations")
        draft_target = root / validator.DRAFT_RELATIVE.parent
        draft_target.parent.mkdir(parents=True)
        shutil.copytree(REPO / validator.DRAFT_RELATIVE.parent, draft_target)
        return root

    def test_production_default_discovery_ignores_draft_and_is_read_only(self):
        parent = self.make_root("stage-b-discovery-parent")
        errors, evidence = validator.validate_production_discovery(REPO, parent)
        self.assertEqual([], errors)
        self.assertEqual("0.44.1", evidence["fields"]["Latest available"])
        self.assertEqual("0.44.1", evidence["fields"]["Planned target"])
        self.assertEqual("0", evidence["fields"]["Pending migrations"])
        self.assertEqual(evidence["state_before"], evidence["state_after"])
        self.assertTrue(evidence["project_unchanged"])
        self.assertTrue(evidence["cleaned"])
        self.assertFalse(Path(evidence["temp_root"]).exists())

    def test_production_discovery_redirect_to_draft_fails_actual_check(self):
        candidate = self.candidate_repo()
        script = candidate / "scripts/forgekit-upgrade.py"
        text = script.read_text(encoding="utf-8")
        needle = 'Path(__file__).resolve().parents[1] / "migrations"'
        replacement = (
            'Path(__file__).resolve().parents[1] / '
            '".forgekit/changes/v045-rule-ownership-skill-convergence/stage-b-migration-draft"'
        )
        self.assertIn(needle, text)
        script.write_text(text.replace(needle, replacement, 1), encoding="utf-8")
        errors, evidence = validator.validate_production_discovery(candidate, candidate)
        self.assertTrue(errors)
        self.assertTrue(
            any("Latest available" in item or "Planned target" in item or "0.45.0" in item for item in errors),
            errors,
        )
        self.assertTrue(evidence["cleaned"])

    def test_discovery_exception_cleans_validator_temp_directory(self):
        candidate = self.candidate_repo()
        script = candidate / "scripts/forgekit-upgrade.py"
        script.write_text("this is not valid python !!!\n", encoding="utf-8")
        errors, evidence = validator.validate_production_discovery(candidate, candidate)
        self.assertTrue(errors)
        self.assertTrue(evidence["cleaned"])
        self.assertFalse(Path(evidence["temp_root"]).exists())


class StageBMigrationBehaviorTests(ExplicitTempMixin, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = REPO / f".stage-b-behavior-{uuid.uuid4().hex[:8]}"
        cls.parent.mkdir()
        cls.errors, cls.evidence = validator.validate_migration_behavior(REPO, temp_parent=cls.parent)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.parent, ignore_errors=True)

    def scenario(self, name):
        self.assertEqual([], self.errors)
        return self.evidence["scenarios"][name]

    def by_target(self, scenario):
        return {item["target_path"]: item for item in scenario["report"]["items"]}

    def test_stock_agents_and_claude_update_with_origin_rollback_bytes(self):
        scenario = self.scenario("stock")
        self.assertEqual({"stock"}, {item["classification"] for item in scenario["report"]["items"]})
        self.assertEqual([], scenario["state"]["last_upgrade"]["review_needed_actions"])
        for target in validator.ENTRY_NAMES:
            packet = scenario["packets"][target]
            self.assertEqual((DRAFT / "files" / target).read_bytes(), scenario["after_entries"][target])
            self.assertEqual(scenario["before_entries"][target], packet["artifacts"]["rollback"])

    def test_stock_stage_c_skills_update_with_origin_rollback_bytes(self):
        scenario = self.scenario("stock")
        for target in validator.stage_c_skill_targets(REPO):
            packet = scenario["packets"][target]
            self.assertEqual((DRAFT / "files" / target).read_bytes(), scenario["after_entries"][target])
            self.assertEqual(scenario["before_entries"][target], packet["artifacts"]["rollback"])

    def test_custom_agents_preserved_with_complete_packet_and_summary(self):
        scenario = self.scenario("custom")
        item = self.by_target(scenario)["AGENTS.md"]
        packet = scenario["packets"]["AGENTS.md"]
        self.assertEqual("custom", item["classification"])
        self.assertEqual(scenario["before_entries"]["AGENTS.md"], scenario["after_entries"]["AGENTS.md"])
        self.assertEqual(scenario["before_entries"]["AGENTS.md"], packet["artifacts"]["local"])
        self.assertEqual((DRAFT / "files/AGENTS.md").read_bytes(), packet["artifacts"]["incoming"])
        self.assertTrue(packet["artifacts"]["diff"])
        self.assertIn("AGENTS.md", scenario["report_markdown"])
        self.assertIn("custom", scenario["report_markdown"])

    def test_custom_claude_preserved_with_complete_packet_and_summary(self):
        scenario = self.scenario("custom")
        item = self.by_target(scenario)["CLAUDE.md"]
        packet = scenario["packets"]["CLAUDE.md"]
        self.assertEqual("custom", item["classification"])
        self.assertEqual(scenario["before_entries"]["CLAUDE.md"], scenario["after_entries"]["CLAUDE.md"])
        self.assertEqual(scenario["before_entries"]["CLAUDE.md"], packet["artifacts"]["rollback"])
        self.assertTrue(packet["artifacts"]["diff"])

    def test_unknown_baseline_preserved_without_guessing(self):
        scenario = self.scenario("unknown")
        item = self.by_target(scenario)["CLAUDE.md"]
        self.assertEqual("unknown-baseline", item["classification"])
        self.assertEqual(scenario["before_entries"]["CLAUDE.md"], scenario["after_entries"]["CLAUDE.md"])
        self.assertIsNone(scenario["packets"]["CLAUDE.md"]["metadata"]["baseline_sha256"])

    def test_missing_installs_incoming_without_fabricated_origin(self):
        scenario = self.scenario("missing")
        self.assertEqual({"missing"}, {item["classification"] for item in scenario["report"]["items"]})
        for target in validator.ENTRY_NAMES:
            packet = scenario["packets"][target]
            self.assertIsNone(scenario["before_entries"][target])
            self.assertEqual((DRAFT / "files" / target).read_bytes(), scenario["after_entries"][target])
            self.assertIsNone(packet["artifacts"]["local"])
            self.assertIsNone(packet["artifacts"]["rollback"])
            self.assertEqual("delete_upgrade_created_file", packet["metadata"]["rollback_action"])
        self.assertTrue(scenario["rollback_restored"])

    def test_mixed_stock_custom_classifications_do_not_pollute_each_other(self):
        scenario = self.scenario("mixed")
        by_target = self.by_target(scenario)
        self.assertEqual("stock", by_target["AGENTS.md"]["classification"])
        self.assertEqual("custom", by_target["CLAUDE.md"]["classification"])
        self.assertEqual((DRAFT / "files/AGENTS.md").read_bytes(), scenario["after_entries"]["AGENTS.md"])
        self.assertEqual(scenario["before_entries"]["CLAUDE.md"], scenario["after_entries"]["CLAUDE.md"])
        self.assertNotEqual(by_target["AGENTS.md"]["packet_id"], by_target["CLAUDE.md"]["packet_id"])

    def test_mixed_rollback_restores_complete_upgrade_start(self):
        scenario = self.scenario("mixed")
        self.assertTrue(scenario["rollback_restored"])

    def test_same_path_multi_migration_rollback_retains_upgrade_origin(self):
        self.assertEqual([], self.errors)
        chain = self.evidence["chain"]
        self.assertEqual(b"stage-a-origin\r\n", chain["rollback"])
        self.assertTrue(chain["rollback_restored"])

    def test_behavior_gate_cleans_all_isolated_projects_and_reports(self):
        self.assertEqual([], self.errors)
        self.assertTrue(self.evidence["cleaned"])
        self.assertFalse(Path(self.evidence["temp_root"]).exists())


if __name__ == "__main__":
    unittest.main()
