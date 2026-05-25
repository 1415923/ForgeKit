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
6. Use iterative solution shaping, not a one-shot questionnaire:
   - Ask only the next 3 to 5 highest-leverage questions.
   - If the user cannot answer, provide 2 to 4 realistic options with tradeoffs and a recommended default.
   - If current knowledge is insufficient, propose a research path: local docs to inspect, official docs to search, example projects to compare, or small throwaway prototypes to run.
   - Clearly mark each item as Confirmed, Assumption, Research needed, or Deferred.
   - Keep interviewing and revising the plan until v0.1.0 scope, data model, deployment target, validation command, and safety boundary are coherent.
   - Do not treat "unknown" as a reason to stop; turn unknowns into decision options, research tasks, or deferred non-goals.
7. When the user describes a product idea in natural language, translate it into:
   - problem and target users
   - MVP workflow
   - explicit non-goals
   - data and state boundaries
   - technical options and recommendation
   - validation strategy
   - risks and open decisions
   - first implementation slice, only when coding is allowed
8. For large, cross-module, migration, refactor, or high-risk work, require the large-change protocol before implementation:
   - read `governance/large-change-execution.md`
   - create or update the exploration report in `docs/`
   - create or update the implementation plan in `docs/`
   - do not start broad coding until the implementation plan says coding is allowed
9. Fill or update:
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
10. Preserve existing project-specific facts. Do not overwrite real information with template text.
11. Remove or replace template history that belongs to ForgeKit itself. Generated projects must not keep ForgeKit Agent Harness roadmap tasks as if they were project tasks.
12. Do not modify business code unless the user explicitly asks.

## Gate Before Coding

If the development plan, version roadmap, landing conditions, or first implementation slice are unclear, ask follow-up questions instead of starting implementation.

If the user cannot answer a gate question, do not repeat the same question. Provide a decision table, a recommended default, and a concrete way to verify the choice.

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
- Confirmed decisions, assumptions, research-needed items, and deferred non-goals.
- The next 3-5 questions or decision options to continue the project planning discussion.
- Reference or research suggestions when the user cannot decide from current context.
- Suggested first implementation slice only if coding is allowed.
- Validation commands that are safe to run.
