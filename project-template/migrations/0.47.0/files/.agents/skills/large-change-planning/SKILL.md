---
name: large-change-planning
description: Plan changes with material trust, compatibility, migration or recovery impact. Do not trigger from file count.
---

# Large Change Planning

## Trigger Boundary

Use when objective impact requires a staged plan: crossing a trust boundary, changing a public interface, migrating persistent data, changing authentication or permissions, introducing an irreversible step, creating high rollback cost, coordinating independent projects or release units, or resolving uncertainty that materially changes safe implementation.

A small diff can trigger this Skill when its impact is high. A broad deterministic projection or other local, reversible, fully verifiable change does not trigger it merely because many files or modules are involved. Do not use it for an ordinary bounded fix whose scope and validation are already clear.

## Read-Only Default and Authorization

Assessment and planning are read-only by default. Only an explicit request to create or update a named change artifact authorizes that bounded local write, without asking again for equivalent authorization. Approval of a plan or design authorizes only the stage stated in the plan; it is not authorization for every implementation stage.

Planning never authorizes dependency installation, commit, push, publish, release, deploy, production change, data deletion, irreversible migration, permission or credential change, or work in an adjacent project. Those actions require specific target-and-impact authorization.

## Impact Branch

Apply, but do not redefine, the neutral execution contract in `governance/ai-engineering-loop.md`. Declare each planned execution as `DIAGNOSTIC`, `SMOKE`, or `FORMAL`; keep Effect Risk separate under `governance/agent-entry-contract.md`. A real or paid call is not automatically Formal, and there is no release execution intent.

Use the same neutral owner to state impact from trust boundary, irreversibility, persistent data, public compatibility, security and permissions, external effects, rollback difficulty, deployment impact, verification capability, and evidence uncertainty. Do not score risk from counts or use a fixed threshold.

When scope is clear, local, reversible, low impact, and deterministically verifiable, use a short plan or explicitly route back to direct implementation. Do not create a long planning document merely to prove this Skill was selected.

## Planning Contract

For a genuinely high-impact or multi-stage change, establish only the artifacts proportionate to risk and freeze:

- scope and affected users or systems
- trust boundary and authorized project roots
- non-goals
- confirmed facts, assumptions, and unresolved evidence
- stage authorization and the paths each stage may write
- acceptance IDs with positive and rejection cases
- dependencies, risks, and verification evidence per stage
- rollback or recovery mechanism
- any applicable independent checker condition supported by objective consequence or an explicit gate
- Formal claim, evidence location, retention, and applicable acceptance/review steps when Formal execution is planned

An active change artifact is the plan authority. Do not create a competing implementation plan or copy the same contract across several documents.

## Stage Boundary

Explore before proposing edits. Do not start implementation in this Skill. At each handoff, state the currently authorized stage, allowed write scope, required validation, rollback, blockers, and which acceptance IDs remain open. If evidence changes scope, trust boundary, or acceptance, return to planning instead of silently expanding implementation.

Independent review is required when objective impact or an explicit gate requires it; it is not mandatory for every low-risk code edit. Self-review does not satisfy an independent gate.

Expected Change inside the frozen contract is not Blocking. Treat only evidence-backed unauthorized Post-Freeze Drift under the neutral contract as a possible C3 finding. If repeated governance-only blocking produces no new mainline evidence, perform the neutral simplification review before proposing another governance layer; do not create a counter, state file, or checker.

## Minimum Writeback and Output

Without explicit artifact-write authorization, return the plan in chat and make no repository change. With authorization, update only the active change artifacts that own the plan and confirmed state. Do not write speculation as fact or historical intent as current completion.

End with the risk rationale, scope/trust boundary/non-goals, assumptions, stage authorization, acceptance IDs, verification and rollback, checker condition, and the next authorized decision. Do not proceed into a later stage automatically.
