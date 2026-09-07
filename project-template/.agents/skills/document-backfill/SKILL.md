---
name: document-backfill
description: Fill bootstrap gaps or backfill existing owner documents from evidence, only on an explicit request.
---

# Document Backfill

Use only for an explicit fill/backfill request or authorized handoff. Inspect-only requests remain read-only.
- Initialized project with unfilled setup fields: [bootstrap](references/bootstrap.md).
- Missing or stale documentation of implemented facts: [facts](references/facts.md).

Load only the selected branch and the relevant fact owner. Fill evidence-backed facts, preserve customization, and leave unknowns unresolved.
Completion means the requested gaps are handled, relevant validation is complete, and remaining conflicts are reported.
Do not require every document to be populated or start implementation after filling.
