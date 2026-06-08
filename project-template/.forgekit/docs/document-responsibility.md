# Document Responsibility

Use this matrix to decide where facts belong before editing documents.

| Document | Responsible For | Not Responsible For | Update Trigger |
| --- | --- | --- | --- |
| `README.md` | Project purpose, quick start, user-visible run path | Long governance process, internal history | User entry, startup, or product positioning changes |
| `AGENTS.md` / `CLAUDE.md` | AI entry, boundary rules, task routing | Long checklists, template bodies, historical records | Startup order, write boundary, or gate changes |
| `.forgekit/project-boundary.yml` | ForgeKitRoot, ProjectRoot, managed docs root, change root, write policy | Product plan or architecture detail | Directory layout or write policy changes |
| `.forgekit/docs/*` | Current ForgeKit-managed project facts | One-off implementation logs | Current facts, requirements, architecture, validation, or release state changes |
| `.forgekit/changes/<id>/*` | Medium/high risk change proposal, tasks, verification, review, and ship notes | Long-term current-state facts | Change start, implementation, verification, review, or release |
| `docs/**` business docs | Existing business documentation and evidence source | ForgeKit governance templates by default | User explicitly asks to update business docs |

Business docs are read-mostly by default. Read and cite them as evidence, but do not write ForgeKit governance templates into them unless the user explicitly confirms the target files and reason.
