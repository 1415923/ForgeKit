---
name: handover-review
description: Audit and stabilize an inherited or existing project before further development. Use when Codex is asked to take over a project, inspect bugs, assess maintainability, identify compatibility boundaries, repair defects without changing major architecture, or plan future development based on current code, customer requirements, and deployment constraints.
---

# Handover Review

## Workflow

1. Read the governance overview in `governance/`, `.codex/handover.md`, project root files, `.codex/`, `docs/`, build configs, startup docs, and relevant stack rules.
2. Evidence-first gate for existing projects:
   - Before asking broad questions, inspect candidate docs: root README, docs README, usage guide, install/setup guide, quick start, test guide, deployment guide, API docs, architecture notes, changelog, CI config, dependency manifests, package scripts, Makefile, Docker files, and test directories.
   - Extract answers from those files first. Do not ask the user for facts already present in inspected docs unless the docs are contradictory, stale, unsafe, or incomplete.
   - Report the evidence summary before questions: files read, stack facts, startup commands, test commands, deployment notes, environment variables, known limitations, contradictions, and remaining unknowns.
   - Ask only targeted questions about contradictions, missing evidence, or decisions that local files cannot answer.
3. Identify current technology stack, runtime environment, deployment method, CI/CD path, task or issue model, upstream/downstream dependencies, and compatibility boundaries from evidence.
4. Run or propose safe read-only checks first: `git status`, build config inspection, test command discovery, service requirements.
5. Perform broad review before changing code:
   - startup and build risks
   - correctness bugs
   - security risks
   - compatibility risks
   - ownership gaps for core modules
   - task or issue model gaps
   - duplicated or excessive files
   - missing tests and docs
6. Classify issues:
   - P0: cannot start, data loss, security critical, main flow broken
   - P1: clear bug, important compatibility risk, important test gap
   - P2: quality, duplication, local design debt
   - P3: major architecture or technology change
7. Fix P0/P1 first with minimal compatible changes.
8. Put P2/P3 into roadmap or review/refactor gate. Do not make large architecture changes during handover unless the user explicitly confirms.
9. For high-impact changes, require change impact assessment before implementation.

## Compatibility Boundaries

Do not change these by default:

- public API paths, request shape, response shape, error codes
- database schema or existing data semantics
- authentication, authorization, token, cookie, or session behavior
- external service contracts
- deployment method, ports, environment variables
- CI/CD jobs, artifact names, runtime environment, and rollback method
- module ownership, required reviewers, and Critical areas
- file storage paths or object storage layout
- user-visible core flows

## Required Documents

Update or create:

- inherited project audit document in `docs/`
- defect repair plan in `docs/`
- version roadmap in `docs/`
- risk register in `docs/`
- traceability matrix in `docs/`
- technical debt record in `docs/`
- quality metrics baseline in `docs/`
- environment matrix and release pipeline facts in `docs/`
- code ownership matrix in `docs/`
- project task board in `docs/`
- incident or defect review in `docs/` for severe or repeated historical issues
- change impact assessment in `docs/` when high-impact changes are proposed
- governance notes in `governance/` when version or architecture policy changes
- changelog or version record in `docs/`

## Output

End with:

- Evidence read and facts extracted.
- Current project status.
- Compatibility boundaries.
- P0/P1 defects and proposed fixes.
- P2/P3 items deferred to review/refactor or roadmap.
- Technical debt baseline.
- Quality baseline.
- Environment and CI/CD baseline.
- Ownership and review baseline.
- Task and issue baseline.
- Required change impact assessments.
- Required incident or defect reviews.
- Whether new feature development is allowed yet.
- Required user confirmations.
