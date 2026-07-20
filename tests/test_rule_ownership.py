import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ownership = load_module("rule_ownership", REPO / "scripts/validate-rule-ownership.py")


class RuleOwnershipTests(unittest.TestCase):
    def test_approved_matrix_has_41_unique_concrete_owners(self):
        rows = ownership.validate(
            REPO,
            ".forgekit/changes/v045-rule-ownership-skill-convergence/design.md",
        )
        self.assertEqual(41, len(rows))
        self.assertEqual(41, len({row["rule_id"] for row in rows}))

    def test_owner_rejects_wildcard_placeholder_and_natural_language(self):
        for value in (
            "skills/*/SKILL.md",
            "skills/<skill>/SKILL.md",
            "对应文件",
            "共享合同",
            "各 Skill",
        ):
            with self.subTest(value=value), self.assertRaises(ownership.OwnershipError):
                ownership.validate_owner(REPO, "MUTATION", value)

    def test_agents_projection_cannot_be_normative_owner(self):
        rows = ownership.validate(
            REPO,
            ".forgekit/changes/v045-rule-ownership-skill-convergence/design.md",
        )
        self.assertFalse(any(row["owner"].startswith("project-template/.agents/") for row in rows))

    def test_projection_manifest_is_derived_from_route_owners(self):
        rows = ownership.parse_matrix(
            REPO / ".forgekit/changes/v045-rule-ownership-skill-convergence/design.md"
        )
        routes = [row for row in rows if row["rule_id"].startswith("ROUTE-")]
        ownership.validate_projection_manifest(REPO, routes)
        bad = [dict(row) for row in routes]
        bad[0]["owner"] = "skills/not-in-manifest/SKILL.md"
        with self.assertRaises(ownership.OwnershipError):
            ownership.validate_projection_manifest(REPO, bad)


if __name__ == "__main__":
    unittest.main()
