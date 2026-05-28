---
name: large-change-planning
description: Plan large, cross-module, migration, refactor, or high-risk changes before implementation. Use when a task may touch many files, unclear boundaries, API/data/config/deployment behavior, or needs staged execution.
---

# Large Change Planning

## Trigger

Use this skill before coding when any condition is true:

- The change may touch more than 5 files or more than 2 modules.
- The change affects API, database, permissions, configuration, deployment, external services, hardware interfaces, or data migration.
- The user asks for a major version, subsystem, rewrite, migration, inherited-project remediation, or broad refactor.
- Ownership, validation commands, rollback, or non-goals are unclear.
- A previous review, refactor, release, or defect gate is still open.

## Workflow

1. Define task boundaries:
   - goal
   - non-goals
   - affected users or workflows
   - expected version or milestone
   - safety constraints and actions that require user confirmation
2. Explore before editing:
   - read `AGENTS.md` or `CLAUDE.md`
   - read the codebase map doc
   - inspect relevant source files, tests, configs, build files, scripts, and docs
   - search for existing implementations and duplicated concepts
   - identify current validation commands
3. Produce or update the exploration report:
   - current behavior and evidence
   - modules, entry points, data flow, and integration points
   - risks, unknowns, constraints, and likely blast radius
   - files read and important source paths
4. Produce or update the implementation plan:
   - staged tasks
   - files likely to change
   - validation per stage
   - rollback or recovery notes
   - user decisions still needed
   - session boundary for each stage
5. Ask for confirmation before broad implementation:
   - summarize planned edits and validation
   - name unresolved risks
   - wait for explicit approval when the task involves broad code changes, dependency install, migrations, external services, push, tag, deploy, or long-running services
6. Implement one stage at a time after confirmation:
   - stay inside the approved scope
   - update docs and task state as work proceeds
   - run agreed validation or record why it could not run
   - stop and revise the plan if evidence contradicts the plan

## Required Outputs

- Exploration report in the project docs when the change is broad or risky.
- Staged implementation plan in the project docs before broad implementation.
- Current stage summary before edits.
- Validation result after each stage.
- Remaining risks and next stage recommendation.

## Rules

- Do not start broad implementation from a vague user request.
- Do not replace exploration with a generic checklist.
- Do not read the whole repository without a search strategy.
- Do not merge unrelated refactors into the stage.
- Do not skip user confirmation for high-risk actions.
- Prefer small staged edits with clear validation over one large change.
