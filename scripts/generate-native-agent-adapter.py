#!/usr/bin/env python3
import argparse
import shutil
import sys
from pathlib import Path


VERSION = "0.40.1"

TARGET_FILES = {
    "claude-code": [
        (
            "native-adapters/claude-code/agents/forgekit-planner.md",
            ".claude/agents/forgekit-planner.md",
        ),
        (
            "native-adapters/claude-code/agents/forgekit-reviewer.md",
            ".claude/agents/forgekit-reviewer.md",
        ),
        (
            "native-adapters/claude-code/agents/forgekit-verifier.md",
            ".claude/agents/forgekit-verifier.md",
        ),
        (
            "native-adapters/claude-code/skills/forgekit-loop/SKILL.md",
            ".claude/skills/forgekit-loop/SKILL.md",
        ),
    ],
    "codex": [
        (
            "native-adapters/codex/agents/forgekit-planner.toml",
            ".codex/agents/forgekit-planner.toml",
        ),
        (
            "native-adapters/codex/agents/forgekit-reviewer.toml",
            ".codex/agents/forgekit-reviewer.toml",
        ),
        (
            "native-adapters/codex/agents/forgekit-verifier.toml",
            ".codex/agents/forgekit-verifier.toml",
        ),
        (
            "native-adapters/codex/config.example.toml",
            ".codex/config.example.toml",
        ),
    ],
}


def fail(message):
    raise SystemExit(f"[fail] {message}")


def resolve_repo_root():
    return Path(__file__).resolve().parents[1]


def ensure_project_root(path):
    root = Path(path).expanduser().resolve()
    if not root.exists():
        fail(f"project-root does not exist: {root}")
    if not root.is_dir():
        fail(f"project-root is not a directory: {root}")
    return root


def ensure_inside_root(project_root, relative_target):
    target = (project_root / relative_target).resolve()
    try:
        target.relative_to(project_root)
    except ValueError:
        fail(f"target path escapes project-root: {relative_target}")
    return target


def selected_targets(target):
    if target == "all":
        return ["claude-code", "codex"]
    return [target]


def build_plan(repo_root, project_root, target):
    plan = []
    for target_name in selected_targets(target):
        for source_rel, target_rel in TARGET_FILES[target_name]:
            source = repo_root / source_rel
            if not source.is_file():
                fail(f"missing adapter template: {source_rel}")
            destination = ensure_inside_root(project_root, target_rel)
            plan.append(
                {
                    "target": target_name,
                    "source_rel": source_rel,
                    "target_rel": target_rel,
                    "source": source,
                    "destination": destination,
                }
            )
    return plan


def codex_config_has_native_adapter(path):
    try:
        return "[forgekit.native_agents]" in path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def file_matches_source(source, destination):
    try:
        return source.read_bytes() == destination.read_bytes()
    except OSError:
        return False


def adapter_file_already_present(item):
    if item["target_rel"] == ".codex/config.example.toml":
        return codex_config_has_native_adapter(item["destination"])
    return file_matches_source(item["source"], item["destination"])


def apply_plan(plan, dry_run, force):
    counts = {"planned": len(plan), "written": 0, "skipped": 0, "present": 0}
    rows = []
    for item in plan:
        exists = item["destination"].exists()
        if dry_run:
            action = "planned"
        elif exists and not force:
            if adapter_file_already_present(item):
                action = "present"
                counts["present"] += 1
            else:
                action = "skipped"
                counts["skipped"] += 1
        else:
            item["destination"].parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(item["source"], item["destination"])
            action = "written"
            counts["written"] += 1
        rows.append((action, item))
    return counts, rows


def print_report(args, project_root, counts, rows):
    print("# ForgeKit Native Agent Adapter Generation")
    print("")
    print(f"Version: {VERSION}")
    print(f"Mode: {'dry-run' if args.dry_run else 'write'}")
    print(f"Target: {args.target}")
    print(f"ProjectRoot: {project_root}")
    print(f"Force: {str(args.force).lower()}")
    print("")
    print("Policy:")
    print("- Generates reviewable native agent configuration only.")
    print("- Does not start Claude Code or Codex.")
    print("- Does not run a loop, daemon, scheduler, or dispatcher.")
    print("- Does not create worktrees, merge, commit, push, or create PRs.")
    print("- Does not generate an implementer agent.")
    print("- Codex config is written only as .codex/config.example.toml.")
    print("")
    print("Summary:")
    print(f"- planned: {counts['planned']}")
    print(f"- written: {counts['written']}")
    print(f"- present: {counts['present']}")
    print(f"- skipped: {counts['skipped']}")
    print("")
    print("Files:")
    for action, item in rows:
        print(
            f"- {action}: {item['source_rel']} -> {item['target_rel']} "
            f"({item['target']})"
        )
    if args.dry_run:
        print("")
        print("Dry-run only. No files were written.")
    elif counts["skipped"]:
        print("")
        print("Existing files were skipped. Re-run with --force to overwrite.")


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Generate opt-in ForgeKit native agent adapter files."
    )
    parser.add_argument(
        "--target",
        choices=["claude-code", "codex", "all"],
        required=True,
        help="Adapter target to generate.",
    )
    parser.add_argument(
        "--project-root",
        required=True,
        help="Existing project root where adapter files should be generated.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned writes without writing files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing adapter files.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    repo_root = resolve_repo_root()
    project_root = ensure_project_root(args.project_root)
    plan = build_plan(repo_root, project_root, args.target)
    counts, rows = apply_plan(plan, args.dry_run, args.force)
    print_report(args, project_root, counts, rows)


if __name__ == "__main__":
    main()
