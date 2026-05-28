#!/usr/bin/env bash
set -u

strict=0
if [[ "${1:-}" == "--strict" || "${1:-}" == "-Strict" ]]; then
  strict=1
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
warnings=()

add_warning() {
  warnings+=("$1")
}

path_required() {
  local relative_path="$1"
  if [[ ! -e "$repo_root/$relative_path" ]]; then
    add_warning "Missing document commonly needed for sync checks: $relative_path"
  fi
}

changed_paths() {
  if ! command -v git >/dev/null 2>&1; then
    return 0
  fi
  if [[ ! -d "$repo_root/.git" ]]; then
    return 0
  fi
  if ! git -C "$repo_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    return 0
  fi

  {
    git -C "$repo_root" diff --name-only HEAD -- docs .codex governance 2>/dev/null || true
    git -C "$repo_root" diff --cached --name-only -- docs .codex governance 2>/dev/null || true
  } | awk 'NF' | sort -u
}

test_stale_phrases() {
  local docs_root="$repo_root/docs"
  [[ -d "$docs_root" ]] || return 0

  local patterns=(
    "still under workaround"
    "temporary workaround"
    "known stale"
    "stale description"
    "workaround still active"
    "仍在规避"
    "仍需规避"
    "临时规避"
    "过期描述"
    "描述过期"
  )

  local pattern
  for pattern in "${patterns[@]}"; do
    while IFS= read -r match; do
      [[ -n "$match" ]] || continue
      add_warning "Possible stale doc phrase: $match"
    done < <(grep -RIn --include='*.md' -F "$pattern" "$docs_root" 2>/dev/null || true)
  done
}

test_version_changed_reasons() {
  local version_doc="$repo_root/docs/版本更新记录.md"
  [[ -f "$version_doc" ]] || return 0

  awk '
    /^### Changed[[:space:]]*$/ { inside=1; next }
    /^### / && inside { inside=0 }
    inside && /^[[:space:]]*-[[:space:]]+/ {
      if ($0 !~ /原因|Reason|Because|because/) {
        print FNR
      }
    }
  ' "$version_doc" | while IFS= read -r line_no; do
    [[ -n "$line_no" ]] || continue
    echo "Changed entry should include a reason in version update record:$line_no"
  done
}

test_changed_docs_need_version_record() {
  local paths
  paths="$(changed_paths)"
  [[ -n "$paths" ]] || return 0

  if ! printf '%s\n' "$paths" | grep -Fxq "docs/版本更新记录.md"; then
    add_warning "Docs or governance changed, but the version update record is not changed. Confirm whether it needs an entry with reason."
  fi

  if printf '%s\n' "$paths" | grep -Eq '缺陷|风险|事故|安全|依赖|部署|环境|接口|数据库|实施计划|探索报告'; then
    add_warning "Risk-sensitive docs changed. Check related docs such as risk register, change impact, testing, release pipeline, and version update record."
  fi
}

path_required "docs/版本更新记录.md"
path_required "docs/版本路线图.md"
path_required "docs/项目任务看板.md"
path_required "docs/测试文档.md"
path_required "docs/风险登记册.md"
path_required "docs/变更影响评估.md"

test_stale_phrases

while IFS= read -r warning; do
  [[ -n "$warning" ]] || continue
  add_warning "$warning"
done < <(test_version_changed_reasons)

test_changed_docs_need_version_record

if [[ ${#warnings[@]} -eq 0 ]]; then
  echo "[ok] Document sync check passed"
  exit 0
fi

echo "[warn] Document sync check found items to review"
for warning in "${warnings[@]}"; do
  echo " - $warning"
done

echo
echo "Recommended prompt:"
echo "Check whether other docs need synchronized updates. If the version update record has Changed entries, add the reason for each change."

if [[ "$strict" -eq 1 ]]; then
  exit 1
fi

exit 0
