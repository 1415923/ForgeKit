import contextlib
import importlib.util
import io
import json
import os
import subprocess
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


projection = load_module("skill_projection", REPO / "scripts/sync-skill-projections.py")


def make_directory_link(link, target):
    if os.name == "nt":
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True)
        if result.returncode != 0:
            raise OSError(result.stderr.decode(errors="replace") or result.stdout.decode(errors="replace"))
    else:
        link.symlink_to(target, target_is_directory=True)


class SkillProjectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="forgekit-projection-", dir=Path("D:/tmp"))
        self.root = Path(self.temp.name)
        for marker in ("VERSION", ".codex-plugin/plugin.json"):
            path = self.root / marker
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}\n" if path.suffix == ".json" else "0.44.1\n", encoding="utf-8")
        self.manifest = json.loads((REPO / "config/skill-projections.json").read_text(encoding="utf-8"))
        manifest_path = self.root / "config/skill-projections.json"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")
        for entry in self.manifest["entries"]:
            for managed in entry["managed_files"]:
                data = f"{entry['skill']}:{managed}\n".encode("utf-8")
                for base in (self.manifest["source_root"], self.manifest["target_root"]):
                    path = self.root / base / entry["skill"] / managed
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)

    def tearDown(self):
        self.temp.cleanup()

    def plan(self):
        return projection.load_plan(self.root, "config/skill-projections.json")

    def test_schema_has_nine_explicit_nonrecursive_entries(self):
        plan = self.plan()
        self.assertEqual(18, len(plan))
        self.assertEqual(9, len({item.skill for item in plan}))
        self.assertEqual({"SKILL.md", "agents/openai.yaml"}, {item.managed_file for item in plan})

    def test_check_reports_both_hashes_and_detects_each_file_type(self):
        for suffix in ("SKILL.md", "agents/openai.yaml"):
            item = next(item for item in self.plan() if item.managed_file == suffix)
            original = item.target.read_bytes()
            try:
                item.target.write_bytes(original + b"mutation\r\n")
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertFalse(projection.check(self.plan()))
                rendered = output.getvalue()
                self.assertIn(item.skill, rendered)
                self.assertIn(item.source_relative, rendered)
                self.assertIn(item.target_relative, rendered)
                self.assertIn("source SHA-256=", rendered)
                self.assertIn("target SHA-256=", rendered)
            finally:
                item.target.write_bytes(original)
            self.assertEqual(original, item.target.read_bytes())

    def test_missing_source_and_target_fail(self):
        source_item = self.plan()[0]
        source_item.source.unlink()
        self.assertFalse(projection.check(self.plan()))
        source_item.source.write_bytes(b"restored\n")
        source_item.target.unlink()
        self.assertFalse(projection.check(self.plan()))

    def test_single_and_double_sided_crlf_violate_raw_lf_contract(self):
        item = self.plan()[0]
        original = item.source.read_bytes()
        crlf = original.replace(b"\n", b"\r\n")
        item.source.write_bytes(crlf)
        self.assertFalse(projection.check(self.plan()))
        item.target.write_bytes(crlf)
        self.assertFalse(projection.check(self.plan()))
        with self.assertRaisesRegex(projection.ProjectionError, "LF checkout contract"):
            projection.apply(self.plan())

    def test_apply_only_copies_declared_files(self):
        target_root = self.root / self.manifest["target_root"]
        unmanaged = target_root / self.manifest["entries"][0]["skill"] / "references/unmanaged.md"
        unmanaged.parent.mkdir(parents=True)
        unmanaged.write_bytes(b"preserve\r\n")
        claude = self.root / "project-template/.claude/skills/adapter/SKILL.md"
        claude.parent.mkdir(parents=True)
        claude.write_bytes(b"claude-specific\n")
        item = self.plan()[0]
        item.target.write_bytes(b"drift")
        self.assertTrue(projection.apply(self.plan()))
        self.assertEqual(b"preserve\r\n", unmanaged.read_bytes())
        self.assertEqual(b"claude-specific\n", claude.read_bytes())

    def test_path_escape_fails_before_any_copy(self):
        target = self.plan()[0].target
        target.write_bytes(b"sentinel")
        bad = dict(self.manifest)
        bad["target_root"] = "../outside"
        (self.root / "config/skill-projections.json").write_text(json.dumps(bad), encoding="utf-8")
        with self.assertRaises(projection.ProjectionError):
            projection.load_plan(self.root, "config/skill-projections.json")
        self.assertEqual(b"sentinel", target.read_bytes())

    def test_unmanaged_manifest_file_is_rejected(self):
        self.manifest["entries"][0]["managed_files"].append("references/all.md")
        (self.root / "config/skill-projections.json").write_text(json.dumps(self.manifest), encoding="utf-8")
        with self.assertRaises(projection.ProjectionError):
            self.plan()

    def test_unsafe_characters_are_rejected_without_a_second_skill_authority(self):
        source_text = (REPO / "scripts/sync-skill-projections.py").read_text(encoding="utf-8")
        self.assertNotIn("EXPECTED_SKILLS", source_text)
        with self.assertRaises(projection.ProjectionError):
            projection.safe_posix_relative("unsafe:name", "test")

    def test_full_plan_parent_conflict_fails_before_first_copy(self):
        plan = self.plan()
        first = plan[0]
        first.target.write_bytes(b"first-before")
        second = plan[1]
        shutil.rmtree(second.target.parent)
        second.target.parent.write_bytes(b"parent-is-a-file")
        before = {item.target_relative: item.target.read_bytes() for item in plan if item.target.is_file()}
        with self.assertRaisesRegex(projection.ProjectionError, "target parent is not a directory"):
            projection.apply(plan)
        after = {item.target_relative: item.target.read_bytes() for item in plan if item.target.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(b"first-before", first.target.read_bytes())

    def test_target_directory_and_non_regular_source_fail_preflight(self):
        plan = self.plan()
        target_item = plan[0]
        target_item.target.unlink()
        target_item.target.mkdir()
        with self.assertRaisesRegex(projection.ProjectionError, "target is not a regular file"):
            projection.apply(plan)
        target_item.target.rmdir()
        target_item.target.write_bytes(b"restored")
        source_item = plan[1]
        source_item.source.unlink()
        source_item.source.mkdir()
        with self.assertRaisesRegex(projection.ProjectionError, "source is missing or not a regular file"):
            projection.apply(plan)

    def test_reparse_or_symlink_target_fails_during_preflight(self):
        real_target = self.root / "real-target"
        real_target.mkdir()
        managed_root = self.root / "project-template/.agents/skills"
        shutil.rmtree(managed_root)
        try:
            make_directory_link(managed_root, real_target)
        except OSError as exc:
            self.skipTest(f"directory symlink is unavailable: {exc}")
        try:
            with self.assertRaises(projection.ProjectionError):
                self.plan()
        finally:
            managed_root.rmdir()


if __name__ == "__main__":
    unittest.main()
