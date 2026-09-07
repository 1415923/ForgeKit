import importlib.util
import json
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from structured_upgrade import build_plan, apply_plan, Conflict, digest, preserved_entry_candidate, payload

spec = importlib.util.spec_from_file_location('v047_upgrade', ROOT / 'scripts/forgekit-upgrade.py')
upgrade = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upgrade)


class ReleaseMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='forgekit-v047-', dir='D:/tmp' if os.name == 'nt' else None)
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / 'project'
        shutil.copytree(ROOT / 'migrations/0.47.0/baseline', self.project)
        self.state = json.loads((ROOT / 'project-template/.forgekit/state.json').read_text(encoding='utf-8'))
        self.state.update(forgekit_version='0.46.0', last_upgrade=None)
        self.write('.forgekit/state.json', json.dumps(self.state))
        boundary = (self.project / '.forgekit/project-boundary.yml').read_text(encoding='utf-8').replace('<path-to-forgekit>', ROOT.as_posix())
        self.write('.forgekit/project-boundary.yml', boundary)
        self.write('README.md', 'user-owned business README\n')
        self.pending, _ = upgrade.pending_migrations((0, 46, 0), upgrade.load_migrations(ROOT / 'migrations'))

    def write(self, path, text):
        p = self.project / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text.encode())

    def snapshot(self):
        return {p.relative_to(self.project).as_posix(): p.read_bytes() for p in self.project.rglob('*') if p.is_file()}

    def plan(self):
        plan = build_plan(self.project, self.state, self.pending)
        self.assertFalse(plan['public']['conflicts'], json.dumps(plan['public']['conflicts'], ensure_ascii=False, indent=2))
        return plan

    def test_stock_upgrade_and_idempotent_cli(self):
        before_readme = (self.project / 'README.md').read_bytes()
        result = apply_plan(self.project, self.plan())
        self.assertEqual('applied', result['status'])
        self.assertEqual(before_readme, (self.project / 'README.md').read_bytes())
        self.assertFalse((self.project / '.codex/rules.md').exists())
        self.assertTrue((self.project / '.agents/skills/project-assessment/SKILL.md').is_file())
        before = self.snapshot()
        state, _ = upgrade.state_status(self.project)
        pending, _ = upgrade.pending_migrations(upgrade.parse_version(state['forgekit_version']), upgrade.load_migrations(ROOT / 'migrations'))
        self.assertEqual([], pending)
        self.assertEqual(before, self.snapshot())

    def test_customized_agents_facts_and_retired_documents(self):
        p = self.project / 'AGENTS.md'
        p.write_bytes(p.read_bytes() + b'\n## Team conventions\nUse fixture database only.\n')
        p = self.project / '.forgekit/docs/local-toolchain.md'
        p.write_bytes(p.read_bytes() + '\n## 项目命令\npython -m pytest tests/unit\n'.encode())
        p = self.project / '.forgekit/docs/requirements.md'
        p.write_bytes(p.read_bytes().replace('待补充'.encode(), '保留用户确认需求'.encode(), 1))
        p = self.project / '.codex/scope.md'
        p.write_bytes(p.read_bytes().replace('- 版本号：待补充'.encode(), '- 版本号：2.3.1'.encode()))
        result = apply_plan(self.project, self.plan())
        self.assertEqual('applied', result['status'])
        self.assertIn(b'Use fixture database only.', (self.project / 'AGENTS.md').read_bytes())
        self.assertIn(b'python -m pytest tests/unit', (self.project / '.forgekit/docs/testing.md').read_bytes())
        self.assertIn('保留用户确认需求', (self.project / '.forgekit/docs/requirements.md').read_text(encoding='utf-8'))
        self.assertIn('2.3.1', (self.project / '.forgekit/docs/project-plan.md').read_text(encoding='utf-8'))

    def test_custom_rule_conflict_keeps_entire_project(self):
        p = self.project / 'AGENTS.md'
        p.write_bytes(p.read_bytes().replace(b'Local writes are limited to the authorized scope.', b'Local writes can change any project.'))
        before = self.snapshot()
        plan = build_plan(self.project, self.state, self.pending)
        self.assertTrue(plan['public']['conflicts'])
        with self.assertRaises(Conflict):
            apply_plan(self.project, plan)
        self.assertEqual(before, self.snapshot())

    def test_rewritten_fact_document_keeps_its_own_headings(self):
        text = '# 接口事实\n\n当前只有 CLI，没有 HTTP API。\n\n## 实际命令\nrun --offline\n'
        self.write('.forgekit/docs/api.md', text)
        plan = self.plan()
        self.assertIn('.forgekit/docs/api.md', plan['public']['preserved_documents'])
        apply_plan(self.project, plan)
        self.assertEqual(text.encode(), (self.project / '.forgekit/docs/api.md').read_bytes())

    def test_fact_policy_cannot_be_applied_to_governance_owner(self):
        import copy
        pending = copy.deepcopy(self.pending)
        action = next(a for a in pending[0]['actions'] if a['target'] == '.forgekit/docs/maker-checker-protocol.md')
        action['content_policy'] = 'project_facts'
        self.write(action['target'], '# Replaced gate\nNo independent review needed.\n')
        before = self.snapshot()
        plan = build_plan(self.project, self.state, pending)
        self.assertTrue(plan['public']['conflicts'])
        with self.assertRaises(Conflict):
            apply_plan(self.project, plan)
        self.assertEqual(before, self.snapshot())

    def test_historical_checkout_newlines_and_migration_payloads(self):
        import base64
        import zlib
        self.from_v045()
        catalog = json.loads((ROOT / 'migrations/0.47.0/legacy-baselines.json').read_text(encoding='utf-8'))
        rules = zlib.decompress(base64.b64decode(catalog['blobs'][catalog['versions']['0.36.0']['.codex/rules.md']]))
        normalized = rules.decode('utf-8-sig').replace('\r\n', '\n').encode()
        (self.project / '.codex/rules.md').write_bytes(b'\xef\xbb\xbf' + normalized.replace(b'\n', b'\r\n'))
        path = 'scripts/forgekit-upgrade.py'
        tag_ids = {v[path] for v in catalog['versions'].values() if path in v}
        payload_id = next(h for h in catalog['artifacts'][path] if h not in tag_ids)
        (self.project / path).write_bytes(zlib.decompress(base64.b64decode(catalog['blobs'][payload_id])))
        apply_plan(self.project, self.plan())
        self.assertFalse((self.project / '.codex/rules.md').exists())

    def test_chinese_conflict_pipe_with_cp936_parent(self):
        self.write('AGENTS.md', '# User guide\n## 中文规则\nChanged mandatory rules.\n')
        before = self.snapshot()
        env = dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING='cp936')
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/forgekit-project.py'), '--target', str(self.project), '--lang', 'zh-CN', '--dry-run'], env=env, cwd=ROOT, capture_output=True)
        text = result.stdout.decode('cp936')
        self.assertEqual(2, result.returncode, text + result.stderr.decode('cp936'))
        self.assertIn('升级未执行', text)
        self.assertNotIn('\ufffd', text)
        self.assertNotIn('计划写入', text)
        self.assertEqual(before, self.snapshot())

    def test_entry_command_upgrades_without_manual_snippet(self):
        env = dict(os.environ, PYTHONUTF8='1')
        command = [sys.executable, str(ROOT / 'scripts/forgekit-project.py'), '--target', str(self.project), '--yes', '--lang', 'en-US']
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('no manual snippet', result.stdout)
        self.assertIn('Migration chain: 0.46.0 -> 0.47.0', result.stdout)

    def test_entry_command_previews_and_applies_reviewed_full_rewrite(self):
        self.write('AGENTS.md', '# Project entry\n\n## Production boundary\nNever deploy without explicit authorization.\n')
        local = (self.project / 'AGENTS.md').read_bytes()
        migration = self.pending[-1]
        action = next(a for a in migration['actions'] if a.get('target') == 'AGENTS.md')
        incoming = payload(migration, action['source'])
        candidate = preserved_entry_candidate(local, incoming)
        packet = {'schema_version': 1, 'project_root': str(self.project.resolve()), 'from_version': '0.46.0',
                  'entries': [{'target': 'AGENTS.md', 'migration_id': migration['id'], 'local_sha256': digest(local),
                               'incoming_sha256': digest(incoming), 'resolved_sha256': digest(candidate),
                               'resolved_text': candidate.decode()}]}
        path = Path(self.temp.name) / 'resolution.json'
        path.write_text(json.dumps(packet), encoding='utf-8')
        command = [sys.executable, '-X', 'utf8', str(ROOT / 'scripts/forgekit-project.py'), '--target', str(self.project),
                   '--entry-resolutions', str(path), '--lang', 'zh-CN']
        before = self.snapshot()
        result = subprocess.run(command + ['--dry-run'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn('显式保留入口', result.stdout)
        self.assertEqual(before, self.snapshot())
        result = subprocess.run(command + ['--yes'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(candidate, (self.project / 'AGENTS.md').read_bytes())
        self.assertEqual('0.47.0', json.loads((self.project / '.forgekit/state.json').read_bytes())['forgekit_version'])

    def test_entry_resolution_errors_are_visible_in_unified_entry(self):
        path = Path(self.temp.name) / 'bad-resolution.json'
        path.write_text('{"schema_version": 1, "project_root": "elsewhere"}')
        before = self.snapshot()
        result = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'scripts/forgekit-project.py'), '--target', str(self.project),
                                 '--entry-resolutions', str(path), '--yes', '--lang', 'zh-CN'], cwd=ROOT,
                                capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn('different project', result.stdout)
        self.assertEqual(before, self.snapshot())

    def from_v045(self):
        self.project = Path(self.temp.name) / 'project-v045'
        archive = subprocess.run(['git', 'archive', '--format=zip', 'v0.45.0', 'project-template'], cwd=ROOT, capture_output=True, check=True)
        with zipfile.ZipFile(io.BytesIO(archive.stdout)) as files:
            for name in files.namelist():
                if name.endswith('/'):
                    continue
                relative = name[len('project-template/'):]
                if relative.startswith(('docs/', 'changes/')):
                    relative = '.forgekit/' + relative
                path = self.project / relative
                self.assertTrue(path.resolve().is_relative_to(self.project.resolve()))
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(files.read(name))
        self.state['forgekit_version'] = '0.45.0'
        self.write('.forgekit/state.json', json.dumps(self.state))
        self.pending, _ = upgrade.pending_migrations((0, 45, 0), upgrade.load_migrations(ROOT / 'migrations'))

    def test_chain_custom_rules_do_not_reintroduce_retired_template(self):
        self.from_v045()
        p = self.project / '.codex/rules.md'
        p.write_bytes(p.read_bytes() + b'\nUse fixture database only.\n')
        apply_plan(self.project, self.plan())
        result = (self.project / 'AGENTS.md').read_bytes()
        self.assertIn(b'Use fixture database only.', result)
        self.assertLess(len(result), 5000)

    def test_chain_user_section_is_preserved_without_nested_region(self):
        self.from_v045()
        p = self.project / '.codex/rules.md'
        p.write_bytes(p.read_bytes() + b'\n## Team convention\nUse fixture database only.\n')
        apply_plan(self.project, self.plan())
        result = (self.project / 'AGENTS.md').read_bytes()
        self.assertIn(b'Use fixture database only.', result)
        self.assertEqual(1, result.count(b'<!-- forgekit:user begin -->'))
        self.assertLess(len(result), 5000)

    def test_rule_inserted_inside_existing_section_is_preserved(self):
        p = self.project / '.codex/rules.md'
        lines = p.read_bytes().splitlines(keepends=True)
        offset = next(i for i, line in enumerate(lines) if line.startswith(b'## ')) + 1
        lines.insert(offset, b'\nUse fixture database only.\n')
        p.write_bytes(b''.join(lines))
        apply_plan(self.project, self.plan())
        result = (self.project / 'AGENTS.md').read_bytes()
        self.assertIn(b'Use fixture database only.', result)
        self.assertLess(len(result), 5000)

    def test_previously_upgraded_v046_keeps_per_file_ancestry(self):
        self.from_v045()
        migration = next(m for m in self.pending if m['to'] == '0.46.0')
        for action in migration['actions']:
            if not action.get('target'):
                continue
            path = self.project / action['target']
            if action['type'] == 'remove_file_if_baseline_matches':
                path.unlink(missing_ok=True)
            elif action.get('source'):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((migration['_path'].parent / action['source']).read_bytes())
        self.state['forgekit_version'] = '0.46.0'
        self.write('.forgekit/state.json', json.dumps(self.state))
        self.pending = [m for m in self.pending if m['to'] == '0.47.0']
        apply_plan(self.project, self.plan())
        self.assertEqual('0.47.0', json.loads((self.project / '.forgekit/state.json').read_text())['forgekit_version'])

    def test_old_links_are_retargeted_and_fenced_commands_preserved(self):
        p = self.project / '.forgekit/docs/local-toolchain.md'
        p.write_bytes(p.read_bytes() + b'\n## Team instructions\nSee [commands](local-toolchain.md) and `.forgekit/docs/context-continuity.md`.\n```sh\necho local-toolchain.md\n```\n')
        apply_plan(self.project, self.plan())
        result = (self.project / '.forgekit/docs/testing.md').read_bytes()
        self.assertIn(b'[commands](testing.md)', result)
        self.assertIn(b'`.forgekit/docs/work-session-checkpoint.md`', result)
        self.assertIn(b'echo local-toolchain.md', result)

    def test_custom_roots_chain_and_legacy_readme_lock_retirement(self):
        self.from_v045()
        boundary_path = self.project / '.forgekit/project-boundary.yml'
        boundary = boundary_path.read_text(encoding='utf-8').replace('.forgekit/docs', '.forgekit/custom-docs').replace('.forgekit/changes', '.forgekit/custom-changes')
        boundary_path.write_text(boundary, encoding='utf-8')
        for old, new in [('docs', 'custom-docs'), ('changes', 'custom-changes')]:
            (self.project / '.forgekit' / old).rename(self.project / '.forgekit' / new)
        self.write('.forgekit/template-lock.json', json.dumps({'schema_version': 1, 'files': [{'target_path': 'README.md'}]}))
        result = apply_plan(self.project, self.plan())
        self.assertFalse((self.project / '.forgekit/changes').exists())
        self.assertFalse((self.project / '.forgekit/docs').exists())
        lock = json.loads((self.project / '.forgekit/template-lock.json').read_text())
        self.assertFalse(any(e['target_path'] == 'README.md' for e in lock['files']))
        self.assertIn('.forgekit/custom-changes/_template/review.md', [a['target'] for a in result['actions']])

    def test_active_task_with_missing_source_blocks_all_writes(self):
        self.write('.forgekit/docs/task-board.md', '# Tasks\n| ID | Title | Status | Source |\n| --- | --- | --- | --- |\n| TASK-123 | Work | In Progress | SRC-123 |\n')
        before = self.snapshot()
        plan = build_plan(self.project, self.state, self.pending)
        self.assertTrue(plan['public']['conflicts'])
        with self.assertRaises(Conflict):
            apply_plan(self.project, plan)
        self.assertEqual(before, self.snapshot())

    def test_stock_historical_tag_chain(self):
        for version in ('0.36.0', '0.43.0', '0.43.1', '0.43.2', '0.44.0'):
            with self.subTest(version=version):
                archive = subprocess.run(['git', 'archive', '--format=zip', 'v' + version, 'project-template'], cwd=ROOT, capture_output=True, check=True)
                project = Path(self.temp.name) / version
                project.mkdir()
                with zipfile.ZipFile(io.BytesIO(archive.stdout)) as files:
                    for name in files.namelist():
                        if name.endswith('/'):
                            continue
                        relative = name[len('project-template/'):]
                        if relative == 'README.md':
                            continue
                        if relative.startswith(('docs/', 'changes/')):
                            relative = '.forgekit/' + relative
                        target = project / relative
                        self.assertTrue(target.resolve().is_relative_to(project.resolve()))
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(files.read(name))
                state_path = project / '.forgekit/state.json'
                state = json.loads(state_path.read_text(encoding='utf-8-sig'))
                state['forgekit_version'] = version
                state_path.write_text(json.dumps(state), encoding='utf-8')
                for name in ('AGENTS.md', 'CLAUDE.md'):
                    path = project / name
                    path.write_bytes(path.read_bytes() + b'\nUse the project fixture test command.\n')
                pending, target = upgrade.pending_migrations(upgrade.parse_version(version), upgrade.load_migrations(ROOT / 'migrations'))
                self.assertEqual((0, 47, 0), target)
                plan = build_plan(project, state, pending)
                self.assertFalse(plan['public']['conflicts'], json.dumps(plan['public']['conflicts'], ensure_ascii=False, indent=2))
                if version == '0.43.2':
                    self.assertEqual(['0.43.2', '0.44.0', '0.44.1', '0.45.0', '0.46.0', '0.47.0'], plan['public']['version_chain'])
                apply_plan(project, plan)
                self.assertEqual('0.47.0', json.loads(state_path.read_text())['forgekit_version'])
                for name in ('AGENTS.md', 'CLAUDE.md'):
                    result = (project / name).read_bytes()
                    self.assertEqual(1, result.count(b'Use the project fixture test command.'))


if __name__ == '__main__':
    unittest.main()
