---
name: project-init
description: Initialize or repair a project's Codex workflow, interview the user about project plan and architecture, and fill first-version `.codex/` and `docs/` files from questionnaire answers. Use when Codex is asked to set up a new project, process initialization answers, discuss architecture before implementation, choose stack templates, or decide whether coding may start.
---

# Project Init

## Workflow

1. Read `AGENTS.md` first if present, then read the governance overview, `.codex/init.generated.md`, `.codex/questionnaires/`, existing `.codex/`, existing `docs/`, and project root files.
2. Identify the project type, active stack templates, current phase, delivery target, and hardware/software landing conditions.
3. If `.codex/stacks/` exists, read only relevant stack folders. Do not load unrelated stacks.
4. If questionnaire answers exist, use `governance/project-bootstrap-fill.md` to convert them into first-version `.codex/` rules and `docs/`.
5. Interview the user before large-scale coding when key facts are unclear:
   - problem definition
   - technical stack options and decision
   - hardware/software landing conditions
   - architecture direction
   - risks and blockers
   - Epic / Feature / Task / Bug model
   - version roadmap
6. For large, cross-module, migration, refactor, or high-risk work, require the large-change protocol before implementation:
   - read `governance/large-change-execution.md`
   - create or update the exploration report in `docs/`
   - create or update the implementation plan in `docs/`
   - do not start broad coding until the implementation plan says coding is allowed
7. Fill or update:
   - `.codex/project.md`
   - `.codex/scope.md`
   - `.codex/commands.md`
   - `.codex/style.md`
   - `.codex/testing.md`
   - `.codex/security.md`
   - `.codex/git.md`
   - `.codex/version-gates.md`
   - `docs/project plan`
   - version roadmap document in `docs/`
   - `docs/requirements`
   - `docs/architecture`
   - `docs/technology selection`
   - `docs/environment matrix`
   - `docs/release pipeline`
   - `docs/project task board`
8. Preserve existing project-specific facts. Do not overwrite real information with template text.
9. Do not modify business code unless the user explicitly asks.

## Gate Before Coding

If the development plan, version roadmap, landing conditions, or first implementation slice are unclear, ask follow-up questions instead of starting implementation.

If the requested work is large or cross-module, require exploration and implementation planning before coding.

Do not recommend large-scale coding until there is at least a first version of:

- project plan
- version roadmap
- technical stack decision
- software/hardware conditions
- architecture governance and ADR needs
- RFC needs, traceability IDs, readiness, and risks
- v0.1.0 scope and v0.1.1 review/refactor gate
- first-pass environment matrix and release pipeline assumptions
- first-pass Epic / Feature / Task / Bug model
- exploration report and implementation plan for large changes

## Selection Rules

- Use `templates/README.md` only to decide which stack template applies.
- For Java projects, read `java-springboot` only when Java/Spring Boot is present.
- For FPGA projects, read `fpga-vivado-vitis` only when Vivado/Vitis/HLS is present.
- For full-stack projects, read only the backend and frontend stacks actually present.

## Output

End with:

- Project classification.
- Selected stack templates.
- Files created or updated.
- Plan status: confirmed, partial, or blocked.
- Key decisions that still need user confirmation.
- The next 3-5 questions to continue the project planning discussion.
- Suggested first implementation slice only if coding is allowed.
- Validation commands that are safe to run.
