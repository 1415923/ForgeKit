import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
import unicodedata
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


packets = load_module("upgrade_packets", REPO / "scripts/upgrade_review_packets.py")
sys.path.insert(0, str(REPO / "scripts"))
upgrader = load_module("forgekit_upgrade_for_tests", REPO / "scripts/forgekit-upgrade.py")


def make_directory_link(link, target):
    if os.name == "nt":
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True)
        if result.returncode != 0:
            raise OSError(result.stderr.decode(errors="replace") or result.stdout.decode(errors="replace"))
    else:
        link.symlink_to(target, target_is_directory=True)


class UpgradeReviewPacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="forgekit-upgrade-packets-")
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def packet_tree(self, root):
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*")
            if path.is_file()
        }

    def origin(self, path="governance/file.bin", data=b"A\r\n", version="0.44.1"):
        return {
            "managed_path": path,
            "source_version": version,
            "existed_before_upgrade": data is not None,
            "original_bytes": data,
            "original_sha256": hashlib.sha256(data).hexdigest() if data is not None else None,
        }

    def publish(self, *, incoming=b"B\n", origin=None, fault=None, callback=None, classification="stock", cleanup=None, warnings=None):
        origin = origin or self.origin()
        return packets.prepare_packet(
            self.root,
            target_version="0.45.0",
            managed_path=origin["managed_path"],
            source_version=origin["source_version"],
            classification=classification,
            baseline_sha256=None,
            local_bytes=origin["original_bytes"],
            incoming_bytes=incoming,
            resolution_status="rollback_ready",
            user_action="restore",
            origin_snapshot=origin,
            fault_injector=fault,
            on_publish=callback,
            old_cleanup=cleanup,
            warning_callback=warnings.append if warnings is not None else None,
        )

    def report_item(self, packet):
        item = {
            "key": "migration::action::governance/file.bin",
            "action_id": "action",
            "target_path": packet["managed_path"],
            "source_migration": "migration",
            "reason": "test",
            "impact": "test",
            "recommended_action": "test",
            "status": "resolved_replace_template",
            "expected_baseline_checksum": None,
            "actual_checksum": packet["rollback_sha256"],
            "incoming_template_checksum": packet["incoming_sha256"],
        }
        upgrader.attach_packet(item, packet)
        return item

    def test_packet_id_is_stable_and_case_preserving(self):
        path = "governance/CaseSensitive.md"
        expected = "0.45.0--" + hashlib.sha256(path.encode("utf-8")).hexdigest()[:16]
        self.assertEqual(expected, packets.packet_id("0.45.0", path))
        self.assertEqual(expected, packets.packet_id("0.45.0", path))

    def test_packet_path_rejects_escape_absolute_and_unsafe_version(self):
        for value in ("../escape", "/absolute", "C:/absolute", "a/./b", "a\\b"):
            with self.subTest(value=value), self.assertRaises(packets.PacketError):
                packets.packet_id("0.45.0", value)
        with self.assertRaises(packets.PacketError):
            packets.packet_id("0.45.0/unsafe", "governance/file.md")

    def test_portable_windows_and_unicode_path_policy(self):
        invalid_paths = [
            "CON",
            "governance/NUL.txt",
            "governance/COM1",
            "governance/trailing.",
            "governance/trailing ",
            "governance/a:b",
            "//server/share",
            "\\\\?\\C:\\device",
        ]
        for value in invalid_paths:
            with self.subTest(value=value), self.assertRaises(packets.PacketError):
                packets.normalize_managed_path(value)
        for version in ("", ".", "..", "0.45", "v0.45.0", "0.45.0.", "CON"):
            with self.subTest(version=version), self.assertRaises(packets.PacketError):
                packets.packet_id(version, "governance/file.md")
        unicode_path = "治理/规则.md"
        expected = "0.45.0--" + hashlib.sha256(unicode_path.encode("utf-8")).hexdigest()[:16]
        self.assertEqual(expected, packets.packet_id("0.45.0", unicode_path))

        decomposed = unicodedata.normalize("NFD", "é")
        composed = unicodedata.normalize("NFC", "é")
        if decomposed != composed:
            (self.root / decomposed).mkdir()
            with self.assertRaisesRegex(packets.PacketError, "Unicode normalization conflict"):
                packets.ensure_portable_path(self.root, f"{composed}/file.md")

    def test_missing_packet_does_not_fabricate_original_bytes(self):
        packet = packets.prepare_packet(
            self.root,
            target_version="0.45.0",
            managed_path="governance/missing.md",
            source_version="0.44.1",
            classification="missing",
            baseline_sha256=None,
            local_bytes=None,
            incoming_bytes=b"incoming\r\n",
            resolution_status="rollback_ready",
            user_action="delete created file",
        )
        self.assertFalse(packet["local_existed"])
        self.assertIsNone(packet["artifacts"]["local"])
        self.assertIsNone(packet["artifacts"]["rollback"])
        packet_root = self.root / ".forgekit/reports/review-needed" / packet["packet_id"]
        self.assertFalse((packet_root / "local/governance/missing.md").exists())
        self.assertFalse((packet_root / "rollback/governance/missing.md").exists())

    def test_packet_root_symlink_is_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        packet_root = self.root / ".forgekit/reports/review-needed"
        packet_root.parent.mkdir(parents=True)
        try:
            make_directory_link(packet_root, outside)
        except OSError as exc:
            self.skipTest(f"directory symlink is unavailable: {exc}")
        try:
            with self.assertRaises(packets.PacketError):
                packets.prepare_packet(
                    self.root,
                    target_version="0.45.0",
                    managed_path="governance/file.md",
                    source_version="0.44.1",
                    classification="missing",
                    baseline_sha256=None,
                    local_bytes=None,
                    incoming_bytes=b"incoming\n",
                    resolution_status="rollback_ready",
                    user_action="delete created file",
                )
        finally:
            packet_root.rmdir()

    def test_packet_failure_injection_preserves_old_packet_and_cleans_siblings(self):
        initial = self.publish(incoming=b"old-incoming\n")
        fixed = self.root / ".forgekit/reports/review-needed" / initial["packet_id"]
        before = self.packet_tree(fixed)
        stages = [
            "after_local",
            "after_incoming",
            "after_rollback",
            "after_diff",
            "before_packet_json",
            "after_old_rename",
            "after_publish",
        ]
        for stage in stages:
            def fail_at(actual, expected=stage):
                if actual == expected:
                    raise RuntimeError(f"fault:{expected}")
            with self.subTest(stage=stage), self.assertRaises(packets.PacketError):
                self.publish(incoming=f"new-{stage}\n".encode(), fault=fail_at)
            self.assertEqual(before, self.packet_tree(fixed))
            siblings = [path.name for path in fixed.parent.iterdir() if path.name.startswith((".tmp-", ".old-"))]
            self.assertEqual([], siblings)
            packets.validate_complete_packet(fixed)

    def test_packet_identity_conflict_never_overwrites_origin(self):
        packet = self.publish()
        fixed = self.root / ".forgekit/reports/review-needed" / packet["packet_id"]
        before = self.packet_tree(fixed)
        conflicting = self.origin(data=b"different-origin\n")
        with self.assertRaisesRegex(packets.PacketError, "packet identity conflict"):
            self.publish(incoming=b"C\n", origin=conflicting)
        self.assertEqual(before, self.packet_tree(fixed))

    def test_summary_failure_rolls_back_packet_and_both_summaries(self):
        packet = self.publish(incoming=b"old\n")
        fixed = self.root / ".forgekit/reports/review-needed" / packet["packet_id"]
        packet_before = self.packet_tree(fixed)
        reports = self.root / ".forgekit/reports"
        json_report = reports / "upgrade-review-needed.json"
        md_report = reports / "upgrade-review-needed.md"
        json_report.write_bytes(b"old-json\n")
        md_report.write_bytes(b"old-md\n")

        def callback(_packet):
            def report_fault(stage):
                if stage == "after_json_publish":
                    raise RuntimeError("summary fault")
            upgrader.write_review_reports(self.root, "0.45.0", [], fault_injector=report_fault)

        with self.assertRaises(packets.PacketError):
            self.publish(incoming=b"new\n", callback=callback)
        self.assertEqual(packet_before, self.packet_tree(fixed))
        self.assertEqual(b"old-json\n", json_report.read_bytes())
        self.assertEqual(b"old-md\n", md_report.read_bytes())
        self.assertFalse(any(path.name.startswith((".tmp-", ".old-")) for path in reports.rglob("*")))

    def test_old_cleanup_failure_keeps_committed_packet_and_summaries_consistent(self):
        old_packet = self.publish(incoming=b"custom-incoming\n", classification="custom")
        reports = self.root / ".forgekit/reports"
        fixed = reports / "review-needed" / old_packet["packet_id"]
        upgrader.write_review_reports(self.root, "0.45.0", [self.report_item(old_packet)])
        warnings = []

        def publish_summary(packet):
            upgrader.write_review_reports(self.root, "0.45.0", [self.report_item(packet)])

        def refuse_old_cleanup(path):
            if path.name.startswith(".old-"):
                raise PermissionError("simulated old packet cleanup denial")
            packets.shutil.rmtree(path)

        new_packet = self.publish(
            incoming=b"stock-incoming\n",
            classification="stock",
            callback=publish_summary,
            cleanup=refuse_old_cleanup,
            warnings=warnings,
        )
        canonical = packets.validate_complete_packet(fixed)
        self.assertEqual("stock", canonical["classification"])
        self.assertEqual(new_packet["incoming_sha256"], canonical["incoming_sha256"])
        report = json.loads((reports / "upgrade-review-needed.json").read_text(encoding="utf-8"))
        summary_item = report["items"][0]
        self.assertEqual(canonical["packet_id"], summary_item["packet_id"])
        self.assertEqual(canonical["classification"], summary_item["classification"])
        self.assertEqual(canonical["incoming_sha256"], summary_item["incoming_template_checksum"])
        self.assertEqual(canonical["rollback_sha256"], summary_item["rollback_checksum"])
        self.assertEqual(canonical["artifacts"], summary_item["packet_artifacts"])
        markdown = (reports / "upgrade-review-needed.md").read_text(encoding="utf-8")
        self.assertIn("- Classification: stock", markdown)
        self.assertIn(f"- Packet: review-needed/{canonical['packet_id']}", markdown)
        self.assertIn(f"- Incoming template checksum: {canonical['incoming_sha256']}", markdown)
        old_dirs = [path for path in fixed.parent.iterdir() if path.name.startswith(".old-")]
        self.assertEqual(1, len(old_dirs))
        self.assertEqual("custom", json.loads((old_dirs[0] / "packet.json").read_text(encoding="utf-8"))["classification"])
        self.assertEqual([fixed], packets.canonical_packet_directories(fixed.parent))
        self.assertTrue(any("committed" in warning and "cleanup pending" in warning for warning in warnings))

        retry = self.publish(incoming=b"stock-incoming\n", classification="stock", callback=publish_summary)
        self.assertEqual("stock", packets.validate_complete_packet(fixed)["classification"])
        self.assertEqual(new_packet["incoming_sha256"], retry["incoming_sha256"])
        self.assertFalse(any(path.name.startswith((".old-", ".tmp-")) for path in fixed.parent.iterdir()))
        self.assertFalse(any((self.root / name).exists() for name in ("rollback", "backup", "review")))

    def test_two_real_migrations_keep_upgrade_start_rollback(self):
        project = self.root / "chain-project"
        migration_root = self.root / "chain-migrations"
        (project / ".forgekit").mkdir(parents=True)
        state = {
            "schema_version": 1,
            "forgekit_version": "0.43.0",
            "managed_docs_root": ".forgekit/docs",
            "change_root": ".forgekit/changes",
            "mode": "standard",
            "features": {},
            "last_upgrade": None,
        }
        (project / ".forgekit/state.json").write_text(json.dumps(state), encoding="utf-8")
        target = project / "governance/shared.bin"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"A")
        for directory, from_version, to_version, baseline, incoming in (
            ("0.44.0", "0.43.0", "0.44.0", b"A", b"B"),
            ("0.45.0", "0.44.0", "0.45.0", b"B", b"C"),
        ):
            package = migration_root / directory
            (package / "baseline").mkdir(parents=True)
            (package / "files").mkdir()
            (package / "baseline/shared.bin").write_bytes(baseline)
            (package / "files/shared.bin").write_bytes(incoming)
            migration = {
                "id": f"chain-{directory}",
                "title": "same managed path chain",
                "from": from_version,
                "to": to_version,
                "risk": "high",
                "actions": [{
                    "id": f"write-{directory}",
                    "type": "replace_file_if_baseline_matches",
                    "safety": "safe",
                    "source": "files/shared.bin",
                    "baseline": "baseline/shared.bin",
                    "target": "governance/shared.bin",
                }],
                "manual_review": [],
                "non_goals": [],
            }
            (package / "migration.json").write_text(json.dumps(migration), encoding="utf-8")
        command = [
            sys.executable, "-B", str(REPO / "scripts/forgekit-upgrade.py"), "apply", "--safe",
            "--repo-root", str(project), "--migration-root", str(migration_root),
            "--review-needed-policy", "replace-template",
        ]
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(b"C", target.read_bytes())
        identity = packets.packet_id("0.45.0", "governance/shared.bin")
        packet_root = project / ".forgekit/reports/review-needed" / identity
        metadata = packets.validate_complete_packet(packet_root)
        rollback = packet_root / "rollback/governance/shared.bin"
        self.assertEqual(b"A", rollback.read_bytes())
        self.assertEqual(hashlib.sha256(b"A").hexdigest(), metadata["rollback_sha256"])
        before_retry = self.packet_tree(packet_root)
        retry = subprocess.run(command, text=True, capture_output=True, check=False)
        self.assertEqual(0, retry.returncode, retry.stdout + retry.stderr)
        self.assertEqual(before_retry, self.packet_tree(packet_root))
        target.write_bytes(rollback.read_bytes())
        self.assertEqual(b"A", target.read_bytes())

    def test_existing_upgrade_cli_preserves_custom_and_builds_all_packets(self):
        project = self.root / "project"
        migration_root = self.root / "migrations"
        package = migration_root / "0.45.0"
        (project / ".forgekit").mkdir(parents=True)
        state = {
            "schema_version": 1,
            "forgekit_version": "0.44.1",
            "managed_docs_root": ".forgekit/docs",
            "change_root": ".forgekit/changes",
            "mode": "standard",
            "features": {},
            "last_upgrade": None,
        }
        (project / ".forgekit/state.json").write_text(json.dumps(state), encoding="utf-8")
        originals = {
            "governance/stock.bin": b"stock-before\r\n\x00",
            "governance/custom.bin": b"custom-local\n",
            "governance/unknown.bin": b"unknown-local\n",
        }
        for relative, data in originals.items():
            path = project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        files = package / "files"
        baseline = package / "baseline"
        files.mkdir(parents=True)
        baseline.mkdir(parents=True)
        for name in ("stock", "custom", "missing", "unknown"):
            (files / f"{name}.bin").write_bytes(f"{name}-incoming\n".encode())
        (baseline / "stock.bin").write_bytes(originals["governance/stock.bin"])
        (baseline / "custom.bin").write_bytes(b"custom-stock\n")
        migration = {
            "id": "v045-stage-a-fixture",
            "title": "Stage A packet fixture",
            "from": "0.44.1",
            "to": "0.45.0",
            "risk": "high",
            "actions": [
                {"id": "stock", "type": "replace_file_if_baseline_matches", "safety": "safe", "source": "files/stock.bin", "baseline": "baseline/stock.bin", "target": "governance/stock.bin"},
                {"id": "custom", "type": "replace_file_if_baseline_matches", "safety": "safe", "source": "files/custom.bin", "baseline": "baseline/custom.bin", "target": "governance/custom.bin"},
                {"id": "missing", "type": "copy_file_if_missing", "safety": "safe", "source": "files/missing.bin", "target": "governance/missing.bin"},
                {"id": "unknown", "type": "replace_file_if_baseline_matches", "safety": "safe", "source": "files/unknown.bin", "baseline": "baseline/does-not-exist.bin", "target": "governance/unknown.bin"}
            ],
            "manual_review": [],
            "non_goals": [],
        }
        (package / "migration.json").write_text(json.dumps(migration), encoding="utf-8")
        command = [
            sys.executable,
            "-B",
            str(REPO / "scripts/forgekit-upgrade.py"),
            "apply",
            "--safe",
            "--repo-root",
            str(project),
            "--migration-root",
            str(migration_root),
            "--review-needed-policy",
            "manual-merge",
        ]
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(b"stock-incoming\n", (project / "governance/stock.bin").read_bytes())
        self.assertEqual(originals["governance/custom.bin"], (project / "governance/custom.bin").read_bytes())
        self.assertEqual(originals["governance/unknown.bin"], (project / "governance/unknown.bin").read_bytes())
        self.assertEqual(b"missing-incoming\n", (project / "governance/missing.bin").read_bytes())
        report_path = project / ".forgekit/reports/upgrade-review-needed.json"
        report_text = report_path.read_text(encoding="utf-8")
        report = json.loads(report_text)
        self.assertNotIn(str(project), report_text)
        self.assertEqual({"stock", "custom", "missing", "unknown-baseline"}, {item["classification"] for item in report["items"]})
        by_class = {item["classification"]: item for item in report["items"]}
        stock_packet = project / ".forgekit/reports" / by_class["stock"]["packet_artifacts"]["rollback"]
        self.assertEqual(originals["governance/stock.bin"], stock_packet.read_bytes())
        missing_packet = project / ".forgekit/reports/review-needed" / by_class["missing"]["packet_id"]
        self.assertFalse((missing_packet / "local/governance/missing.bin").exists())
        self.assertFalse((missing_packet / "rollback/governance/missing.bin").exists())
        for item in report["items"]:
            for artifact in item["packet_artifacts"].values():
                if artifact is not None:
                    self.assertFalse(Path(artifact).is_absolute())
                    self.assertTrue(artifact.startswith("review-needed/"))
        self.assertFalse((project / ".forgekit/rollback").exists())
        self.assertFalse((project / ".forgekit/backups").exists())


if __name__ == "__main__":
    unittest.main()
