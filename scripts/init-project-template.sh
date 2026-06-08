#!/usr/bin/env bash
set -euo pipefail

target_path=""
project_name=""
mode="Standard"
force=0
upgrade=0
export_upgrade_templates=0
stacks=()

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/init-project-template.sh --target-path /path/to/project --project-name my-app [--mode Standard] [--upgrade] [--export-upgrade-templates] [--force] [--stacks java-springboot,vue]

Options:
  --target-path PATH     Required. Directory to generate the project template into.
  --project-name NAME    Optional project name written into init metadata.
  --mode MODE            Lite, Standard, or Enterprise. Default: Standard.
  --stacks LIST          Optional comma-separated stack templates to copy.
  --upgrade              Safe upgrade mode. Existing files are preserved.
  --export-upgrade-templates
                         Export newer template copies under .codex/upgrade-templates for review.
  --force                Overwrite existing files. Cannot be combined with --upgrade.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target-path)
      target_path="${2:-}"
      shift 2
      ;;
    --project-name)
      project_name="${2:-}"
      shift 2
      ;;
    --mode)
      mode="${2:-Standard}"
      shift 2
      ;;
    --stacks)
      IFS=',' read -r -a stacks <<< "${2:-}"
      shift 2
      ;;
    --force)
      force=1
      shift
      ;;
    --upgrade)
      upgrade=1
      shift
      ;;
    --export-upgrade-templates)
      export_upgrade_templates=1
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

if [[ -z "$target_path" ]]; then
  echo "Missing required --target-path" >&2
  usage >&2
  exit 1
fi

case "$mode" in
  Lite|Standard|Enterprise) ;;
  *)
    echo "Invalid --mode: $mode. Expected Lite, Standard, or Enterprise." >&2
    exit 1
    ;;
esac

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
project_template_dir="$repo_root/project-template"
templates_dir="$repo_root/templates"
questionnaires_dir="$repo_root/questionnaires"
resolved_target="$(mkdir -p "$target_path" && cd "$target_path" && pwd)"

