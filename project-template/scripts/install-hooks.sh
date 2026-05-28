#!/usr/bin/env bash
set -euo pipefail

profile="docs-warn"
target="git"
dry_run=0
status=0
uninstall=0

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/install-hooks.sh [--profile docs-warn|docs-strict] [--target git|claude|codex] [--dry-run] [--status] [--uninstall]

Examples:
  ./scripts/install-hooks.sh --profile docs-warn --target git
  ./scripts/install-hooks.sh --profile docs-strict --target git
  ./scripts/install-hooks.sh --status
  ./scripts/install-hooks.sh --uninstall
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      profile="${2:-docs-warn}"
      shift 2
      ;;
    --target)
      target="${2:-git}"
      shift 2
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    --status)
      status=1
      shift
      ;;
    --uninstall)
      uninstall=1
      shift
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

case "$profile" in
  docs-warn|docs-strict) ;;
  *)
    echo "Invalid --profile: $profile" >&2
    exit 1
    ;;
esac

case "$target" in
  git|claude|codex) ;;
  *)
    echo "Invalid --target: $target" >&2
    exit 1
    ;;
esac

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
hook_start="# BEGIN FORGEKIT DOC SYNC HOOK"
hook_end="# END FORGEKIT DOC SYNC HOOK"

assert_git_repo() {
  if [[ ! -d "$repo_root/.git" ]]; then
    echo "Git hooks require a Git repository. Run git init first, or use the manual command from .codex/hooks.md." >&2
    exit 1
  fi
}

hook_body() {
  local strict_arg=""
  if [[ "$profile" == "docs-strict" ]]; then
    strict_arg=" --strict"
  fi
  cat <<EOF
$hook_start
  if [ -f "./scripts/check-doc-sync.sh" ]; then
    sh ./scripts/check-doc-sync.sh$strict_arg
  status=\$?
  if [ "\$status" -ne 0 ]; then
    exit "\$status"
  fi
fi
$hook_end
EOF
}

is_installed() {
  local hook_path="$1"
  [[ -f "$hook_path" ]] && grep -Fq "$hook_start" "$hook_path"
}

remove_managed_block() {
  local hook_path="$1"
  awk -v start="$hook_start" -v end="$hook_end" '
    $0 == start { skip=1; next }
    $0 == end { skip=0; next }
    skip != 1 { print }
  ' "$hook_path"
}

install_git_hook() {
  local hook_path="$repo_root/.git/hooks/pre-commit"

  if [[ "$status" -eq 1 ]]; then
    if [[ ! -d "$repo_root/.git" ]]; then
      echo "[info] current project is not a Git repository; Git hook is not installed"
      return 0
    fi
    if is_installed "$hook_path"; then
      echo "[ok] ForgeKit document sync is installed in .git/hooks/pre-commit"
    else
      echo "[info] ForgeKit document sync is not installed in .git/hooks/pre-commit"
    fi
    return 0
  fi

  assert_git_repo

  if [[ "$uninstall" -eq 1 ]]; then
    if [[ ! -f "$hook_path" ]]; then
      echo "[ok] no git pre-commit hook to uninstall"
      return 0
    fi
    if [[ "$dry_run" -eq 1 ]]; then
      echo "[dry-run] would remove ForgeKit document sync from .git/hooks/pre-commit"
      return 0
    fi
    local tmp_file
    tmp_file="$(mktemp)"
    remove_managed_block "$hook_path" > "$tmp_file"
    mv "$tmp_file" "$hook_path"
    chmod +x "$hook_path"
    echo "[ok] removed ForgeKit document sync from .git/hooks/pre-commit"
    return 0
  fi

  mkdir -p "$(dirname "$hook_path")"
  local tmp_file
  tmp_file="$(mktemp)"
  if [[ -f "$hook_path" ]]; then
    remove_managed_block "$hook_path" > "$tmp_file"
  else
    printf '#!/usr/bin/env bash\n' > "$tmp_file"
  fi
  {
    printf '\n'
    hook_body
    printf '\n'
  } >> "$tmp_file"

  if [[ "$dry_run" -eq 1 ]]; then
    echo "[dry-run] would install ForgeKit document sync into .git/hooks/pre-commit"
    echo "[dry-run] profile: $profile"
    rm -f "$tmp_file"
    return 0
  fi

  mv "$tmp_file" "$hook_path"
  chmod +x "$hook_path"
  echo "[ok] installed ForgeKit document sync into .git/hooks/pre-commit"
  echo "[ok] profile: $profile"
}

case "$target" in
  git)
    install_git_hook
    ;;
  claude)
    echo "[info] Claude Code lifecycle hook installer is not enabled yet."
    echo "[info] Use Git hook target now: ./scripts/install-hooks.sh --target git --profile docs-warn"
    echo "[info] See .codex/hooks.md for Claude Code project-hook guidance."
    ;;
  codex)
    echo "[info] Codex lifecycle hook installer is not enabled yet."
    echo "[info] Use Git hook target now: ./scripts/install-hooks.sh --target git --profile docs-warn"
    echo "[info] Codex hook loading differs by version; keep this explicit until plugin-local hooks are stable."
    ;;
esac
