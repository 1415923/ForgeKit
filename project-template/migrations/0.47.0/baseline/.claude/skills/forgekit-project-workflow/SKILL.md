---
name: forgekit-project-workflow
description: Lightweight Claude Code entry skill for ForgeKit project workflow. Use when initializing, reviewing, handing over, planning, or checking a ForgeKit-generated project.
---

# ForgeKit Project Workflow

Use this skill as the Claude Code bridge into a ForgeKit-generated project.

## Start Here

1. Read `CLAUDE.md` first.
2. Use `.forgekit/docs/codebase-map.md` to choose code and document entry points.
3. Use `.forgekit/docs/local-toolchain.md` when local validation commands matter.
4. Use `.forgekit/docs/codex-next-work-order.md` when project direction is unclear.
5. Read `.codex/project.md`, `.codex/scope.md`, `.codex/commands.md`, and selected `.codex/stacks/` only as needed.

## Discovery State

Before implementation, classify the project state:

- `unclear`: ask about goal, users, pain, success evidence, and non-goals.
- `options-needed`: present 2 to 4 viable options with tradeoffs and a recommended default.
- `research-needed`: name the unknown, blocked decision, and references or prototypes to inspect.
- `existing-project-scan`: inspect local files first, infer stack and constraints, then ask targeted questions.
- `ready-for-plan`: write the project plan, roadmap, task split, risks, and execution confirmation.

## Boundaries

- Do not start broad coding without a first-pass project plan and version scope.
- Do not ask the user to choose a stack before product shape and constraints are clear.
- Do not enable hooks, MCP, plugins, subagents, issue tracker writes, or CI changes without explicit confirmation.
- Do not install dependencies, initialize Git, commit, push, deploy, run migrations, or start long-running services without explicit confirmation.

## Output

End with:

- Project classification.
- Discovery state.
- Stack status.
- Confirmed decisions, assumptions, research-needed items, and deferred non-goals.
- Next 3 to 5 questions or decision options.
- Safe validation commands.
