---
name: forgekit-request-code-review
description: Prepare and request an independent ForgeKit code review after code changes, before release or commit gates, or before bounded-auto closure. Use from the maker context to build a minimal review packet and invoke forgekit-code-reviewer without passing conversation history.
---

# Request Independent Code Review

Use this skill from the maker context. Do not perform the independent review yourself.

## Decide the gate

- Documentation-only change: independent review is optional unless risk or user instructions require it.
- Code change: independent review is the default.
- Core logic, API, data, permissions, scripts, release, tag, or bounded-auto closure: independent review is mandatory.

## Build the review packet

Provide only:

1. Task or requirement summary.
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

- `pass`: allow handoff or commit preparation.
- `needs-fix`: return findings to the maker; fix or obtain explicit user risk acceptance, then request review again.
- `manual-review`: stop the gate and request human confirmation.

Record the result in the active change `review.md` when a change folder exists. Otherwise report it in the final handoff.
