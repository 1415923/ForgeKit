import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


def run(command, cwd):
    return subprocess.run(
        command, cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30
    )


class FreshCloneCrlfTests(unittest.TestCase):
    def test_root_and_generated_project_publish_the_lf_contract(self):
        required = {
            ".gitattributes", "*.md", "*.json", "*.yaml", "*.yml",
            "*.toml", "*.py", "*.ps1", "*.sh",
        }
        for relative in (".gitattributes", "project-template/.gitattributes"):
            rules = {
                line.split()[0]: " ".join(line.split()[1:])
                for line in (REPO / relative).read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.lstrip().startswith("#")
            }
            self.assertTrue(required <= set(rules))
            for pattern in required:
                self.assertEqual("text eol=lf", rules[pattern])
        manifest = json.loads(
            (REPO / "project-template/.forgekit/template-manifest.json").read_text(encoding="utf-8")
        )
        entries = [item["source_path"] for item in manifest["files"]]
        self.assertEqual(1, entries.count(".gitattributes"))

    def test_autocrlf_true_and_false_keep_lf_when_rule_exists_and_diverge_without_it(self):
        with tempfile.TemporaryDirectory(prefix="fk-crlf-unit-", dir=Path("D:/tmp")) as temp_name:
            temp = Path(temp_name)
            source = temp / "s"
            source.mkdir()
            run(["git", "init"], source)
            (source / ".gitattributes").write_bytes(b".gitattributes text eol=lf\n*.md text eol=lf\n")
            (source / "sample.md").write_bytes(b"alpha\nbeta\n")
            run(["git", "add", ".gitattributes", "sample.md"], source)
            run([
                "git", "-c", "user.name=ForgeKit Test", "-c",
                "user.email=forgekit-test@example.invalid", "commit", "-m", "lf contract",
            ], source)
            for mode, name in (("false", "lf"), ("true", "cr")):
                clone = temp / name
                run(["git", "-c", f"core.autocrlf={mode}", "clone", "--no-local", str(source), str(clone)], temp)
                blob = run(["git", "show", "HEAD:sample.md"], clone).stdout
                self.assertEqual(blob, (clone / "sample.md").read_bytes())

            (source / ".gitattributes").write_bytes(b".gitattributes text eol=lf\n")
            run(["git", "add", ".gitattributes"], source)
            run([
                "git", "-c", "user.name=ForgeKit Test", "-c",
                "user.email=forgekit-test@example.invalid", "commit", "-m", "remove md rule",
            ], source)
            bad = temp / "bad"
            run(["git", "-c", "core.autocrlf=true", "clone", "--no-local", str(source), str(bad)], temp)
            blob = run(["git", "show", "HEAD:sample.md"], bad).stdout
            self.assertNotEqual(blob, (bad / "sample.md").read_bytes())

    def test_fresh_clone_gate_has_no_post_clone_overlay(self):
        source = (REPO / "scripts/test-fresh-clone-crlf.py").read_text(encoding="utf-8")
        verify_body = source.split("def verify_clone", 1)[1].split("def verify_missing_attribute_mutation", 1)[0]
        self.assertNotIn("copyfile", verify_body)
        self.assertIn("byte-exact checkout mismatch", verify_body)
        self.assertIn("git\", \"check-attr", verify_body)
        self.assertIn('evidence["working_tree_snapshot"]', source)
        self.assertIn("retired paths materialized from the current release contract", source)


if __name__ == "__main__":
    unittest.main()
