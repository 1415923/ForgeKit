---
name: document-backfill
description: Incrementally migrate facts from existing project documents into ForgeKit managed docs. Use when the user asks to read old README, usage, test, architecture, deployment, or design documents and complete `.codex/` or `.forgekit/docs/` without losing detail.
---

# Document Backfill

## Trigger

Use this skill when the user asks to:

- read existing project documents and fill ForgeKit managed docs
- migrate old project docs into `.forgekit/docs/`
- digest usage, test, deployment, architecture, API, or design notes
- avoid reading all docs at once
- preserve details from legacy or inherited project documentation

## Workflow

1. Confirm source and target roots:
   - source documents, such as read-mostly business `docs/`, `README`, usage notes, test plans, deployment notes, API docs, architecture docs, design docs, changelog, or release notes
   - target ForgeKit managed docs, usually `.codex/`, `.forgekit/docs/`, and `governance/`
2. Build a source document queue:
   - list candidate files with short reason and likely `.forgekit/docs/` targets
   - sort by project overview, startup/setup, architecture, testing, deployment, API, known issues, release notes
   - do not read every source document into one large summary
3. Process exactly one source document at a time:
   - read the source document
   - extract transferable facts
   - classify facts as Confirmed, Assumption, Conflict, Stale, or Unknown
   - identify target ForgeKit managed docs to update
   - update target `.forgekit/docs` immediately
   - record source file paths for imported facts when practical
   - report what was migrated before moving to the next source document
4. Preserve detail:
   - startup steps and environment variables
   - test scenarios, expected results, test data, and validation commands
   - deployment paths, ports, services, credentials boundaries, and rollback notes
   - API behavior, request and response shape, error behavior, and compatibility rules
   - architecture decisions, module responsibilities, data flow, external dependencies
   - known defects, limitations, operational risks, and release constraints
5. Ask only targeted questions:
   - ask when source docs contradict each other
   - ask when a fact is unsafe, stale, incomplete, or impossible to map
   - do not ask for information already found in a source document
6. Stop conditions:
   - source queue is complete
   - user asks to stop
   - a contradiction blocks accurate backfill
   - a target doc would require a product or architecture decision not supported by evidence

## Target Mapping

- Project purpose, users, scope -> `.forgekit/docs/project-plan.md`, `.codex/project.md`, `.codex/scope.md`
- Startup, commands, local workflow -> `.codex/commands.md`, `.forgekit/docs/local-toolchain.md`
- Architecture and modules -> `.forgekit/docs/architecture.md`, `.forgekit/docs/codebase-map.md`
- Requirements and acceptance -> `.forgekit/docs/requirements.md`, `.forgekit/docs/traceability.md`
- Test plans and validation -> `.forgekit/docs/testing.md`, `.codex/testing.md`
- Deployment and environments -> `.forgekit/docs/deployment.md`, `.forgekit/docs/environment-matrix.md`, `.forgekit/docs/release-pipeline.md`
- API behavior -> `.forgekit/docs/api.md`
- Data model -> `.forgekit/docs/database-design.md`
- Known defects -> `.forgekit/docs/defect-review.md`, `.forgekit/docs/defect-fix-plan.md`
- Risks and operations -> `.forgekit/docs/risk-register.md`, `.forgekit/docs/incident-review.md`
- Release history -> `.forgekit/docs/changelog.md`, `.forgekit/docs/version-roadmap.md`
- Ownership and review -> `.forgekit/docs/code-ownership.md`, `.forgekit/docs/task-board.md`

## Output After Each Source Document

End each source document pass with:

- Source processed.
- Target docs updated.
- Confirmed facts migrated.
- Conflicts or stale facts found.
- Unknowns that still need user input.
- Next source document proposed.

## Rules

- Do not collapse multiple source docs into one generic summary.
- Do not overwrite real project facts with template text.
- Do not invent missing details.
- Do not start coding during backfill unless the user explicitly changes the task.
- Prefer smaller, traceable updates over broad rewrites.
- If a target doc already contains useful content, merge carefully and preserve it.
