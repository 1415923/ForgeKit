import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
MIGRATION_ROOT = REPO / "migrations"
PACKAGE = MIGRATION_ROOT / "0.46.0"
TEMPLATE_PACKAGE = REPO / "project-template/migrations/0.46.0"


def sha256_bytes(content):
    return "sha256:" + hashlib.sha256(content).hexdigest()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def run(command, cwd=REPO, expected=(0,)):
    environment = dict(os.environ)
    environment["PYTHONUTF8"] = "1"
    completed = subprocess.run(
        [str(item) for item in command],
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=environment,
        check=False,
    )
    if completed.returncode not in expected:
        raise AssertionError(
            f"command returned {completed.returncode}, expected {expected}: {command}\n{completed.stdout}"
        )
    return completed


def git_bytes(specification):
    completed = subprocess.run(
        ["git", "show", specification],
        cwd=REPO,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr.decode("utf-8", errors="replace"))
    return completed.stdout


def tree_snapshot(root):
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"), key=lambda item: item.as_posix())
        if path.is_file()
    }


def tree_inventory(root):
    inventory = {}
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        inventory[relative] = None if path.is_dir() else path.read_bytes()
    return inventory


class StageDTestCase(unittest.TestCase):
    def make_root(self, label):
        root = REPO / f".stage-d-{label}-{uuid.uuid4().hex[:8]}"
        root.mkdir()
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def descriptor(self, package=PACKAGE):
        return load_json(package / "migration.json")

    def write_boundary(self, governance_root, project_root="."):
        (governance_root / ".forgekit").mkdir(parents=True, exist_ok=True)
        relative_project = Path(project_root).as_posix()
        (governance_root / ".forgekit/project-boundary.yml").write_text(
            "# Version used when this project boundary file was created.\n"
            "# Current ForgeKit version is tracked in .forgekit/state.json.\n"
            "forgekit:\n"
            "  version: \"0.44.0\"\n"
            "  mode: \"Standard\"\n\n"
            "roots:\n"
            f"  forgekit_root: \"{REPO.as_posix()}\"\n"
            f"  project_root: \"{relative_project}\"\n"
            "  managed_docs_root: \".forgekit/docs\"\n"
            "  change_root: \".forgekit/changes\"\n"
            "  business_docs_roots:\n"
            "    - \"docs\"\n\n"
            "write_policy:\n"
            "  allow:\n"
            "    - \".forgekit/**\"\n"
            "    - \"governance/**\"\n"
            "    - \"scripts/**\"\n",
            encoding="utf-8",
        )

    def make_project(self, label, *, project_root=".", readme=None, package=PACKAGE):
        root = self.make_root(label)
        descriptor = self.descriptor(package)
        state = load_json(REPO / "project-template/.forgekit/state.json")
        state["forgekit_version"] = "0.45.0"
        state["last_upgrade"] = None
        (root / ".forgekit").mkdir(parents=True)
        (root / ".forgekit/state.json").write_text(
            json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        self.write_boundary(root, project_root)
        lock_files = []
        for action in descriptor["actions"]:
            target = root / Path(action["target"])
            baseline = package / Path(action["baseline"])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(baseline.read_bytes())
            checksum = sha256_bytes(target.read_bytes())
            lock_files.append({
                "source_path": action["target"],
                "target_path": action["target"],
                "role": "metadata",
                "update_policy": "replace",
                "render_mode": "copy",
                "source_checksum": checksum,
                "installed_checksum": checksum,
            })
        if project_root != ".":
            (root / project_root).mkdir(parents=True, exist_ok=True)
        if readme is not None:
            (root / "README.md").write_bytes(readme)
            checksum = sha256_bytes(readme)
            lock_files.append({
                "source_path": "README.md",
                "target_path": "README.md",
                "role": "readme",
                "update_policy": "ask",
                "render_mode": "copy",
                "source_checksum": checksum,
                "installed_checksum": checksum,
            })
        lock = {
            "schema_version": 1,
            "installed_version": "0.45.0",
            "installed_at": "2026-01-01T00:00:00Z",
            "managed_docs_root": ".forgekit/docs",
            "change_root": ".forgekit/changes",
            "files": lock_files,
        }
        (root / ".forgekit/template-lock.json").write_text(
            json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return root

    def apply(self, project, *, package_root=MIGRATION_ROOT, policy="manual-merge"):
        return run([
            sys.executable,
            "-B",
            REPO / "scripts/forgekit-upgrade.py",
            "apply",
            "--safe",
            "--repo-root",
            project,
            "--migration-root",
            package_root,
            "--review-needed-policy",
            policy,
        ])

    def make_toolkit(self):
        toolkit = self.make_root("toolkit")
        (toolkit / "scripts").mkdir()
        for name in (
            "forgekit-project.py",
            "forgekit-upgrade.py",
            "upgrade_review_packets.py",
            "check-current-docs-integrity.py",
            "init-project-template.ps1",
            "init-project-template.sh",
            "update-template-manifest.py",
        ):
            shutil.copy2(REPO / "scripts" / name, toolkit / "scripts" / name)
        shutil.copytree(MIGRATION_ROOT, toolkit / "migrations")
        (toolkit / "config").mkdir()
        shutil.copy2(REPO / "config/skill-projections.json", toolkit / "config/skill-projections.json")
        shutil.copytree(REPO / "project-template", toolkit / "project-template")
        state = load_json(toolkit / "project-template/.forgekit/state.json")
        state["forgekit_version"] = "0.46.0"
        (toolkit / "project-template/.forgekit/state.json").write_text(
            json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        manifest_path = toolkit / "project-template/.forgekit/template-manifest.json"
        manifest = load_json(manifest_path)
        manifest["template_version"] = "0.46.0"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (toolkit / "VERSION").write_text("0.46.0\n", encoding="utf-8")
        return toolkit


class MigrationPayloadTests(StageDTestCase):
    def test_exact_predecessor_payload_and_mirrors(self):
        descriptor = self.descriptor()
        self.assertEqual("0.45.0", descriptor["from"])
        self.assertEqual("0.46.0", descriptor["to"])
        self.assertEqual(38, len(descriptor["actions"]))
        self.assertEqual(tree_snapshot(PACKAGE), tree_snapshot(TEMPLATE_PACKAGE))
        self.assertEqual("0.45.0", (REPO / "VERSION").read_text(encoding="utf-8").strip())
        self.assertEqual(
            "0.45.0",
            load_json(REPO / "project-template/.forgekit/state.json")["forgekit_version"],
        )

    def test_payload_baselines_and_incoming_files_are_exact(self):
        descriptor = self.descriptor()
        old_manifest = json.loads(git_bytes("v0.45.0:project-template/.forgekit/template-manifest.json"))

        def expanded(value):
            return value.replace("${managed_docs_root}", ".forgekit/docs").replace("${change_root}", ".forgekit/changes")

        for action in descriptor["actions"]:
            baseline = PACKAGE / action["baseline"]
            self.assertTrue(baseline.is_file(), action["id"])
            old_item = next(item for item in old_manifest["files"] if expanded(item["target_path"]) == action["target"])
            self.assertEqual(
                git_bytes(f"v0.45.0:project-template/{old_item['source_path']}"),
                baseline.read_bytes(),
                action["id"],
            )
            if action["type"] == "replace_file_if_baseline_matches":
                incoming = PACKAGE / action["source"]
                current = REPO / "project-template" / Path(action["target"])
                if action["target"].startswith(".forgekit/docs/"):
                    name = Path(action["target"]).name
                    current = REPO / "project-template/docs" / name
                    internal = REPO / "project-template/.forgekit/docs" / name
                    if internal.is_file():
                        current = internal
                if action["target"] == ".forgekit/changes/_template/review.md":
                    current = REPO / "project-template/changes/_template/review.md"
                self.assertEqual(current.read_bytes(), incoming.read_bytes(), action["id"])
        removals = [a for a in descriptor["actions"] if a["type"] == "remove_file_if_baseline_matches"]
        self.assertEqual(3, len(removals))
        self.assertFalse(any(action.get("target") == "README.md" for action in descriptor["actions"]))
        self.assertIn("README.md", descriptor["template_lock"]["retire_targets"])


class MigrationBehaviorTests(StageDTestCase):
    def test_stock_success_readme_absent_lock_convergence_and_idempotency(self):
        project = self.make_project("stock")
        boundary_before = (project / ".forgekit/project-boundary.yml").read_bytes()
        task_board = project / ".forgekit/docs/task-board.md"
        task_board.write_text("# Task Board\n\n- Active task: T-1\n", encoding="utf-8")
        self.assertFalse((project / "README.md").exists())
        self.assertFalse((project / ".forgekit/docs/risk-register.md").exists())
        first = self.apply(project)
        self.assertIn("project is fully updated to 0.46.0", first.stdout)
        state = load_json(project / ".forgekit/state.json")
        self.assertEqual("0.46.0", state["forgekit_version"])
        self.assertEqual(boundary_before, (project / ".forgekit/project-boundary.yml").read_bytes())
        for name in ("loop-readiness.md", "loop-blueprint.md", "loop-operations.md"):
            self.assertFalse((project / ".forgekit/docs" / name).exists())
        self.assertFalse((project / "README.md").exists())
        self.assertEqual("# Task Board\n\n- Active task: T-1\n", task_board.read_text(encoding="utf-8"))
        self.assertFalse((project / ".forgekit/docs/risk-register.md").exists())
        self.assertFalse((project / ".forgekit/docs/testing.md").exists())
        lock = load_json(project / ".forgekit/template-lock.json")
        self.assertEqual("0.46.0", lock["installed_version"])
        retired = {"README.md", ".forgekit/docs/loop-readiness.md", ".forgekit/docs/loop-blueprint.md", ".forgekit/docs/loop-operations.md"}
        self.assertTrue(retired.isdisjoint({item["target_path"] for item in lock["files"]}))
        after_first = tree_snapshot(project)
        second = self.apply(project)
        self.assertIn("No migration is required", second.stdout)
        self.assertEqual(after_first, tree_snapshot(project))

    def test_custom_unknown_and_custom_readme_are_preserved(self):
        temp_migrations = self.make_root("unknown-migrations")
        shutil.copytree(PACKAGE, temp_migrations / "0.46.0")
        package = temp_migrations / "0.46.0"
        project = self.make_project("custom-unknown", readme=b"user readme\r\n", package=package)
        custom = project / ".forgekit/docs/maker-checker-protocol.md"
        unknown = project / "governance/agent-entry-contract.md"
        custom.write_bytes(b"custom protocol\r\n")
        unknown.write_bytes(b"unknown local contract\n")
        (package / "baseline/governance/agent-entry-contract.md").unlink()
        self.apply(project, package_root=temp_migrations)
        self.assertEqual(b"custom protocol\r\n", custom.read_bytes())
        self.assertEqual(b"unknown local contract\n", unknown.read_bytes())
        self.assertEqual(b"user readme\r\n", (project / "README.md").read_bytes())
        report = load_json(project / ".forgekit/reports/upgrade-review-needed.json")
        by_target = {item["target_path"]: item for item in report["items"]}
        self.assertEqual("custom", by_target[".forgekit/docs/maker-checker-protocol.md"]["classification"])
        self.assertEqual("unknown-baseline", by_target["governance/agent-entry-contract.md"]["classification"])
        self.assertNotIn("README.md", {item["target_path"] for item in load_json(project / ".forgekit/template-lock.json")["files"]})

    def test_custom_removed_loop_is_preserved_even_with_replace_policy(self):
        project = self.make_project("custom-loop", readme=b"force-safe user README\n")
        custom = project / ".forgekit/docs/loop-operations.md"
        custom.write_bytes(b"custom legacy operations\n")
        self.apply(project, policy="replace-template")
        self.assertEqual(b"custom legacy operations\n", custom.read_bytes())
        self.assertEqual(b"force-safe user README\n", (project / "README.md").read_bytes())
        report = load_json(project / ".forgekit/reports/upgrade-review-needed.json")
        item = next(item for item in report["items"] if item["target_path"].endswith("loop-operations.md"))
        self.assertEqual("resolved_manual_merge", item["status"])
        self.assertTrue(item["preserve_only"])

    def test_absent_install_lock_remains_absent(self):
        project = self.make_project("no-lock")
        (project / ".forgekit/template-lock.json").unlink()
        self.apply(project)
        self.assertFalse((project / ".forgekit/template-lock.json").exists())
        self.assertEqual("0.46.0", load_json(project / ".forgekit/state.json")["forgekit_version"])

    def test_failure_rolls_back_exact_upgrade_start_state_including_lock_and_custom(self):
        project = self.make_project("rollback", readme=b"custom readme\n")
        custom = project / ".forgekit/docs/maker-checker-protocol.md"
        custom.write_bytes(b"custom before failure\r\n")
        before = tree_inventory(project)
        scripts_path = str(REPO / "scripts")
        sys.path.insert(0, scripts_path)
        self.addCleanup(lambda: sys.path.remove(scripts_path))
        spec = importlib.util.spec_from_file_location("stage_d_upgrader", REPO / "scripts/forgekit-upgrade.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        def fail_after_state(stage):
            if stage == "after_state_write":
                raise RuntimeError("injected mid-migration failure")

        with self.assertRaisesRegex(RuntimeError, "injected mid-migration failure"):
            module.command_apply(project, MIGRATION_ROOT, True, "manual-merge", "en-US", fail_after_state)
        self.assertEqual(before, tree_inventory(project))
        self.assertEqual(b"custom before failure\r\n", custom.read_bytes())
        self.assertEqual("0.45.0", load_json(project / ".forgekit/state.json")["forgekit_version"])
        self.assertEqual("0.45.0", load_json(project / ".forgekit/template-lock.json")["installed_version"])

    def test_legacy_stock_readme_is_advisory_and_byte_preserved(self):
        legacy = run(["git", "show", "v0.45.0:project-template/README.md"]).stdout.encode("utf-8")
        project = self.make_project("legacy-readme", readme=legacy)
        plan = run([
            sys.executable, "-B", REPO / "scripts/forgekit-upgrade.py", "plan",
            "--repo-root", project, "--migration-root", MIGRATION_ROOT,
        ])
        self.assertIn("README ownership is retired", plan.stdout)
        self.apply(project)
        self.assertEqual(legacy, (project / "README.md").read_bytes())


class TopologyAndCompatibilityTests(StageDTestCase):
    def test_fresh_layout_dry_runs_are_read_only(self):
        toolkit = self.make_toolkit()
        target = self.make_root("fresh") / "demo-workspace"
        in_place = run([sys.executable, "-B", toolkit / "scripts/forgekit-project.py", "--target", target, "--dry-run"])
        self.assertIn("Layout: in-place", in_place.stdout)
        self.assertIn(f"ProjectRoot: {target.resolve()}", in_place.stdout)
        self.assertIn("CurrentWriteScope: read-only", in_place.stdout)
        self.assertFalse(target.exists())
        nested = run([
            sys.executable, "-B", toolkit / "scripts/forgekit-project.py", "--target", target,
            "--dry-run", "--layout", "legacy-nested",
        ])
        self.assertIn("Layout: legacy-nested", nested.stdout)
        self.assertIn(f"ProjectRoot: {(target / 'demo').resolve()}", nested.stdout)
        self.assertFalse(target.exists())

    def test_fresh_v046_in_place_and_legacy_nested_apply(self):
        toolkit = self.make_toolkit()
        parent = self.make_root("fresh-apply")
        in_place = parent / "in-place"
        run([
            sys.executable, "-B", toolkit / "scripts/forgekit-project.py", "--target", in_place,
            "--yes", "--layout", "in-place",
        ])
        self.assertEqual("0.46.0", load_json(in_place / ".forgekit/state.json")["forgekit_version"])
        self.assertFalse((in_place / "README.md").exists())
        self.assertNotIn("README.md", {item["target_path"] for item in load_json(in_place / ".forgekit/template-lock.json")["files"]})
        governance = parent / "legacy-workspace"
        run([
            sys.executable, "-B", toolkit / "scripts/forgekit-project.py", "--target", governance,
            "--yes", "--layout", "legacy-nested",
        ])
        project_root = governance / "legacy"
        self.assertEqual("0.46.0", load_json(governance / ".forgekit/state.json")["forgekit_version"])
        self.assertTrue(project_root.is_dir())
        self.assertFalse((project_root / ".forgekit").exists())
        self.assertFalse((project_root / "README.md").exists())

    def test_outer_and_inner_upgrade_resolve_same_topology_and_yes_authorizes_write(self):
        toolkit = self.make_toolkit()
        outer = self.make_project("nested", project_root="app")
        inner = outer / "app"
        outer_plan = run([sys.executable, "-B", toolkit / "scripts/forgekit-project.py", "--target", outer, "--dry-run"])
        inner_plan = run([sys.executable, "-B", toolkit / "scripts/forgekit-project.py", "--target", inner, "--dry-run"])
        for marker in (f"GovernanceRoot: {outer.resolve()}", f"ProjectRoot: {inner.resolve()}", "CurrentWriteScope: read-only"):
            self.assertIn(marker, outer_plan.stdout)
            self.assertIn(marker, inner_plan.stdout)
        applied = run([
            sys.executable, "-B", toolkit / "scripts/forgekit-project.py", "--target", inner,
            "--yes", "--review-needed-policy", "manual-merge",
        ])
        self.assertIn("apply authorization granted by --yes", applied.stdout)
        self.assertEqual("0.46.0", load_json(outer / ".forgekit/state.json")["forgekit_version"])
        self.assertFalse((inner / ".forgekit").exists())
        current = run([sys.executable, "-B", toolkit / "scripts/forgekit-project.py", "--target", inner, "--dry-run"])
        self.assertIn("Installed ForgeKit version: 0.46.0", current.stdout)
        self.assertNotIn("VERSION MISMATCH", current.stdout)

    def test_ambiguous_exact_ancestors_block_without_write(self):
        toolkit = self.make_toolkit()
        outer = self.make_root("ambiguous")
        nested = outer / "nested"
        requested = nested / "project"
        requested.mkdir(parents=True)
        state = load_json(REPO / "project-template/.forgekit/state.json")
        state["forgekit_version"] = "0.45.0"
        for governance, project_root in ((outer, "nested/project"), (nested, "project")):
            (governance / ".forgekit").mkdir(parents=True, exist_ok=True)
            (governance / ".forgekit/state.json").write_text(json.dumps(state) + "\n", encoding="utf-8")
            self.write_boundary(governance, project_root)
        before = tree_snapshot(outer)
        result = run([
            sys.executable, "-B", toolkit / "scripts/forgekit-project.py", "--target", requested, "--yes",
        ], expected=(2,))
        self.assertIn("C4", result.stdout)
        self.assertIn("AMBIGUOUS", result.stdout)
        self.assertIn("No files were changed", result.stdout)
        self.assertEqual(before, tree_snapshot(outer))

    def test_post_upgrade_checker_machine_compatibility_and_legacy_guard(self):
        project = self.make_project("checkers")
        for name in ("task-board.md", "task-intake.md", "risk-register.md", "traceability.md", "testing.md"):
            target = project / ".forgekit/docs" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / "project-template/docs" / name, target)
        self.apply(project)
        current = run([
            sys.executable, "-B", project / "scripts/check-current-docs-integrity.py",
            "--repo-root", project, "--json",
        ], expected=(0, 1, 2))
        current_report = json.loads(current.stdout)
        for field in ("status", "active_tasks", "blocking_count", "warning_count", "findings"):
            self.assertIn(field, current_report)
        for finding in current_report["findings"]:
            for field in ("severity", "code", "message", "impact_severity", "blocking"):
                self.assertIn(field, finding)
        workspace = run([
            sys.executable, "-B", project / "scripts/check-workspace-integrity.py",
            "--repo-root", project, "--json",
        ], expected=(0, 1, 2))
        workspace_report = json.loads(workspace.stdout)
        for field in ("status", "summary", "blocking_count", "warning_count", "findings"):
            self.assertIn(field, workspace_report)
        self.assertEqual("not-enabled", workspace_report["status"])
        state = load_json(project / ".forgekit/state.json")
        state["features"]["multi_project_scoped_docs_enabled"] = True
        (project / ".forgekit/state.json").write_text(json.dumps(state) + "\n", encoding="utf-8")
        (project / ".forgekit/workspace-map.json").write_text("{invalid", encoding="utf-8")
        runtime = run([
            sys.executable, "-B", project / "scripts/check-workspace-integrity.py",
            "--repo-root", project, "--json",
        ], expected=(2,))
        runtime_report = json.loads(runtime.stdout)
        self.assertEqual("runtime-error", runtime_report["status"])
        self.assertIn("summary", runtime_report)
        checker_text = (project / "scripts/check-workspace-integrity.py").read_text(encoding="utf-8")
        self.assertIn('"path"', checker_text)
        self.assertIn('"loop-operations.md"', checker_text)


if __name__ == "__main__":
    unittest.main()
