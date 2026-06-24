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
    git -C "$repo_root" diff --name-only HEAD -- .forgekit .codex governance 2>/dev/null || true
    git -C "$repo_root" diff --cached --name-only -- .forgekit .codex governance 2>/dev/null || true
  } | awk 'NF' | grep -v '^.forgekit/upgrade-export/' | grep -v '^.forgekit/upgrade/' | grep -v '^.forgekit/archive/' | grep -v '^.forgekit/archive-plan.md$' | grep -v '^.forgekit/archive-apply-report.md$' | grep -v '^.forgekit/archive-reference-report.md$' | grep -v '^.forgekit/current-docs-sync-report.md$' | grep -v '^.forgekit/smart-archive-report.md$' | grep -v '^.forgekit/smart-archive-apply-report.md$' | sort -u
}

test_stale_phrases() {
  local docs_root="$repo_root/.forgekit/docs"
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
  local version_doc="$repo_root/.forgekit/docs/changelog.md"
  [[ -f "$version_doc" ]] || return 0

  awk '
    /^### Changed[[:space:]]*$/ { inside=1; next }
    /^### / && inside { inside=0 }
    inside && /^[[:space:]]*-[[:space:]]+/ {
      if ($0 !~ /Reason:|Because:|because:/) {
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

  if ! printf '%s\n' "$paths" | grep -Fxq ".forgekit/docs/changelog.md"; then
    add_warning "Docs or governance changed, but the version update record is not changed. Confirm whether it needs an entry with reason."
  fi

  if printf '%s\n' "$paths" | grep -Eq 'defect|risk|incident|security|dependency|deployment|environment|api|database|implementation-plan|exploration-report|change-impact'; then
    add_warning "Risk-sensitive docs changed. Check related docs such as risk register, change impact, testing, release pipeline, and version update record."
  fi
}

test_change_artifacts() {
  local changes_root="$repo_root/.forgekit/changes"
  [[ -d "$changes_root" ]] || return 0

  local dir proposal risk required name relative
  for dir in "$changes_root"/*; do
    [[ -d "$dir" ]] || continue
    [[ "$(basename "$dir")" != "_template" ]] || continue
    relative="${dir#$repo_root/}"
    proposal="$dir/proposal.md"
    if [[ ! -f "$proposal" ]]; then
      add_warning "Change is missing proposal.md: $relative"
      continue
    fi

    local status
    status="$(awk -F': *' 'tolower($1) == "status" { print tolower($2); exit }' "$proposal")"
    if [[ -z "$status" ]]; then
      add_warning "Change proposal is missing Status: metadata: $relative/proposal.md"
    elif [[ "$status" == "archived" ]]; then
      continue
    elif [[ "$status" == "done" ]]; then
      add_warning "Change is done and may be archived: $relative"
      continue
    elif [[ "$status" != "draft" && "$status" != "active" ]]; then
      add_warning "Change proposal has unknown Status value '$status': $relative/proposal.md"
    fi

    risk="$(awk -F': *' 'tolower($1) == "risk" { print tolower($2); exit }' "$proposal")"
    if [[ -z "$risk" ]]; then
      add_warning "Change proposal is missing Risk: metadata: $relative/proposal.md"
      continue
    fi

    required=""
    if [[ "$risk" == "medium" ]]; then
      required="proposal.md tasks.md verification.md review.md"
    elif [[ "$risk" == "high" ]]; then
      required="proposal.md design.md tasks.md verification.md review.md ship.md"
    elif [[ "$risk" != "low" ]]; then
      add_warning "Change proposal has unknown Risk value '$risk': $relative/proposal.md"
      continue
    fi

    for name in $required; do
      if [[ ! -f "$dir/$name" ]]; then
        add_warning "Change with Risk: $risk is missing required artifact: $relative/$name"
      fi
    done
  done
}

test_current_docs_length() {
  local docs_root="$repo_root/.forgekit/docs"
  [[ -d "$docs_root" ]] || return 0

  while IFS= read -r file; do
    [[ -n "$file" ]] || continue
    local line_count relative
    line_count="$(wc -l < "$file" | tr -d ' ')"
    if [[ "$line_count" -gt 600 ]]; then
      relative="${file#$repo_root/}"
      add_warning "Current state doc is long ($line_count lines). Consider moving historical process details to a change or archive: $relative"
    fi
  done < <(find "$docs_root" -type f -name '*.md' 2>/dev/null)
}

path_required ".forgekit/docs/changelog.md"
path_required ".forgekit/docs/version-roadmap.md"
path_required ".forgekit/docs/task-board.md"
path_required ".forgekit/docs/testing.md"
path_required ".forgekit/docs/risk-register.md"
path_required ".forgekit/docs/change-impact.md"

test_stale_phrases

while IFS= read -r warning; do
  [[ -n "$warning" ]] || continue
  add_warning "$warning"
done < <(test_version_changed_reasons)

test_changed_docs_need_version_record
test_change_artifacts
test_current_docs_length

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
