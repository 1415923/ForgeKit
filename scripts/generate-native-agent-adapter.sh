#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: generate-native-agent-adapter.sh --target claude-code|codex|all --project-root <path> [--dry-run] [--force]

Generates opt-in ForgeKit native agent adapter files only.
It does not start Claude Code or Codex, run a loop, create worktrees, merge,
commit, push, or create PRs.
EOF
}

target=""
project_root=""
dry_run=0
force=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      target="${2:-}"
      shift 2
      ;;
    --project-root)
      project_root="${2:-}"
      shift 2
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    --force)
      force=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$target" || -z "$project_root" ]]; then
  usage >&2
  exit 2
fi

case "$target" in
  claude-code|codex|all) ;;
  *)
    echo "Invalid --target: $target" >&2
    exit 2
    ;;
esac

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
  python_cmd="python3"
elif command -v python >/dev/null 2>&1; then
  python_cmd="python"
else
  echo "Python is required to generate ForgeKit native agent adapter files." >&2
  exit 1
fi

args=(
  "$script_dir/generate-native-agent-adapter.py"
  --target "$target"
  --project-root "$project_root"
)

if [[ "$dry_run" -eq 1 ]]; then
  args+=(--dry-run)
fi
if [[ "$force" -eq 1 ]]; then
  args+=(--force)
fi

"$python_cmd" "${args[@]}"
