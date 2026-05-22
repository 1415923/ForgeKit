---
name: project-init
description: Initialize or repair a project's Codex workflow files and documentation, with emphasis on project development plan, technical choices, version roadmap, hardware/software landing conditions, and gating before coding. Use when Codex is asked to set up a new project, discuss architecture before implementation, fill `.codex/` rules, process a questionnaire, choose stack templates, create initial docs, or bring an existing project into this workflow.
---

# Project Init

## Workflow

1. Read `governance/sdlc.md`, `governance/architecture-governance.md`, `governance/rfc-process.md`, `governance/adr-process.md`, `governance/traceability.md`, `governance/definition-of-ready.md`, `governance/risk-management.md`, `governance/cicd-environment-governance.md`, `governance/project-management-task-model.md`, and project root files first: `README.md`, build configs, existing `docs/`, `.codex/`, and any questionnaire.
2. Identify the project type, active stack templates, current phase, delivery target, and hardware/software landing conditions.
3. If `.codex/stacks/` exists, read only relevant stack folders. Do not load unrelated stacks.
4. Discuss and fill the project development plan before large-scale coding:
   - problem definition
   - technical stack options and decision
   - hardware/software landing conditions
   - architecture direction
   - risks and blockers
   - Epic / Feature / Task / Bug model
   - version roadmap
5. Fill or update:
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
6. Preserve existing project-specific facts. Do not overwrite real information with template text.
7. Do not modify business code unless the user explicitly asks.

## Gate Before Coding

If the development plan, version roadmap, or landing conditions are unclear, ask follow-up questions instead of starting implementation.

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
- Whether coding is allowed yet.
- Open questions.
- Suggested next tasks.
- Validation commands that are safe to run.