map_template_path() {
  local relative_path="$1"
  case "$relative_path" in
    docs/*)
      printf '.forgekit/docs/%s' "${relative_path#docs/}"
      ;;
    changes/*)
      printf '.forgekit/changes/%s' "${relative_path#changes/}"
      ;;
    *)
      printf '%s' "$relative_path"
      ;;
  esac
}

copy_tree() {
  local source_dir="$1"
  local destination_dir="$2"

  if [[ ! -d "$source_dir" ]]; then
    echo "Source directory not found: $source_dir" >&2
    exit 1
  fi

  mkdir -p "$destination_dir"
  while IFS= read -r -d '' source_file; do
    local relative_path="${source_file#"$source_dir"/}"
    local destination_relative_path
    destination_relative_path="$(map_template_path "$relative_path")"
    local destination_file="$destination_dir/$destination_relative_path"
    mkdir -p "$(dirname "$destination_file")"

    if [[ -e "$destination_file" && "$force" -ne 1 ]]; then
      echo "[skip] $destination_relative_path already exists"
      continue
    fi

    cp -f "$source_file" "$destination_file"
    echo "[copy] $destination_relative_path"
  done < <(find "$source_dir" -type f -print0)
}

upgrade_copied=()
upgrade_same=()
upgrade_review=()
upgrade_exported=()
upgrade_export_dir=""

same_file() {
  local left="$1"
  local right="$2"
  cmp -s "$left" "$right"
}

copy_tree_upgrade() {
  local source_dir="$1"
  local destination_dir="$2"
  local export_dir="$3"

  if [[ ! -d "$source_dir" ]]; then
    echo "Source directory not found: $source_dir" >&2
    exit 1
  fi

  mkdir -p "$destination_dir"
  while IFS= read -r -d '' source_file; do
    local relative_path="${source_file#"$source_dir"/}"
    local destination_relative_path
    destination_relative_path="$(map_template_path "$relative_path")"
    local destination_file="$destination_dir/$destination_relative_path"
    mkdir -p "$(dirname "$destination_file")"

    if [[ ! -e "$destination_file" ]]; then
      cp -f "$source_file" "$destination_file"
      upgrade_copied+=("$destination_relative_path")
      echo "[copy] $destination_relative_path"
      continue
    fi

    if same_file "$source_file" "$destination_file"; then
      upgrade_same+=("$destination_relative_path")
      echo "[same] $destination_relative_path"
      continue
    fi

    upgrade_review+=("$destination_relative_path")
    echo "[review] $destination_relative_path differs; existing file preserved"

    if [[ "$export_upgrade_templates" -eq 1 ]]; then
      local export_file="$export_dir/$destination_relative_path"
      mkdir -p "$(dirname "$export_file")"
      cp -f "$source_file" "$export_file"
      upgrade_exported+=("$destination_relative_path")
    fi
  done < <(find "$source_dir" -type f -print0)
}

write_list() {
  local title="$1"
  local -n values_ref="$2"
  local report_file="$3"
  {
    echo "$title"
    if [[ ${#values_ref[@]} -eq 0 ]]; then
      echo "- None"
    else
      local item
      for item in "${values_ref[@]}"; do
        echo "- $item"
      done
    fi
    echo
  } >> "$report_file"
}

write_upgrade_report() {
  local report_file="$resolved_target/.codex/upgrade-report.md"
  mkdir -p "$(dirname "$report_file")"
  {
    echo "# ForgeKit Upgrade Report"
    echo
    echo "Generated by scripts/init-project-template.sh --upgrade."
    echo
    echo "Existing project files were preserved. Files listed under review differ from the newer ForgeKit template and should be merged manually or with AI assistance."
    echo
  } > "$report_file"

  write_list "## Copied Missing Files" upgrade_copied "$report_file"
  write_list "## Review Existing Files" upgrade_review "$report_file"
  write_list "## Same Files" upgrade_same "$report_file"

  {
    echo "## Merge Guidance"
    echo "- Do not overwrite project facts with template text."
    echo "- Prefer merging new sections, safety rules, scripts, and routing hints into existing files."
    echo "- Ask the AI assistant to compare this report with current project files before applying changes."
    if [[ "$export_upgrade_templates" -eq 1 ]]; then
      echo "- New template copies were exported under: $upgrade_export_dir"
    else
      echo "- Re-run with --export-upgrade-templates to export newer template copies for side-by-side diff."
    fi
    echo
    echo "Legacy filename migration:"
    echo "- Upgrade mode does not automatically rename existing Chinese document names or #Uxxxx escaped file names."
    echo "- Review the detected list below and migrate paths manually after checking project-specific references."
    local legacy
    legacy="$(find "$resolved_target" -type f | sed "s#^$resolved_target/##" | grep -E '#U|代码库地图|本地工具链检查|版本路线图|版本更新记录|项目开发方案|项目任务看板|技术选型|使用说明' || true)"
    if [[ -z "$legacy" ]]; then
      echo "- Detected: none."
    else
      echo "- Detected legacy paths:"
      printf '%s\n' "$legacy" | sed 's/^/  - /'
    fi
    echo
    echo "Boundary migration:"
    echo "- v0.16.0 adds .forgekit/project-boundary.yml for ForgeKitRoot, ProjectRoot, managed_docs_root, and change_root."
    echo "- Existing projects may still use docs/ or changes/ for ForgeKit-managed files; upgrade mode does not move them automatically."
    echo "- New projects use .forgekit/docs and .forgekit/changes by default."
    echo "- Treat business docs roots such as docs/ as read-mostly evidence unless the user explicitly confirms target files and reasons for writing."
    echo
    echo "Suggested prompt:"
    echo "Review .codex/upgrade-report.md and merge useful new ForgeKit template sections into the existing project files without overwriting project facts."
  } >> "$report_file"

  echo "[copy] .codex/upgrade-report.md"
}

relative_path_between() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -c "import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]).replace('\\\\','/'))" "$1" "$2"
  elif command -v python >/dev/null 2>&1; then
    python -c "import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]).replace('\\\\','/'))" "$1" "$2"
  else
    printf '<path-to-forgekit>'
  fi
}

write_boundary_config() {
  local boundary_file="$resolved_target/.forgekit/project-boundary.yml"
  if [[ -e "$boundary_file" && "$force" -ne 1 && "$upgrade" -eq 1 ]]; then
    echo "[skip] .forgekit/project-boundary.yml already exists"
    return 0
  fi

  local relative_forgekit_root
  relative_forgekit_root="$(relative_path_between "$repo_root" "$resolved_target")"
  mkdir -p "$(dirname "$boundary_file")"
  cat > "$boundary_file" <<EOF
forgekit:
  version: "0.16.0"
  mode: "$mode"

roots:
  forgekit_root: "$relative_forgekit_root"
  project_root: "."
  managed_docs_root: ".forgekit/docs"
  change_root: ".forgekit/changes"
  business_docs_roots:
    - "docs"

write_policy:
  allow:
    - ".codex/**"
    - ".agents/**"
    - ".claude/**"
    - ".forgekit/docs/**"
    - ".forgekit/changes/**"
  task_scoped:
    - "src/**"
    - "tests/**"
    - "scripts/**"
  read_mostly:
    - "docs/**"
  ask:
    - "README.md"
    - "AGENTS.md"
    - "CLAUDE.md"
    - ".github/**"
    - "package.json"
    - "pom.xml"
    - "build.gradle"
  readonly:
    - "$relative_forgekit_root/**"
    - ".git/**"
    - "node_modules/**"
    - "target/**"
    - "dist/**"
    - "build/**"
EOF
  echo "[copy] .forgekit/project-boundary.yml"
}

write_codex_metadata() {
  local metadata_file="$resolved_target/.codex/init.generated.md"
  if [[ -e "$metadata_file" && "$force" -ne 1 ]]; then
    echo "[skip] .codex/init.generated.md already exists"
    return 0
  fi

  local stack_text="deferred"
  if [[ ${#stacks[@]} -gt 0 && -n "${stacks[*]// /}" ]]; then
    stack_text="$(IFS=', '; echo "${stacks[*]}")"
  fi

  mkdir -p "$(dirname "$metadata_file")"
  cat > "$metadata_file" <<EOF
# Init Metadata

Generated by scripts/init-project-template.sh.

- ProjectName: $project_name
- Mode: $mode
- Stacks: $stack_text
- StackSelection: deferred means no stack was chosen during initialization. This is normal.

Use this file as initialization metadata. Merge real project facts into .codex/project.md, .codex/scope.md, .forgekit/docs/codebase-map.md, .forgekit/docs/local-toolchain.md, and .forgekit/docs/tech-decisions.md manually or with Codex.

Stack guidance:
- New projects: confirm product shape, users, constraints, risks, and the v0.1.0 closed loop before choosing a stack.
- Existing projects: infer the stack from project files before asking the user technical-stack questions.
- Feature, fix, and refactor work defaults to the existing stack unless the user explicitly asks for migration or architecture change.

Mode guidance:
- Lite: metadata hint for lightweight AI filling and governance discussion.
- Standard: metadata hint for normal AI filling and governance discussion.
- Enterprise: metadata hint for stricter AI filling and governance discussion.
- The initializer copies the same template files for every mode; mode does not crop files in the current version.
EOF
  echo "[copy] .codex/init.generated.md"
}

write_claude_metadata() {
  local metadata_file="$resolved_target/.claude/init.generated.md"
  if [[ -e "$metadata_file" && "$force" -ne 1 ]]; then
    echo "[skip] .claude/init.generated.md already exists"
    return 0
  fi

  local stack_text="deferred"
  if [[ ${#stacks[@]} -gt 0 && -n "${stacks[*]// /}" ]]; then
    stack_text="$(IFS=', '; echo "${stacks[*]}")"
  fi

  mkdir -p "$(dirname "$metadata_file")"
  cat > "$metadata_file" <<EOF
# Claude Init Metadata

Generated by scripts/init-project-template.sh.

- ProjectName: $project_name
- Mode: $mode
- Stacks: $stack_text
- StackSelection: deferred means no stack was chosen during initialization. This is normal.

Use this file as Claude Code initialization metadata. Merge real project facts into .codex/project.md, .codex/scope.md, .forgekit/docs/codebase-map.md, .forgekit/docs/local-toolchain.md, and .forgekit/docs/tech-decisions.md manually or with Claude Code.

Recommended Claude Code startup order:
1. CLAUDE.md
2. .claude/skills/forgekit-project-workflow/SKILL.md
3. docs codebase map
4. local toolchain check document under docs
5. Codex next-step work order under docs
6. .codex/project.md, .codex/scope.md, .codex/commands.md
7. .codex/stacks/README.md, then related .codex/stacks/<stack>/ only when a stack is confirmed
8. Task-specific governance files
EOF
  echo "[copy] .claude/init.generated.md"
}

echo "[init] target: $resolved_target"
echo "[init] base template: $project_template_dir"
if [[ "$upgrade" -eq 1 ]]; then
  if [[ "$force" -eq 1 ]]; then
    echo "Error: --upgrade cannot be combined with --force. Upgrade mode must preserve existing project facts." >&2
    exit 2
  fi
  echo "[init] mode: upgrade existing project; existing files are preserved"
  if [[ "$export_upgrade_templates" -eq 1 ]]; then
    echo "[init] export newer templates for review under .codex/upgrade-templates"
  fi
fi

upgrade_export_dir="$resolved_target/.codex/upgrade-templates"
if [[ "$upgrade" -eq 1 && "$force" -ne 1 ]]; then
  copy_tree_upgrade "$project_template_dir" "$resolved_target" "$upgrade_export_dir"
else
  copy_tree "$project_template_dir" "$resolved_target"
fi

if [[ -d "$questionnaires_dir" ]]; then
  if [[ "$upgrade" -eq 1 && "$force" -ne 1 ]]; then
    copy_tree_upgrade "$questionnaires_dir" "$resolved_target/.codex/questionnaires" "$upgrade_export_dir/.codex/questionnaires"
  else
    copy_tree "$questionnaires_dir" "$resolved_target/.codex/questionnaires"
  fi
fi

for stack in "${stacks[@]}"; do
  stack="$(echo "$stack" | xargs)"
  [[ -z "$stack" ]] && continue
  stack_dir="$templates_dir/$stack"
  if [[ ! -d "$stack_dir" ]]; then
    echo "Unknown stack template: $stack" >&2
    exit 1
  fi
  echo "[init] stack template: $stack"
  if [[ "$upgrade" -eq 1 && "$force" -ne 1 ]]; then
    copy_tree_upgrade "$stack_dir" "$resolved_target/.codex/stacks/$stack" "$upgrade_export_dir/.codex/stacks/$stack"
  else
    copy_tree "$stack_dir" "$resolved_target/.codex/stacks/$stack"
  fi
done

write_codex_metadata
write_claude_metadata
write_boundary_config

if [[ "$upgrade" -eq 1 && "$force" -ne 1 ]]; then
  write_upgrade_report
fi

echo "[init] done"
echo
echo "Next steps:"
echo "1. Enter the generated project:"
echo "   cd $resolved_target"
echo "2. Start your AI coding tool from that project:"
echo "   Codex: codex"
echo "   Claude Code: claude"
echo "3. Send the startup message:"
echo "   Codex: Read AGENTS.md, prefer .agents/skills/project-init/SKILL.md, and help me initialize this project with ForgeKit. Do not read a user-level or system-level project-init path."
echo "   Claude Code: Read CLAUDE.md, prefer .agents/skills/project-init/SKILL.md, and help me initialize this project with ForgeKit. Do not read a user-level or system-level project-init path."
echo
echo "Boundary:"
echo "- ForgeKitRoot is the toolkit/template source: $repo_root"
echo "- ProjectRoot is the business repository and Git commit location: $resolved_target"
echo "- Managed ForgeKit docs default to .forgekit/docs; change artifacts default to .forgekit/changes."
echo "- Existing business docs/ is read-mostly by default; do not write ForgeKit governance templates there unless the user confirms."
echo "- Do not copy ForgeKit itself into ProjectRoot or commit ForgeKitRoot as part of the business repository."
echo
echo "Do not choose a tech stack here. ForgeKit will confirm or infer it during the discovery interview."
if [[ "$upgrade" -eq 1 ]]; then
  echo "Upgrade note: existing files were preserved. Review .codex/upgrade-report.md and merge useful template updates manually."
fi
