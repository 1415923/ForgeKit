import importlib.util
import copy
import json
import os
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from structured_upgrade import (Conflict, apply_plan, build_plan, merge_text,
                                merge_markdown, merge_entry, sections, mark_sections,
                                digest, preserved_entry_candidate)


class MarkdownTests(unittest.TestCase):
    def test_nonoverlapping_edits(self):
        self.assertEqual(merge_text(b'a\nb\nc\n', b'A\nb\nc\n', b'a\nb\nC\n'), b'A\nb\nC\n')

    def test_overlapping_changes_conflict(self):
        with self.assertRaises(Conflict):
            merge_text(b'a\n', b'user\n', b'template\n')

    def test_bom_crlf_and_fenced_heading(self):
        text = '\ufeff# 文档\r\n## 事实\r\n```md\r\n## 不是章节\r\n```\r\n'.encode()
        self.assertEqual(len(sections(text)), 2)

    def test_stable_sections_reorder(self):
        base = mark_sections(b'# Doc\n## One\nx\n## Two\ny\n')
        local = base.replace(b'x\n', b'filled\n')
        incoming = mark_sections(b'# Doc\n## Two\ny\n## One\nx\n')
        result = merge_markdown(base, local, incoming)
        self.assertIn(b'filled', result)
        self.assertLess(result.index(b'## Two'), result.index(b'## One'))

    def test_entry_append_preserved_and_rule_edit_rejected(self):
        old = b'# Guide\n## Rules\nOld rule.\n'
        new = b'# New guide\n## Boundary\nNew rule.\n'
        result = merge_entry(old, old + b'\nUse our test server.\n', new)
        self.assertIn(b'Use our test server.', result)
        self.assertNotIn(b'Old rule.', result)
        with self.assertRaises(Conflict):
            merge_entry(old, old.replace(b'Old', b'Changed'), new)

    def test_entry_customization_survives_multiple_template_steps(self):
        old = b'# Old\n\n## Boundary\nRule A.\n'
        middle = b'# Middle\n\n## Boundary\nRule B.\n'
        latest = b'# Latest\n\n## Boundary\nRule C.\n'
        local = old + b'\nUse the team test command.\n'
        first = merge_entry(old, local, middle)
        second = merge_entry(middle, first, latest)
        self.assertEqual(1, second.count(b'Use the team test command.'))
        self.assertEqual(1, second.count(b'forgekit:origin'))
        self.assertEqual(1, second.count(b'forgekit:user begin'))
        self.assertIn(b'Rule C.', second)
        self.assertNotIn(b'Rule B.', second)

    def test_existing_legacy_origin_and_new_insertion_keep_distinct_provenance(self):
        base = b'# Middle\n\n## Rules\nRule.\n'
        local = base + b'\n<!-- forgekit:user begin -->\n<!-- forgekit:origin legacy-entry -->\nExisting convention.\n<!-- forgekit:user end -->\n'
        latest = b'# New\n\n## Rules\nNew rule.\n'
        result = merge_entry(base, local, latest)
        self.assertEqual(1, result.count(b'forgekit:origin'))
        local = local.replace(b'## Rules\n', b'## Rules\nAdditional convention.\n')
        result = merge_entry(base, local, latest)
        self.assertEqual(2, result.count(b'forgekit:origin'))
        self.assertIn(b'Existing convention.', result)
        self.assertIn(b'Additional convention.', result)


class EntryResolutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        (self.root / '.forgekit').mkdir(parents=True)
        self.state = {'forgekit_version': '0.46.0'}
        (self.root / '.forgekit/state.json').write_text(json.dumps(self.state))
        self.package = Path(self.temp.name) / 'package'
        self.package.mkdir()
        self.local = '# 项目入口\r\n## 边界\r\n禁止生产部署。\r\n'.encode()
        self.incoming = b'# New entry\n## Rules\nRespect project boundaries.\n'
        (self.root / 'AGENTS.md').write_bytes(self.local)
        (self.package / 'old').write_bytes(b'# Old entry\nOld rules.\n')
        (self.package / 'new').write_bytes(self.incoming)
        self.migration = {'id': 'v047', 'from': '0.46.0', 'to': '0.47.0', '_path': self.package / 'migration.json',
                          'actions': [{'type': 'merge_entry', 'target': 'AGENTS.md', 'baseline': 'old', 'source': 'new'}]}
        self.candidate = preserved_entry_candidate(self.local, self.incoming)
        self.packet = {'schema_version': 1, 'project_root': str(self.root.resolve()), 'from_version': '0.46.0',
                       'entries': [{'target': 'AGENTS.md', 'migration_id': 'v047', 'local_sha256': digest(self.local),
                                    'incoming_sha256': digest(self.incoming), 'resolved_sha256': digest(self.candidate),
                                    'resolved_text': self.candidate.decode()}]}
        self.path = Path(self.temp.name) / 'resolution.json'
        self.save(self.packet)

    def save(self, packet):
        self.path.write_text(json.dumps(packet, ensure_ascii=False), encoding='utf-8')

    def plan(self, path=None):
        return build_plan(self.root, self.state, [self.migration], path)

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    def test_default_blocks_but_explicit_candidate_applies(self):
        before = self.snapshot()
        self.assertTrue(self.plan()['public']['conflicts'])
        plan = self.plan(self.path)
        self.assertFalse(plan['public']['conflicts'])
        self.assertEqual(before, self.snapshot())
        result = apply_plan(self.root, plan, plan['public']['plan_hash'])
        self.assertEqual(self.candidate, (self.root / 'AGENTS.md').read_bytes())
        self.assertIn('禁止生产部署。'.encode(), self.candidate)
        self.assertEqual(digest(self.path.read_bytes()), result['entry_resolution']['packet_sha256'])

    def test_rejects_wrong_bindings_targets_and_edited_candidate(self):
        variants = []
        for field, value in [('project_root', str(self.package)), ('from_version', '0.45.0'), ('entries', [])]:
            packet = copy.deepcopy(self.packet)
            packet[field] = value
            variants.append(packet)
        for field, value in [('target', 'governance/rules.md'), ('migration_id', 'different'),
                             ('local_sha256', '0' * 64), ('incoming_sha256', '0' * 64),
                             ('resolved_sha256', '0' * 64), ('resolved_text', '# Lost project rules')]:
            packet = copy.deepcopy(self.packet)
            packet['entries'][0][field] = value
            variants.append(packet)
        edited = copy.deepcopy(self.packet)
        edited['entries'][0].update(resolved_text=self.incoming.decode(), resolved_sha256=digest(self.incoming))
        variants.append(edited)
        duplicate = copy.deepcopy(self.packet)
        duplicate['entries'].append(copy.deepcopy(duplicate['entries'][0]))
        variants.append(duplicate)
        for packet in variants:
            with self.subTest(packet=packet):
                before = self.snapshot()
                self.save(packet)
                with self.assertRaises(Conflict):
                    apply_plan(self.root, self.plan(self.path))
                self.assertEqual(before, self.snapshot())

    def test_changed_packet_and_project_after_plan_are_rejected(self):
        plan = self.plan(self.path)
        before = self.snapshot()
        self.path.write_bytes(self.path.read_bytes() + b'\n')
        with self.assertRaises(Conflict):
            apply_plan(self.root, plan)
        with self.assertRaises(Conflict):
            apply_plan(self.root, self.plan(self.path), plan['public']['plan_hash'])
        self.assertEqual(before, self.snapshot())
        self.save(self.packet)
        (self.root / 'AGENTS.md').write_bytes(self.local + b'New rule.\n')
        before = self.snapshot()
        with self.assertRaises(Conflict):
            apply_plan(self.root, plan)
        self.assertEqual(before, self.snapshot())

    def test_later_rewrite_of_reviewed_candidate_blocks(self):
        local = b'# Custom\nUse `.forgekit/docs/old.md`.\n'
        (self.root / 'AGENTS.md').write_bytes(local)
        candidate = preserved_entry_candidate(local, self.incoming)
        self.packet['entries'][0].update(local_sha256=digest(local), resolved_text=candidate.decode(), resolved_sha256=digest(candidate))
        self.save(self.packet)
        self.migration['reference_paths'] = ['AGENTS.md']
        self.migration['actions'].append({'type': 'relocate_markdown', 'target': '.forgekit/docs/old.md',
                                         'destinations': {'*': '.forgekit/docs/new.md'}})
        before = self.snapshot()
        with self.assertRaises(Conflict):
            apply_plan(self.root, self.plan(self.path))
        self.assertEqual(before, self.snapshot())

    def test_nested_user_region_rejected(self):
        with self.assertRaises(Conflict):
            preserved_entry_candidate(self.candidate, self.incoming)


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        self.root.mkdir()
        self.package = Path(self.temp.name) / 'package'
        self.package.mkdir()
        self.state = {'schema_version': 1, 'forgekit_version': '0.46.0', 'features': {}}
        self.put('.forgekit/state.json', json.dumps(self.state).encode())
        self.put('.forgekit/docs/old.md', b'# Facts\n## Command\npytest -q\n')
        self.put('.forgekit/docs/new.md', b'# Validation\n')
        (self.package / 'old').write_bytes(b'# Facts\n## Command\nTODO\n')
        self.migration = {'id': 'v047', 'to': '0.47.0', '_path': self.package / 'migration.json',
                          'actions': [{'id': 'move', 'type': 'relocate_markdown', 'target': '.forgekit/docs/old.md',
                                       'baseline': 'old', 'destinations': {'*': '.forgekit/docs/new.md'}}]}

    def put(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    def plan(self):
        return build_plan(self.root, self.state, [self.migration])

    def test_plan_readonly_relocation_and_apply(self):
        before = self.snapshot()
        plan = self.plan()
        self.assertEqual(before, self.snapshot())
        result = apply_plan(self.root, plan, plan['public']['plan_hash'])
        self.assertEqual(result['status'], 'applied')
        self.assertFalse((self.root / '.forgekit/docs/old.md').exists())
        self.assertIn('pytest -q', (self.root / '.forgekit/docs/new.md').read_text())
        self.assertEqual(json.loads((self.root / '.forgekit/state.json').read_text())['forgekit_version'], '0.47.0')

    def test_all_writes_roll_back(self):
        before = self.snapshot()
        def fail(stage):
            if stage == 'after_state_write':
                raise OSError('injected')
        with self.assertRaises(OSError):
            apply_plan(self.root, self.plan(), fault=fail)
        self.assertEqual(before, self.snapshot())

    def test_changed_input_and_plan_hash_stop_before_writes(self):
        plan = self.plan()
        self.put('.forgekit/docs/old.md', b'changed')
        before = self.snapshot()
        with self.assertRaises(Conflict):
            apply_plan(self.root, plan)
        self.assertEqual(before, self.snapshot())
        with self.assertRaises(Conflict):
            apply_plan(self.root, self.plan(), 'stale-hash')
        self.assertEqual(before, self.snapshot())

    def test_conflicts_no_writes(self):
        self.put('.forgekit/docs/old.md', b'## duplicate\none\n## duplicate\ntwo\n')
        before = self.snapshot()
        plan = self.plan()
        self.assertTrue(plan['public']['conflicts'])
        with self.assertRaises(Conflict):
            apply_plan(self.root, plan)
        self.assertEqual(before, self.snapshot())

    def test_unsafe_target(self):
        self.migration['actions'][0]['target'] = '.forgekit/../../outside'
        self.assertTrue(self.plan()['public']['conflicts'])

    def test_hardlink_is_rejected_without_touching_external_file(self):
        outside = Path(self.temp.name) / 'external'
        outside.write_bytes(b'private original')
        victim = self.root / '.forgekit/docs/old.md'
        victim.unlink()
        os.link(outside, victim)
        plan = self.plan()
        self.assertTrue(plan['public']['conflicts'])
        self.assertEqual(b'private original', outside.read_bytes())

    def test_backup_exists_before_first_project_write(self):
        def inspect(stage):
            if stage == 'after_write:.forgekit/docs/new.md':
                backups = list(self.root.glob('.forgekit/reports/upgrades/*/rollback.json'))
                self.assertEqual(1, len(backups))
                self.assertIn('.forgekit/docs/new.md', json.loads(backups[0].read_text())['files'])
        result = apply_plan(self.root, self.plan(), fault=inspect)
        self.assertEqual('applied', json.loads((self.root / result['report']).read_text())['status'])

    def test_one_failed_restore_does_not_abort_other_restores(self):
        before = self.snapshot()
        write = Path.write_bytes
        def fail_restore(path, data):
            if path.name == 'old.md':
                raise PermissionError('injected restore failure')
            return write(path, data)
        def fail(stage):
            if stage == 'after_state_write':
                raise OSError('injected transaction failure')
        with mock.patch.object(Path, 'write_bytes', fail_restore):
            with self.assertRaisesRegex(Conflict, 'rollback incomplete'):
                apply_plan(self.root, self.plan(), fault=fail)
        self.assertEqual(before['.forgekit/state.json'], (self.root / '.forgekit/state.json').read_bytes())
        self.assertEqual(before['.forgekit/docs/new.md'], (self.root / '.forgekit/docs/new.md').read_bytes())
        self.assertEqual(1, len(list(self.root.glob('.forgekit/reports/upgrades/*/rollback.json'))))

    def test_list_and_wildcard_predecessors(self):
        for value in (['0.45.0', '0.46.0'], '*'):
            self.migration['from'] = value
            self.assertFalse(self.plan()['public']['conflicts'])


if __name__ == '__main__':
    unittest.main()
