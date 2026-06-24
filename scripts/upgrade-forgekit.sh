#!/usr/bin/env bash
set -euo pipefail

project_path=""

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/upgrade-forgekit.sh --project-path /path/to/project

This is report-only. It writes .forgekit/upgrade/* and does not overwrite project files.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-path)
      project_path="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$project_path" ]]; then
  echo "Missing required --project-path" >&2
  usage >&2
  exit 1
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

if command -v python3 >/dev/null 2>&1; then
  python3 "$script_dir/upgrade-forgekit.py" --repo-root "$repo_root" --project-path "$project_path"
elif command -v python >/dev/null 2>&1; then
  python "$script_dir/upgrade-forgekit.py" --repo-root "$repo_root" --project-path "$project_path"
else
  echo "Python is required for ForgeKit guided upgrade." >&2
  exit 1
fi
