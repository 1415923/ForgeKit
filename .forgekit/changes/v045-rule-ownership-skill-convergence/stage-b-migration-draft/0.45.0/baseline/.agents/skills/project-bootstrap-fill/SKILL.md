---
name: project-bootstrap-fill
description: Fill first-version Codex project documents from initialization questionnaire answers and produce the next planning questions. Use when Codex is asked to convert questionnaire answers, pasted project facts, or `.codex/questionnaires/` content into initial `.codex/` rules and `.forgekit/docs/` files while preparing a project-plan discussion before coding.
---

# Project Bootstrap Fill

## Workflow

1. Read `AGENTS.md` if present, then read `governance/project-bootstrap-fill.md`, `.codex/init.generated.md`, `.codex/questionnaires/`, `.codex/stacks/`, existing `.codex/`, and existing business `docs/` and `.forgekit/docs/`.
2. Extract stable facts from the questionnaire or user-provided answers:
   - project identity
   - project goal
   - project type
   - selected stacks
   - delivery target
   - landing environment
   - version scope
   - risks
   - required commands
   - security and permission boundaries
3. Do not invent facts. If information is unknown, keep `TBD` or `needs confirmation` and list open questions.
4. Fill or update the first version of:
   - `.codex/project.md`
   - `.codex/scope.md`
   - `.codex/commands.md`
   - `.codex/style.md`
   - `.codex/testing.md`
   - `.codex/security.md`
   - `.codex/git.md`
   - `.codex/version-gates.md`
   - `.forgekit/docs/project-plan.md`
   - `.forgekit/docs/tech-decisions.md`
   - `.forgekit/docs/version-roadmap.md`
   - `.forgekit/docs/requirements.md`
   - `.forgekit/docs/environment-matrix.md`
   - `.forgekit/docs/release-pipeline.md`
   - `.forgekit/docs/code-ownership.md`
   - `.forgekit/docs/task-board.md`
   - `.forgekit/docs/traceability.md`
   - `.forgekit/docs/risk-register.md`
5. Preserve user-edited content. Merge facts into existing documents instead of replacing them wholesale.
6. After filling documents, start the planning loop: summarize what is known, identify important unknowns, and ask the next 3-5 questions needed to confirm the project plan.

## Filling Rules

- Map project goal and success criteria to project plan and requirements.
- Map selected stacks to project rules, commands, style, testing, and technology selection.
- Map landing conditions to environment matrix, release pipeline, deployment notes, and risk register.
- Map v0.1.0 and v0.1.1 answers to version roadmap, task board, traceability matrix, and version gates.
- Map permissions and security answers to `.codex/security.md`, dependency review needs, and risk register.
- Map ownership facts to code ownership. If no people are known, use roles.

## Gate

If project plan, technology choice, landing conditions, v0.1.0 scope, or review/refactor gate are still unclear, say coding is not ready.

If enough facts exist for a first implementation slice, say coding is allowed only for the listed scope.

## Output

End with:

- Files updated.
- Filled facts.
- Plan status: confirmed, partial, or blocked.
- Next planning questions.
- Missing commands.
- Initial EPIC / FEAT / TASK / BUG entries.
- Risks and assumptions.
- Whether coding is allowed.
