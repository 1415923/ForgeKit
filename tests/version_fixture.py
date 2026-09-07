"""Version-pinned fixtures for historical release assertions, never current behavior tests.

Older tests assert exact v0.45/v0.46 prose, counts and incoming bytes. Run those
against their immutable release, while v047 tests exercise the current engine.
This uses local Git objects only and does not fetch or mutate the source repo.
"""
import atexit
import io
import os
import subprocess
import tempfile
import zipfile
from functools import lru_cache
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
V046 = '3325d9728c0d3b3591dde551e184e2c687dc7032'


@lru_cache(maxsize=1)
def v046_repo():
    temp = tempfile.TemporaryDirectory(prefix='forgekit-v046-contract-', dir='D:/tmp' if os.name == 'nt' else None)
    atexit.register(temp.cleanup)
    root = Path(temp.name)
    subprocess.run(['git', '-c', 'core.autocrlf=false', 'clone', '--shared', '--no-checkout', str(SOURCE), str(root)], capture_output=True, check=True)
    subprocess.run(['git', '-c', 'core.autocrlf=false', 'checkout', '--detach', V046], cwd=root, capture_output=True, check=True)
    return root
