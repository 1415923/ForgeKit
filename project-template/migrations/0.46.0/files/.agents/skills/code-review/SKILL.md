---
name: code-review
description: Review an existing implementation, diff, tests, or prior review findings for correctness, regressions, boundary conditions, and evidence gaps. Use for initial code review, independent checker work, or targeted findings recheck. Do not use to implement a feature, perform a full security audit, or decide release readiness.
---

# Code Review

## Trigger Boundary

Use this Skill when the user asks to review code or an existing diff, validate implementation evidence, perform an independent checker pass, or recheck named findings.

Do not use it as the maker for a requested implementation. Route a primary security audit to `security-review`, release readiness to `release-check`, project takeover to `handover-review`, and ForgeKit adoption fit to `project-suitability`. Select only the Skill or Skills justified by the actual intent; these review Skills are not a mandatory pipeline.

## Default Mode: Read-Only

Review is read-only by default. Inspect relevant files, diffs, tests, commands, and current change artifacts without modifying source, tests, governance, or status documents. Discovering a defect does not authorize repair.

If the user or governing workflow separately and explicitly authorizes a named repair, end the reviewer role and hand the named finding to a bounded maker workflow. That bounded maker may change only non-empty explicit writable paths, must record changed-path evidence and validation evidence, and must not expand to another finding, path, project, or external action. A later independent recheck returns to read-only mode.

## Evidence and Scope

Start with the requested diff or finding set. Load project rules and active change artifacts only when they affect the reviewed contract. Prefer current code and reproducible command or test evidence over plans or narrative claims.

Check correctness, regressions, error and boundary paths, compatibility, data or migration effects, ownership boundaries, and missing tests. Invoke a deeper security review only when the change has an actual security surface. Invoke a release check only for release readiness.

When evidence is missing or cannot be reproduced, report `NEEDS_TEST` or state that the finding cannot be closed. Do not infer a pass from documentation that merely claims success.

## Review Modes

- Initial review: assess the frozen scope and acceptance contract. Report newly discovered blocking issues only when they expose a real authorization, data, execution, artifact, safety, or false-success failure.
- Independent checker: remain separate from the maker and verify evidence from a fresh read-only context. Self-review does not satisfy an independent gate.
- Findings recheck: focus on the named prior findings and classify each as Closed, Partially closed, or Still open. A regression introduced by the fix may still block when it violates the frozen contract or causes a critical consequence. Keep unrelated hardening as follow-up.

A review decision authorizes only the stage named by the governing proposal.

## Risk and Checker Boundary

Require an independent checker because of objective impact, explicit user request, or an existing stage, security, migration, or release gate. Do not require one merely because a change touches a particular number of files, lines, or modules.

Apply the universal finding contract in `.forgekit/docs/maker-checker-protocol.md`. Impact severity and Blocking are independent. A high-impact consequence does not stop the current action without a supported failure path and bounded scope.

## Output

Lead with findings and cite the closest available file, line, command, or test evidence. Every finding reports:

- `impact_severity: CRITICAL | MAJOR | MINOR | NOTE`
- `blocking: YES | NO`
- `evidence`

Every `blocking: YES` finding also reports exactly one `primary_consequence: C1 | C2 | C3 | C4`, plus `failure_path` and `blocked_scope`. Add `secondary_consequences` or `validation_relevance` only when evidence supports them. Never infer Blocking from severity, a checker exit, or `--strict`.

Then state open questions, test gaps, the stage-limited decision, and residual risk. If there are no findings, say so and identify any remaining validation gap.

## External Actions

Do not commit, push, tag, release, publish, deploy, rotate credentials, change production permissions, or perform another external or irreversible action. Each such action requires explicit user authorization and is never implied by review or fix authorization.
