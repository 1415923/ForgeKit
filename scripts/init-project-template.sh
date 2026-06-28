#!/usr/bin/env bash
set -euo pipefail

target_path=""
project_name=""
mode="Standard"
force=0
upgrade=0
export_upgrade_templates=0
native_agent_adapter="none"
stacks=()

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/init-project-template.sh --target-path /path/to/project --project-name my-app [--mode Standard] [--native-agent-adapter none|claude-code|codex|all] [--upgrade] [--export-upgrade-templates] [--force] [--stacks java-springboot,vue]

Options:
  --target-path PATH     Required. Directory to generate the project template into.
  --project-name NAME    Optional project name written into init metadata.
  --mode MODE            Lite, Standard, or Enterprise. Default: Standard.
  --stacks LIST          Optional comma-separated stack templates to copy.
  --native-agent-adapter TARGET
                         Optional. none, claude-code, codex, or all. Default: none.
  --upgrade              Safe upgrade mode. Existing files are preserved.
  --export-upgrade-templates
                         Export newer candidate templates under .forgekit/upgrade-export/<version>/ for review.
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
    --native-agent-adapter)
      native_agent_adapter="${2:-none}"
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

case "$native_agent_adapter" in
  none|claude-code|codex|all) ;;
  *)
    echo "Invalid --native-agent-adapter: $native_agent_adapter. Expected none, claude-code, codex, or all." >&2
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

skip_template_path() {
  local relative_path="${1//\\//}"
  case "$relative_path" in
    .forgekit/template-manifest.json|.forgekit/template-lock.json|.forgekit/upgrade-report.md|.forgekit/archive-plan.md|.forgekit/archive-apply-report.md|.forgekit/archive-reference-report.md|.forgekit/current-docs-sync-report.md|.forgekit/smart-archive-report.md|.forgekit/smart-archive-apply-report.md|.forgekit/upgrade-export/*|.forgekit/upgrade/*)
      return 0
      ;;
    *)
      return 1
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
    if skip_template_path "$relative_path"; then
      continue
    fi
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
  version: "0.35.2"
  mode: "$mode"

roots:
  forgekit_root: "$relative_forgekit_root"
  project_root: "$project_root_relative"
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

init_code_root() {
  if [[ -z "${project_name// }" ]]; then
    project_root_relative="."
    return 0
  fi

  case "$project_name" in
    *[\\/:*?\"'<>|]*)
      echo "ProjectName contains characters that cannot be used as a folder name: $project_name" >&2
      exit 1
      ;;
  esac

  mkdir -p "$resolved_target/$project_name"
  project_root_relative="./$project_name"
  echo "[copy] $project_name/"
}

python_cmd() {
  if command -v python3 >/dev/null 2>&1; then
    printf 'python3'
  elif command -v python >/dev/null 2>&1; then
    printf 'python'
  else
    echo "Python is required for ForgeKit template versioning." >&2
    exit 1
  fi
}

template_versioning() {
  local command="$1"
  "$(python_cmd)" "$repo_root/scripts/update-template-manifest.py" "$command" --repo-root "$repo_root" --project-root "$resolved_target"
}

generate_native_agent_adapter() {
  if [[ "$native_agent_adapter" == "none" ]]; then
    return 0
  fi

  local args=(
    "$repo_root/scripts/generate-native-agent-adapter.py"
    --target "$native_agent_adapter"
    --project-root "$resolved_target"
  )
  if [[ "$force" -eq 1 ]]; then
    args+=(--force)
  fi
  "$(python_cmd)" "${args[@]}"
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
3. .forgekit/project-boundary.yml
4. .forgekit/docs/codebase-map.md
5. .forgekit/docs/local-toolchain.md
6. .forgekit/docs/codex-next-work-order.md
7. .codex/project.md, .codex/scope.md, .codex/commands.md
8. .codex/stacks/README.md, then related .codex/stacks/<stack>/ only when a stack is confirmed
9. Task-specific governance files
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
  echo "[init] mode: report-only upgrade; existing files, lock, and business docs are preserved"
  if [[ "$export_upgrade_templates" -eq 1 ]]; then
    echo "[init] export newer templates for review under .forgekit/upgrade-export"
  fi
fi

if [[ "$upgrade" -eq 1 && "$force" -ne 1 ]]; then
  template_versioning upgrade-report
else
  copy_tree "$project_template_dir" "$resolved_target"

  if [[ -d "$questionnaires_dir" ]]; then
    copy_tree "$questionnaires_dir" "$resolved_target/.codex/questionnaires"
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
    copy_tree "$stack_dir" "$resolved_target/.codex/stacks/$stack"
  done

  init_code_root
  write_codex_metadata
  write_claude_metadata
  write_boundary_config
  template_versioning install-lock
  generate_native_agent_adapter
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
if [[ -z "${project_name// }" ]]; then
  echo "- ProjectRoot is the business repository and Git commit location: $resolved_target"
else
  echo "- Outer workspace is ForgeKit governance: $resolved_target"
  echo "- ProjectRoot is the business code folder and Git commit location: $resolved_target/$project_name"
fi
echo "- Managed ForgeKit docs default to .forgekit/docs; change artifacts default to .forgekit/changes."
echo "- Existing business docs/ is read-mostly by default; do not write ForgeKit governance templates there unless the user confirms."
echo "- Do not copy ForgeKit itself into ProjectRoot or commit ForgeKitRoot as part of the business repository."
if [[ "$native_agent_adapter" != "none" && "$upgrade" -ne 1 ]]; then
  echo "- Native Agent Adapter was generated for target: $native_agent_adapter. Generated config still needs runtime verification before it can be called native success."
  echo "- Codex schema check: python3 scripts/check-codex-native-agents.py --repo-root ."
fi
echo
echo "Do not choose a tech stack here. ForgeKit will confirm or infer it during the discovery interview."
if [[ "$upgrade" -eq 1 ]]; then
  echo "Upgrade note: report-only mode preserved existing files and lock. Review .forgekit/upgrade-report.md and candidate templates under .forgekit/upgrade-export manually."
fi


