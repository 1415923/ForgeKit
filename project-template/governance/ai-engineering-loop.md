# AI Engineering Loop

ForgeKit turns AI coding into a lightweight engineering loop: clarify the work, size its objective impact, create only the needed reviewable artifacts, implement within the authorized scope, verify, review as applicable, and write confirmed facts back before closure.

ForgeKit does not replace the framework, CI, issue tracker, or architecture process. It provides project-local prompts, Skills, templates, and checks so work can keep making evidence-backed progress inside visible boundaries.

## Execution Intent

Execution Intent describes what an execution is meant to prove. It has exactly three values:

| Intent | Meaning |
| --- | --- |
| `DIAGNOSTIC` | Bring-up or debugging. A failed attempt may be repaired and rerun; it does not establish Formal identity. |
| `SMOKE` | Demonstrates that a real path can run. It may be repaired and rerun within its bounded Effect envelope; it does not automatically become Formal or release evidence. |
| `FORMAL` | Produces claim-bearing evidence under a predeclared contract. Only this intent creates claim-critical freeze obligations. |

Execution Intent is independent from Effect Risk. A real, paid, credentialed, or external call is not automatically `FORMAL`; every Intent must separately comply with the Effect Risk and authorization contract in `agent-entry-contract.md`. There is no `RELEASE` Execution Intent. Release readiness is a separate consumer decision.

## Progress-Preserving Execution

- Preserve the caller's declared Intent across an attempt. Do not relabel a failed `DIAGNOSTIC` or `SMOKE` run as `FORMAL`, or relabel an inconvenient Formal result as diagnostic.
- Diagnostic bring-up and zero-call failures may be fixed and rerun without creating a Formal evidence identity.
- A bounded Smoke may exercise a real path when its external effects, credentials, budget, retries, and stop conditions are authorized. Real execution alone does not make it Formal or trigger release review.
- For `FORMAL`, declare the claim, applicable acceptance, evidence location, and any required aggregate, review, or checker before execution. Do not add those gates after seeing the outcome.
- Continue safe mainline work while evidence supports it. A warning, hygiene issue, or command-level nonzero does not stop unrelated work unless the universal finding contract proves a scoped Blocking consequence.

## Change Impact and Artifacts

| Change impact | Typical work | Proportionate workflow |
| --- | --- | --- |
| low | Local, reversible, no public behavior or persistent-state impact, and directly verifiable | Clarify if needed, edit surgically, run relevant validation, summarize. A change folder is optional. |
| medium | Small feature, public template/script behavior, compatibility surface, or a change needing staged evidence | Use `proposal.md`, `tasks.md`, `verification.md`, and `review.md`; confirm the plan before implementation. |
| high | Architecture, migration, security/permission, production data, irreversible action, deployment, or hard-to-verify compatibility impact | Add `design.md` and `ship.md`; confirm design and stage authorization before implementation. Use `retro.md` only when useful. |

Judge impact from trust boundaries, irreversibility, persistent data, public compatibility, security and permissions, external effects, rollback difficulty, deployment impact, verification capability, and evidence uncertainty. File, line, or module count does not determine impact. User authorization permits an action but does not lower its objective impact.

## Freeze Before Implementation

For medium and high-impact changes, freeze the scope, trust boundary, non-goals, stage authorization, and a risk-proportional acceptance matrix before implementation. Each acceptance ID needs a positive case, a key rejection case, and evidence from the real entry or orchestration path. Low-impact changes may keep the lightweight flow.

Changing a frozen contract returns the affected scope to design or acceptance. Review findings must not silently enlarge it.

## Expected Change vs Post-Freeze Drift

- A change explicitly required by the frozen scope or acceptance contract is Expected Change and is not Blocking merely because the baseline differs.
- Post-Freeze Drift requires a locatable frozen reference and a change outside or contrary to it.
- Only unauthorized Post-Freeze Drift with a supported C3 failure path may block the affected claim or stage. It must still satisfy the universal finding contract in `maker-checker-protocol.md`.
- New evidence may require an explicit return to planning; it does not authorize a reviewer or maker to rewrite the contract implicitly.

## Formal Evidence Retention

First valid Formal evidence must not be silently overwritten, replaced, discarded, hidden, or cherry-picked to improve a claim. Its provenance and result must remain traceable under the project's applicable evidence and retention policy.

The evidence may be compressed, moved, archived, or removed under an existing authorized policy, provided an active claim remains traceable and verifiable. ForgeKit does not require a materialized workspace to remain forever in its original location and does not create a permanent physical-storage regime.

```text
claim-integrity retention
!=
permanent physical storage
```

## Formal Authority Chain

```text
Formal execution
-> first valid evidence retained and traceable
-> applicable acceptance / aggregate / review required by the predeclared Formal contract
-> current fact owner explicitly references accepted evidence
-> current authority
```

Acceptance, aggregate, review, and checker are required only as applicable to the predeclared Formal contract and a real C1-C4 consequence. A Formal run does not automatically require all of them or an independent review. First valid evidence is not automatically current authority, and this chain does not add a new gate.

## Review Convergence

Review consumes the universal `impact_severity` and `blocking` fields from `maker-checker-protocol.md`. Severity does not decide the gate. A review pass authorizes only the stage named in the proposal; commit, external smoke, full execution, and release remain separate decisions.

After a normal maker fix round, re-review should focus on prior Blocking findings. If repeated fixes do not resolve the supported failure path, return to design to simplify, split, or refactor rather than extending an indefinite patch loop.

## Governance Stop-Loss

Repeated governance-only blocking without new mainline evidence requires a simplification review before another governance or review layer is added.

This is a heuristic, not a counter, state file, checker, validator, or fixed “Nth occurrence” trigger. Another layer requires either a newly supported C1-C4 consequence under the universal finding contract or an explicit user gate. Otherwise simplify or remove the redundant layer and preserve progress.

## Completion

- Record actual verification results in `verification.md` when the change contract requires it.
- Record applicable review decisions and residual risk in `review.md`.
- For high-impact changes, record release and rollback facts in `ship.md` when that stage is reached.
- Before task/change/phase closure, handoff, or ship, write confirmed facts to their responsible current owner; active change or checkpoint artifacts are only temporary carriers.
- Do not declare completion from “tests passed” alone when applicable acceptance, review, current-owner writeback, or rollback evidence is still open.
