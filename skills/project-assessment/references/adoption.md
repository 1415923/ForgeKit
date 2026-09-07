# Project Suitability

## Trigger Boundary

Use this Skill to decide whether ForgeKit is appropriate for a project and whether adoption should be full, constrained, lightweight, or not recommended.

Do not use it to initialize a project, fill bootstrap documents, review code or security, or decide release readiness. Other intents route separately to `project-init`, `document-backfill`, the takeover branch, `code-review`, `security-review`, or `release-check`. A suitability recommendation does not invoke those Skills automatically and does not create a mandatory pipeline.

## Default Mode: Read-Only and Advisory

Assessment is a read-only advisory assessment by default. Inspect available project evidence without creating `.forgekit`, editing AGENTS or CLAUDE entries, installing tools, initializing Git, migrating files, or replacing existing governance.

If the user separately and explicitly authorizes recording the assessment, hand that write to a bounded writer. That bounded writer may change only non-empty explicit writable paths in the authorized project, must record changed-path evidence and validation evidence, preserve confirmed existing content, and must not expand to another finding, path, project, or external action. Recording an assessment does not authorize initialization or remediation.

## Evidence

Assess only relevant dimensions:

- existing governance, ownership, review, and documentation systems
- single-repository, multi-repository, or multi-project boundaries
- user and maintainer responsibilities
- source layout, generated or binary-heavy areas, and current tools
- reproducible build, test, validation, deployment, and recovery evidence
- security, compliance, production, credential, and external-system constraints
- likely need for initialization, bootstrap fill, handover, backfill, or later review
- adoption cost, expected benefit, and conflict with established workflows

Apply the existing-project root and topology contract in `governance/agent-entry-contract.md`. Distinguish the active GovernanceRoot/ProjectRoot from historical, archive, artifact, scratch, or materialized-workspace shadows. Do not use `nearest ancestor wins`, create a root registry, or recommend a second `.forgekit` root when one exact legacy ancestor boundary already resolves the requested ProjectRoot.

Historical shadows are non-blocking by default. They can support a scoped C4 finding only when an authorized write target cannot be uniquely resolved. Evidence/archive executable source is a warning unless an active runtime/build/entry references it or creates source/authority ambiguity. A stale README is also non-blocking unless current authority contradicts it, the proposed write depends on that stale fact, and an evidence-backed C4 failure path exists. Business/workspace README remains user-owned.

Use existing evidence before asking questions. Ask only for missing facts that can change the recommendation. Do not treat missing evidence as permission to automate broadly.

## Decision

Return one result:

- `suitable`: ForgeKit can be adopted with the proposed intensity.
- `suitable-with-constraints`: adoption is useful only under named boundaries or prerequisites.
- `not-recommended`: adoption cost, conflict, or risk outweighs benefit.
- `insufficient-evidence`: the available evidence cannot support a responsible recommendation.

State the evidence, rationale, trust and project boundaries, adoption cost and benefit, conflicts, recommended governance intensity, and the smallest safe next step. The next step may be a separate read-only audit. Do not treat `not-recommended` as an instruction to redesign the project.

When reporting findings, apply `.forgekit/docs/maker-checker-protocol.md`; impact severity does not imply Blocking.

## Authorization and External Actions

Do not initialize ForgeKit or create `.forgekit`, create other project structure, migrate or overwrite rules, call every other Skill, or modify source. Do not commit, push, tag, publish, release, deploy, or operate external systems. Do not automatically invoke initialization. Any later local adoption work or external action requires its own explicit user authorization and routing.
