---
name: document-backfill
description: Backfill an identified owner document from already implemented, verifiable project facts. Use only for an explicit factual backfill request or handoff; do not use for future design, project initialization, broad governance generation, planning, or implementation.
---

# Document Backfill

## Trigger Boundary

Use when code or implementation already exists, a specific corresponding document is missing or stale, and the user explicitly asks to backfill it from verifiable facts. An explicit handoff may identify the source set and owner document.

Do not use for future design, new-project initialization, bootstrap placeholders, automatic generation of a governance suite, current work logging, or writing a plan as completed work.

## Default Mode and Authorization

Source discovery and a backfill preview are read-only. When the user explicitly authorizes backfill for a source set and target owner, edit that bounded local scope without asking again for equivalent authorization.

Backfill authorization does not include business-code changes, governance-template edits, adjacent projects, external source retrieval, commit, push, publish, release, deploy, deletion, or irreversible migration. Obtain specific authorization before any such action.

## Fact Backfill Workflow

1. Identify the missing or stale document, its owner, the source set, and the fact domain. Use `.forgekit/docs/document-responsibility.md` to select one owner for each fact.
2. Read code, configuration, tests, commands, and user-provided evidence relevant to that domain. Distinguish confirmed current facts from assumptions, conflicts, stale history, and unknowns.
3. Choose a reviewable batch based on shared fact domain, source consistency, rollback simplicity, risk, and remaining context capacity. Do not use a fixed document count or mechanically stop after a fixed batch size.
4. Backfill only confirmed current facts. Preserve the target's structure and user customization, avoid repeating existing content, and do not duplicate one fact across owner documents.
5. Record narrow source paths when they materially support later verification. Keep each completed batch recoverable by reporting the processed sources, target, validation, conflicts, and remaining work.
6. Stop or narrow the batch when evidence conflicts, crosses fact domains, changes an owner decision, or cannot be safely verified.

## Conflict and Uncertainty Handling

When code, documents, tests, or user statements conflict, do not guess or select a convenient version. Preserve confirmed user facts, identify each source, mark the conflict `TODO_REVIEW`, and leave the disputed target content unchanged until resolved.

Evidence gaps remain `UNKNOWN` or `TODO_REVIEW`; they never authorize plausible completion. Do not write future behavior, architecture, deployment, ownership, or completion state as fact merely to make a document look complete.

## Minimum Writeback

Write only the owner document required by the authorized fact domain and the minimum recoverable progress needed for a longer backfill. Do not create unrelated documents, rewrite the full documentation set, or place project business facts in governance files.

End each actual batch with sources processed, owner document changed, confirmed facts added, existing customization preserved, conflicts or unknowns left unresolved, validation performed, and the next optional batch. Backfill never starts implementation automatically.
