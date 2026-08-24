---
name: forgekit-request-code-review
description: Prepare and request an independent ForgeKit code review when the user, frozen contract, or evidence-backed consequence makes that gate applicable. Use from the maker context to build a minimal review packet and invoke forgekit-code-reviewer without passing conversation history.
---

# Request Independent Code Review

Use this skill from the maker context. Do not perform the independent review yourself.

## Decide the gate

- Use independent review when the user or frozen contract explicitly requires it, or objective C1-C4 consequence makes independent evidence applicable.
- Code, script, documentation, file count, and bounded-auto execution do not mechanically create the gate.
- When an independent gate exists, self-review cannot satisfy it; when none exists, requesting review remains optional and must not become a new blocker.

## Build the review packet

Provide only:

1. Task or requirement summary.
   Include frozen scope, trust boundary, non-goals, acceptance IDs, authorized stage, and review mode for medium/high risk changes.
2. Base/head range, staged range, or an explicit diff boundary.
3. `git diff --stat`.
4. `git diff` or the exact changed files.
5. Validation and test output actually observed.
6. Known risks, verification gaps, and `TODO_REVIEW` items.

Do not provide the maker's full conversation history, long explanations, self-evaluation, unsupported "already fixed" claims, all `.forgekit/docs/**`, or unrelated project background.

## Request the reviewer

Invoke `forgekit-code-reviewer` with the review packet. Use a fresh native subagent context when available. Do not use a fork that inherits the maker conversation.

If the reviewer agent is unavailable, output:

```text
ReviewDecision: manual-review
ReviewType: self-review
ReviewerAgent: unavailable
TODO_REVIEW: Independent reviewer was not available.
```

Do not convert fallback or same-context self-review into independent review.

## Handle the decision

- `pass`: authorize only the stage named by the governing review request; it does not automatically authorize handoff, commit, smoke, or release.
- `needs-fix`: return findings to the maker; fix or obtain explicit user risk acceptance, then request review again.
- After the normal maker fix round, request `blocker-recheck` with the prior Blocking findings instead of a fresh open-ended review. If governance-only blocking repeats without new mainline evidence, perform simplification review before adding another review layer.
- `manual-review`: stop the gate and request human confirmation.

Record the result in the active change `review.md` when a change folder exists. Otherwise report it in the final handoff.
