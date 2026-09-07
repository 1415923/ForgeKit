"""Current release gate; historical exact-text tests remain version-pinned."""
import argparse
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', default=Path(__file__).resolve().parents[1])
    parser.add_argument('--static-only', action='store_true')
    args = parser.parse_args()
    repo = Path(args.repo_root).resolve()
    commands = [[sys.executable, '-B', str(repo / 'scripts/validate-v047.py'), '--repo-root', str(repo)],
                [sys.executable, '-B', str(repo / 'scripts/sync-skill-projections.py'), 'check', '--repo-root', str(repo)]]
    if not args.static_only:
        commands += [[sys.executable, '-B', '-m', 'unittest', 'discover', '-s', str(repo / 'tests'), '-p', 'test_*.py'],
                     [sys.executable, '-B', str(repo / 'scripts/smoke-v047.py'), '--repo-root', str(repo)]]
    env = dict(os.environ, PYTHONUTF8='1', FORGEKIT_STAGE_E_RUNTIME_CANARY_CHILD='1')
    for command in commands:
        result = subprocess.run(command, cwd=repo, env=env)
        if result.returncode:
            return result.returncode
    print('[ok] v0.47 release gate passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
