---
name: document-backfill
description: Incrementally migrate facts from existing project documents into ForgeKit project docs. Use when the user asks to read old README, usage, test, architecture, deployment, or design documents and complete `.codex/` or `docs/` without losing detail.
---

# Document Backfill

## Trigger

Use this skill when the user asks to:

- read existing project documents and fill ForgeKit docs
- migrate old project docs into `docs/`
- digest usage, test, deployment, architecture, API, or design notes
- avoid reading all docs at once
- preserve details from legacy or inherited project documentation

## Workflow

1. Confirm source and target roots:
   - source documents, such as old `docs/`, `README`, usage notes, test plans, deployment notes, API docs, architecture docs, design docs, changelog, or release notes
   - target ForgeKit docs, usually `.codex/`, `docs/`, and `governance/`
2. Build a source document queue:
   - list candidate files with short reason and likely target docs
   - sort by project overview, startup/setup, architecture, testing, deployment, API, known issues, release notes
   - do not read every source document into one large summary
3. Process exactly one source document at a time:
   - read the source document
   - extract transferable facts
   - classify facts as Confirmed, Assumption, Conflict, Stale, or Unknown
   - identify target ForgeKit docs to update
   - update target docs immediately
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

- Project purpose, users, scope -> project plan doc, `.codex/project.md`, `.codex/scope.md`
- Startup, commands, local workflow -> `.codex/commands.md`, local toolchain check doc
- Architecture and modules -> architecture doc, codebase map doc
- Requirements and acceptance -> requirements doc, traceability matrix doc
- Test plans and validation -> testing doc, `.codex/testing.md`
- Deployment and environments -> deployment doc, environment matrix doc, release pipeline doc
- API behavior -> API doc
- Data model -> database design doc
- Known defects -> defect review doc, defect repair plan doc
- Risks and operations -> risk register doc, incident review doc
- Release history -> version update record doc, version roadmap doc
- Ownership and review -> code ownership doc, project task board doc

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
