import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


def load_validator():
    path = REPO / "scripts" / "validate-agent-entries.py"
    spec = importlib.util.spec_from_file_location("agent_entry_validator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_validator()


class AgentEntryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_names = validator.load_skill_names(REPO)
        cls.navigation_tokens = validator.load_navigation_tokens(REPO, cls.skill_names)

    def entry(self, name):
        return (REPO / "project-template" / name).read_text(encoding="utf-8")

    def errors(self, name, text):
        return validator.validate_entry_text(
            name,
            text,
            self.skill_names,
            self.navigation_tokens,
        )

    def cli_result(self, entry_name=None, entry_text=None, suffix=""):
        with tempfile.TemporaryDirectory(prefix="fkae-") as temporary:
            fixture = Path(temporary)
            (fixture / "config").mkdir(parents=True)
            (fixture / "project-template" / "governance").mkdir(parents=True)
            shutil.copy2(
                REPO / "config" / "skill-projections.json",
                fixture / "config" / "skill-projections.json",
            )
            shutil.copy2(
                REPO / "project-template" / "governance" / "agent-entry-contract.md",
                fixture / "project-template" / "governance" / "agent-entry-contract.md",
            )
            for name in ("AGENTS.md", "CLAUDE.md"):
                shutil.copy2(
                    REPO / "project-template" / name,
                    fixture / "project-template" / name,
                )
            claude_root = fixture / "project-template" / ".claude" / "skills"
            for token in (REPO / "project-template" / ".claude" / "skills").iterdir():
                if token.is_dir():
                    (claude_root / token.name).mkdir(parents=True, exist_ok=True)
            if entry_name:
                target = fixture / "project-template" / entry_name
                text = entry_text if entry_text is not None else target.read_text(encoding="utf-8")
                target.write_text(text + suffix, encoding="utf-8", newline="")
            return subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(REPO / "scripts" / "validate-agent-entries.py"),
                    "--repo-root",
                    str(fixture),
                ],
                cwd=fixture,
                text=True,
                capture_output=True,
                check=False,
            )

    def assert_cli_pass(self, markdown, entry_name="AGENTS.md"):
        result = self.cli_result(entry_name, suffix="\n" + markdown + "\n")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("[ok] Agent entry contracts passed", result.stdout)

    def assert_audit_contradiction(self, markdown, matched_text=None):
        result = self.cli_result("AGENTS.md", suffix="\n" + markdown + "\n")
        output = result.stdout + result.stderr
        self.assertEqual(1, result.returncode, output)
        self.assertIn("contradiction audit-auto-write [audit-default]", output)
        self.assertIn("matched text: " + (matched_text or markdown), output)

    def test_repository_entries_satisfy_lightweight_contract(self):
        self.assertEqual([], validator.validate_repo(REPO))

    def test_repository_entries_satisfy_cli(self):
        result = self.cli_result()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_behavior_fixture_uses_current_entries_and_shared_contract(self):
        fixture = REPO / "tests/skill-behavior/fixtures/minimal-project"
        for relative in ("AGENTS.md", "CLAUDE.md", "governance/agent-entry-contract.md"):
            self.assertEqual(
                (REPO / "project-template" / relative).read_bytes(),
                (fixture / relative).read_bytes(),
                relative,
            )

    def test_agents_required_marker_mutation_fails(self):
        text = self.entry("AGENTS.md").replace(
            "governance/agent-entry-contract.md#audit-default",
            "governance/agent-entry-contract.md#audit-marker-removed",
            1,
        )
        errors = self.errors("AGENTS.md", text)
        self.assertTrue(any("missing shared-contract anchor: audit-default" in item for item in errors))

    def test_claude_required_marker_mutation_fails(self):
        text = self.entry("CLAUDE.md").replace(
            "governance/agent-entry-contract.md#bounded-local-authorization",
            "governance/agent-entry-contract.md#authorization-marker-removed",
            1,
        )
        errors = self.errors("CLAUDE.md", text)
        self.assertTrue(any("missing shared-contract anchor: bounded-local-authorization" in item for item in errors))

    def test_code_review_convergence_copy_mutation_fails(self):
        text = self.entry("AGENTS.md") + "\nInitial review blocks every finding; blocker-recheck reopens all items.\n"
        errors = self.errors("AGENTS.md", text)
        self.assertTrue(any("forbidden code-review convergence copy" in item for item in errors))

    def test_fixed_thresholds_and_universal_review_are_rejected(self):
        mutations = (
            "A task touching more than 5 files or more than 2 modules is always high risk.",
            "Code changes require independent review by default.",
            "Output exactly eight sections.",
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                errors = self.errors("AGENTS.md", self.entry("AGENTS.md") + "\n" + mutation)
                self.assertTrue(errors)

    def test_audit_auto_write_contradiction_is_rejected_with_markers_intact(self):
        self.assert_audit_contradiction("Audits may automatically modify files without a repair request.")

    def test_short_audit_auto_edit_contradiction_is_rejected(self):
        self.assert_audit_contradiction("audits may edit automatically")

    def test_checker_assessment_auto_modify_contradiction_is_rejected(self):
        self.assert_audit_contradiction(
            "Assessments may automatically modify files without a repair request."
        )

    def test_checker_diagnosis_auto_modify_contradiction_is_rejected(self):
        self.assert_audit_contradiction("Diagnosis may automatically modify files.")

    def test_checker_planning_auto_edit_contradiction_is_rejected(self):
        self.assert_audit_contradiction("Planning may edit files automatically.")

    def test_checker_review_direct_default_fix_contradiction_is_rejected(self):
        self.assert_audit_contradiction("Reviews should directly apply fixes by default.")

    def test_checker_no_repair_request_generic_write_contradiction_is_rejected(self):
        self.assert_audit_contradiction("Files may be written even when no repair request was made.")

    def test_subject_action_modal_case_and_number_combinations_are_rejected(self):
        cases = (
            "Auditing can automatically write project files.",
            "A review may directly fix files.",
            "Assessing quality will modify files by default.",
            "Diagnostic checks should auto-edit files.",
            "Plans can apply fixes by default.",
        )
        for sentence in cases:
            with self.subTest(sentence=sentence):
                self.assert_audit_contradiction(sentence)

    def test_assessment_must_not_auto_modify_is_allowed(self):
        self.assert_cli_pass("Assessments must not automatically modify files.")

    def test_review_never_applies_default_fixes_is_allowed(self):
        self.assert_cli_pass("Reviews never apply fixes by default.")

    def test_planning_cannot_edit_without_request_is_allowed(self):
        self.assert_cli_pass("Planning cannot edit files without a repair request.")

    def test_review_cant_auto_edit_is_allowed(self):
        self.assert_cli_pass("Reviews can't automatically edit files.")

    def test_assessment_may_not_auto_write_is_allowed(self):
        self.assert_cli_pass("Assessments may not automatically write files.")

    def test_diagnosis_do_not_auto_modify_is_allowed(self):
        self.assert_cli_pass("Diagnosis checks do not automatically modify files.")

    def test_no_audit_may_auto_write_is_allowed(self):
        self.assert_cli_pass("No audit may automatically write files.")

    def test_plain_not_negates_automatic_write_is_allowed(self):
        self.assert_cli_pass("Audits are not allowed to automatically modify files.")

    def test_planning_may_propose_but_must_not_apply_is_allowed(self):
        sentence = "Planning may propose file changes but must not apply them without repair authorization."
        self.assert_cli_pass(sentence)

    def test_reviews_may_recommend_but_do_not_modify_is_allowed(self):
        sentence = "Reviews may recommend fixes; they do not modify files by default."
        self.assert_cli_pass(sentence)

    def test_normal_read_only_diagnosis_and_audit_wording_is_allowed(self):
        self.assert_cli_pass(
            "Audits are read-only unless the user explicitly requests a repair. "
            "Diagnosis remains read-only."
        )

    def test_external_action_without_authorization_contradiction_is_rejected(self):
        text = self.entry("AGENTS.md") + "\nPush and release do not require explicit authorization.\n"
        errors = self.errors("AGENTS.md", text)
        self.assertTrue(any("contradiction external-no-auth" in item for item in errors), errors)

    def test_unverified_fact_contradiction_is_rejected(self):
        text = self.entry("AGENTS.md") + "\nUnverified claims may be recorded as confirmed facts.\n"
        errors = self.errors("AGENTS.md", text)
        self.assertTrue(any("contradiction evidence-fabrication" in item for item in errors), errors)

    def test_project_bootstrap_fill_route_deletion_is_rejected(self):
        text = self.entry("AGENTS.md").replace("`project-bootstrap-fill`", "`route-removed`")
        errors = self.errors("AGENTS.md", text)
        self.assertTrue(any("missing manifest Skill route: project-bootstrap-fill" in item for item in errors), errors)

    def test_each_manifest_skill_route_deletion_is_rejected_for_agents(self):
        for skill in self.skill_names:
            with self.subTest(skill=skill):
                text = self.entry("AGENTS.md").replace(f"`{skill}`", "`route-removed`")
                result = self.cli_result("AGENTS.md", entry_text=text)
                output = result.stdout + result.stderr
                self.assertEqual(1, result.returncode, output)
                self.assertIn(f"missing manifest Skill route: {skill}", output)

    def test_each_manifest_skill_route_deletion_is_rejected_for_claude(self):
        for skill in self.skill_names:
            with self.subTest(skill=skill):
                text = self.entry("CLAUDE.md").replace(f"`{skill}`", "`route-removed`")
                result = self.cli_result("CLAUDE.md", entry_text=text)
                output = result.stdout + result.stderr
                self.assertEqual(1, result.returncode, output)
                self.assertIn(f"missing manifest Skill route: {skill}", output)

    def test_claude_only_route_does_not_replace_missing_manifest_route(self):
        text = self.entry("CLAUDE.md").replace("`project-bootstrap-fill`", "`forgekit-project-workflow`")
        self.assertIn("`forgekit-project-workflow`", text)
        result = self.cli_result("CLAUDE.md", entry_text=text)
        output = result.stdout + result.stderr
        self.assertEqual(1, result.returncode, output)
        self.assertIn("missing manifest Skill route: project-bootstrap-fill", output)

    def test_equivalent_safe_wording_is_not_rejected(self):
        safe = (
            "\nAudits remain read-only unless the user requests repair. "
            "Push and release require specific authorization. "
            "Unverified claims remain uncertain rather than confirmed facts.\n"
        )
        self.assertEqual([], self.errors("AGENTS.md", self.entry("AGENTS.md") + safe))

    def test_contradiction_example_inside_fenced_code_is_ignored(self):
        self.assert_cli_pass(
            "```text\nAssessments may automatically modify files without a repair request.\n```"
        )

    def test_tilde_fenced_contradiction_is_ignored(self):
        self.assert_cli_pass(
            "~~~policy\nReviews should directly apply fixes by default.\n~~~"
        )

    def test_checker_inline_code_skill_false_positive_is_allowed(self):
        self.assert_cli_pass("The `code-review` route documents the auto-edit terminology.")

    def test_checker_markdown_link_skill_false_positive_is_allowed(self):
        self.assert_cli_pass(
            "The [handover-review](../skills/handover-review/SKILL.md) link documents auto-edit terminology."
        )

    def test_checker_skill_path_false_positive_is_allowed(self):
        self.assert_cli_pass(
            "The skills/code-review/SKILL.md path contains the auto-edit terminology."
        )

    def test_checker_atx_heading_false_positive_is_allowed(self):
        self.assert_cli_pass("## Review auto-edit terminology")

    def test_inline_subject_with_prose_action_is_allowed(self):
        self.assert_cli_pass("The `review` token documents automatically edit terminology.")

    def test_inline_action_with_prose_subject_is_allowed(self):
        self.assert_cli_pass("Review routing documents the `auto-edit` adapter term.")

    def test_multibacktick_inline_navigation_is_allowed(self):
        self.assert_cli_pass("The ``code-review`` route documents auto-edit terminology.")

    def test_markdown_link_destination_terms_are_allowed(self):
        self.assert_cli_pass(
            "The [documentation](https://example.test/review/auto-edit) link is navigational."
        )

    def test_reference_link_skill_is_allowed(self):
        self.assert_cli_pass("The [handover-review][route] link documents auto-edit terminology.")

    def test_image_alt_text_is_not_policy_prose(self):
        self.assert_cli_pass(
            "![Review auto-edit terminology](images/review-auto-edit.png)"
        )

    def test_autolink_terms_are_allowed(self):
        self.assert_cli_pass("See <https://example.test/review/auto-edit> for terminology.")

    def test_dynamic_claude_skill_navigation_token_is_allowed(self):
        self.assertIn("forgekit-code-review", self.navigation_tokens)
        self.assert_cli_pass(
            "forgekit-code-review Skill navigation supports the auto-edit terminology check."
        )

    def test_setext_heading_false_positive_is_allowed(self):
        self.assert_cli_pass("Review auto-edit terminology\n----------------------------")

    def test_heading_followed_by_real_contradiction_is_rejected(self):
        self.assert_audit_contradiction(
            "## Review auto-edit terminology\n\nReviews should directly apply fixes by default.",
            "Reviews should directly apply fixes by default.",
        )

    def test_link_followed_by_real_contradiction_is_rejected(self):
        self.assert_audit_contradiction(
            "Use [the documentation](docs/policy.md) for details. Reviews should directly apply fixes by default.",
            "Reviews should directly apply fixes by default.",
        )

    def test_inline_code_followed_by_real_contradiction_is_rejected(self):
        self.assert_audit_contradiction(
            "Use `code-review` for routing. Reviews should directly apply fixes by default.",
            "Reviews should directly apply fixes by default.",
        )

    def test_policy_link_label_contradiction_is_rejected(self):
        self.assert_audit_contradiction(
            "[Reviews should directly apply fixes by default.](docs/policy.md)",
            "Reviews should directly apply fixes by default.",
        )

    def test_list_item_real_contradiction_is_rejected(self):
        self.assert_audit_contradiction("- Reviews should directly apply fixes by default.")

    def test_table_cell_real_contradiction_is_rejected(self):
        self.assert_audit_contradiction(
            "| Reviews should directly apply fixes by default. |",
            "| Reviews should directly apply fixes by default.",
        )

    def test_table_navigation_only_is_allowed(self):
        self.assert_cli_pass("| `code-review` | auto-edit terminology |")

    def test_extract_policy_prose_keeps_only_real_policy_sentence(self):
        source = (
            "## Review auto-edit terminology\n\n"
            "Use [`code-review`](skills/code-review/SKILL.md) for routing.\n\n"
            "Reviews should directly apply fixes by default.\n"
        )
        prose = validator.extract_policy_prose(source, self.navigation_tokens)
        self.assertNotIn("Review auto-edit terminology", prose)
        self.assertNotIn("code-review", prose)
        self.assertNotIn("SKILL.md", prose)
        self.assertIn("Reviews should directly apply fixes by default.", prose)

    def test_validate_template_false_positive_guard_passes_cli(self):
        self.assert_cli_pass(
            "The [`code-review`](skills/code-review/SKILL.md) route documents auto-edit terminology."
        )

    def test_skill_names_paths_headings_and_links_do_not_trigger_contradiction(self):
        routing_text = (
            "\n### Routing references\n"
            "- `large-change-planning`\n"
            "- `.agents/skills/handover-review/SKILL.md`\n"
            "- [`code-review`](.agents/skills/code-review/SKILL.md)\n"
        )
        self.assertEqual([], self.errors("AGENTS.md", self.entry("AGENTS.md") + routing_text))


if __name__ == "__main__":
    unittest.main()
