# Task Intake

## Purpose

This is the source-first ledger for assigned work. Keep the original task source here before turning it into requirements, task-board items, work-log entries, or changelog notes.

Use this file to answer one question: what exactly was assigned, by whom, when, for whom, and under which human review status?

Boundaries:

- Preserve redacted original text. Do not keep only an AI summary.
- Do not store passwords, tokens, certificates, private keys, internal addresses, private package contents, or sensitive configuration values.
- This file is not `requirements.md`, not `task-board.md`, not `work-log.md`, and not `changelog.md`.
- If the source has not been reviewed by a person, keep `Human Review: pending`.

## When to Use

Create a source record when work comes from:

- leader-plan-cell
- wechat
- meeting
- document
- manual-note

## Source Record Template

```text
Source ID: SRC-YYYYMMDD-001
Source Type: leader-plan-cell | wechat | meeting | document | manual-note
Received At: YYYY-MM-DD HH:MM
Sender / Source: <name or source label>
Original Location: <chat, meeting note, document path, plan row, or pointer>
Human Review: pending | confirmed | corrected | rejected
Confidentiality: normal | sensitive-redacted
Derived Task IDs: TASK-001, BUG-001, FEAT-001
```

### Original Text

Paste the redacted original assignment here. Keep wording close enough for a human to check whether AI misunderstood or over-compressed it.

### Responsibility Split

| Person / Role | Responsibility | Confirmation |
| --- | --- | --- |
| <name or role> | <responsibility> | pending |

### Time Window

| Field | Value |
| --- | --- |
| Expected start | TBD |
| Expected finish | TBD |
| Deadline / checkpoint | TBD |
| Time ambiguity | TBD |

### AI Interpretation

Keep this short.

- Parsed intent:
- Scope:
- Out of scope:
- Assumptions:

### Derived Tasks

| Task ID | Title | Source ID | Status |
| --- | --- | --- | --- |
| TASK-001 | TBD | SRC-YYYYMMDD-001 | Todo |

### Open Questions

| Question | Why it matters | Owner | Status |
| --- | --- | --- | --- |
| TBD | TBD | TBD | Open |

### Human Review Status

| Field | Value |
| --- | --- |
| Human Review | pending |
| Reviewer | TBD |
| Review Notes | TBD |
| Corrected Interpretation | TBD |

## Redaction Rules

- If sensitive information appears, redact it before writing and set `Confidentiality: sensitive-redacted`.
- Keep enough context to preserve meaning, but never copy secrets.
- After confirmation, sync only stable facts to `requirements.md`.
- Sync execution state to `task-board.md` with Source ID backlinks.
- Sync completed user-visible changes to `changelog.md`; do not copy the source text there.
