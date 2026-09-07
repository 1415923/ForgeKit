"""Current release mutation tests; these never substitute an old release fixture."""
import importlib.util
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('current_contract', ROOT / 'scripts/validate-v047.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class CurrentContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='forgekit-v047-contract-', dir='D:/tmp' if os.name == 'nt' else None)
        cls.addClassCleanup(cls.temp.cleanup)
        cls.repo = Path(cls.temp.name) / 'repo'
        cls.repo.mkdir()
        for name in ('config', 'scripts', 'skills', 'project-template', 'migrations', '.codex-plugin', '.claude-plugin', '.agents'):
            shutil.copytree(ROOT / name, cls.repo / name, ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('VERSION', '.gitattributes'):
            shutil.copyfile(ROOT / name, cls.repo / name)

    def mutate(self, relative, transform, expected):
        path = self.repo / relative
        original = path.read_bytes()
        try:
            changed = transform(original)
            self.assertNotEqual(original, changed, 'Mutation must change the fixture')
            path.write_bytes(changed)
            self.assertTrue(any(expected in error for error in validator.validate(self.repo)), expected)
        finally:
            path.write_bytes(original)

    def test_current_release_passes(self):
        self.assertEqual([], validator.validate(self.repo))

    def test_alias_cannot_be_implicitly_invoked(self):
        self.mutate('skills/handover-review/agents/openai.yaml', lambda b: b.replace(b'false', b'true'), 'Explicit-only policy')

    def test_current_entry_cannot_authorize_review_writes(self):
        self.mutate('project-template/AGENTS.md', lambda b: b + b'\nAudits automatically modify files.\n', 'contradiction')

    def test_current_entry_cannot_lose_canonical_route(self):
        self.mutate('project-template/CLAUDE.md', lambda b: b.replace(b'project-assessment', b'unknown-capability'), 'Missing canonical route')

    def test_incoming_payload_drift_is_rejected(self):
        self.mutate('migrations/0.47.0/files/AGENTS.md', lambda b: b + b'\ndrift\n', 'Incoming payload drift')

    def test_version_drift_is_rejected(self):
        self.mutate('.codex-plugin/plugin.json', lambda b: b.replace(b'0.47.0', b'0.46.0'), 'Public version drift')

    def test_missing_lf_contract_is_rejected(self):
        self.mutate('.gitattributes', lambda b: b.replace(b'*.md text eol=lf', b'# missing'), 'checkout-contract')

    def test_missing_reference_is_rejected(self):
        self.mutate('skills/project-assessment/SKILL.md', lambda b: b.replace(b'references/takeover.md', b'references/missing.md'), 'Broken Skill reference')


if __name__ == '__main__':
    unittest.main()
