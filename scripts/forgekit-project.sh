#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
  python_cmd="python3"
elif command -v python >/dev/null 2>&1; then
  python_cmd="python"
else
  echo "[fail] Python 3 was not found." >&2
  exit 1
fi

exec "$python_cmd" "$script_dir/forgekit-project.py" "$@"
