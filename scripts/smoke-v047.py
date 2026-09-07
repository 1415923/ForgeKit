"""Initialize the current template and run checks in an isolated generated project."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def run(command, cwd):
    result = subprocess.run(command, cwd=cwd, env=dict(os.environ, PYTHONUTF8='1'), capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode:
        raise RuntimeError(' '.join(map(str, command)) + '\n' + result.stdout + result.stderr)
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    repo = Path(args.repo_root).resolve()
    with tempfile.TemporaryDirectory(prefix='forgekit-v047-smoke-', dir='D:/tmp' if os.name == 'nt' else None) as temp:
        target = Path(temp) / 'project'
        target.mkdir()
        readme = target / 'README.md'
        readme.write_bytes(b'# Business README\nOwned by the project.\n')
        original = readme.read_bytes()
        command = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(repo / 'scripts/init-project-template.ps1'), '-TargetPath', str(target), '-ProjectName', 'v047-smoke', '-Mode', 'Standard'] if os.name == 'nt' else ['bash', str(repo / 'scripts/init-project-template.sh'), '--target-path', str(target), '--project-name', 'v047-smoke', '--mode', 'Standard']
        run(command, repo)
        assert readme.read_bytes() == original, 'Business README changed'
        state = json.loads((target / '.forgekit/state.json').read_text(encoding='utf-8-sig'))
        assert state['forgekit_version'] == '0.47.0'
        lock = json.loads((target / '.forgekit/template-lock.json').read_text(encoding='utf-8'))
        assert lock['schema_version'] == 2 and lock['installed_version'] == '0.47.0'
        for entry in lock['files']:
            assert entry['target_path'] != 'README.md'
            data = (target / entry['target_path']).read_bytes()
            assert entry['installed_checksum'] == 'sha256:' + hashlib.sha256(data).hexdigest(), entry['target_path']
            assert 'baseline_b64' in entry, entry['target_path']
        for source in json.loads((repo / 'config/v047-document-moves.json').read_text()):
            relative = '.forgekit/' + source if source.startswith('docs/') else source
            assert not (target / relative).exists(), relative
        if os.name == 'nt':
            for script in ('run-harness-check.ps1', 'check-doc-sync.ps1'):
                run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(target / 'scripts' / script)], target)
        else:
            run(['bash', str(target / 'scripts/check-doc-sync.sh')], target)
        for script in ('check-current-docs-integrity.py', 'check-workspace-integrity.py'):
            run([sys.executable, '-B', str(target / 'scripts' / script), '--repo-root', str(target)], target)
        print('[ok] v0.47 generated project: initialization, README ownership, lock, retired paths, harness and current-doc integrity')


if __name__ == '__main__':
    main()
