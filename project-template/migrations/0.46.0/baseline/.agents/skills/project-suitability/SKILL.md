---
name: project-suitability
description: Assess whether a new or existing project should adopt ForgeKit and at what governance intensity. Use when the user asks whether ForgeKit fits, what adoption mode is appropriate, or whether a read-only audit should precede adoption. Do not initialize, migrate, or rewrite the project.
---

# Project Suitability

## Trigger Boundary

Use this Skill to decide whether ForgeKit is appropriate for a project and whether adoption should be full, constrained, lightweight, or not recommended.

Do not use it to initialize a project, fill bootstrap documents, conduct a handover audit, review code or security, or decide release readiness. Those intents route separately to `project-init`, `project-bootstrap-fill`, `handover-review`, `code-review`, `security-review`, or `release-check`. A suitability recommendation does not invoke those Skills automatically and does not create a mandatory pipeline.

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

Use existing evidence before asking questions. Ask only for missing facts that can change the recommendation. Do not treat missing evidence as permission to automate broadly.

## Decision

Return one result:

- `suitable`: ForgeKit can be adopted with the proposed intensity.
- `suitable-with-constraints`: adoption is useful only under named boundaries or prerequisites.
- `not-recommended`: adoption cost, conflict, or risk outweighs benefit.
- `insufficient-evidence`: the available evidence cannot support a responsible recommendation.

State the evidence, rationale, trust and project boundaries, adoption cost and benefit, conflicts, recommended governance intensity, and the smallest safe next step. The next step may be a separate read-only audit. Do not treat `not-recommended` as an instruction to redesign the project.

## Authorization and External Actions

Do not initialize ForgeKit or create `.forgekit`, create other project structure, migrate or overwrite rules, call every other Skill, or modify source. Do not commit, push, tag, publish, release, deploy, or operate external systems. Do not automatically invoke initialization. Any later local adoption work or external action requires its own explicit user authorization and routing.
