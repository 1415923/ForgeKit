# Project Bootstrap Fill

## Trigger Boundary

Use only when the project is already initialized, bootstrap owner documents contain placeholders or clear omissions, and the user asks to fill those gaps from existing evidence. An explicit handoff from `project-init` is also valid.

Do not replace `project-init`, `project-assessment`, the facts backfill branch, project implementation, a full documentation rewrite, or release review. Do not create a chain that routes back into initialization.

## Default Mode and Authorization

When the request is only to inspect gaps, produce a read-only preview. When the user explicitly asks to fill bootstrap documents in the current project, perform reversible local edits within those documents without asking again for equivalent authorization.

Local fill authorization never includes business code, unrelated documents, adjacent projects, commit, push, publish, release, deploy, deletion, external systems, or irreversible migration.

## Evidence Fill Contract

1. Read existing project evidence before editing: the boundary, initialization state, selected stack material, current owner documents, relevant README or build configuration, and the user's confirmed facts.
2. Identify the exact placeholder or missing field and the document that owns it. Use `governance/project-bootstrap-fill.md` and `.forgekit/docs/document-responsibility.md` for mapping; do not copy their full mapping into this Skill.
3. Fill only gaps supported by code, configuration, tests, commands, current project files, or explicit user facts.
4. Preserve existing customization and confirmed content. Merge surgically; do not rewrite a document merely to normalize its style.
5. Use `TODO_REVIEW` or `UNKNOWN` when evidence is insufficient. Do not invent stack, commands, owners, environments, deployment, security, roadmap, or task state.
6. If new evidence conflicts with an existing confirmed fact, do not write the conflicting field or choose the newest guess. Report both sources and request resolution only when it changes the fill result.
7. Validate the changed documents and stop when the requested gaps are addressed. Do not require every section to be filled, use a fixed question count, or create unrelated documents.

## Minimum Writeback

Write each confirmed fact once, in its owning bootstrap document. Record only the minimum state needed to explain the fill, including explicit unresolved items. Do not turn historical plans into current completion, duplicate facts across owners, or place project business facts in governance templates.

End with the gaps inspected, files actually changed, evidence used, conflicts left untouched, unresolved markers, and validation performed. Filling bootstrap facts does not authorize implementation or external actions.
